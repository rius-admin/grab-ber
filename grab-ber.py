
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

# International domain extensions (updated for 2025)
INTERNATIONAL_TLDS = [
    # Global
    '.com', '.net', '.org', '.info', '.biz', '.xyz',
    # Asia
    '.id', '.co.id', '.ac.id', '.sch.id', '.go.id', '.my', '.com.my', '.sg', 
    '.com.sg', '.in', '.co.in', '.ph', '.com.ph', '.th', '.co.th',
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

class ActiveWordPressScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.get_random_user_agent()})
        self.active_wp_sites = []
        self.output_file = "active_wordpress_2025.txt"
        self.timeout = 15  # Shorter timeout for faster scanning
        self.threads = 50
        self.total_scanned = 0
        self.start_time = datetime.now()
        self.clear_terminal()

    def clear_terminal(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

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
        
        # Create more natural sounding domains
        name = ''
        for i in range(length):
            if i % 2 == 0:
                name += random.choice(consonants)
            else:
                name += random.choice(vowels)
        
        # Occasionally add numbers (like web2.0 style)
        if random.random() > 0.7:
            name += str(random.randint(0, 9))
        
        return name + random.choice(INTERNATIONAL_TLDS)

    def is_domain_active(self, domain):
        """Check if domain is active (DNS + HTTP)"""
        try:
            # First check DNS resolution
            socket.gethostbyname(domain)
            
            # Then check HTTP connection
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
        
        # First check homepage for WordPress signs
        try:
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
        except:
            pass
        
        # Check specific WordPress endpoints
        for endpoint in endpoints:
            try:
                response = self.session.head(
                    f"http://{domain}{endpoint}",
                    timeout=self.timeout,
                    allow_redirects=False
                )
                if response.status_code == 200:
                    return True
            except:
                continue
                
        return False

    def scan_domain(self, domain):
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
                print(f"{colors.GREEN}[ACTIVE WP] {domain.ljust(40)}{colors.RESET}")
                self.active_wp_sites.append(domain)
                with open(self.output_file, 'a') as f:
                    f.write(f"{domain}\n")
            else:
                print(f"{colors.YELLOW}[ACTIVE] {domain.ljust(40)}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}[ERROR] {domain} - {str(e)}{colors.RESET}")

    def show_stats(self):
        """Show scanning statistics"""
        elapsed = datetime.now() - self.start_time
        print(f"\n{colors.CYAN}=== SCAN RESULTS ==={colors.RESET}")
        print(f"Domains scanned: {self.total_scanned}")
        print(f"Active WordPress sites found: {len(self.active_wp_sites)}")
        print(f"Scan duration: {elapsed}")
        print(f"Results saved to: {os.path.abspath(self.output_file)}")

    def run(self, count=100):
        """Run the scanner"""
        print(f"{colors.BLUE}Starting Active WordPress Scanner (2025){colors.RESET}")
        print(f"Scanning for {count} live WordPress sites\n")
        
        # Generate random domains
        domains = [self.generate_domain() for _ in range(count)]
        
        # Run with threading
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.scan_domain, domains)
        
        self.show_stats()

if __name__ == "__main__":
    try:
        scanner = ActiveWordPressScanner()
        count = int(input("Enter number of domains to scan: "))
        scanner.run(count)
    except KeyboardInterrupt:
        print(f"\n{colors.RED}Scanning stopped by user!{colors.RESET}")
    except Exception as e:
        print(f"\n{colors.RED}Error: {str(e)}{colors.RESET}")
