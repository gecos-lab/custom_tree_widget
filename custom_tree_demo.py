import sys
import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
)

from custom_tree import CustomTreeWidget


class MainWindow(QWidget):
    def __init__(
        self,
        collection_df=None,
        tree_labels=None,
        item_labels=None,
    ):
        super().__init__()
        layout = QVBoxLayout(self)
        print(collection_df)
        print(tree_labels)
        print(item_labels)
        self.tree_widget = CustomTreeWidget(
            collection_df=collection_df,
            tree_labels=tree_labels,
            item_labels=item_labels,
        )
        layout.addWidget(self.tree_widget.header_widget)
        layout.addWidget(self.tree_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tree_labels = ["role", "topology", "feature", "scenario"]
    item_labels = ["name", "uid"]
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
        }
    )
    main_window = MainWindow(
        collection_df=collection_df,
        tree_labels=tree_labels,
        item_labels=item_labels,
    )
    main_window.show()
    main_window.tree_widget.checkboxToggled.connect(
        lambda uids: print("Checked items:", uids)
    )
    main_window.tree_widget.itemsSelected.connect(
        lambda uids: print("Selected items:", uids)
    )
    sys.exit(app.exec())
