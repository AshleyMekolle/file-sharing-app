import socket
import threading
import json
import struct
import zipfile
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from utils import get_wifi_ip

class Networking:
    def __init__(self, file_ops):
        self.file_ops = file_ops
        self.host = get_wifi_ip() or socket.gethostbyname(socket.gethostname())
        self.port = 5000
        self.devices_list = None  # Will be set by GUI
        self.shared_directory = self.file_ops.shared_directory

    def start_file_server(self):
        def serve():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                print(f"File server started on {self.host}:{self.port}")
                while True:
                    conn, addr = s.accept()
                    print(f"Accepted connection from {addr}")
                    threading.Thread(target=self.handle_client, args=(conn, addr)).start()

        threading.Thread(target=serve, daemon=True).start()

    def handle_client(self, conn, addr):
        try:
            data = conn.recv(1024).decode()
            if data.startswith("REQUEST_FILE_LIST"):
                file_list = self.file_ops.share_file_list()
                conn.sendall(json.dumps(file_list).encode())
            elif data.startswith("DOWNLOAD:"):
                file_name = data.split(":")[1]
                self.send_file(conn, file_name)
            elif data.startswith("UPLOAD:"):
                file_name = data.split(":")[1]
                self.receive_file(conn, file_name)
        except Exception as e:
            print(f"Error handling connection from {addr}: {str(e)}")
        finally:
            conn.close()

    def send_file(self, conn, file_name):
        file_path = os.path.join(self.shared_directory, file_name)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            conn.sendall(struct.pack("!Q", file_size))
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    conn.sendall(chunk)
            print(f"File {file_name} sent successfully")
        else:
            conn.sendall(struct.pack("!Q", 0))  # Send 0 size to indicate file not found

    def receive_file(self, conn, file_name):
        file_size = struct.unpack("!Q", conn.recv(8))[0]
        if file_size > 0:
            file_path = os.path.join(self.shared_directory, file_name)
            with open(file_path, "wb") as f:
                remaining = file_size
                while remaining > 0:
                    chunk = conn.recv(min(remaining, 4096))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)
            print(f"File {file_name} received successfully")
            self.file_ops.update_file_tree()
        else:
            print(f"File {file_name} not found on sender's side")

    def scan_network(self):
        self.devices_list.delete(0, tk.END)
        self.devices_list.insert(tk.END, "🔍 Scanning for devices...")

        def scan():
            self.devices_list.delete(0, tk.END)
            network = '.'.join(self.host.split('.')[:-1]) + '.'
            active_hosts = []

            def check_host(ip):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.1)
                        s.connect((ip, self.port))
                        return ip
                except:
                    return None

            threads = []
            for i in range(1, 255):
                ip = network + str(i)
                thread = threading.Thread(target=lambda: active_hosts.append(check_host(ip)))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            active_hosts = [host for host in active_hosts if host]
            for host in active_hosts:
                if host != self.host:
                    self.devices_list.insert(tk.END, f"💻 {host}")

            if self.devices_list.size() == 0:
                self.devices_list.insert(tk.END, "No devices found")

        threading.Thread(target=scan).start()

    def on_device_select(self, event):
        selected_indices = self.devices_list.curselection()
        if selected_indices:
            selected_ip = self.devices_list.get(selected_indices[0]).split()[-1]
            file_list = self.request_file_list(selected_ip)
            if file_list:
                self.display_remote_files(file_list, selected_ip)
            else:
                messagebox.showerror("Error", f"Unable to retrieve file list from {selected_ip}")

    def request_file_list(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(5)
                s.connect((ip, self.port))
                s.sendall("REQUEST_FILE_LIST".encode())
                data = s.recv(4096)
                return json.loads(data.decode())
            except Exception as e:
                print(f"Error requesting file list from {ip}: {str(e)}")
                return None

    def display_remote_files(self, file_list, remote_ip):
        remote_files_window = tk.Toplevel()
        remote_files_window.title(f"Files on {remote_ip}")
        remote_files_window.geometry("400x300")

        listbox = tk.Listbox(remote_files_window, font=("Segoe UI", 12))
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        for file in file_list:
            listbox.insert(tk.END, file['name'])

        def download_selected():
            selection = listbox.curselection()
            if selection:
                file_name = listbox.get(selection[0])
                save_path = filedialog.asksaveasfilename(defaultextension="", initialfile=file_name)
                if save_path:
                    self.download_file(remote_ip, file_name, save_path)

        download_button = tk.Button(remote_files_window, text="Download", command=download_selected)
        download_button.pack(pady=10)

    def download_file(self, remote_ip, file_name, save_path):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((remote_ip, self.port))
                s.sendall(f"DOWNLOAD:{file_name}".encode())
                file_size = struct.unpack("!Q", s.recv(8))[0]
                if file_size > 0:
                    with open(save_path, "wb") as f:
                        remaining = file_size
                        while remaining > 0:
                            chunk = s.recv(min(remaining, 4096))
                            if not chunk:
                                break
                            f.write(chunk)
                            remaining -= len(chunk)
                    messagebox.showinfo("Download Complete", f"{file_name} has been downloaded successfully.")
                else:
                    messagebox.showerror("Download Error", f"File {file_name} not found on the remote device.")
            except Exception as e:
                messagebox.showerror("Download Error", f"Failed to download {file_name}: {str(e)}")

    def upload_file(self, remote_ip):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((remote_ip, self.port))
                    s.sendall(f"UPLOAD:{file_name}".encode())
                    file_size = os.path.getsize(file_path)
                    s.sendall(struct.pack("!Q", file_size))
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(4096)
                            if not chunk:
                                break
                            s.sendall(chunk)
                    messagebox.showinfo("Upload Complete", f"{file_name} has been uploaded successfully.")
                except Exception as e:
                    messagebox.showerror("Upload Error", f"Failed to upload {file_name}: {str(e)}")

    def add_manual_device(self):
        ip = simpledialog.askstring("Add Device", "Enter the IP address of the device:")
        if ip:
            self.devices_list.insert(tk.END, f"💻 {ip}")
            messagebox.showinfo("Device Added", f"Device with IP {ip} has been added to the list.")

    def show_current_ip(self):
        messagebox.showinfo("Current IP", f"Your current IP address is: {self.host}")

