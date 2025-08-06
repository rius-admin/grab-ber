
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
    '.com', '.net', '.org', '.info', '.biz', '.bet', '.cc', '.pro', '.live', '.top', '.game',
    '.id', '.co.id', '.ac.id', '.sch.id', '.go.id', '.vvip', '.win', '.max', '.gg',
    '.my', '.in', '.biz.id', '.gov', '.co.in', '.ac.in', '.edu', '.edu.my', '.edu.in', '.click',
    '.shop', '.online', '.vip',  '.co.il', '.il', '.my.id', '.fun', '.sch.id', '.go.id',
    '.jp', '.or.id', '.mil.id', '.co', '.gov.in', '.gov.my', '.site', '.id', '.website', '.com',
]

# Common subdomains
COMMON_SUBDOMAINS = [
    'blog', 'shop', 'store', 'news', 'dev', 'test', 'staging', 'akun',
    'ruang', 'kelas', 'wins', 'naga', 'pasti', 'auto', 'zonk', 'bumi', 'selalu',
    'no', 'mobile', 'api', 'secure', 'mail', 'webmail', 'admin', 'dashboard', 
    'app', 'apps', 'support', 'help', 'forum', 'community', 'status', 'cdn',
    'static', 'media', 'images', 'img', 'download', 'downloads', 'docs', 'wiki',
    'pages', 'abcdefghijklmnopqrstuvwxyz', 'auth', 'login', 'human', 'user', 'newsnew',
    'new', 'test', 'tes', 'coba', 'ujicoba', 'cobauji', 'file', 'files', '1admin', 'page',
    'i', 'host', 'you', 'beli', 'rumah', '88', '77', '777', '78', '86', 'slot', 'bet',
    'buaya', 'ayam', 'jambu', 'magga', 'naga', 'gacor', 'jp', 'aggur', 'bos', 'thailand',
    'cambodia', 'japan', 'indo', 'indonesia', 'malaysia', 'vvip', 'vip', 'pro', 'rusia',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6',
    '7', '8', '9', '10',
]

class WordPressScanner:
    def __init__(self):
        self.session = requests.Session()
        self.active_wp_sites = []
        self.threads = 14  # Reduced threads for controlled speed
        self.timeout = 14  # Increased timeout for reliability
        self.total_scanned = 0
        self.start_time = datetime.now()
        self.output_file = "list.txt"  # Changed to list.txt
        self.clear_terminal()
        self.initialize_file()
        self.delay = 0.5  # Delay between requests in seconds

    def clear_terminal(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def initialize_file(self):
        """Initialize the output file if it doesn't exist"""
        if not os.path.exists(self.output_file):
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("# Active WordPress Sites List\n")
                f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            print(f"{colors.YELLOW}[+] Created {self.output_file} automatically{colors.RESET}")

    def show_logo(self):
        """Display program logo"""
        logo = f"""
{colors.CYAN}
  WordPress Domain Grabber
{colors.YELLOW}  [ Active Sites Only ]
{colors.CYAN}
  Start Time: {colors.WHITE}{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
  Output File: {colors.WHITE}{self.output_file}
{colors.RESET}"""
        print(logo)

    def get_random_user_agent(self):
        """Get random modern user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(agents)

    def generate_domain(self, count):
        """Generate natural-looking domains and subdomains"""
        prefixes = ['web', 'site', 'blog', 'online', 'shop', 'buaya', 'news', 'tech', 'blog', 'shop', 'store', 'news', 'dev', 'test', 'staging', 'akun',
    'no', 'mobile', 'api', 'secure', 'mail', 'webmail', 'admin', 'dashboard', 
    'ruang', 'kelas', 'wins', 'naga', 'pasti', 'auto', 'zonk', 'bumi', 'selalu',
    'app', 'apps', 'support', 'help', 'forum', 'community', 'status', 'cdn',
    'static', 'media', 'images', 'img', 'download', 'downloads', 'docs', 'wiki',
    'pages', 'abcdefghijklmnopqrstuvwxyz', 'auth', 'login', 'human', 'user', 'newsnew',
    'new', 'test', 'tes', 'coba', 'ujicoba', 'cobauji', 'file', 'files', '1admin', 'page',
    'i', 'host', 'you', 'beli', 'rumah', '88', '77', '777', '78', '86', 'slot',
    'buaya', 'ayam', 'jambu', 'magga', 'naga', 'gacor', 'jp', 'aggur', 'bos', 'thailand',
    'cambodia', 'japan', 'indo', 'indonesia', 'malaysia', 'vvip', 'vip', 'pro', 'rusia',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6',
    '7', '8', '9', '10',]
        suffixes = ['hub', 'center', 'point', 'buaya', 'base', 'zone', 'corp', 'blog', 'shop', 'store', 'news', 'dev', 'test', 'staging', 'akun',
    'no', 'mobile', 'api', 'secure', 'mail', 'webmail', 'admin', 'dashboard', 
    'app', 'apps', 'support', 'help', 'forum', 'community', 'status', 'cdn',
    'ruang', 'kelas', 'wins', 'naga', 'pasti', 'auto', 'zonk', 'bumi', 'selalu',
    'static', 'media', 'images', 'img', 'download', 'downloads', 'docs', 'wiki',
    'pages', 'abcdefghijklmnopqrstuvwxyz', 'auth', 'login', 'human', 'user', 'newsnew',
    'new', 'test', 'tes', 'coba', 'ujicoba', 'cobauji', 'file', 'files', '1admin', 'page',
    'i', 'host', 'you', 'beli', 'rumah', '88', '77', '777', '78', '86', 'slot',
    'buaya', 'ayam', 'jambu', 'magga', 'naga', 'gacor', 'jp', 'aggur', 'bos', 'thailand',
    'cambodia', 'japan', 'indo', 'indonesia', 'malaysia', 'vvip', 'vip', 'pro', 'rusia',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6',
    '7', '8', '9', '10',]
        
        domains = []
        for _ in range(count):
            # Create natural sounding domains
            if random.random() < 0.7:
                name = random.choice(prefixes) + random.choice(suffixes)
            else:
                vowels = 'aeiou'
                consonants = 'bcdfghjklmnpqrstvwxyz'
                name = random.choice(consonants) + random.choice(vowels)
                name += ''.join(random.choice(consonants + vowels) for _ in range(random.randint(3, 5)))
            
            base_domain = name + random.choice(COMMON_TLDS)
            domains.append(base_domain)
            
            # Generate subdomains for some domains
            if random.random() < 0.3:  # 30% chance to generate subdomains
                subdomain = random.choice(COMMON_SUBDOMAINS) + '.' + base_domain
                domains.append(subdomain)
        
        return domains

    def is_domain_active(self, domain):
        """Check if domain is active with controlled speed"""
        time.sleep(self.delay)  # Add delay between checks
        try:
            socket.gethostbyname(domain)
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
        try:
            # First quick check
            response = self.session.get(
                f"http://{domain}",
                timeout=self.timeout,
                allow_redirects=True,
                verify=False
            )
            
            # Fast WordPress detection
            if 'wp-content' in response.text or 'wp-includes' in response.text:
                return True
            if '<meta name="generator" content="WordPress' in response.text:
                return True
            
            # Secondary checks if needed
            wp_endpoints = ['/wp-login.php', '/wp-admin/', '/readme.html']
            for endpoint in wp_endpoints:
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
        except:
            pass
        return False

    def scan_domain(self, domain):
        """Scan a single domain with proper output"""
        self.total_scanned += 1
        domain = domain.strip()
        
        if not domain:
            return
            
        try:
            if not self.is_domain_active(domain):
                print(f"{colors.RED}[OFFLINE] {domain.ljust(40)}{colors.RESET}")
                return
                
            if self.is_wordpress_site(domain):
                print(f"{colors.GREEN}[WORDPRESS] {domain.ljust(40)}{colors.RESET}")
                self.active_wp_sites.append(domain)
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{domain}\n")
            else:
                print(f"{colors.YELLOW}[SKIPPED] {domain.ljust(40)}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}[ERROR] {domain} - {str(e)}{colors.RESET}")

    def run_scan(self, count):
        """Main scanning function"""
        print(f"{colors.CYAN}\n[+] Generating {count} domains to scan...{colors.RESET}")
        domains = self.generate_domain(count)
        
        print(f"{colors.CYAN}[+] Scanning for active WordPress sites...{colors.RESET}")
        print(f"{colors.CYAN}[+] Controlled scanning speed (delay: {self.delay}s){colors.RESET}")
        
        # Clear previous results but keep header
        with open(self.output_file, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                if line.startswith('#'):
                    f.write(line)
            f.truncate()
        
        # Scan with controlled threading
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.scan_domain, domains)
        
        # Show summary
        elapsed = datetime.now() - self.start_time
        print(f"\n{colors.CYAN}=== Cyber Sederhana Team ===")
        print(f"Total domains _ {self.total_scanned}")
        print(f"Active WordPress sites found: {len(self.active_wp_sites)}")
        print(f"Scan durasi_ {elapsed}")
        print(f"{colors.GREEN}list sudah tersimpan di file list.txt {os.path.abspath(self.output_file)}{colors.RESET}")

    def run(self):
        """Main program flow"""
        self.show_logo()
        try:
            count = int(input(f"{colors.CYAN}[+] Enter number of domains to scan: {colors.WHITE}"))
            self.run_scan(count)
        except ValueError:
            print(f"{colors.RED}[!] Please enter a valid number{colors.RESET}")

if __name__ == "__main__":
    try:
        # Check dependencies
        try:
            import requests
        except ImportError:
            print(f"{colors.RED}[!] Installing required packages...{colors.RESET}")
            os.system("pip install requests urllib3")
            import requests
            
        scanner = WordPressScanner()
        scanner.run()
    except KeyboardInterrupt:
        print(f"\n{colors.RED}[!] Scan stopped by user!{colors.RESET}")
    except Exception as e:
        print(f"\n{colors.RED}[!] Error: {str(e)}{colors.RESET}")
