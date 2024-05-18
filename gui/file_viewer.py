import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import torch
import numpy as np

import core.utils as utils

class FileViewer(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self.load_button = Gtk.Button(label="Load File")
        self.pack_start(self.load_button, False, False, 0)
        
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.pack_start(self.paned, True, True, 0)
        
        self.tree_store = Gtk.TreeStore(str, str, str)
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        
        for i, column_title in enumerate(["Key", "Type", "Shape/Value"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.tree_view.append_column(column)
        
        self.tree_scrolled_window = Gtk.ScrolledWindow()
        self.tree_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.tree_scrolled_window.add(self.tree_view)

        # Set the default size of the tree_scrolled_window
        self.tree_scrolled_window.set_size_request(-1, 400)  # Width: auto, Height: 400
        
        self.paned.add1(self.tree_scrolled_window)
        
        # Create a vertical box to hold the content label, range input, and content text view
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self.content_label = Gtk.Label(label="Contents:")
        self.content_box.pack_start(self.content_label, False, False, 0)
        
        self.range_input = Gtk.Entry()
        self.range_input.set_placeholder_text("Select range: [start:end]")
        self.content_box.pack_start(self.range_input, False, False, 0)
        
        self.content_scrolled_window = Gtk.ScrolledWindow()
        self.content_scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.content_textview = Gtk.TextView()
        self.content_textview.set_editable(False)
        self.content_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.content_scrolled_window.add(self.content_textview)
        
        self.content_box.pack_start(self.content_scrolled_window, True, True, 0)
        
        self.paned.add2(self.content_box)
        
        self.tree_view.get_selection().connect("changed", self.on_tree_selection_changed)
    
    def display_data(self, data, parent=None, key='Root'):
        '''
        Display a data structure in the tree view.

        Except when parent==None, the entry for `data` is already created 
        in the tree view at `parent`.  
        '''
        if parent is None:
            self.tree_store.clear()

        if isinstance(data, (torch.Tensor, np.ndarray)):
            shape_disp = str(list(data.shape))
        elif isinstance(data, str):
            shape_disp = data
        else:
            shape_disp = ''
        this = self.tree_store.append(parent, [key, str(type(data)), shape_disp])

        if isinstance(data, dict):
            for key, value in data.items():
                self.display_data(data=value, parent=this, key=key)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                self.display_data(data=value, parent=this, key=str(index))
    
    def on_tree_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        if tree_iter is not None:
            key = model[tree_iter][0]
            data_type = model[tree_iter][1]
            shape_or_value = model[tree_iter][2]
            self.update_content_textview(key, data_type, shape_or_value)
    
    def update_content_textview(self, key, data_type, shape_or_value):
        buffer = self.content_textview.get_buffer()
        buffer.set_text('')
        
        # Display the contents of arrays
        if "torch.Tensor" in data_type or "numpy.ndarray" in data_type:
            data = self.get_data_from_tree(key)
            if data is not None:
                buffer.insert(buffer.get_end_iter(), utils.pretty_print(data))
                '''
                if data.ndim == 0:
                    buffer.insert(buffer.get_end_iter(), str(data.item()))
                elif data.ndim == 1:
                    buffer.insert(buffer.get_end_iter(), str(data))
                elif data.ndim == 2:
                    for row in data:
                        buffer.insert(buffer.get_end_iter(), ' '.join(map(str, row)) + '\n')
                        '''

    def get_data_from_tree(self, key):
        # Traverse the tree to find the data corresponding to the key
        def traverse(data, key):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == key:
                        return v
                    result = traverse(v, key)
                    if result is not None:
                        return result
            elif isinstance(data, list):
                for index, value in enumerate(data):
                    result = traverse(value, key)
                    if result is not None:
                        return result
            return None
        
        # Start traversal from the root data
        return traverse(self.root_data, key)
    
    def set_root_data(self, data):
        self.root_data = data
        self.display_data(data)
