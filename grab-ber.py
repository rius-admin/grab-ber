import urllib3
import re
import time
import random
import sys
import os
import socket
import requests
from concurrent.futures import ThreadPoolExecutor
import platform
import subprocess
import webbrowser
from datetime import datetime

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Warna terminal
color = ["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m", "\033[36m", "\033[37m", "\033[39m"]

class WordPressGrabber:
    def __init__(self):
        self.s = requests.Session()
        self.wordpress_sites = []
        self.output_file = "list.txt"
        self.threads = 50
        self.request_timeout = 30
        self.total_requested = 0
        self.telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"  # Ganti dengan token bot Anda
        self.telegram_chat_id = "YOUR_CHAT_ID"  # Ganti dengan chat ID Anda
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.start_time = datetime.now()
        self.clear_terminal()

    def clear_terminal(self):
        """Membersihkan terminal dan membuka browser"""
        os.system('cls' if os.name == 'nt' else 'clear')
        webbrowser.open("https://www.google.com")  # Ganti dengan URL yang Anda inginkan

    def send_telegram_message(self, message):
        """Mengirim pesan ke Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        params = {
            'chat_id': self.telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        try:
            response = requests.post(url, params=params)
            return response.json()
        except Exception as e:
            print(f"{color[0]}Error sending Telegram message: {e}{color[7]}")
            return None

    def logo(self):
        """Menampilkan logo"""
        Logo = '''
  dP    dP  88888888b              dP     dP   .d888888   a88888b. dP     dP 
  Y8.  .8P  88                     88     88  d8'    88  d8'   `88 88   .d8' 
   Y8aa8P  a88aaaa                 88aaaaa88a 88aaaaa88a 88        88aaa8P'  
     88     88                     88     88  88     88  88        88   `8b. 
     88     88                     88     88  88     88  Y8.   .88 88     88 
     dP     88888888P              dP     dP  88     88   Y88888P' dP     dP 
                      oooooooooooo                                           
                                                                            
     {y}WordPress Domain Grabber {w}[{g}v2.2{w}]{w}
     {m}Telegram Notification Enabled{w}
     {c}Start Time: {w}{time}{w}
'''.format(
    g=color[1], w=color[7], m=color[4], y=color[2], 
    r=color[0], c=color[3], time=self.start_time.strftime("%Y-%m-%d %H:%M:%S")
)
        for Line in Logo.split('\n'):
            print(random.choice(color) + Line)
            time.sleep(0.01)

    def get_user_input(self):
        """Mendapatkan input dari pengguna"""
        self.logo()
        print(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Mode:{color[6]}")
        print(f" {color[6]}1. Gunakan file list (misal: list.txt)")
        print(f" {color[6]}2. Generate domain baru (random)")
        
        choice = input(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Pilih mode (1/2): {color[6]}")
        
        if choice == "1":
            file_name = input(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Nama file list: {color[6]}")
            if not os.path.exists(file_name):
                print(f" {color[6]}[{color[0]}x{color[6]}] {color[0]}File tidak ditemukan!")
                self.send_telegram_message("🚫 <b>Error:</b> File tidak ditemukan!")
                exit()
            domains = open(file_name, "r").read().splitlines()
            self.total_requested = len(domains)
            return domains
        elif choice == "2":
            self.total_requested = int(input(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Jumlah domain yang diinginkan: {color[6]}"))
            return self.generate_random_domains()
        else:
            print(f" {color[6]}[{color[0]}x{color[6]}] {color[0]}Pilihan tidak valid!")
            self.send_telegram_message("🚫 <b>Error:</b> Pilihan tidak valid!")
            exit()

    def generate_random_domains(self):
        """Generate domain acak"""
        domains = []
        tlds = ['.com', '.net', '.org', '.info', '.biz']
        for _ in range(self.total_requested):
            name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(5, 12)))
            tld = random.choice(tlds)
            domains.append(f"{name}{tld}")
        return domains

    def check_wordpress(self, domain):
        """Memeriksa apakah domain menggunakan WordPress"""
        try:
            headers = {'User-Agent': random.choice(self.user_agents)}
            url = f"http://{domain}"
            
            # Cek WordPress login page
            response = self.s.get(url + "/wp-login.php", headers=headers, 
                                timeout=self.request_timeout, verify=False)
            if "wp-login.php" in response.url and response.status_code == 200:
                return True
            
            # Cek WordPress readme.html
            response = self.s.get(url + "/readme.html", headers=headers, 
                                 timeout=self.request_timeout, verify=False)
            if "WordPress" in response.text and response.status_code == 200:
                return True
                
            # Cek WordPress meta generator tag
            response = self.s.get(url, headers=headers, 
                                timeout=self.request_timeout, verify=False)
            if '<meta name="generator" content="WordPress' in response.text:
                return True
                
        except Exception as e:
            pass
            
        return False

    def process_domain(self, domain):
        """Memproses setiap domain"""
        try:
            domain = domain.strip()
            if not domain:
                return
                
            # Cek WordPress
            if self.check_wordpress(domain):
                print(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}WordPress Found: {color[7]}{domain}")
                if domain not in self.wordpress_sites:
                    self.wordpress_sites.append(domain)
                    with open(self.output_file, "a") as f:
                        f.write(domain + "\n")
                    # Kirim notifikasi ke Telegram untuk setiap 10 domain ditemukan
                    if len(self.wordpress_sites) % 10 == 0:
                        msg = f"✅ <b>Progress:</b> {len(self.wordpress_sites)} WordPress sites found!\n⏳ Running time: {datetime.now() - self.start_time}"
                        self.send_telegram_message(msg)
            else:
                print(f" {color[6]}[{color[0]}-{color[6]}] {color[0]}Not WordPress: {color[7]}{domain}")
                
        except Exception as e:
            print(f" {color[6]}[{color[0]}!{color[6]}] {color[0]}Error processing: {color[7]}{domain}")

    def run(self):
        """Menjalankan program utama"""
        domains = self.get_user_input()
        
        # Kirim notifikasi mulai ke Telegram
        start_msg = f"🚀 <b>Memulai WordPress Domain Grabber</b>\n\n" \
                   f"📋 <b>Total Domain:</b> {len(domains)}\n" \
                   f"⏰ <b>Waktu Mulai:</b> {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_telegram_message(start_msg)
        
        print(f"\n {color[6]}[{color[1]}+{color[6]}] {color[2]}Memulai proses...")
        print(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Output akan disimpan di: {color[7]}{self.output_file}")
        
        # Jalankan dengan multithreading
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.process_domain, domains)
        
        # Hitung waktu eksekusi
        end_time = datetime.now()
        elapsed_time = end_time - self.start_time
        
        # Hasil akhir
        print(f"\n {color[6]}[{color[1]}+{color[6]}] {color[2]}Selesai!")
        print(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Total WordPress sites ditemukan: {color[7]}{len(self.wordpress_sites)}")
        print(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}File output: {color[7]}{os.path.abspath(self.output_file)}")
        print(f" {color[6]}[{color[1]}+{color[6]}] {color[2]}Waktu eksekusi: {color[7]}{elapsed_time}\n")
        
        # Kirim notifikasi selesai ke Telegram
        end_msg = f"🏁 <b>WordPress Domain Grabber Selesai</b>\n\n" \
                 f"✅ <b>Total Ditemukan:</b> {len(self.wordpress_sites)}\n" \
                 f"⏱ <b>Waktu Eksekusi:</b> {elapsed_time}\n" \
                 f"📁 <b>File Output:</b> <code>{os.path.abspath(self.output_file)}</code>"
        self.send_telegram_message(end_msg)

if __name__ == "__main__":
    try:
        # Periksa dependensi
        try:
            import requests
        except ImportError:
            print(f"{color[0]}Module 'requests' tidak ditemukan. Menginstall...{color[7]}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
            
        grabber = WordPressGrabber()
        grabber.run()
    except KeyboardInterrupt:
        print(f"\n {color[6]}[{color[0]}-{color[6]}] {color[3]}Interrupted by user. Exiting...")
        grabber.send_telegram_message("🛑 <b>Proses dihentikan oleh pengguna!</b>")
        exit()
    except Exception as e:
        print(f"\n {color[6]}[{color[0]}!{color[6]}] {color[0]}Error: {e}{color[7]}")
        grabber.send_telegram_message(f"⚠️ <b>Error:</b> <code>{str(e)}</code>")
        exit()
