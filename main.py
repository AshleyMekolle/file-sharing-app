import tkinter as tk
from gui import create_gui
from file_operations import FileOperations
from networking import Networking
from utils import get_wifi_ip, resource_path

class FileSharingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MEMO File Sharing App")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")
        self.resizable(True, True)

        self.file_ops = FileOperations()
        self.networking = Networking(self.file_ops)
        
        create_gui(self, self.file_ops, self.networking)
        self.networking.start_file_server()

if __name__ == "__main__":
    app = FileSharingApp()
    app.mainloop()

