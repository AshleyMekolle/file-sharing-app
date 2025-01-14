import socket
import threading
import json
import struct
import zipfile
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from utils import get_wifi_ip, scan_network

class Networking:
    def __init__(self, file_ops):
        self.file_ops = file_ops
        self.host = get_wifi_ip()
        if not self.host:
            self.host = socket.gethostbyname(socket.gethostname())
            print(f"Warning: Could not get WiFi IP, using fallback IP: {self.host}")
        self.port = 5000
        self.devices_list = None  # Will be set by GUI

    def start_file_server(self):
        def serve():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                print(f"File server started on {self.host}:{self.port}")
                while True:
                    conn, addr = s.accept()
                    print(f"Accepted connection from {addr}")
                    with conn:
                        try:
                            data = conn.recv(1024)
                            if data == b"REQUEST_FILE_LIST":
                                file_list = self.file_ops.share_file_list()
                                conn.sendall(file_list.encode())
                            elif data.startswith(b"DOWNLOAD:"):
                                item_name = data[9:].decode()
                                self.handle_download(conn, item_name)
                            elif data == b"TEST_CONNECTION":
                                conn.sendall(b"CONNECTION_OK")
                        except Exception as e:
                            print(f"Error handling connection from {addr}: {str(e)}")

        threading.Thread(target=serve, daemon=True).start()

    def scan_network(self):
        self.devices_list.delete(0, tk.END)
        self.devices_list.insert(tk.END, "🔍 Scanning for devices...")
        self.devices_list.update()

        def scan():
            self.devices_list.delete(0, tk.END)
            if self.host:
                active_hosts = scan_network(self.host)
                for host, hostname in active_hosts:
                    self.devices_list.insert(tk.END, f"💻 {host} ({hostname})")
            
            if self.devices_list.size() == 0:
                self.devices_list.insert(tk.END, "No devices found")

        threading.Thread(target=scan, daemon=True).start()

    def on_device_select(self, event):
        selected_indices = self.devices_list.curselection()
        if selected_indices:
            selected_ip = self.devices_list.get(selected_indices[0]).split()[1]
            file_list = self.request_file_list(selected_ip)
            if file_list:
                self.display_remote_files(file_list, selected_ip)
            else:
                messagebox.showerror("Error", f"Unable to retrieve file list from {selected_ip}")

    def request_file_list(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(5)  # Set a timeout of 5 seconds
                s.connect((ip, self.port))
                s.sendall(b"REQUEST_FILE_LIST")
                data = s.recv(4096)
                return json.loads(data.decode())
            except socket.timeout:
                print(f"Connection to {ip} timed out")
                return None
            except Exception as e:
                print(f"Error requesting file list from {ip}: {str(e)}")
                return None

    def display_remote_files(self, file_list, remote_ip):
        remote_files_window = tk.Toplevel()
        remote_files_window.title(f"Files on {remote_ip}")
        remote_files_window.geometry("400x300")

        listbox = tk.Listbox(remote_files_window)
        listbox.pack(fill=tk.BOTH, expand=True)

        for file in file_list:
            listbox.insert(tk.END, file['name'])

        download_button = tk.Button(remote_files_window, text="Download Selected", command=lambda: self.download_selected(listbox, remote_ip))
        download_button.pack()

    def download_selected(self, listbox, remote_ip):
        selected = listbox.curselection()
        if selected:
            file_name = listbox.get(selected[0])
            self.request_download(remote_ip, file_name)

    def request_download(self, remote_ip, file_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((remote_ip, self.port))
                s.sendall(f"DOWNLOAD:{file_name}".encode())
                file_size = struct.unpack("!Q", s.recv(8))[0]
            
                save_path = filedialog.asksaveasfilename(defaultextension="", initialfile=file_name)
                if save_path:
                    with open(save_path, "wb") as f:
                        remaining = file_size
                        while remaining:
                            chunk = s.recv(min(remaining, 4096))
                            if not chunk:
                                break
                            f.write(chunk)
                            remaining -= len(chunk)
                    messagebox.showinfo("Download Complete", f"{file_name} has been downloaded successfully.")
            except Exception as e:
                messagebox.showerror("Download Error", f"Failed to download {file_name}: {str(e)}")

    def handle_download(self, conn, item_name):
        item_path = os.path.join(self.file_ops.shared_directory, item_name)
        if os.path.isdir(item_path):
            # Create a temporary zip file
            zip_path = os.path.join(self.file_ops.shared_directory, f"{item_name}.zip")
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

    def show_current_ip(self):
        ip = get_wifi_ip() or socket.gethostbyname(socket.gethostname())
        messagebox.showinfo("Current IP", f"Your current IP address is: {ip}")

    def test_connection(self):
        ip = simpledialog.askstring("Test Connection", "Enter the IP address to test:")
        if ip:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((ip, self.port))
                    s.sendall(b"TEST_CONNECTION")
                    response = s.recv(1024)
                    if response == b"CONNECTION_OK":
                        messagebox.showinfo("Connection Test", f"Successfully connected to {ip}")
                    else:
                        messagebox.showerror("Connection Test", f"Received unexpected response from {ip}")
            except socket.timeout:
                messagebox.showerror("Connection Test", f"Connection to {ip} timed out")
            except Exception as e:
                messagebox.showerror("Connection Test", f"Failed to connect to {ip}: {str(e)}")

