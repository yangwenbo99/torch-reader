import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from .file_viewer import FileViewer
from core.file_loader import load_file
from core.data_parser import parse_data

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Torch-Reader")
        self.set_default_size(800, 600)
        
        self.file_viewer = FileViewer()
        self.add(self.file_viewer)
        
        self.initUI()
    
    def initUI(self):
        self.file_viewer.load_button.connect("clicked", self.load_file)
    
    def load_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Open File", 
            parent=self, 
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_pt = Gtk.FileFilter()
        filter_pt.set_name("PyTorch Checkpoints")
        filter_pt.add_pattern("*.pt")
        dialog.add_filter(filter_pt)
        
        filter_npy = Gtk.FileFilter()
        filter_npy.set_name("NumPy Files")
        filter_npy.add_pattern("*.npy")
        dialog.add_filter(filter_npy)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            data = load_file(file_path)
            # parsed_data = parse_data(data)
            self.file_viewer.display_data(data)
            self.file_viewer.set_root_data(data)
            self.set_title(f"Torch-Reader - {file_path}")
        
        dialog.destroy()
