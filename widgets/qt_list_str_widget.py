""" Enaml widget for editing a list of string
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
from atom.api import (Bool, List, observe, set_default, Unicode, Enum, Int, Signal)

from enaml.widgets.api import RawWidget
from enaml.core.declarative import d_
from enaml.qt.QtGui import QListWidget, QListWidgetItem, QAbstractItemView
from enaml.qt.QtCore import Qt

class QtListStrWidget(RawWidget):
    """ A Qt4 implementation of an Enaml ProxyListStrView.

    """

    __slots__ = '__weakref__'

    #: The list of str being viewed
    items = d_(List(Unicode()))

    #: The index of the currently selected str
    selected_index = d_(Int(-1))
    
    #: The currently selected str
    selected_item = d_(Unicode())

    #: Whether or not the items should be checkable
    checkable = d_(Bool(True))

    #: Whether or not the items should be editable
    editable = d_(Bool(True))

    #: .
    hug_width = set_default('weak')

    item_changed = Signal()
    
    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self, parent):
        """ Create the QListWidget widget.

        """
        # Create the list model and accompanying controls:
        widget = QListWidget(parent)
        for item in self.items:
            self.add_item(widget, item)


        # set selected_item here so that first change fires an 'update' rather than 'create' event
        self.selected_item = ''
        if self.items:
            self.selected_index = 0
            self.selected_item = self.items[0]
            widget.setCurrentRow(0) 

        widget.itemSelectionChanged.connect(self.on_selection)
        widget.itemChanged.connect(self.on_edit)

        return widget


    def add_item(self, widget, item):
        itemWidget = QListWidgetItem(item)
        if self.checkable:
            itemWidget.setCheckState(Qt.Checked)
        if self.editable:
            _set_item_flag(itemWidget, Qt.ItemIsEditable, True)
        widget.addItem(itemWidget)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_selection(self):
        """ The signal handler for the index changed signal.

        """
        widget = self.get_widget()
        self.selected_index = widget.currentRow()
        self.selected_item = self.items[widget.currentRow()] if self.selected_index >= 0 else u''            

    def on_edit(self, item):
        """ The signal handler for the item changed signal.
        """
        widget = self.get_widget()
        oldLabel = self.items[widget.currentRow()]
        newLabel = item.text()
        self.item_changed(oldLabel, newLabel)
        self.items[widget.currentRow()] = newLabel
        self.selected_item = item.text()

    #--------------------------------------------------------------------------
    # ProxyListStrView API
    #--------------------------------------------------------------------------

    def set_items(self, items, widget = None):
        """
        """
        widget = self.get_widget()
        count = widget.count()
        nitems = len(items)
        for idx, item in enumerate(items[:count]):
            itemWidget = widget.item(idx)
            itemWidget.setText(item)
        if nitems > count:
            for item in items[count:]:
                self.add_item(widget, item)
        elif nitems < count:
            for idx in reversed(xrange(nitems, count)):
                widget.takeItem(idx)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('items')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        name = change['name']
        if self.get_widget():
            if name == 'items':
                self.set_items(self.items)       

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
