from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag


class DraggableButton(QPushButton):
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
        print("Current order:", order)  # Debug print
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
    checkboxToggled = Signal(list)
    itemsSelected = Signal(list)

    def __init__(self, collection_df=None, tree_labels=None, item_labels=None):
        super().__init__()
        self.collection_df = collection_df
        self.tree_labels = tree_labels
        self.item_labels = item_labels
        self.header_labels = ["Tree"] + self.item_labels
        self.setColumnCount(3)
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
        self.itemSelectionChanged.connect(self.handle_selection_changed)

    def mousePressEvent(self, event):
        if not (event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)):
            if event.button() == Qt.LeftButton:
                self.clearSelection()
        super().mousePressEvent(event)

    def populate_tree(self):
        self.clear()
        hierarchy = self.header_widget.get_order()
        print("Populating tree with hierarchy:", hierarchy)  # Debug print
        for _, row in self.collection_df.iterrows():
            parent = self.invisibleRootItem()
            for level in hierarchy:
                parent = self.find_or_create_item(parent, row[level])
            name_item = QTreeWidgetItem([""] + [row[col] for col in self.item_labels])
            name_item.setFlags(name_item.flags() | Qt.ItemIsUserCheckable)
            name_item.setCheckState(0, Qt.Unchecked)
            parent.addChild(name_item)
        self.resize_columns()

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
        print("Rearranging hierarchy")  # Debug print
        self.populate_tree()

    def handle_item_changed(self, item, column):
        if column == 0 and item.checkState(0) != Qt.PartiallyChecked:
            self.update_child_check_states(item, item.checkState(0))
            self.update_parent_check_states(item)
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

    def emit_checkbox_toggled(self):
        checked_items = list(
            filter(
                None,
                [
                    item.text(1)
                    for item in self.findItems("", Qt.MatchContains | Qt.MatchRecursive)
                    if item.checkState(0) == Qt.Checked
                ],
            )
        )
        self.checkboxToggled.emit(checked_items)

    def handle_selection_changed(self):
        selected_items = list(
            filter(None, [item.text(1) for item in self.selectedItems()])
        )
        self.itemsSelected.emit(selected_items)

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
