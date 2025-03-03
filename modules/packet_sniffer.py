import os
import asyncio
from scapy.all import sniff, wrpcap, conf
import time

class PacketSniffer:
    def __init__(self, browsers_instance):
        self.browsers = browsers_instance
        self.temp_path = self.browsers.temp_path
        self.packet_file = os.path.join(self.temp_path, "network_packets.pcap")  
        self.txt_file = os.path.join(self.temp_path, "network_packets.txt")  
        self.running = True
        self.sniff_duration = 20  
        self.packets = []

    def sniff_packets(self):
        """Sniff packets using scapy with Npcap."""
        print("Starting packet sniff with Npcap (admin/root required)...")
        try:
            # Sniff with Npcap (Windows) or libpcap (Linux/macOS)
            packets = sniff(timeout=self.sniff_duration)
            self.packets = packets  

            if packets:
            
                wrpcap(self.packet_file, packets)
                print(f"Saved {len(packets)} packets to {self.packet_file}")
                with open(self.txt_file, "w", encoding="utf-8") as f:
                    for pkt in packets:
                        if pkt.haslayer("IP"):
                            src_ip = pkt["IP"].src
                            dst_ip = pkt["IP"].dst
                            proto = pkt["IP"].proto
                            packet_info = (
                                f"Time: {time.ctime(pkt.time)} | Src: {src_ip} | Dst: {dst_ip} | "
                                f"Proto: {proto} | Payload: {pkt.summary()[:100]}..."
                            )
                            f.write(f"{packet_info}\n")
                        else:
                            f.write(f"Time: {time.ctime(pkt.time)} | Non-IP packet: {pkt.summary()[:100]}...\n")
                print(f"Wrote summary of {len(packets)} packets to {self.txt_file}")
            else:
                with open(self.txt_file, "w", encoding="utf-8") as f:
                    f.write("No packets captured. Ensure Npcap is installed and script runs as admin/root.")
                print("No packets captured")

        except Exception as e:
            print(f"Packet sniffing failed: {e}")
            with open(self.txt_file, "w", encoding="utf-8") as f:
                f.write(f"Sniffing failed: {str(e)}. Install Npcap (Windows) or libpcap (Linux/macOS) and run as admin/root.")
            print(f"Error logged to {self.txt_file}")

    async def extract_data(self):
        sniff_task = asyncio.to_thread(self.sniff_packets)
        await asyncio.gather(sniff_task)