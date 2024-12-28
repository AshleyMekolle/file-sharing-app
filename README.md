# MEMO File Sharing App: Complete Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [System Requirements](#system-requirements)
4. [Installation Guide](#installation-guide)
5. [Usage Instructions](#usage-instructions)
6. [Security Considerations](#security-considerations)
7. [Troubleshooting](#troubleshooting)
8. [Future Development](#future-development)
9. [Support and Contact](#support-and-contact)

## 1. Introduction

MEMO File Sharing App is a powerful, user-friendly desktop application designed for seamless file sharing across local networks. Built with Python and Tkinter, MEMO offers an intuitive interface with a modern design, making file sharing and management a breeze for users of all technical levels.

## 2. Features

- **Dual Mode Operation**: Switch between Public and Private sharing modes.
- **File Sharing**: Easily share files across your local network.
- **Folder Management**: Create and organize folders for shared files.
- **Visibility Control**: Toggle folder visibility between public and private.
- **Network Discovery**: Scan and discover devices on your local network.
- **Private Device Management**: Maintain a list of trusted devices for secure sharing.
- **Sharing History**: Keep track of all file sharing activities.
- **Modern UI**: Sleek, responsive interface with animations and a dark theme.
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux.

## 3. System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, Fedora 30+)
- **Python**: Version 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for the application, plus additional space for shared files
- **Network**: Active internet connection for installation; local network for file sharing
- **Display**: 1280x720 resolution or higher

## 4. Installation Guide

### Step 1: Install Python
If you don't have Python installed:
1. Visit the official Python website: https://www.python.org/downloads/
2. Download the latest version for your operating system.
3. Run the installer, ensuring you check "Add Python to PATH".

### Step 2: Download MEMO File Sharing App
1. Visit the MEMO GitHub repository: https://github.com/AshleyMekolle/file-sharing-app
2. Click on "Code" and select "Download ZIP".
3. Extract the ZIP file to your desired location.

### Step 3: Set Up a Virtual Environment (Optional but Recommended)
Open a terminal/command prompt and navigate to the extracted folder:

```bash
cd path/to/FileSharingApp
python -m venv venv
Activate the virtual environment:

- On Windows: `venv\Scripts\activate`
- On macOS/Linux: `source venv/bin/activate`


### Step 4: Install Required Packages

With the virtual environment activated, run:

```shellscript
pip install pillow sv_ttk
```

### Step 5: Prepare the Logo

Ensure you have a file named `file-icon.png` in the same directory as the `FileSharingApp.py` script.

### Step 6: Run the Application

Execute the following command:

```shellscript
python FileSharingApp.py
```

## 5. Usage Instructions

### Main Interface

The app's main window is divided into four tabs: Files, Devices, Private, and History.

### Public/Private Mode Toggle

- Located at the top of the main window.
- Click to switch between Public and Private modes.
- Public mode allows sharing with all devices on the network.
- Private mode restricts sharing to devices in your private list.


### File Management (Files Tab)

1. **Sharing a File**:

1. Click "Share File".
2. Select the file from your system.
3. The file is copied to the shared directory.



2. **Creating a Folder**:

1. Click "Create Folder".
2. Enter a name for the new folder.



3. **Adding Files to a Folder**:

1. Select a folder in the file tree.
2. Click "Add to Folder".
3. Choose files to add.



4. **Toggling Folder Visibility**:

1. Select a folder.
2. Click "Toggle Visibility" to switch between public and private.





### Network Management

1. **Scanning for Devices** (Devices Tab):

1. Click "Scan Network".
2. Wait for the scan to complete.



2. **Managing Private Devices** (Private Tab):

1. Enter the IP address of a trusted device.
2. Click "Add Device".





### Viewing History (History Tab)

- Displays a log of all file sharing activities.
- Entries show the file name, action, and timestamp.


## 6. Security Considerations

- **Network Security**: MEMO operates on your local network. Ensure your Wi-Fi is password-protected.
- **Private Mode**: Use this for sensitive files to restrict access.
- **Regular Updates**: Keep the app and your operating system updated.
- **Firewall Settings**: You may need to allow MEMO through your firewall.
- **Trusted Devices**: Regularly review and update your list of private devices.


## 7. Troubleshooting

1. **App Doesn't Start**:

1. Ensure Python is correctly installed and in your PATH.
2. Verify all required packages are installed.



2. **Can't See Other Devices**:

1. Check if all devices are on the same network.
2. Temporarily disable firewalls for testing.



3. **Files Not Showing Up**:

1. Ensure the shared directory hasn't been moved or deleted.
2. Check folder permissions.



4. **Slow Performance**:

1. Reduce the number of files in the shared directory.
2. Ensure your system meets the minimum requirements.



5. **UI Issues**:

1. Update Pillow and sv_ttk to their latest versions.
2. Restart the application after updates.





## 8. Future Development

We're constantly working to improve MEMO. Planned features include:

- End-to-end encryption for file transfers
- Cloud integration for remote access
- Mobile companion app
- Customizable themes
- Automated sync folders


## 9. Support and Contact

For support, feature requests, or bug reports:

- Open an issue on our GitHub repository
- Email us at [support@mimoapp.com](mailto:support@mimoapp.com)
- Join our community forum at [https://community.mimoapp.com](https://community.mimoapp.com)


Thank you for choosing MEMO File Sharing App!

