
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

# International domain extensions (updated for current year)
INTERNATIONAL_TLDS = [
    # Global
    '.com', '.net', '.org', '.info', '.biz', '.xyz',
    # Asia
    '.id', '.co.id', '.ac.id', '.sch.id', '.go.id', '.my', '.gov.may" '.com.my', '.sg', 
    '.com.sg', '.in', '.co.in', '.ph', '.com.ph', '.th', '.co.th', '.in', '.gov.in',
    # Europe
    '.uk', '.co.uk', '.de', '.fr', '.es', '.it', '.nl', '.eu',
    # Americas
    '.us', '.ca', '.mx', '.br', '.com.br', '.ar',
    # Middle East
    '.ae', '.sa', '.qa', '.eg',
    # Africa
    '.za', '.co.za', '.ng', '.ke',
    # Government/Education
    '.gov', '.edu', '.mil', '.ac', '.sch'
]

class WordPressScanner:
    def __init__(self):
        self.session = requests.Session()
        self.active_wp_sites = []
        self.threads = 50
        self.timeout = 15
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
  dP    dP  88888888b              dP     dP   .d888888   a88888b. dP     dP 
  Y8.  .8P  88                     88     88  d8'    88  d8'   `88 88   .d8' 
   Y8aa8P  a88aaaa                 88aaaaa88a 88aaaaa88a 88        88aaa8P'  
     88     88                     88     88  88     88  88        88   `8b. 
     88     88                     88     88  88     88  Y8.   .88 88     88 
     dP     88888888P              dP     dP  88     88   Y88888P' dP     dP 
                      oooooooooooo                                           
                                                                            
{colors.YELLOW}     WordPress Domain Grabber {colors.WHITE}[{colors.GREEN}v4.0{colors.WHITE}]
{colors.CYAN}     Start Time: {colors.WHITE}{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
{colors.RESET}"""
        print(logo)

    def get_random_user_agent(self):
        """Get random modern user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
        ]
        return random.choice(agents)

    def generate_domain(self):
        """Generate random domain with international TLDs"""
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        length = random.randint(6, 14)
        
        # Create natural sounding domains
        name = ''
        for i in range(length):
            if i % 2 == 0:
                name += random.choice(consonants)
            else:
                name += random.choice(vowels)
        
        # Occasionally add numbers
        if random.random() > 0.7:
            name += str(random.randint(0, 9))
        
        return name + random.choice(INTERNATIONAL_TLDS)

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
                allow_redirects=True
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
            '/wp-json/',
            '/xmlrpc.php'
        ]
        
        try:
            # First check homepage for WordPress signs
            response = self.session.get(
                f"http://{domain}",
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Check for WordPress meta tag
            if '<meta name="generator" content="WordPress' in response.text:
                return True
                
            # Check for common WordPress paths
            if 'wp-content' in response.text or 'wp-includes' in response.text:
                return True
                
            # Check specific WordPress endpoints
            for endpoint in endpoints:
                try:
                    ep_response = self.session.head(
                        f"http://{domain}{endpoint}",
                        timeout=self.timeout,
                        allow_redirects=False
                    )
                    if ep_response.status_code == 200:
                        return True
                except:
                    continue
                    
        except:
            pass
            
        return False

    def scan_domain(self, domain, output_file):
        """Scan a single domain"""
        self.total_scanned += 1
        domain = domain.strip()
        
        if not domain:
            return
            
        try:
            # Skip if domain is not active
            if not self.is_domain_active(domain):
                print(f"{colors.RED}[OFFLINE] {domain.ljust(40)}{colors.RESET}")
                return
                
            # Check for WordPress
            if self.is_wordpress_site(domain):
                print(f"{colors.GREEN}[ACTIVE WP] {domain.ljust(40)}{colors.RESET}")
                self.active_wp_sites.append(domain)
                with open(output_file, 'a') as f:
                    f.write(f"{domain}\n")
            else:
                print(f"{colors.YELLOW}[ACTIVE] {domain.ljust(40)}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}[ERROR] {domain} - {str(e)}{colors.RESET}")

    def run_file_mode(self):
        """Mode 1: Scan domains from file"""
        file_name = input(f"{colors.CYAN}\n[+] Enter file path (e.g., domains.txt): {colors.WHITE}")
        
        if not os.path.exists(file_name):
            print(f"{colors.RED}[!] File not found!{colors.RESET}")
            return
            
        output_file = file_name  # Save results back to original file
        domains = open(file_name, "r").read().splitlines()
        
        print(f"{colors.BLUE}\n[+] Scanning {len(domains)} domains from file...{colors.RESET}")
        print(f"{colors.BLUE}[+] Results will be saved to: {output_file}{colors.RESET}")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(lambda d: self.scan_domain(d, output_file), domains)
        
        self.show_stats(output_file)

    def run_random_mode(self):
        """Mode 2: Generate and scan random domains"""
        count = int(input(f"{colors.CYAN}\n[+] Enter number of domains to generate: {colors.WHITE}"))
        output_file = "wordpress_results.txt"
        
        print(f"{colors.BLUE}\n[+] Generating and scanning {count} random domains...{colors.RESET}")
        print(f"{colors.BLUE}[+] Results will be saved to: {output_file}{colors.RESET}")
        
        # Generate and scan domains
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for _ in range(count):
                domain = self.generate_domain()
                executor.submit(self.scan_domain, domain, output_file)
        
        self.show_stats(output_file)

    def show_stats(self, output_file):
        """Show scanning statistics"""
        elapsed = datetime.now() - self.start_time
        print(f"\n{colors.CYAN}=== SCAN RESULTS ===")
        print(f"Domains scanned: {self.total_scanned}")
        print(f"Active WordPress sites found: {len(self.active_wp_sites)}")
        print(f"Scan duration: {elapsed}")
        print(f"Results saved to: {os.path.abspath(output_file)}{colors.RESET}")

    def run(self):
        """Main program flow"""
        self.show_logo()
        
        print(f"{colors.CYAN}\n[+] Select operation mode:{colors.RESET}")
        print(f"{colors.WHITE}1. Scan domains from file")
        print(f"2. Generate and scan random domains{colors.RESET}")
        
        choice = input(f"{colors.CYAN}\n[+] Enter choice (1/2): {colors.WHITE}")
        
        if choice == "1":
            self.run_file_mode()
        elif choice == "2":
            self.run_random_mode()
        else:
            print(f"{colors.RED}[!] Invalid choice!{colors.RESET}")

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
