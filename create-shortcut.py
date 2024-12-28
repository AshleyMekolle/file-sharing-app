import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "MEMO File Sharing App.lnk")
    target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FileSharingApp.py")
    wDir = os.path.dirname(target)
    icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "file-icon.png")

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = sys.executable
    shortcut.Arguments = f'"{target}"'
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()

if __name__ == "__main__":
    create_shortcut()