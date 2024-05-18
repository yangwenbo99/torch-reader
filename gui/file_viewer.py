import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import re
import traceback

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
        
        self.tree_store = Gtk.TreeStore(str, str, str, object)
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
        self.range_input.connect("activate", self.on_range_input_activate)

        
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
        this = self.tree_store.append(parent, [key, str(type(data)), shape_disp, data])

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
            data_object = model[tree_iter][3]
            self.update_content_textview(key, data_type, shape_or_value, data_object)
            self.selected_data = data_object
    
    def update_content_textview(
            self, key: str, data_type: str, 
            shape_or_value: str, data_object: object):
        buffer = self.content_textview.get_buffer()
        buffer.set_text('')
        # Display the contents of arrays
        if "Tensor" in data_type or "ndarray" in data_type or \
                "str" in data_type or "int" in data_type or \
                "float" in data_type or "bool" in data_type:
            if data_object is not None:
                buffer.insert(buffer.get_end_iter(), utils.pretty_print(data_object))

    def set_buffer_text(self, text: str):
        buffer = self.content_textview.get_buffer()
        buffer.set_text(text)

    def display_data_item(self, data):
        self.set_buffer_text(utils.pretty_print(data))


    def on_range_input_activate(self, entry):
        range_text = entry.get_text()
        if (santized_range := self.sanitize_range(range_text)):
            try:
                # Evaluate the sanitized range expression in a restricted environment
                selected_data = eval(
                        f"a[{santized_range}]", 
                        {"__builtins__": {}, },
                        {"a": self.selected_data})
                self.display_data_item(selected_data)
            except Exception as e:
                self.set_buffer_text(f"Error evaluating range: a[{santized_range}]\n{repr(e)}")
                traceback.print_exc()
        else:
            self.set_buffer_text("Invalid range input detected")

    def sanitize_range(self, expression: str):
        # Remove spaces and validate characters
        sanitized = re.sub(r"\s", "", expression)
        if len(sanitized) == 0:
            return None

        if sanitized[0] == '[' and sanitized[-1] == ']':
            sanitized = sanitized[1:-1]
        if re.match(r"^[0-9:\-,]+$", sanitized):
            return sanitized
        else:
            return None
    
    def set_root_data(self, data):
        self.root_data = data
        self.display_data(data)

        self.selected_data = data
