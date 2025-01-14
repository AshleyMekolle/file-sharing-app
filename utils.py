import os
import sys
import socket
import subprocess
import re

def get_wifi_ip():
    try:
        if os.name == 'nt':  # For Windows
            output = subprocess.check_output(['ipconfig'], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            wifi_section = None
            for i, line in enumerate(output.splitlines()):
                if "Wireless LAN adapter Wi-Fi" in line or "Wi-Fi" in line:
                    wifi_section = i
                    break
            if wifi_section is not None:
                for line in output.splitlines()[wifi_section:wifi_section+20]:  # Scan the next 20 lines for IPv4
                    if "IPv4 Address" in line or "IPv4" in line:
                        return line.split(':')[-1].strip()
        else:  # For Unix-based systems
            output = subprocess.check_output(['ip', 'addr'], stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
            pattern = r'inet\s+(\d+\.\d+\.\d+\.\d+).+wlan|inet\s+(\d+\.\d+\.\d+\.\d+).+en0'
            match = re.search(pattern, output)
            if match:
                return match.group(1) or match.group(2)
    except subprocess.SubprocessError as e:
        print(f"Subprocess error while getting Wi-Fi IP: {e}")
    except Exception as e:
        print(f"Error getting Wi-Fi IP: {e}")
    return None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
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
                except socket.timeout:
                    pass  # Ignore timeouts
                except socket.error as se:
                    print(f"Socket error while connecting to {host}: {se}")
                except Exception as e:
                    print(f"Unexpected error scanning host {host}: {e}")
        return active_hosts
    except Exception as e:
        print(f"Error scanning network: {e}")
        return []

# Example usage
if __name__ == "__main__":
    wifi_ip = get_wifi_ip() or "172.26.144.1"
    print(f"Wi-Fi IP detected: {wifi_ip}")
    active_hosts = scan_network(wifi_ip)
    if active_hosts:
        print("Active hosts on the network:")
        for ip, hostname in active_hosts:
            print(f"{ip} - {hostname}")
    else:
        print("No active hosts detected.")
