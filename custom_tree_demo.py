import sys
from typing import List, Optional

import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

from custom_tree import CustomTreeWidget


class MainWindow(QWidget):
    """
    The MainWindow class represents the primary graphical user interface window
    incorporating a tree widget for data visualization and interaction.
    """

    def __init__(
        self,
        collection_df: Optional[pd.DataFrame] = None,
        tree_labels: Optional[List[str]] = None,
        name_label: Optional[str] = None,
        uid_label: Optional[str] = None,
        combo_label: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.collection: str = "this_collection"
        self.selected_uids: List[str] = []

        self.tree_widget = self._setup_tree_widget(
            collection_df, tree_labels, name_label, uid_label, combo_label
        )
        self._setup_layout()

    def _setup_tree_widget(
        self,
        collection_df: Optional[pd.DataFrame],
        tree_labels: Optional[List[str]],
        name_label: Optional[str],
        uid_label: Optional[str],
        combo_label: Optional[str],
    ) -> CustomTreeWidget:
        """Create and configure the CustomTreeWidget."""
        return CustomTreeWidget(
            parent=self,
            collection_df=collection_df,
            tree_labels=tree_labels,
            name_label=name_label,
            uid_label=uid_label,
            combo_label=combo_label,
        )

    def _setup_layout(self) -> None:
        """Setup the main window layout."""
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_widget.header_widget)
        layout.addWidget(self.tree_widget)


def create_test_data() -> pd.DataFrame:
    """Create sample data for testing the tree widget."""
    return pd.DataFrame(
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


def setup_signal_connections(window: MainWindow) -> None:
    """Setup signal connections for the main window's tree widget."""
    window.tree_widget.checkboxToggled.connect(
        lambda coll, uids: print("Collection, checked uids:", coll, " - ", uids)
    )
    window.tree_widget.itemsSelected.connect(
        lambda coll, uids: print("Collection, selected uids:", coll, " - ", uids)
    )
    window.tree_widget.propertyToggled.connect(
        lambda coll, uid, prop: print(
            "Collection, changed uid, prop:", coll, " - ", uid, " - ", prop
        )
    )


def main() -> None:
    """Main application entry point."""
    app = QApplication(sys.argv)

    tree_labels = ["role", "topology", "feature", "scenario"]
    name_label = "name"
    uid_label = "uid"
    combo_label = "properties"
    collection_df = create_test_data()

    main_window = MainWindow(
        collection_df=collection_df,
        tree_labels=tree_labels,
        name_label=name_label,
        uid_label=uid_label,
        combo_label=combo_label,
    )
    main_window.show()
    setup_signal_connections(main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
