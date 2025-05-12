"""custom_tree_demo.py © Andrea Bistacchi"""

import sys
import random
import time

from typing import List, Optional
import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from PySide6.QtCore import QObject, Qt
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
    # signal for selection change, emits a list of UIDs
    newSelection = pyqtSignal(list)


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

        # Store labels as instance variables
        self.uid_label = uid_label or "uid"  # Default to "uid" if None
        self.prop_label = prop_label or "properties"  # Default to "properties" if None

        self._signals = MainWindowSignals()

        self.collection = Collection()
        self.collection.name = "this_collection"
        # self.collection.selected_uids = []
        self.collection.selected_uids = ["2", "4", "6"]

        self.actors_df = pd.DataFrame(
            columns=["uid", "actor", "show", "collection", "show_property"]
        )
        self.actors_df["uid"] = collection_df["uid"]
        self.actors_df["collection"] = self.collection.name
        self.actors_df["actor"] = collection_df["name"]
        # self.actors_df["show"] = True
        # self.actors_df["show_property"] = "none"
        self.actors_df["show"] = ["True", "False", "True", "False", "True", "False"]
        self.actors_df["show_property"] = ["none", "X", "Y", "Z", "none", "none"]

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
        self.setup_test_buttons()

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
        print(
            "Collection, turn_on_uids, turn_off_uids, actors_df:",
            collection,
            turn_on_uids,
            turn_off_uids,
            "\n",
            actors_df,
        )

    def _on_property_toggled(self, collection, changed_uid, changed_prop):
        """Handle property toggle event."""
        actors_df = self.actors_df
        print(
            "Collection, changed_uid, changed_prop, actors_df:",
            collection,
            changed_uid,
            changed_prop,
            "\n",
            actors_df,
        )

    def setup_signal_connections(self) -> None:
        """Setup signal connections for the main window's tree widget."""
        self.collection.signals.itemsSelected.connect(self._on_items_selected)
        self.signals.checkboxToggled.connect(
            lambda collection, turn_on_uids, turn_off_uids: self._on_checkbox_toggled(
                collection, turn_on_uids, turn_off_uids
            )
        )
        self.signals.propertyToggled.connect(
            lambda collection, changed_uid, changed_prop: self._on_property_toggled(
                collection, changed_uid, changed_prop
            )
        )
        # new connection for selection change
        self.signals.newSelection.connect(self.tree_widget.set_selection_from_uids)

    def test_add_random_items(self):
        """Test function that adds random items to the tree and measures performance."""
        # Get the maximum current UID
        current_max_uid = max(int(uid) for uid in self.actors_df["uid"])

        # Get original data structure
        orig_df = self.tree_widget.collection_df

        # Create new random data entries (between 1 and 5)
        num_to_add = random.randint(1, 5)

        # Create new entries by randomly shuffling values within each column
        new_entries = []
        for i in range(num_to_add):
            new_uid = str(current_max_uid + i + 1)
            new_entry = {
                "role": random.choice(orig_df["role"].tolist()),
                "topology": random.choice(orig_df["topology"].tolist()),
                "feature": random.choice(orig_df["feature"].tolist()),
                "scenario": random.choice(orig_df["scenario"].tolist()),
                "name": f"New_Feature_{new_uid}",
                "uid": new_uid,
                "properties": random.choice(orig_df["properties"].tolist()).copy(),
            }
            new_entries.append(new_entry)

        # Create DataFrame from new entries
        new_df = pd.DataFrame(new_entries)

        print(f"\nTesting addition of {num_to_add} items...")
        print(f"New entries:\n{new_df}")

        # Measure time
        start_time = time.time()

        # Update tree widget's collection_df
        self.tree_widget.collection_df = pd.concat(
            [self.tree_widget.collection_df, new_df], ignore_index=True
        )

        # Add items to tree widget
        used_individual_add = self.tree_widget.add_items_to_tree(new_df["uid"].tolist())

        # Update actors_df with new entries - ensure "show" values are strings
        new_actors = pd.DataFrame(
            {
                "uid": new_df["uid"],
                "actor": new_df["name"],
                "show": [
                    "True" for _ in range(len(new_df))
                ],  # Explicitly using string "True"
                "collection": [self.collection.name] * len(new_df),
                "show_property": ["none"] * len(new_df),
            }
        )

        # Convert show column to string type to ensure consistency
        new_actors["show"] = new_actors["show"].astype(str)
        self.actors_df = pd.concat([self.actors_df, new_actors], ignore_index=True)

        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

        print(f"Time taken: {elapsed_time:.2f} ms")
        print(
            f"Method used: {'Individual add' if used_individual_add else 'Complete rebuild'}"
        )

        # Verify items were added
        for uid in new_df["uid"]:
            found = False
            for item in self.tree_widget.findItems(
                "", Qt.MatchContains | Qt.MatchRecursive
            ):
                if self.tree_widget.get_item_uid(item) == uid:
                    found = True
                    break
            print(f"UID {uid}: {'✓ Added successfully' if found else '✗ Not found!'}")

    def test_remove_random_items(self):
        """Test function to remove random items from the tree"""
        if len(self.tree_widget.collection_df) == 0:
            print("No items to remove")
            return

        # Generate random number of items to remove (between 1 and 5)
        num_items = min(random.randint(1, 5), len(self.tree_widget.collection_df))

        # Randomly select UIDs using the stored uid_label
        uids_to_remove = (
            self.tree_widget.collection_df["uid"].sample(n=num_items).tolist()
        )

        print(f"Removing {len(uids_to_remove)} items: {uids_to_remove}")

        # Remove from tree (which will also update its collection_df)
        self.tree_widget.remove_items_from_tree(uids_to_remove)

        # Remove from actors_df
        self.actors_df = self.actors_df[~self.actors_df["uid"].isin(uids_to_remove)]

    def test_property_update(self):
        """
        Test function to update properties of selected items by adding or removing properties.
        """
        selected_uids = self.collection.selected_uids

        if not selected_uids:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select items in the tree to update their properties.",
            )
            return

        # Get first item's current properties from collection_df - with safety checks
        first_uid = selected_uids[0]
        mask = self.tree_widget.collection_df[self.uid_label] == first_uid
        matching_rows = self.tree_widget.collection_df[mask]

        if matching_rows.empty:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not find item with UID: {first_uid} in the collection.",
            )
            return

        current_props = matching_rows[self.prop_label].iloc[0]

        # Alternate between adding and removing a property
        if isinstance(current_props, list):
            if len(current_props) > 1:
                # Remove the last property
                new_props = current_props[:-1]
            else:
                # Add a new property
                new_props = current_props.copy()  # Make a copy of the list
                new_props.append(f"new_prop_{len(current_props)}")
        else:
            # Handle case where current_props is not a list
            new_props = ["new_prop_1"]

        # Update properties in the DataFrame using at[] to handle lists
        for uid in selected_uids:
            mask = self.tree_widget.collection_df[self.uid_label] == uid
            matching_rows = self.tree_widget.collection_df[mask]
            if not matching_rows.empty:
                idx = matching_rows.index[0]
                self.tree_widget.collection_df.at[idx, self.prop_label] = (
                    new_props.copy()
                )

        # Update the tree widget's combo boxes
        items = self.tree_widget.findItems("", Qt.MatchContains | Qt.MatchRecursive)
        for item in items:
            item_uid = self.tree_widget.get_item_uid(item)
            if item_uid in selected_uids:
                combo = self.tree_widget.itemWidget(
                    item, self.tree_widget.columnCount() - 1
                )
                if combo:
                    current_value = combo.currentText()
                    combo.clear()
                    combo.addItems(
                        ["none"] + self.tree_widget.default_labels + new_props
                    )
                    # Try to restore the previous selection if it still exists
                    index = combo.findText(current_value)
                    if index >= 0:
                        combo.setCurrentIndex(index)

    def test_random_selection(self):
        """Test function to emit random selection of UIDs."""
        # Get random number of items to select (between 1 and 5)
        num_items = min(random.randint(1, 5), len(self.tree_widget.collection_df))

        # Randomly select UIDs
        random_uids = self.tree_widget.collection_df["uid"].sample(n=num_items).tolist()

        print(f"Emitting new selection with {len(random_uids)} items: {random_uids}")

        # Emit the new selection signal
        self.signals.newSelection.emit(random_uids)

    def setup_test_buttons(self):
        """Set up test buttons in the main window"""
        # Create button layout
        self.button_layout = QHBoxLayout()

        # Create Add button
        self.test_add_btn = QPushButton("Test Add Random Items", self)
        self.test_add_btn.clicked.connect(self.test_add_random_items)
        self.button_layout.addWidget(self.test_add_btn)

        # Add the new Remove button
        self.test_remove_btn = QPushButton("Test Remove Random Items", self)
        self.test_remove_btn.clicked.connect(self.test_remove_random_items)
        self.button_layout.addWidget(self.test_remove_btn)

        # Add the property update test button
        test_prop_button = QPushButton("Test Property Update")
        test_prop_button.clicked.connect(self.test_property_update)
        self.button_layout.addWidget(test_prop_button)

        # Add the random selection test button
        test_selection_button = QPushButton("Test Random Selection")
        test_selection_button.clicked.connect(self.test_random_selection)
        self.button_layout.addWidget(test_selection_button)

        # Add button layout to the main layout
        self.layout().addLayout(self.button_layout)


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
