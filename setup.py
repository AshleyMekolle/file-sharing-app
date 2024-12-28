import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "tkinter", "socket", "threading", "shutil", "PIL", "sv_ttk"],
    "include_files": ["send-button.png"],
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="MIMO File Sharing App",
    version="1.0",
    description="A fun and user-friendly file sharing application",
    options={"build_exe": build_exe_options},
    executables=[Executable("FileSharingApp.py", base=base, icon="send-button.ico")]
)