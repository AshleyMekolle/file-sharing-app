import os
import sys
import socket
import subprocess
import re

def get_wifi_ip():
    try:
        if os.name == 'nt':  # For Windows
            output = subprocess.check_output(['ipconfig']).decode('utf-8')
            for line in output.split('\n'):
                if 'IPv4 Address' in line and 'Wi-Fi' in output.split('\n')[output.split('\n').index(line) - 2]:
                    return line.split(':')[-1].strip()
        else:  # For Unix-based systems (Linux, macOS)
            output = subprocess.check_output(['ifconfig']).decode('utf-8')
            pattern = r'inet\s+(\d+\.\d+\.\d+\.\d+).*broadcast'
            for line in output.split('\n'):
                if 'wlan0' in line or 'en0' in line:  # Common WiFi interface names
                    match = re.search(pattern, output[output.index(line):])
                    if match:
                        return match.group(1)
    except Exception as e:
        print(f"Error getting Wi-Fi IP: {e}")
    
    return None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def scan_network(ip_address):
    try:
        subnet = '.'.join(ip_address.split('.')[:-1])
        active_hosts = []
        for i in range(1, 255):
            host = f"{subnet}.{i}"
            if host != ip_address:
                try:
                    with socket.create_connection((host, 5000), timeout=0.1) as s:
                        s.sendall(b"TEST_CONNECTION")
                        if s.recv(1024) == b"CONNECTION_OK":
                            try:
                                hostname = socket.gethostbyaddr(host)[0]
                            except socket.herror:
                                hostname = "Unknown"
                            active_hosts.append((host, hostname))
                except:
                    pass
        return active_hosts
    except Exception as e:
        print(f"Error scanning network: {e}")
        return []

