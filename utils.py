import os
import sys
import socket
import subprocess
import re
import nmap
import ipaddress

def get_wifi_ip():
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
        # Create a network address with subnet mask
        network = ipaddress.IPv4Network(f"{ip_address}/24", strict=False)
        
        nm = nmap.PortScanner()
        nm.scan(hosts=str(network), arguments='-sn')
        
        active_hosts = []
        for host in nm.all_hosts():
            if nm[host]['status']['state'] == 'up':
                active_hosts.append(host)
        
        return active_hosts
    except Exception as e:
        print(f"Error scanning network: {e}")
        return []

