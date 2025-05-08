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
    The MainWindow class represents the primary graphical user interface window
    incorporating a tree widget for data visualization and interaction.

    This class is built upon the QWidget provided by PyQt.

    The purpose of this class is to provide a test layout containing a header widget and tree widget, which reflect the specified data and labels, enabling a structured view and potential further customization for users. It takes data and label inputs and initializes a custom tree widget to manage their display.

    :ivar tree_widget: The custom tree widget is used for displaying data and labels.
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
        self.selected_uids = []  # Store selected UIDs here
        self.collection = "this_collection"  # Or whatever initial value
        self.tree_widget = CustomTreeWidget(
            parent=self,  # Pass self as parent
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
        lambda coll, uids: print("Collection, checked uids:", coll, " - ", uids)
    )
    main_window.tree_widget.itemsSelected.connect(
        lambda coll, uids: print("Collection, selected uids:", coll, " - ", uids)
    )
    main_window.tree_widget.propertyToggled.connect(
        lambda coll, uid, prop: print("Collection, changed uid, prop:", coll, " - ", uid, " - ", prop)
    )
    sys.exit(app.exec())
