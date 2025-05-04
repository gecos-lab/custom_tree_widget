from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QSizePolicy,
    QComboBox,  # Add this import
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag


class DraggableButton(QPushButton):
    """
    A draggable button widget.

    The DraggableButton class extends QPushButton to implement a button widget
    that can be clicked and dragged. It supports checkable behavior and is
    sized according to its size hint. The primary feature of this button is
    its ability to initiate drag-and-drop actions when it is dragged with the
    left mouse button.

    :ivar _text: The text displayed on the button.
    :type _text: str
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

    CustomHeader can be utilized in applications where a customizable header
    layout with draggable elements is needed.

    :ivar layout: Layout manager for arranging buttons within the header.
    :type layout: QHBoxLayout
    :ivar buttons: List of draggable buttons displayed in the header.
    :type buttons: list
    """

    orderChanged = Signal()

    def __init__(self, parent=None, labels=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)  # Remove spacing between buttons
        self.buttons = []
        for label in labels:
            button = DraggableButton(label)
            button.clicked.connect(self.on_button_clicked)
            self.layout.addWidget(button)
            self.buttons.append(button)
        self.layout.addStretch()
        self.setAcceptDrops(True)

    def on_button_clicked(self):
        self.orderChanged.emit()

    def get_order(self):
        order = [button.text() for button in self.buttons if button.isChecked()]
        return order

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        source_button = event.source()
        if source_button in self.buttons:
            self.layout.removeWidget(source_button)
            drop_position = event.position().toPoint()
            closest_button = None
            min_distance = float("inf")
            for button in self.buttons:
                distance = abs(button.geometry().center().x() - drop_position.x())
                if distance < min_distance:
                    min_distance = distance
                    closest_button = button
            if closest_button:
                index = self.layout.indexOf(closest_button)
                if (
                    drop_position.x()
                    > closest_button.geometry().left()
                    + closest_button.geometry().width() / 2
                ):
                    index += 1
                self.layout.insertWidget(index, source_button)
            else:
                self.layout.addWidget(source_button)
            self.buttons = [
                self.layout.itemAt(i).widget()
                for i in range(self.layout.count())
                if isinstance(self.layout.itemAt(i).widget(), DraggableButton)
            ]
            self.orderChanged.emit()

    def dragMoveEvent(self, event):
        event.accept()


class CustomTreeWidget(QTreeWidget):
    """
    CustomTreeWidget is a specialized QTreeWidget used for displaying hierarchical data
    with customizable headers, checkable items, and property management.
    
    ...existing docstring...
    
    :ivar name_label: Label for the column containing item names/descriptions.
    :type name_label: str
    :ivar uid_label: Label for the column containing unique identifiers.
    :type uid_label: str
    """

    checkboxToggled = Signal(list)
    itemsSelected = Signal(list)
    propertyToggled = Signal(str, str)  # uid, new_property

    def __init__(
        self,
        collection_df=None,
        tree_labels=None,
        name_label=None,     # Renamed from item_labels to name_label
        combo_label=None,
        uid_label=None,      # Specific parameter for the UID column
    ):
        super().__init__()
        self.collection_df = collection_df
        self.tree_labels = tree_labels
        self.name_label = name_label    # Store name column
        self.combo_label = combo_label
        self.uid_label = uid_label      # Store UID column name
        self.header_labels = ["Tree", name_label]  # Only two columns plus combo
        self.blockSignals(False)
        self.setColumnCount(3)          # Tree, Name, Combo
        self.setHeaderLabels(self.header_labels)
        self.setSelectionMode(QTreeWidget.MultiSelection)
        self.header_widget = CustomHeader(labels=self.tree_labels)
        self.header_widget.orderChanged.connect(self.rearrange_hierarchy)
        self.populate_tree()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.header().hide()  # Hide the table header
        self.itemExpanded.connect(self.resize_columns)
        self.itemCollapsed.connect(self.resize_columns)
        self.itemChanged.connect(self.handle_item_changed)
        self.itemSelectionChanged.connect(self.emit_selection_changed)

    def populate_tree(self):
        # Store checked states before clearing the tree
        checked_uids = []
        if self.invisibleRootItem().childCount() > 0:
            for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
                uid = self.get_item_uid(item)
                if uid and item.checkState(0) == Qt.Checked:
                    checked_uids.append(uid)
        
        self.clear()
        hierarchy = self.header_widget.get_order()
        for _, row in self.collection_df.iterrows():
            parent = self.invisibleRootItem()
            for level in hierarchy:
                parent = self.find_or_create_item(parent, row[level])
                
            # Create item with empty first column and name in second column
            name_item = QTreeWidgetItem(["", row[self.name_label]])
            
            # Store the UID as item data for reliable reference
            if self.uid_label and self.uid_label in row:
                uid = str(row[self.uid_label])
                name_item.setData(0, Qt.UserRole, uid)
                
                # Restore check state if this item was previously checked
                initial_state = Qt.Checked if uid in checked_uids else Qt.Unchecked
                name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
                name_item.setCheckState(0, initial_state)
            else:
                name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
                name_item.setCheckState(0, Qt.Unchecked)
                
            parent.addChild(name_item)
            
            # Create and set up the QComboBox
            property_combo = QComboBox()
            property_combo.addItems(row[self.combo_label])
            property_combo.currentTextChanged.connect(
                lambda text, item=name_item: self.emit_property_changed(item, text)
            )

            # Add the item and set the combo box in the last column
            self.setItemWidget(name_item, self.columnCount() - 1, property_combo)

        # Expand all items after populating the tree
        self.expandAll()
        self.resize_columns()
        
        # Update parent check states based on children's states
        self.update_all_parent_check_states()
    
    def update_all_parent_check_states(self):
        """Update all parent check states after restoring checked items"""
        # Process in reverse order to ensure children are processed before parents
        all_items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive)
        for item in reversed(all_items):
            if item.parent():
                self.update_parent_check_states(item)

    # ... other methods remain the same as in previous response ...
    
    def emit_checkbox_toggled(self):
        # Update to use UIDs directly
        checked_items = []
        for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if item.checkState(0) == Qt.Checked:
                uid = self.get_item_uid(item)
                if uid:
                    checked_items.append(uid)
        self.checkboxToggled.emit(checked_items)

    def emit_selection_changed(self):
        # Update to use UIDs directly
        selected_items = []
        for item in self.selectedItems():
            uid = self.get_item_uid(item)
            if uid:
                selected_items.append(uid)
        self.itemsSelected.emit(selected_items)

    def emit_property_changed(self, item, new_property):
        uid = self.get_item_uid(item)
        if uid:
            self.propertyToggled.emit(uid, new_property)
    
    def get_item_uid(self, item):
        """Helper function to get the UID stored in the item's data."""
        return item.data(0, Qt.UserRole)

    def resize_columns(self):
        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)

    def find_or_create_item(self, parent, text):
        for i in range(parent.childCount()):
            if parent.child(i).text(0) == text:
                return parent.child(i)
        item = QTreeWidgetItem([text])
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
        item.setCheckState(0, Qt.Unchecked)
        parent.addChild(item)
        return item

    def rearrange_hierarchy(self):
        self.populate_tree()

    def handle_item_changed(self, item, column):
        if column == 0 and item.checkState(0) != Qt.PartiallyChecked:
            self.blockSignals(True)
            self.update_child_check_states(item, item.checkState(0))
            self.update_parent_check_states(item)
            self.blockSignals(False)
            self.emit_checkbox_toggled()

    def update_child_check_states(self, item, check_state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, check_state)
            self.update_child_check_states(child, check_state)

    def update_parent_check_states(self, item):
        parent = item.parent()
        if parent:
            all_checked = all(
                child.checkState(0) == Qt.Checked
                for child in [parent.child(i) for i in range(parent.childCount())]
            )
            all_unchecked = all(
                child.checkState(0) == Qt.Unchecked
                for child in [parent.child(i) for i in range(parent.childCount())]
            )
            if all_checked:
                parent.setCheckState(0, Qt.Checked)
            elif all_unchecked:
                parent.setCheckState(0, Qt.Unchecked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)
            self.update_parent_check_states(parent)


    def show_context_menu(self, position):
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
if __name__ == "__main__":
    import sys
    import pandas as pd
    from PySide6.QtWidgets import QApplication, QMainWindow

    class MainWindow(QMainWindow):
        def __init__(self, collection_df, tree_labels, name_label, uid_label, combo_label):
            super().__init__()
            self.tree = CustomTreeWidget(
                collection_df=collection_df,
                tree_labels=tree_labels,
                name_label=name_label,
                uid_label=uid_label,
                combo_label=combo_label
            )
            self.setCentralWidget(self.tree)

    app = QApplication(sys.argv)
    tree_labels: list[str] = ["role", "topology", "feature", "scenario"]
    name_label = "name"    # Instead of item_labels list, use direct variables
    uid_label = "uid"      # Instead of item_labels list, use direct variables
    combo_label: str = "properties"
    collection_df = pd.DataFrame(
        {
            "role": ["fault", "top", "top", "fault", "top", "top"],
            "topology": [
                "PolyLine",
                "PolyLine",
                "TriSurf",
                "PolyLine",
                "PolyLine",
                "TriSurf",
            ],
            "feature": [
                "Triassic",
                "Jurassic",
                "Triassic",
                "Triassic",
                "Jurassic",
                "Triassic",
            ],
            "scenario": [
                "preliminary",
                "final",
                "preliminary",
                "preliminary",
                "final",
                "preliminary",
            ],
            "name": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"],
            "uid": ["1", "2", "3", "4", "5", "6"],
            "properties": [
                ["a", "aa", "aaa"],
                ["b", "bb"],
                ["c", "cc"],
                ["d", "dd", "ddd"],
                ["eee"],
                ["fff"],
            ],
        }
    )
    main_window = MainWindow(
        collection_df=collection_df,
        tree_labels=tree_labels,
        name_label=name_label,     # Use name_label directly
        uid_label=uid_label,       # Use uid_label directly 
        combo_label=combo_label,
    )
    main_window.show()
    # Rest of the code remains the same
    sys.exit(app.exec())