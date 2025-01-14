import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import sv_ttk
from utils import resource_path

def create_gui(app, file_ops, networking):
    sv_ttk.set_theme("dark")
    
    main_frame = ttk.Frame(app, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    create_title(main_frame)
    create_mode_switch(main_frame, file_ops)
    create_notebook(main_frame, file_ops, networking)

def create_title(parent):
    title_frame = ttk.Frame(parent)
    title_frame.pack(fill=tk.X, pady=10)

    logo = ImageTk.PhotoImage(Image.open(resource_path("file-icon.png")).resize((50, 50)))
    logo_label = ttk.Label(title_frame, image=logo)
    logo_label.image = logo  # Keep a reference
    logo_label.pack(side=tk.LEFT, padx=(0, 10))

    title_label = ttk.Label(title_frame, text="MEMO File Sharing", font=("Segoe UI", 28, "bold"))
    title_label.pack(side=tk.LEFT)

def create_mode_switch(parent, file_ops):
    mode_var = tk.BooleanVar(value=True)
    mode_switch = ttk.Checkbutton(
        parent, 
        text="Public Mode", 
        variable=mode_var, 
        style="Switch.TCheckbutton", 
        command=lambda: toggle_mode(mode_switch, mode_var, file_ops)
    )
    mode_switch.pack(pady=10)

def toggle_mode(switch, var, file_ops):
    file_ops.public_mode = var.get()
    switch.config(text="Public Mode" if file_ops.public_mode else "Private Mode")
    animate_mode_change(switch)
    messagebox.showinfo("Mode Changed", f"Device is now {'Public' if file_ops.public_mode else 'Private'}.")
    file_ops.update_file_tree()

def animate_mode_change(switch):
    for i in range(5):
        switch.config(text="🌞" if i % 2 == 0 else "🌙")
        switch.update()
        switch.after(100)
    switch.config(text="Public Mode" if switch.cget("text") == "🌞" else "Private Mode")

def create_notebook(parent, file_ops, networking):
    notebook = ttk.Notebook(parent)
    notebook.pack(fill=tk.BOTH, expand=True, pady=10)

    create_file_tab(notebook, file_ops)
    create_devices_tab(notebook, networking)
    create_private_tab(notebook, file_ops)
    create_history_tab(notebook, file_ops)

def create_file_tab(notebook, file_ops):
    file_frame = ttk.Frame(notebook)
    notebook.add(file_frame, text="📂 Files")

    file_controls = ttk.Frame(file_frame)
    file_controls.pack(fill=tk.X, pady=5)

    buttons = [
        ("Share File", file_ops.share_file),
        ("Create Folder", file_ops.create_folder),
        ("Add to Folder", file_ops.add_to_folder),
        ("Toggle Visibility", file_ops.toggle_folder_visibility),
        ("Delete", file_ops.delete_item)
    ]

    for text, command in buttons:
        ttk.Button(file_controls, text=text, command=command, style="Accent.TButton").pack(side=tk.LEFT, padx=5)

    file_ops.file_tree = ttk.Treeview(file_frame, columns=("Type", "Visibility"), show="tree headings")
    file_ops.file_tree.heading("Type", text="Type")
    file_ops.file_tree.heading("Visibility", text="Visibility")
    file_ops.file_tree.column("Type", width=100, anchor="center")
    file_ops.file_tree.column("Visibility", width=100, anchor="center")
    file_ops.file_tree.pack(pady=10, fill=tk.BOTH, expand=True)
    file_ops.file_tree.bind("<Double-1>", file_ops.on_item_double_click)

    file_ops.update_file_tree()

def create_devices_tab(notebook, networking):
    devices_frame = ttk.Frame(notebook)
    notebook.add(devices_frame, text="📡 Devices")

    buttons = [
        ("Scan Network", networking.scan_network),
        ("Add Device Manually", networking.add_manual_device),
        ("Show Current IP", networking.show_current_ip),
        ("Test Connection", networking.test_connection)
    ]

    for text, command in buttons:
        ttk.Button(devices_frame, text=text, command=command, style="Accent.TButton").pack(pady=5)

    networking.devices_list = tk.Listbox(devices_frame, font=("Segoe UI", 12), bg="#2c2c2c", fg="white", selectbackground="#007acc")
    networking.devices_list.pack(pady=10, fill=tk.BOTH, expand=True)
    networking.devices_list.bind('<<ListboxSelect>>', networking.on_device_select)

def create_private_tab(notebook, file_ops):
    private_frame = ttk.Frame(notebook)
    notebook.add(private_frame, text="🔒 Private")

    file_ops.private_list = tk.Listbox(private_frame, font=("Segoe UI", 12), bg="#2c2c2c", fg="white", selectbackground="#007acc")
    file_ops.private_list.pack(pady=10, fill=tk.BOTH, expand=True)

    device_entry_frame = ttk.Frame(private_frame)
    device_entry_frame.pack(fill=tk.X, pady=5)

    file_ops.device_ip_entry = ttk.Entry(device_entry_frame, font=("Segoe UI", 12), width=30)
    file_ops.device_ip_entry.pack(side=tk.LEFT, padx=5)

    ttk.Button(device_entry_frame, text="Add Device", command=file_ops.add_private_device, style="Accent.TButton").pack(side=tk.LEFT)

def create_history_tab(notebook, file_ops):
    history_frame = ttk.Frame(notebook)
    notebook.add(history_frame, text="📜 History")

    file_ops.history_list = tk.Listbox(history_frame, font=("Segoe UI", 12), bg="#2c2c2c", fg="white", selectbackground="#007acc")
    file_ops.history_list.pack(pady=10, fill=tk.BOTH, expand=True)

