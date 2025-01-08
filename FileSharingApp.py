import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import socket
import os
import threading
import shutil
from PIL import Image, ImageTk
import sv_ttk
import datetime
import sys
import logging
import json
import struct
import time
import select
import zipfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileSharingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MEMO File Sharing App")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")
        self.resizable(True, True)

        # Apply Sun Valley theme
        sv_ttk.set_theme("dark")

        self.public_mode = True
        self.private_devices = set()
        self.sharing_history = []
        self.folders = {}
        self.current_folder = None
        self.host = self.get_wifi_ip() or socket.gethostbyname(socket.gethostname())
        self.port = 5000

        # Create a directory for shared files
        self.shared_directory = os.path.join(os.path.expanduser("~"), "SharedFiles")
        if not os.path.exists(self.shared_directory):
            os.makedirs(self.shared_directory)

        self.create_widgets()
        self.start_file_server()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title with fun icon
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=10)

        self.logo = ImageTk.PhotoImage(Image.open(self.resource_path("file-icon.png")).resize((50, 50)))
        logo_label = ttk.Label(title_frame, image=self.logo)
        logo_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = ttk.Label(title_frame, text="MEMO File Sharing", font=("Segoe UI", 28, "bold"))
        title_label.pack(side=tk.LEFT)

        # Mode toggle with animation
        self.mode_var = tk.BooleanVar(value=True)
        self.mode_switch = ttk.Checkbutton(
            main_frame, 
            text="Public Mode", 
            variable=self.mode_var, 
            style="Switch.TCheckbutton", 
            command=self.toggle_mode
        )
        self.mode_switch.pack(pady=10)

        # Notebook for different sections
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # File Management tab
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="📂 Files")

        file_controls = ttk.Frame(file_frame)
        file_controls.pack(fill=tk.X, pady=5)

        share_file_button = ttk.Button(file_controls, text="Share File", command=self.share_file, style="Accent.TButton")
        share_file_button.pack(side=tk.LEFT, padx=5)

        create_folder_button = ttk.Button(file_controls, text="Create Folder", command=self.create_folder, style="Accent.TButton")
        create_folder_button.pack(side=tk.LEFT, padx=5)

        add_to_folder_button = ttk.Button(file_controls, text="Add to Folder", command=self.add_to_folder, style="Accent.TButton")
        add_to_folder_button.pack(side=tk.LEFT, padx=5)

        toggle_visibility_button = ttk.Button(file_controls, text="Toggle Visibility", command=self.toggle_folder_visibility, style="Accent.TButton")
        toggle_visibility_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(file_controls, text="Delete", command=self.delete_item, style="Accent.TButton")
        delete_button.pack(side=tk.LEFT, padx=5)

        self.file_tree = ttk.Treeview(file_frame, columns=("Type", "Visibility"), show="tree headings")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.heading("Visibility", text="Visibility")
        self.file_tree.column("Type", width=100, anchor="center")
        self.file_tree.column("Visibility", width=100, anchor="center")
        self.file_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.file_tree.bind("<Double-1>", self.on_item_double_click)

        # Devices tab
        devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(devices_frame, text="📡 Devices")

        scan_button = ttk.Button(devices_frame, text="Scan Network", command=self.scan_network, style="Accent.TButton")
        scan_button.pack(pady=10)

        manual_add_button = ttk.Button(devices_frame, text="Add Device Manually", command=self.add_manual_device, style="Accent.TButton")
        manual_add_button.pack(pady=5)

        show_ip_button = ttk.Button(devices_frame, text="Show Current IP", command=self.show_current_ip, style="Accent.TButton")
        show_ip_button.pack(pady=5)

        self.devices_list = tk.Listbox(devices_frame, font=("Segoe UI", 12), bg="#2c2c2c", fg="white", selectbackground="#007acc")
        self.devices_list.pack(pady=10, fill=tk.BOTH, expand=True)
        self.devices_list.bind('<<ListboxSelect>>', self.on_device_select)

        # Private devices tab
        private_frame = ttk.Frame(self.notebook)
        self.notebook.add(private_frame, text="🔒 Private")

        self.private_list = tk.Listbox(private_frame, font=("Segoe UI", 12), bg="#2c2c2c", fg="white", selectbackground="#007acc")
        self.private_list.pack(pady=10, fill=tk.BOTH, expand=True)

        device_entry_frame = ttk.Frame(private_frame)
        device_entry_frame.pack(fill=tk.X, pady=5)

        self.device_ip_entry = ttk.Entry(device_entry_frame, font=("Segoe UI", 12), width=30)
        self.device_ip_entry.pack(side=tk.LEFT, padx=5)

        add_device_button = ttk.Button(device_entry_frame, text="Add Device", command=self.add_private_device, style="Accent.TButton")
        add_device_button.pack(side=tk.LEFT)

        # History tab
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="📜 History")

        self.history_list = tk.Listbox(history_frame, font=("Segoe UI", 12), bg="#2c2c2c", fg="white", selectbackground="#007acc")
        self.history_list.pack(pady=10, fill=tk.BOTH, expand=True)

        self.update_file_tree()

    def toggle_mode(self):
        self.public_mode = self.mode_var.get()
        self.mode_switch.config(text="Public Mode" if self.public_mode else "Private Mode")
        self.animate_mode_change()
        messagebox.showinfo("Mode Changed", f"Device is now {'Public' if self.public_mode else 'Private'}.")
        self.update_file_tree()

    def animate_mode_change(self):
        for i in range(5):
            self.mode_switch.config(text="🌞" if i % 2 == 0 else "🌙")
            self.update()
            self.after(100)
        self.mode_switch.config(text="Public Mode" if self.public_mode else "Private Mode")

    def share_file(self):
        file_path = filedialog.askopenfilename(title="Select File to Share")
        if file_path:
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(self.shared_directory, file_name)
            shutil.copy2(file_path, dest_path)
            self.sharing_history.append(f"📤 Shared file '{file_name}' at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.update_history()
            self.update_file_tree()
            messagebox.showinfo("File Shared", f"File '{file_name}' has been shared successfully!")

    def create_folder(self):
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            folder_path = os.path.join(self.shared_directory, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                self.folders[folder_name] = {"public": self.public_mode, "files": []}
                self.update_file_tree()
                messagebox.showinfo("Folder Created", f"Folder '{folder_name}' has been created successfully!")
            else:
                messagebox.showerror("Error", f"Folder '{folder_name}' already exists!")

    def ensure_folder_tracked(self, folder_name):
        if folder_name not in self.folders:
            self.folders[folder_name] = {"public": True, "files": []}
            logging.info(f"Added missing folder to tracking: {folder_name}")

    def add_to_folder(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Add to Folder", "Please select a folder to add files to.")
            return

        folder_name = self.file_tree.item(selected[0])['text']
        folder_path = os.path.join(self.shared_directory, folder_name)
        if not os.path.isdir(folder_path):
            messagebox.showwarning("Add to Folder", "Please select a folder, not a file.")
            return

        if not self.public_mode and not self.folders[folder_name]["public"]:
            if not self.check_private_access():
                return

        files = filedialog.askopenfilenames(title="Select Files to Add")
        if files:
            for file_path in files:
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(folder_path, file_name)
                shutil.copy2(file_path, dest_path)
            self.update_file_tree()
            messagebox.showinfo("Files Added", f"{len(files)} file(s) have been added to '{folder_name}'!")

    def toggle_folder_visibility(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Toggle Visibility", "Please select a folder to toggle visibility.")
            return

        item_name = self.file_tree.item(selected[0])['text']
        item_path = os.path.join(self.shared_directory, item_name)
    
        if os.path.isdir(item_path):
            self.ensure_folder_tracked(item_name)
            self.folders[item_name]["public"] = not self.folders[item_name]["public"]
            visibility = "Public" if self.folders[item_name]["public"] else "Private"
            self.update_file_tree()
            messagebox.showinfo("Visibility Changed", f"Folder '{item_name}' is now {visibility}.")
        else:
            messagebox.showwarning("Toggle Visibility", "Please select a folder, not a file.")

    def update_file_tree(self):
        logging.info(f"Updating file tree. Shared directory contents: {os.listdir(self.shared_directory)}")
        logging.info(f"Current folders: {self.folders}")
        self.file_tree.delete(*self.file_tree.get_children())
        for item in os.listdir(self.shared_directory):
            item_path = os.path.join(self.shared_directory, item)
            if os.path.isdir(item_path):
                self.ensure_folder_tracked(item)
                visibility = "Public" if self.folders[item]["public"] else "Private"
                folder_id = self.file_tree.insert("", "end", text=item, values=("Folder", visibility))
                if self.public_mode or self.folders[item]["public"] or self.check_private_access():
                    for file in os.listdir(item_path):
                        self.file_tree.insert(folder_id, "end", text=file, values=("File", ""))
            else:
                self.file_tree.insert("", "end", text=item, values=("File", "Public"))
        logging.info("File tree updated successfully")

    def on_item_double_click(self, event):
        item = self.file_tree.selection()[0]
        item_type = self.file_tree.item(item, "values")[0]
        if item_type == "File":
            file_path = os.path.join(self.shared_directory, self.file_tree.item(item, "text"))
            os.startfile(file_path)

    def delete_item(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Please select an item to delete.")
            return

        item = selected[0]
        item_name = self.file_tree.item(item, "text")
        item_path = os.path.join(self.shared_directory, item_name)

        if os.path.isdir(item_path):
            if not self.public_mode and not self.folders[item_name]["public"]:
                if not self.check_private_access():
                    return
            if messagebox.askyesno("Delete Folder", f"Are you sure you want to delete the folder '{item_name}' and all its contents?"):
                shutil.rmtree(item_path)
                del self.folders[item_name]
        else:
            parent = self.file_tree.parent(item)
            if parent:
                folder_name = self.file_tree.item(parent, "text")
                if not self.public_mode and not self.folders[folder_name]["public"]:
                    if not self.check_private_access():
                        return
            if messagebox.askyesno("Delete File", f"Are you sure you want to delete the file '{item_name}'?"):
                os.remove(item_path)

        self.update_file_tree()

    def scan_network(self):
        self.devices_list.delete(0, tk.END)
        self.devices_list.insert(tk.END, "🔍 Scanning for devices...")
    
        def scan():
            self.devices_list.delete(0, tk.END)
            host = self.get_wifi_ip() or socket.gethostbyname(socket.gethostname())
            subnet = ".".join(host.split(".")[:-1])
            
            def check_ip(ip):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.1)
                        s.connect((ip, self.port))
                        self.devices_list.insert(tk.END, f"💻 {ip}")
                except:
                    pass

            threads = []
            for i in range(1, 255):
                ip = f"{subnet}.{i}"
                thread = threading.Thread(target=check_ip, args=(ip,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            if self.devices_list.size() == 0:
                self.devices_list.insert(tk.END, "No devices found")

        threading.Thread(target=scan).start()

    def add_private_device(self):
        device_ip = self.device_ip_entry.get()
        if device_ip:
            self.private_devices.add(device_ip)
            self.private_list.insert(tk.END, f"🔒 {device_ip}")
            self.device_ip_entry.delete(0, tk.END)

    def update_history(self):
        self.history_list.delete(0, tk.END)
        for entry in self.sharing_history:
            self.history_list.insert(tk.END, entry)

    def check_private_access(self):
        client_ip = socket.gethostbyname(socket.gethostname())
        if client_ip in self.private_devices:
            return True
        else:
            messagebox.showerror("Access Denied", "You don't have permission to access this private folder.")
            return False

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def share_file_list(self):
        file_list = []
        for item in os.listdir(self.shared_directory):
            item_path = os.path.join(self.shared_directory, item)
            if os.path.isdir(item_path):
                if self.folders[item]["public"]:
                    file_list.append({"name": item, "type": "folder", "public": True})
                    for file in os.listdir(item_path):
                        file_list.append({"name": f"{item}/{file}", "type": "file", "public": True})
            else:
                file_list.append({"name": item, "type": "file", "public": True})
        
        return json.dumps(file_list)

    def request_file_list(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, self.port))
                s.sendall(b"REQUEST_FILE_LIST")
                data = s.recv(4096)
                return json.loads(data.decode())
            except:
                return None

    def start_file_server(self):
        def serve():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                while True:
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data == b"REQUEST_FILE_LIST":
                            file_list = self.share_file_list()
                            conn.sendall(file_list.encode())
                        elif data.startswith(b"DOWNLOAD:"):
                            item_name = data[9:].decode()
                            self.handle_download(conn, item_name)


        threading.Thread(target=serve, daemon=True).start()

    def on_device_select(self, event):
        selected_indices = self.devices_list.curselection()
        if selected_indices:
            selected_ip = self.devices_list.get(selected_indices[0]).split()[-1]
            file_list = self.request_file_list(selected_ip)
            if file_list:
                self.display_remote_files(file_list, selected_ip)
            else:
                messagebox.showerror("Error", f"Unable to retrieve file list from {selected_ip}")

    def display_remote_files(self, file_list, remote_ip):
        remote_files_window = tk.Toplevel(self)
        remote_files_window.title(f"Remote Files - {remote_ip}")
        remote_files_window.geometry("500x400")

        remote_files_tree = ttk.Treeview(remote_files_window, columns=("Type", "Visibility"), show="tree headings")
        remote_files_tree.heading("Type", text="Type")
        remote_files_tree.heading("Visibility", text="Visibility")
        remote_files_tree.column("Type", width=100, anchor="center")
        remote_files_tree.column("Visibility", width=100, anchor="center")
        remote_files_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        for item in file_list:
            if item["type"] == "folder":
                folder_id = remote_files_tree.insert("", "end", text=item["name"], values=("Folder", "Public" if item["public"] else "Private"))
            else:
                if "/" in item["name"]:
                    folder, file = item["name"].split("/", 1)
                    folder_id = remote_files_tree.insert("", "end", text=folder, values=("Folder", "Public"))
                    remote_files_tree.insert(folder_id, "end", text=file, values=("File", "Public"))
                else:
                    remote_files_tree.insert("", "end", text=item["name"], values=("File", "Public"))

        download_button = ttk.Button(remote_files_window, text="Download Selected", command=lambda: self.download_selected(remote_files_tree, remote_ip))
        download_button.pack(pady=10)

    def download_selected(self, tree, remote_ip):
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Download", "Please select items to download.")
            return

        save_path = filedialog.askdirectory(title="Select Download Location")
        if not save_path:
            return

        for item in selected_items:
            item_text = tree.item(item, "text")
            item_type = tree.item(item, "values")[0]
            self.request_download(remote_ip, item_text, item_type, save_path)

    def request_download(self, remote_ip, item_name, item_type, save_path):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((remote_ip, self.port))
                s.sendall(f"DOWNLOAD:{item_name}".encode())
                
                file_size = struct.unpack("!Q", s.recv(8))[0]
                received_size = 0
                
                if item_type == "Folder":
                    zip_path = os.path.join(save_path, f"{item_name}.zip")
                    with open(zip_path, "wb") as f:
                        while received_size < file_size:
                            chunk = s.recv(4096)
                            if not chunk:
                                break
                            f.write(chunk)
                            received_size += len(chunk)
                    
                    # Extract the zip file
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(save_path)
                    os.remove(zip_path)
                else:
                    file_path = os.path.join(save_path, item_name)
                    with open(file_path, "wb") as f:
                        while received_size < file_size:
                            chunk = s.recv(4096)
                            if not chunk:
                                break
                            f.write(chunk)
                            received_size += len(chunk)
                
                messagebox.showinfo("Download Complete", f"{item_name} has been downloaded successfully.")
            except Exception as e:
                messagebox.showerror("Download Error", f"Failed to download {item_name}: {str(e)}")

    def handle_download(self, conn, item_name):
        item_path = os.path.join(self.shared_directory, item_name)
        if os.path.isdir(item_path):
            # Create a temporary zip file
            zip_path = os.path.join(self.shared_directory, f"{item_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(item_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, item_path)
                        zipf.write(file_path, arcname)
            
            file_size = os.path.getsize(zip_path)
            conn.sendall(struct.pack("!Q", file_size))
            
            with open(zip_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)
            
            os.remove(zip_path)
        else:
            file_size = os.path.getsize(item_path)
            conn.sendall(struct.pack("!Q", file_size))
            
            with open(item_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)

    def add_manual_device(self):
        ip = simpledialog.askstring("Add Device", "Enter the IP address of the device:")
        if ip:
            self.devices_list.insert(tk.END, f"💻 {ip}")
            messagebox.showinfo("Device Added", f"Device with IP {ip} has been added to the list.")

    def get_wifi_ip(self):
        import subprocess
        import re

        try:
            # For Windows
            if os.name == 'nt':
                output = subprocess.check_output(['ipconfig']).decode('utf-8')
                wifi_section = re.search(r'Wireless LAN adapter WiFi:(.*?)(\n\n|\Z)', output, re.DOTALL)
                if wifi_section:
                    ip_match = re.search(r'IPv4 Address[.\s]+: ([^\s]+)', wifi_section.group(1))
                    if ip_match:
                        return ip_match.group(1)
            # For Unix-based systems (Linux, macOS)
            else:
                output = subprocess.check_output(['ifconfig']).decode('utf-8')
                wifi_section = re.search(r'(wlan0|en0):(.*?)(\n\n|\Z)', output, re.DOTALL)
                if wifi_section:
                    ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', wifi_section.group(2))
                    if ip_match:
                        return ip_match.group(1)
        except Exception as e:
            logging.error(f"Error getting Wi-Fi IP: {e}")
    
        return None

    def show_current_ip(self):
        ip = self.get_wifi_ip() or socket.gethostbyname(socket.gethostname())
        messagebox.showinfo("Current IP", f"Your current IP address is: {ip}")


if __name__ == "__main__":
    app = FileSharingApp()
    app.mainloop()

