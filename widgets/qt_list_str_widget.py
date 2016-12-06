""" Enaml widget for editing a list of string
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
from atom.api import (Bool, List, Tuple, ContainerList, observe, set_default, Unicode, Enum, Int, Signal, Callable)

from enaml.widgets.api import RawWidget
from enaml.core.declarative import d_
from enaml.qt.QtGui import QListWidget, QListWidgetItem, QAbstractItemView, QColor
from enaml.qt.QtCore import Qt

class QtListStrWidget(RawWidget):
    """ A Qt4 implementation of an Enaml ProxyListStrView.

    """

    __slots__ = '__weakref__'

    #: The list of (str, enabled) tuples being viewed
    items = d_(List(Tuple() ) )

    #: The index of the currently selected str
    selected_index = d_(Int(-1))

    #: The currently selected str
    selected_item = d_(Unicode())

    #: Whether or not the items should be checkable
    checkable = d_(Bool(True))

    #: Whether or not the items should be editable
    editable = d_(Bool(True))

    validator = d_(Callable())
    hug_width = set_default('weak')
    item_changed = Signal()
    enable_changed = Signal()


    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self, parent):
        """ Create the QListWidget widget.

        """
        # Create the list model and accompanying controls:
        widget = QListWidget(parent)
        for item, checked in self.items:
            self.add_item(widget, item, checked)

        # set selected_item here so that first change fires an 'update' rather than 'create' event
        self.selected_item = u''
        if self.items:
            self.selected_index = 0
            self.selected_item = self.items[0][0]
            widget.setCurrentRow(0)

        widget.itemSelectionChanged.connect(self.on_selection)
        widget.itemChanged.connect(self.on_edit)

        return widget


    def add_item(self, widget, item, checked=True):
        itemWidget = QListWidgetItem(item)
        if self.checkable:
            itemWidget.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        if self.editable:
            _set_item_flag(itemWidget, Qt.ItemIsEditable, True)
        widget.addItem(itemWidget)
        self.apply_validator(itemWidget, itemWidget.text())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_selection(self):
        """
        The signal handler for the index changed signal.
        """
        widget = self.get_widget()
        self.selected_index = widget.currentRow()
        self.selected_item = self.items[widget.currentRow()][0] if self.selected_index >= 0 else u''

    def on_edit(self, item):
        """
        The signal handler for the item changed signal.
        """
        widget = self.get_widget()
        itemRow = widget.indexFromItem(item).row()
        oldLabel = self.items[itemRow][0]
        newLabel = item.text()

        # only signal the enable change when the labels are the same and is in
        # the item list, also only signal a name change when the labels are not
        # the same and the newlabel is not in the item list
        item_labels = [_[0] for _ in self.items]
        if newLabel == oldLabel and newLabel in item_labels:
            self.items[itemRow] = (newLabel, item.checkState() == Qt.Checked)
            self.enable_changed(item.text(), self.items[itemRow][1])
        elif oldLabel != newLabel and newLabel not in item_labels:
            self.item_changed(oldLabel, newLabel)
            self.selected_item = newLabel
            self.items[itemRow] = (newLabel, item.checkState() == Qt.Checked)
            self.apply_validator(item, newLabel)

    #--------------------------------------------------------------------------
    # ProxyListStrView API
    #--------------------------------------------------------------------------

    def set_items(self, items, widget=None):
        """
        """
        widget = self.get_widget()
        count = widget.count()
        nitems = len(items)
        for idx, item in enumerate(items[:count]):
            itemWidget = widget.item(idx)
            # Update checked state before the text so that we can distinguish a checked state change from a label change
            itemWidget.setCheckState(Qt.Checked if self.items[idx][1] else Qt.Unchecked)
            itemWidget.setText(item[0])
            self.apply_validator(itemWidget, item[0])
        if nitems > count:
            for item in items[count:]:
                self.add_item(widget, item[0])
        elif nitems < count:
            for idx in reversed(range(nitems, count)):
                widget.takeItem(idx)

    #--------------------------------------------------------------------------
    # Utility methods
    #--------------------------------------------------------------------------

    def apply_validator(self, item, label):
        if self.validator and  not self.validator(label):
            item.setTextColor(QColor(255,0,0))
        else:
            item.setTextColor(QColor(0,0,0))

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('items')
    def _update_items(self, change):
        """ An observer which sends state change to the proxy. """

        #this callback may be called before the widget is initialized
        widget = self.get_widget()
        if widget == None:
            return

        self.set_items(self.items)

        # update the selected item because the current row has changed
        self.selected_item = self.items[widget.currentRow()][0] if self.selected_index >= 0 else u''

# Helper methods
def _set_item_flag(item, flag, enabled):
    """ Set or unset the given item flag for the item.

    """
    flags = item.flags()
    if enabled:
        flags |= flag
    else:
        flags &= ~flag
    item.setFlags(flags)
