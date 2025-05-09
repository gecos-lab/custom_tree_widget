"""custom_tree.py © Andrea Bistacchi"""

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QSizePolicy,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag


class DraggableButton(QPushButton):
    """
    DraggableButton extends QPushButton to implement a button widget
    that can be clicked and dragged. It supports checkable behavior and is
    sized according to its size hint. The primary feature of this button is
    its ability to initiate drag-and-drop actions when it is dragged with the
    left mouse button.

    :ivar _text: The text is displayed on the button.
    :type _text: Str
    :ivar _parent: The parent widget, if any, that contains this button.
    :type _parent: QWidget or None
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(self.sizeHint())
        self.setMaximumSize(self.sizeHint())

    def mouseMoveEvent(self, event):
        """
        Handles the mouse move event in the context of a draggable object. This method initiates
        a drag-and-drop operation when the left mouse button is pressed and moved within the
        object's bounds.

        :param event: The mouse event that triggers this method.
        :type event: QMouseEvent
        :return: None
        """

        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)
            drag.setHotSpot(event.pos() - self.rect().topLeft())
            drag.exec(Qt.MoveAction)


class CustomHeader(QWidget):
    """
    CustomHeader is a QWidget subclass that provides a draggable and interactive
    button-based header interface. It allows users to reorder buttons by dragging
    and dropping, and emits a signal when the button order changes.

    CustomHeader can be used in applications where a customizable header
    layout with draggable elements is needed.

    :ivar layout: Layout manager for arranging buttons within the header.
    :type layout: QHBoxLayout
    :ivar buttons: List of draggable buttons is displayed in the header.
    :type buttons: List
    """

    buttonToggled = Signal()

    def __init__(self, parent=None, labels=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.buttons = []
        for label in labels:
            button = DraggableButton(label)
            button.clicked.connect(self.on_button_toggled)
            self.layout.addWidget(button)
            self.buttons.append(button)
        self.layout.addStretch()
        self.setAcceptDrops(True)

    def on_button_toggled(self):
        """
        Handles the button toggle event by emitting the `buttonToggled` signal.
        This activates/deactivates a column in the tree hierarchy.

        :raises: This method does not explicitly raise any exceptions.
        :return: None
        """

        self.buttonToggled.emit()

    def get_order(self):
        """
        Extracts the ordered list of button objects, defining the hierarchy of the tree.

        This method iterates over a list of button objects, checks if each button is
        selected (checked), and then extracts the text of all buttons that are checked.

        :return: A list of strings containing the text of checked buttons.
        :rtype: List
        """

        order = [button.text() for button in self.buttons if button.isChecked()]
        return order

    def dragEnterEvent(self, event):
        """
        Handles the drag enter event when a button is dragged in the header.
        This method is used to provide immediate visual feedback or acceptance/rejection
        of the drag operation based on the type of content being dragged.

        :param event: The QDragEnterEvent contains information about the drag
                      operation, such as the mime data and suggested actions.
        :type event: QDragEnterEvent
        :return: None
        """

        event.accept()

    def dragMoveEvent(self, event):
        """
        Handles the drag move event during a drag-and-drop operation. This method is
        triggered when the drag operation moves within the widget's boundaries. It is
        responsible for accepting or rejecting the drag operation depending on the
        current logic or implementation criteria.

        :param event: The QDragMoveEvent instance contains details of the drag move
            event, such as position and modifiers.
        :return: None
        """

        event.accept()

    def dropEvent(self, event):
        """Handles the drop event to rearrange draggable buttons within the layout."""
        source_button = event.source()
        if source_button not in self.buttons:
            return

        self._rearrange_button(source_button, event.position().toPoint())
        self._update_button_list()
        self.buttonToggled.emit()

    def _rearrange_button(self, source_button, drop_position):
        """Helper method to handle button rearrangement logic."""
        self.layout.removeWidget(source_button)
        closest_button, index = self._find_closest_button(drop_position)

        if closest_button:
            if self._should_insert_after(closest_button, drop_position):
                index += 1
            self.layout.insertWidget(index, source_button)
        else:
            self.layout.addWidget(source_button)

    def _find_closest_button(self, position):
        """Find the closest button to the given position."""
        closest_button = None
        min_distance = float("inf")
        index = -1

        for i, button in enumerate(self.buttons):
            distance = abs(button.geometry().center().x() - position.x())
            if distance < min_distance:
                min_distance = distance
                closest_button = button
                index = i

        return closest_button, index

    def _should_insert_after(self, button, position):
        """Determine if the button should be inserted after the reference button."""
        return position.x() > button.geometry().left() + button.geometry().width() / 2

    def _update_button_list(self):
        """Update the internal button list after rearrangement."""
        self.buttons = [
            widget
            for i in range(self.layout.count())
            if isinstance((widget := self.layout.itemAt(i).widget()), DraggableButton)
        ]


class CustomTreeWidget(QTreeWidget):
    """
    CustomTreeWidget class for managing a hierarchical tree structure with interactive
    checkable items, QComboBox widgets in tree items, and advanced hierarchy
    manipulation features. This class facilitates dynamic population, interaction,
    and customization of tree widgets, making it suitable for complex datasets
    and hierarchical visualizations. It also provides signals for interaction
    such as selection, property changes, and checkbox toggles.

    The class allows for storing UIDs for items, managing checked states,
    handling item selections, and dynamically reordering items based on the
    application's requirements.

    :ivar checkboxToggled: Signal emitted when checkboxes in the tree are toggled,
        passing a list of UIDs for the checked items.
    :type checkboxToggled: Signal
    :ivar itemsSelected:  emitted when items in the tree are selected,
        passing a list of UIDs for the selected items.
    :type itemsSelected: Signal
    :ivar propertyToggled: Signal emitted when a property associated with an item
        changes, passing the UID and the new property value.
    :type propertyToggled: Signal
    :ivar collection_df: Collection DataFrame used to populate the tree structure.
    :type collection_df: Pandas.DataFrame | None
    :ivar tree_labels: The labels representing column hierarchy in the tree.
    :type tree_labels: List[str] | None
    :ivar name_label: The label used for naming individual tree items.
    :type name_label: Str | None
    :ivar prop_label: The label used to populate QComboBox with data in tree items.
    :type prop_label: Str | None
    :ivar uid_label: The label is used to uniquely identify items in the tree through UIDs.
    :type uid_label: Str | None
    :ivar checked_uids: List of UIDs for the currently checked items in the tree.
    :type checked_uids: List[str]
    :ivar selected_uids: List of UIDs for the currently selected items in the tree.
    :type selected_uids: List[str]
    :ivar combo_values: A dictionary mapping UIDs of items to their associated
        combo box selection state.
    :type combo_values: Dict[str, str]
    :ivar header_labels: A list of header labels used for creating tree columns.
    :type header_labels: List[str]
    :ivar header_widget: A CustomHeader instance for managing the column hierarchy
        and reordering tree columns.
    :type header_widget: CustomHeader
    """

    def __init__(
        self,
        parent=None,  # Store parent reference
        collection_df=None,
        tree_labels=None,
        name_label=None,
        uid_label=None,
        prop_label=None,
        default_labels=None,
    ):
        super().__init__()
        self.parent = parent  # Store parent reference
        self.collection_df = collection_df
        self.tree_labels = tree_labels
        self.name_label = name_label
        self.prop_label = prop_label
        self.default_labels = default_labels
        self.uid_label = uid_label
        self.checked_uids = []
        self.combo_values = {}
        self.header_labels = ["Tree", name_label]
        self.blockSignals(False)
        self.setColumnCount(3)
        self.setHeaderLabels(self.header_labels)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.header_widget = CustomHeader(labels=self.tree_labels)
        self.header_widget.buttonToggled.connect(self.rearrange_hierarchy)
        self.populate_tree()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.toggle_with_menu)
        self.header().hide()
        self.itemExpanded.connect(self.resize_columns)
        self.itemCollapsed.connect(self.resize_columns)
        # self.itemChanged.connect(self.on_checkbox_changed)
        self.itemChanged.connect(
            lambda item, column: self.on_checkbox_changed(item, column) if item.childCount() == 0 else None)
        self.itemSelectionChanged.connect(self.emit_selection_changed)

    def _recursive_cleanup(self, item):
        """Recursively clean up widgets in the tree item and its children."""
        for i in range(item.childCount()):
            child = item.child(i)
            self._recursive_cleanup(child)

        # Remove and delete the widget
        widget = self.itemWidget(item, self.columnCount() - 1)
        if widget:
            widget.deleteLater()
            self.removeItemWidget(item, self.columnCount() - 1)

    def _cleanup_tree_widgets(self):
        """Clean up existing widgets in the tree."""
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            self._recursive_cleanup(item)

    def preserve_selection(func):
        """Decorator used to preserve selection during several common tree widget operations."""

        def wrapper(self, *args, **kwargs):
            current_selection = self.parent.collection.selected_uids.copy()
            result = func(self, *args, **kwargs)
            self.restore_selection(current_selection)
            return result

        return wrapper

    def resize_columns(self):
        """Adjusts the width of each column to fit the content it holds."""

        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)

    def restore_selection(self, uids_to_select):
        """
        Restores the selection of items in a widget based on a provided list of unique
        identifiers (UIDs). The function ensures that only the items whose UIDs match
        those provided in the list will be selected, while clearing any previous
        selections. Signals are temporarily blocked to avoid unintended recursive
        calls during this operation.

        :param uids_to_select: List of unique identifiers representing the items to
            be selected.
        :type uids_to_select: List

        :return: None
        """

        if not uids_to_select:
            return

        # Temporarily block signals to prevent recursive calls
        self.blockSignals(True)

        # Clear current selection
        self.clearSelection()

        # Find all items matching our UIDs and select them
        for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            uid = self.get_item_uid(item)
            if uid and uid in uids_to_select:
                item.setSelected(True)

        # Restore our selection list
        self.parent.collection.selected_uids = uids_to_select.copy()

        # Unblock signals
        self.blockSignals(False)

    def get_item_uid(self, item):
        """
        Retrieves the unique identifier (UID) associated with the provided item. The UID
        is stored in the item's data at a specific role in the Qt model.

        :param item: The QObject item from which the UID is to be retrieved. It must
            support the `data` method that accepts a column index and a data role.
        :type item: QObject
        :return: The UID stored in the item's data under `Qt.UserRole`.
        :rtype: Any
        """

        return item.data(0, Qt.UserRole)

    def get_or_create_item(self, parent, text):
        """
        Finds a child item in the given parent by text, or creates one if it does not exist.

        The method iterates through all children of the provided parent and checks if
        any child has the specified text. If a matching child is found, it returns the
        child. Otherwise, it creates a new QTreeWidgetItem with the given text, sets
        appropriate flags for user interaction, assigns an unchecked state to the
        item, adds it as a child to the parent, and then returns the newly created item.

        :param parent:
            The parent QTreeWidgetItem under which the child will be searched or
            created. Should be an instance of QTreeWidgetItem.
        :param text:
            The text to match against existing children of the parent, or to assign
            to the new item if no match is found. Should be a string.
        :return:
            The QTreeWidgetItem that matches the given text, either pre-existing or
            newly created.
        """

        for i in range(parent.childCount()):
            if parent.child(i).text(0) == text:
                return parent.child(i)
        item = QTreeWidgetItem([text])
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
        item.setCheckState(0, Qt.Unchecked)
        parent.addChild(item)
        return item

    def create_property_combo(self, row, uid):
        """
        Creates and configures a combo box widget for a property selection based on the given data row
        and unique identifier.

        This method initializes a QComboBox, populates it with items derived from the specified row data,
        and optionally pre-selects the item corresponding to the stored value for the provided unique
        identifier.

        :param row: A data structure containing property labels to populate the combo box.
        :param uid: A unique identifier is used to retrieve and set the initial value of the combo box
            if it exists in the combo_values map.
        :return: A QComboBox widget is configured with the appropriate items and an optionally pre-selected value.
        :rtype: QComboBox
        """
        property_combo = QComboBox()
        property_combo.addItems(row[self.prop_label])

        if uid in self.combo_values:
            index = property_combo.findText(self.combo_values[uid])
            if index >= 0:
                property_combo.setCurrentIndex(index)

        return property_combo

    def update_child_check_states(self, item, check_state):
        """
        Update the check state of all child items recursively.

        This method updates the check state of all child items within a tree-like structure
        to match the provided check_state. It starts with the specified item and propagates
        the check state to all its descendants.

        :param item: The parent item whose children's check states are to be updated.
        :type item: QTreeWidgetItem
        :param check_state: The state to be applied to all child items. Common values are
            Qt.Checked, Qt.PartiallyChecked, or Qt.Unchecked.
        :type check_state: Qt.CheckState
        :return: None
        """

        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, check_state)
            self.update_child_check_states(child, check_state)

    def update_parent_check_states(self, item):
        """
        Updates the check state of the parent item based on the check states of its child items.

        This method ensures that the check state of the parent reflects whether all, none, or some
        of its child items are checked. If all child items are checked, the parent is set to "checked".
        If none is checked, the parent is set to "unchecked". Otherwise, the parent is set to
        "partially checked". This process is applied recursively to all parent items in the hierarchy.

        :param item: The item whose parent's check state needs to be updated.
        :type item: QTreeWidgetItem
        """

        parent = item.parent()
        if parent:
            children = [parent.child(i) for i in range(parent.childCount())]
            check_states = [child.checkState(0) for child in children]

            if all(state == Qt.Checked for state in check_states):
                parent.setCheckState(0, Qt.Checked)
            elif all(state == Qt.Unchecked for state in check_states):
                parent.setCheckState(0, Qt.Unchecked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)

            self.update_parent_check_states(parent)

    def update_all_parent_check_states(self):
        """
        Update the check state of all parent nodes in a hierarchical model.

        This method iterates over all items in reverse order and updates the check
        state of parent nodes by calling the `update_parent_check_states` method for
        each item that has a parent. The reverse iteration ensures that children nodes
        are processed before their respective parents, maintaining dependency order for
        check state calculations.

        :return: None
        """

        all_items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive)
        for item in reversed(all_items):
            if item.parent():
                self.update_parent_check_states(item)

    def populate_tree(self):
        """
        Populates the tree widget with hierarchical data derived from the collection
        dataframe based on the current order of header buttons.
        """
        # Save current combo values before clearing the tree
        if self.invisibleRootItem().childCount() > 0:
            for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                uid = self.get_item_uid(item)
                if uid:
                    combo = self.itemWidget(item, self.columnCount() - 1)
                    if combo:
                        self.combo_values[uid] = combo.currentText()

        # Clean up existing widgets before clearing the tree
        self._cleanup_tree_widgets()

        self.clear()
        hierarchy = self.header_widget.get_order()
        for _, row in self.collection_df.iterrows():
            parent = self.invisibleRootItem()
            for level in hierarchy:
                parent = self.get_or_create_item(parent, row[level])

            # Create item with empty first column and name in the second column
            name_item = QTreeWidgetItem(["", row[self.name_label]])

            # Store the UID as item data for reliable reference
            if self.uid_label and self.uid_label in row:
                uid = str(row[self.uid_label])
                name_item.setData(0, Qt.UserRole, uid)
                name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
                name_item.setCheckState(0, Qt.Unchecked)
            else:
                name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
                name_item.setCheckState(0, Qt.Unchecked)

            parent.addChild(name_item)

            # Create and set up the QComboBox
            property_combo = QComboBox()
            for label in self.default_labels:
                property_combo.addItem(label)
            property_combo.addItems(row[self.prop_label])

            # Restore the previously selected value if it exists
            if uid in self.combo_values:
                index = property_combo.findText(self.combo_values[uid])
                if index >= 0:
                    property_combo.setCurrentIndex(index)
            property_combo.currentTextChanged.connect(
                lambda text, item=name_item: self.on_combo_changed(item, text)
            )

            # Add the item and set the combo box in the last column
            self.setItemWidget(name_item, self.columnCount() - 1, property_combo)

        # Expand all items and resize columns
        self.expandAll()
        self.resize_columns()

    def rearrange_hierarchy(self):
        """
        Rebuild and rearrange the tree hierarchy while maintaining the stored states of
        selection and checkboxes. During the process, tree signals are temporarily blocked
        to minimize unnecessary updates. Once the process is completed, the original states
        are restored, and the relevant signals are emitted.

        :raises KeyError: If `self.get_item_uid(item)` fails to resolve a valid UID for an item in the tree.
        :raises AttributeError: If `self.populate_tree` or `self.update_all_parent_check_states`
            methods are not implemented in the current class.
        """

        # Store the current selection and checkbox states before repopulating
        saved_selected = self.parent.collection.selected_uids.copy()
        saved_checked = self.checked_uids.copy()

        # Save any additional checkboxes that might not be in self.checked_uids yet
        if self.invisibleRootItem().childCount() > 0:
            for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                uid = self.get_item_uid(item)
                if (
                    uid
                    and item.checkState(0) == Qt.Checked
                    and uid not in saved_checked
                ):
                    saved_checked.append(uid)

        # Block signals temporarily to prevent unnecessary signal emissions during rebuild
        self.blockSignals(True)

        # Repopulate the tree (this will clear selections and checkboxes)
        self.populate_tree()

        # Restore checkbox states
        self.checked_uids = saved_checked  # Restore the checked_uids list directly
        for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            uid = self.get_item_uid(item)
            if uid and uid in saved_checked:
                item.setCheckState(0, Qt.Checked)

        # Update parent checkbox states based on children
        self.update_all_parent_check_states()

        # Restore selection
        self.clearSelection()  # Ensure a clean state before restoring
        if saved_selected:
            # Find all items matching our saved UIDs and select them
            for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                uid = self.get_item_uid(item)
                if uid and uid in saved_selected:
                    item.setSelected(True)

        # Restore our saved selection list directly
        self.parent.collection.selected_uids = saved_selected

        # Unblock signals
        self.blockSignals(False)

        # Emit selection signal to notify any listeners of the restored selection
        if saved_selected:
            self.parent.collection.signals.itemsSelected.emit(
                self.parent.collection.name
            )

    def emit_checkbox_toggled(self):
        """
        Emits a signal when a checkbox in a tree widget is toggled.

        This method iterates over all items in the tree widget and checks their
        checkbox states. If a checkbox is marked as checked, the method retrieves
        the unique identifier (UID) associated with that item and adds it to a list
        of checked items. Finally, it emits the `checkboxToggled` signal with the
        list of checked item UIDs as its payload.

        :raises AttributeError: Raises if `findItems`, `get_item_uid`, or `checkboxToggled.emit`
                                 are not properly defined or accessible within the context.

        :return: None
        """

        # Update the checked state in actors_df based on the current tree state
        for item in self.findItems(
            "", Qt.MatchContains | Qt.MatchRecursive, 1
        ):  # Search in the name column (1)
            uid = self.get_item_uid(item)
            if uid:
                is_checked = item.checkState(0) == Qt.Checked
                is_shown = self.parent.actors_df.loc[
                    self.parent.actors_df["uid"] == uid, "show"
                ].iloc[0]
                if is_checked != is_shown:
                    self.parent.actors_df.loc[
                        self.parent.actors_df["uid"] == uid, "show"
                    ] = is_checked

        # Emit signal
        self.parent.signals.checkboxToggled.emit(self.parent.collection.name)

    @preserve_selection
    def on_checkbox_changed(self, item, column):
        """Handle checkbox state changes."""
        # is this "if" working???
        if column != 0 or item.checkState(0) == Qt.PartiallyChecked:
            return

        self.blockSignals(True)
        self.update_child_check_states(item, item.checkState(0))
        self.update_parent_check_states(item)
        self.blockSignals(False)

        self.emit_checkbox_toggled()

    def toggle_with_menu(self, position):
        """
        Display a context menu at the specified position, allowing the user to toggle
        the state of checkboxes for the currently selected items.

        :param position: The QPoint location where the context menu will be displayed.
        :type position: QPoint
        :return: None
        """

        menu = QMenu()
        toggle_action = menu.addAction("Toggle Checkboxes")
        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == toggle_action:
            for item in self.selectedItems():
                new_state = (
                    Qt.Checked if item.checkState(0) == Qt.Unchecked else Qt.Unchecked
                )
                item.setCheckState(0, new_state)
                self.update_child_check_states(item, new_state)
                self.update_parent_check_states(item)
            self.emit_checkbox_toggled()

    def emit_selection_changed(self):
        """
        Clears the current selection, updates the selection list with UIDs of
        selected items, and emits a signal to notify that the selection has changed.

        :param self: The instance of the class calling this method.
        :return: None
        """

        # Clear the current selection list
        self.parent.collection.selected_uids = []

        # Add the UID of each selected item to the list
        for item in self.selectedItems():
            uid = self.get_item_uid(item)
            if uid:
                self.parent.collection.selected_uids.append(uid)

        # Emit signal
        self.parent.collection.signals.itemsSelected.emit(self.parent.collection.name)

    @preserve_selection
    def on_combo_changed(self, item, text):
        """
        Handles changes in a combo box selection and updates internal state accordingly.

        This method is called in response to a combo box value change event. It updates the
        stored combo box value based on the selected item's unique identifier, emits a property-changed event to notify of the update, and restores the previously selected items to
        maintain the current selection state.

        :param item: The item in the combo box that triggered the change event.
        :param text: The new text value of the combo box for the provided item.
        :return: None
        """

        # # Store the current selection
        # current_selection = self.parent.collection.selected_uids.copy()

        # Update the stored combo value
        uid = self.get_item_uid(item)
        if uid:
            self.combo_values[uid] = text
            # Update show_property in actors_df for the current uid
            self.parent.actors_df.loc[
                self.parent.actors_df["uid"] == uid, "show_property"
            ] = text
            self.parent.signals.propertyToggled.emit(self.parent.collection.name)

            # self.emit_property_changed(item, text)

        # # Restore selection after combo box interaction
        # self.restore_selection(current_selection)
