
import urllib3
import random
import time
import sys
import os
import socket
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Terminal colors
class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# Common domain extensions
COMMON_TLDS = [
    '.com', '.net', '.org', '.info', '.biz',
    '.id', '.co.id', '.ac.id', '.sch.id', '.go.id', '.or.id', '.my.id',
    '.my', '.sg', '.in', '.ph', '.th',
    '.uk', '.de', '.fr', '.es', '.it',
    '.us', '.ca', '.au', '.jp', '.br', '.gov', '.gov.in', '.gov.my', 
    '.mil.id', '.mil', '.xyz', '.shop', '.co', '.il', '.co.il'
]

class WordPressScanner:
    def __init__(self):
        self.session = requests.Session()
        self.active_wp_sites = []
        self.threads = 30  # Reduced for stability
        self.timeout = 10  # Shorter timeout
        self.total_scanned = 0
        self.start_time = datetime.now()
        self.clear_terminal()

    def clear_terminal(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_logo(self):
        """Display program logo"""
        logo = f"""
{colors.CYAN}
  WordPress Site Scanner
{colors.YELLOW}  [ Active Sites Only ]
{colors.CYAN}
  Start Time: {colors.WHITE}{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
{colors.RESET}"""
        print(logo)

    def get_random_user_agent(self):
        """Get random modern user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(agents)

    def is_domain_active(self, domain):
        """Check if domain is active (DNS + HTTP)"""
        try:
            # Check DNS resolution first
            socket.gethostbyname(domain)
            
            # Then check HTTP connection
            self.session.headers.update({'User-Agent': self.get_random_user_agent()})
            response = self.session.head(
                f"http://{domain}", 
                timeout=self.timeout,
                allow_redirects=True,
                verify=False
            )
            return response.status_code < 400
        except:
            return False

    def is_wordpress_site(self, domain):
        """Check if active site uses WordPress"""
        endpoints = [
            '/wp-login.php',
            '/wp-admin/',
            '/readme.html',
            '/wp-includes/js/wp-embed.min.js',
            '/wp-json/'
        ]
        
        try:
            # First check homepage for WordPress signs
            response = self.session.get(
                f"http://{domain}",
                timeout=self.timeout,
                allow_redirects=True,
                verify=False
            )
            
            # Quick checks first
            if 'wp-content' in response.text or 'wp-includes' in response.text:
                return True
                
            # Check meta tag
            if '<meta name="generator" content="WordPress' in response.text:
                return True
                
            # Check endpoints
            for endpoint in endpoints:
                try:
                    ep_response = self.session.head(
                        f"http://{domain}{endpoint}",
                        timeout=self.timeout,
                        allow_redirects=False,
                        verify=False
                    )
                    if ep_response.status_code == 200:
                        return True
                except:
                    continue
                    
        except Exception as e:
            pass
            
        return False

    def scan_domain(self, domain, output_file):
        """Scan a single domain"""
        self.total_scanned += 1
        domain = domain.strip()
        
        if not domain:
            return
            
        try:
            if not self.is_domain_active(domain):
                print(f"{colors.RED}[OFFLINE] {domain.ljust(40)}{colors.RESET}")
                return
                
            if self.is_wordpress_site(domain):
                print(f"{colors.GREEN}[WP FOUND] {domain.ljust(40)}{colors.RESET}")
                self.active_wp_sites.append(domain)
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{domain}\n")
            else:
                print(f"{colors.YELLOW}[ACTIVE] {domain.ljust(40)}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}[ERROR] {domain} - {str(e)}{colors.RESET}")

    def run_scan(self):
        """Main scanning function"""
        output_file = "filelist.txt"
        
        # Check if file exists
        if not os.path.exists(output_file):
            print(f"{colors.RED}[!] File filelist.txt tidak ditemukan!{colors.RESET}")
            print(f"{colors.CYAN}[+] Buat file terlebih dahulu dengan command:{colors.RESET}")
            print(f"nano filelist.txt")
            return
            
        # Read domains from file
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                domains = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"{colors.RED}[!] Gagal membaca file: {str(e)}{colors.RESET}")
            return
            
        if not domains:
            print(f"{colors.RED}[!] File filelist.txt kosong!{colors.RESET}")
            return
            
        print(f"{colors.CYAN}\n[+] Memulai scan untuk {len(domains)} domain...{colors.RESET}")
        print(f"{colors.CYAN}[+] Hasil akan disimpan ke filelist.txt{colors.RESET}")
        
        # Clear existing results
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                pass
        except Exception as e:
            print(f"{colors.RED}[!] Gagal membersihkan file: {str(e)}{colors.RESET}")
            return
        
        # Scan with threading
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for domain in domains:
                executor.submit(self.scan_domain, domain, output_file)
        
        # Show summary
        elapsed = datetime.now() - self.start_time
        print(f"\n{colors.CYAN}=== HASIL SCAN ===")
        print(f"Total discan: {self.total_scanned}")
        print(f"Website WordPress aktif ditemukan: {len(self.active_wp_sites)}")
        print(f"Waktu eksekusi: {elapsed}{colors.RESET}")

    def run(self):
        """Main program flow"""
        self.show_logo()
        self.run_scan()

if __name__ == "__main__":
    try:
        # Check dependencies
        try:
            import requests
        except ImportError:
            print(f"{colors.RED}[!] Menginstall package yang diperlukan...{colors.RESET}")
            os.system("pip install requests urllib3")
            import requests
            
        scanner = WordPressScanner()
        scanner.run()
    except KeyboardInterrupt:
        print(f"\n{colors.RED}[!] Scan dihentikan!{colors.RESET}")
    except Exception as e:
        print(f"\n{colors.RED}[!] Error: {str(e)}{colors.RESET}")
