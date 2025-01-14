import os
import shutil
import datetime
import logging
from tkinter import filedialog, messagebox, simpledialog

class FileOperations:
    def __init__(self):
        self.public_mode = True
        self.private_devices = set()
        self.sharing_history = []
        self.folders = {}
        self.shared_directory = os.path.join(os.path.expanduser("~"), "SharedFiles")
        if not os.path.exists(self.shared_directory):
            os.makedirs(self.shared_directory)
        
        # These will be set by the GUI
        self.file_tree = None
        self.private_list = None
        self.device_ip_entry = None
        self.history_list = None

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

