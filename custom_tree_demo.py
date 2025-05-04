import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
)

from custom_tree import CustomTreeWidget


class MainWindow(QWidget):
    """
    Main application window for displaying a tree structure.

    This class represents the main window of the application, which displays
    a tree structure using a custom widget. It initializes with an optional
    data collection, along with labels for the tree and its items. The tree
    is rendered using a `CustomTreeWidget`. Additional layout configurations
    can be implemented depending on the application's requirements.

    :ivar tree_widget: Instance of `CustomTreeWidget` used to display
        the tree structure within the main window.
    :type tree_widget: CustomTreeWidget
    """

    def __init__(
        self,
        collection_df: "pd.DataFrame | None" = None,
        tree_labels: "list[str] | None" = None,
        name_label: "str | None" = None,
        uid_label: "str | None" = None,
        combo_label: "str | None" = None,
    ) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.tree_widget = CustomTreeWidget(
            collection_df=collection_df,
            tree_labels=tree_labels,
            name_label=name_label,
            uid_label=uid_label,
            combo_label=combo_label,
        )
        layout.addWidget(self.tree_widget.header_widget)
        layout.addWidget(self.tree_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tree_labels: list[str] = ["role", "topology", "feature", "scenario"]
    name_label: str = "name"
    uid_label: str = "uid"
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
        name_label=name_label,
        uid_label=uid_label,
        combo_label=combo_label,
    )
    main_window.show()
    main_window.tree_widget.checkboxToggled.connect(
        lambda uids: print("Checked uids:", uids)
    )
    main_window.tree_widget.itemsSelected.connect(
        lambda uids: print("Selected uids:", uids)
    )
    main_window.tree_widget.propertyToggled.connect(
        lambda uid, prop: print("Changed uid, prop:", uid, " - ", prop)
    )
    sys.exit(app.exec())
