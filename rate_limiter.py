import time
import threading
from collections import deque

try:
    from logger import console_output, track_rate_limit
except ImportError:
    def console_output(msg, msg_type="INFO"):
        print(f"[{msg_type}] {msg}")
    def track_rate_limit(duration):
        pass


class RateLimiter:
    """
    Global rate limiter to prevent Discord API bans with clean logging
    """
    
    def __init__(self, max_requests=45, time_window=1.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = threading.Lock()
        self.global_cooldown_until = 0
        self.in_cooldown = False
        
        console_output(
            f"Rate limiter initialized: {max_requests} req/{time_window}s max",
            msg_type="INFO"
        )
        
    def wait_if_needed(self):
        """Call BEFORE every Discord API request"""
        with self.lock:
            now = time.time()
            
            if now < self.global_cooldown_until:
                if not self.in_cooldown:
                    wait_time = self.global_cooldown_until - now
                    console_output(
                        f"Rate limited - Pausing {wait_time:.0f}s",
                        msg_type="WARNING",
                        suppress_duplicates=True
                    )
                    self.in_cooldown = True
                    track_rate_limit(wait_time)
                
                time.sleep(self.global_cooldown_until - now)
                now = time.time()
                
                if self.in_cooldown:
                    console_output("Resumed after rate limit", msg_type="SUCCESS")
                    self.in_cooldown = False
            
            cutoff = now - self.time_window
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            
            if len(self.requests) >= self.max_requests:
                sleep_time = self.requests[0] + self.time_window - now + 0.1
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
                    cutoff = now - self.time_window
                    while self.requests and self.requests[0] < cutoff:
                        self.requests.popleft()
            
            self.requests.append(now)
    
    def handle_429(self, retry_after=None):
        """Call when receiving 429 rate limit error"""
        with self.lock:
            if retry_after:
                wait_time = retry_after + 1
            else:
                wait_time = 60
            
            self.global_cooldown_until = time.time() + wait_time
            
            if not self.in_cooldown:
                console_output(
                    f"Rate limited by Discord - Pausing {wait_time:.0f}s",
                    msg_type="WARNING",
                    suppress_duplicates=True
                )
                self.in_cooldown = True
                track_rate_limit(wait_time)


rate_limiter = RateLimiter(max_requests=45, time_window=1.0)