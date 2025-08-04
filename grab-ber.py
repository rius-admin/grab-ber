import requests
import random
import time
import os
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Warna terminal
class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# Daftar TLD dari berbagai negara
TLDS = [
    # Indonesia
    '.co.id', '.ac.id', '.sch.id', '.go.id', '.net.id', '.or.id', '.web.id',
    # Malaysia
    '.com.my', '.net.my', '.org.my', '.gov.my', '.edu.my',
    # Singapura
    '.com.sg', '.net.sg', '.org.sg', '.gov.sg', '.edu.sg',
    # Internasional
    '.com', '.net', '.org', '.info', '.biz', '.xyz',
    # Lainnya
    '.gov', '.edu', '.mil'
]

class WordPressScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        self.live_sites = []
        self.output_file = "live_wordpress.txt"
        self.timeout = 10
        self.threads = 30
        self.total_scanned = 0
        self.start_time = datetime.now()

    def generate_domain(self):
        """Generate domain acak dengan TLD berbagai negara"""
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        length = random.randint(6, 12)
        
        # Buat nama domain yang lebih natural
        name = ''
        for i in range(length):
            if i % 2 == 0:
                name += random.choice(consonants)
            else:
                name += random.choice(vowels)
        
        return name + random.choice(TLDS)

    def check_live(self, domain):
        """Cek apakah website masih live"""
        try:
            # Cek konektivitas DNS dan HTTP
            socket.gethostbyname(domain)
            response = self.session.head(f"http://{domain}", timeout=self.timeout)
            return response.status_code < 400
        except:
            return False

    def check_wordpress(self, domain):
        """Deteksi WordPress pada domain live"""
        try:
            # Cek endpoint WordPress umum
            endpoints = [
                '/wp-login.php',
                '/wp-admin/',
                '/readme.html',
                '/wp-includes/js/wp-embed.min.js',
                '/xmlrpc.php'
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(
                        f"http://{domain}{endpoint}", 
                        timeout=self.timeout,
                        allow_redirects=False
                    )
                    if response.status_code == 200:
                        if 'wp-login.php' in response.url or 'WordPress' in response.text:
                            return True
                except:
                    continue
            
            # Cek meta tag generator
            try:
                response = self.session.get(f"http://{domain}", timeout=self.timeout)
                if 'WordPress' in response.text or 'wp-content' in response.text:
                    return True
            except:
                pass
            
            return False
        except:
            return False

    def scan_domain(self, domain):
        """Proses scanning untuk satu domain"""
        self.total_scanned += 1
        try:
            if not self.check_live(domain):
                print(f"{colors.RED}[DEAD] {domain.ljust(30)}{colors.RESET}")
                return
            
            if self.check_wordpress(domain):
                print(f"{colors.GREEN}[WP LIVE] {domain.ljust(30)}{colors.RESET}")
                self.live_sites.append(domain)
                with open(self.output_file, 'a') as f:
                    f.write(domain + '\n')
            else:
                print(f"{colors.YELLOW}[LIVE] {domain.ljust(30)}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}[ERROR] {domain} - {str(e)}{colors.RESET}")

    def show_stats(self):
        """Tampilkan statistik scanning"""
        elapsed = datetime.now() - self.start_time
        print(f"\n{colors.CYAN}=== STATISTIK ==={colors.RESET}")
        print(f"Total discan: {self.total_scanned}")
        print(f"Website live WordPress ditemukan: {len(self.live_sites)}")
        print(f"Waktu eksekusi: {elapsed}")
        print(f"Hasil disimpan di: {self.output_file}")

    def run(self, count=100):
        """Jalankan scanner"""
        print(f"{colors.BLUE}Memulai scanning WordPress...{colors.RESET}")
        print(f"Mencari {count} website live WordPress\n")
        
        # Generate domain acak
        domains = [self.generate_domain() for _ in range(count)]
        
        # Jalankan dengan multithreading
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.scan_domain, domains)
        
        self.show_stats()

if __name__ == "__main__":
    try:
        scanner = WordPressScanner()
        count = int(input("Masukkan jumlah domain yang ingin discan: "))
        scanner.run(count)
    except KeyboardInterrupt:
        print(f"\n{colors.RED}Scanning dihentikan!{colors.RESET}")
    except Exception as e:
        print(f"\n{colors.RED}Error: {str(e)}{colors.RESET}")
