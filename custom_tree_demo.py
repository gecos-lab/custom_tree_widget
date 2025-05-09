"""custom_tree_demo.py © Andrea Bistacchi"""

import sys
from typing import List, Optional
import pandas as pd
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal as pyqtSignal
from custom_tree import CustomTreeWidget


class CollectionSignals(QObject):
    """
    This class is necessary since non-Qt classes cannot emit Qt signals. Therefore, we create a generic
    CollectionSignals() Qt object that will include all signals used by collections. These will be used according
    to the following pattern:

    self.signals = CollectionSignals()

    self.signals.specific_signal.emit(some_message)

    Etc.

    Basically in this way, instead of using inheritance, we add all signals with a quick move by composition.
    """

    itemsSelected = pyqtSignal(
        str
    )  # selection changed on the collection in the signal argument


class Collection:
    """Class to hold collection data and state"""

    def __init__(self):
        self.name = ""
        self.selected_uids = []
        self._signals = CollectionSignals()

    @property
    def signals(self):
        return self._signals


class MainWindowSignals(QObject):
    """
    This class is necessary since non-Qt classes cannot emit Qt signals. Therefore, we create a generic
    MainWindowSignals() Qt object that will include all signals used by collections. These will be used according
    to the following pattern:

    self.signals = MainWindowSignals()

    self.signals.specific_signal.emit(some_message)

    Etc.

    Basically in this way, instead of using inheritance, we add all signals with a quick move by composition.
    """

    # signal broadcast on checkbox toggled with the collection and lists of uids to be turned on or off as arguments
    checkboxToggled = pyqtSignal(str, list, list)
    # signal broadcast on property combobox changed with the collection, uid and property as arguments
    propertyToggled = pyqtSignal(str, str, str)


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
        prop_label: Optional[str] = None,
        default_labels: Optional[List[str]] = None,
    ) -> None:
        super().__init__()

        self._signals = MainWindowSignals()

        self.collection = Collection()
        self.collection.name = "this_collection"
        self.collection.selected_uids = []

        self.actors_df = pd.DataFrame(
            columns=["uid", "actor", "show", "collection", "show_property"]
        )
        self.actors_df["uid"] = collection_df["uid"]
        self.actors_df["collection"] = self.collection.name
        self.actors_df["actor"] = collection_df["name"]
        self.actors_df["show"] = True
        self.actors_df["show_property"] = ""

        self.tree_widget = self._setup_tree_widget(
            collection_df,
            tree_labels,
            name_label,
            uid_label,
            prop_label,
            default_labels,
        )
        self.setup_signal_connections()
        self._setup_layout()

    @property
    def signals(self):
        return self._signals

    def _setup_tree_widget(
        self,
        collection_df: Optional[pd.DataFrame],
        tree_labels: Optional[List[str]],
        name_label: Optional[str],
        uid_label: Optional[str],
        prop_label: Optional[str],
        default_labels: Optional[List[str]],
    ) -> CustomTreeWidget:
        """Create and configure the CustomTreeWidget."""
        return CustomTreeWidget(
            parent=self,
            collection_df=collection_df,
            tree_labels=tree_labels,
            name_label=name_label,
            uid_label=uid_label,
            prop_label=prop_label,
            default_labels=default_labels,
        )

    def _setup_layout(self) -> None:
        """Set up the main window layout."""
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree_widget.header_widget)
        layout.addWidget(self.tree_widget)

    def _on_items_selected(self, collection):
        """Handle items selection event."""
        uids = self.collection.selected_uids
        print("Collection, selected uids:", collection, " - ", uids)

    def _on_checkbox_toggled(self, collection, turn_on_uids, turn_off_uids):
        """Handle checkbox toggle event."""
        actors_df = self.actors_df
        print("Collection, turn_on_uids, turn_off_uids, actors_df:", collection, turn_on_uids, turn_off_uids, "\n", actors_df)

    def _on_property_toggled(self, collection, changed_uid, changed_prop):
        """Handle property toggle event."""
        actors_df = self.actors_df
        print("Collection, changed_uid, changed_prop, actors_df:", collection, changed_uid, changed_prop, "\n", actors_df)

    def setup_signal_connections(self) -> None:
        """Setup signal connections for the main window's tree widget."""
        self.collection.signals.itemsSelected.connect(self._on_items_selected)
        self.signals.checkboxToggled.connect(lambda collection, turn_on_uids, turn_off_uids:self._on_checkbox_toggled(collection, turn_on_uids, turn_off_uids))
        self.signals.propertyToggled.connect(lambda collection, changed_uid, changed_prop: self._on_property_toggled(collection, changed_uid, changed_prop))


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


def main() -> None:
    """Main application entry point."""
    app = QApplication(sys.argv)

    tree_labels = ["role", "topology", "feature", "scenario"]
    name_label = "name"
    uid_label = "uid"
    prop_label = "properties"
    default_labels = ["none", "X", "Y", "Z"]
    collection_df = create_test_data()

    main_window = MainWindow(
        collection_df=collection_df,
        tree_labels=tree_labels,
        name_label=name_label,
        uid_label=uid_label,
        prop_label=prop_label,
        default_labels=default_labels,
    )
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
