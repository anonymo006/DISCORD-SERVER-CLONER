import sys
import time
import threading

class Spinner:
    """Animated spinner for loading operations"""
    
    def __init__(self, message="Loading"):
        self.message = message
        self.spinning = False
        self.thread = None
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.frame_index = 0
    
    def _spin(self):
        """Internal spinning animation"""
        while self.spinning:
            frame = self.frames[self.frame_index % len(self.frames)]
            sys.stdout.write(f'\r{frame} {self.message}')
            sys.stdout.flush()
            self.frame_index += 1
            time.sleep(0.1)
    
    def start(self):
        """Start the spinner"""
        self.spinning = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self, final_message=None):
        """Stop the spinner with optional final message"""
        self.spinning = False
        if self.thread:
            self.thread.join()
        
        if final_message:
            sys.stdout.write(f'\r{final_message}\n')
        else:
            sys.stdout.write('\r' + ' ' * (len(self.message) + 5) + '\r')
        sys.stdout.flush()


class ProgressBar:
    """Visual progress bar for tasks"""
    
    def __init__(self, total, prefix='Progress', length=20):
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0
    
    def update(self, current):
        """Update progress bar"""
        self.current = current
        percent = int((current / self.total) * 100)
        filled = int((self.length * current) // self.total)
        bar = '█' * filled + '░' * (self.length - filled)
        
        sys.stdout.write(f'\r{self.prefix}: [{bar}] {percent}% ({current}/{self.total})')
        sys.stdout.flush()
    
    def finish(self, message="Complete"):
        """Finish progress bar"""
        self.update(self.total)
        sys.stdout.write(f' ✓\n')
        sys.stdout.flush()


class Countdown:
    """Countdown timer with spinner"""
    
    def __init__(self, seconds, message="Waiting"):
        self.seconds = seconds
        self.message = message
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def start(self):
        """Start countdown"""
        for remaining in range(self.seconds, 0, -1):
            frame = self.frames[remaining % len(self.frames)]
            sys.stdout.write(f'\r{frame} {self.message}: {remaining}s')
            sys.stdout.flush()
            time.sleep(1)
        
        sys.stdout.write(f'\r✅ {self.message} complete!     \n')
        sys.stdout.flush()


def print_banner(version="2.1.0", author=""):
    """Print professional banner"""
    banner = f"""
╔════════════════════════════════════════════════════════════╗
║  DISCORD MIRROR BOT v{version:<43}║
║  Bandwidth-Optimized Edition                               ║"""
    
    if author:
        banner += f"\n║  Created by: {author:<46}║"
    
    banner += """
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_box(title, content, width=60):
    """Print content in a box"""
    print(f"\n╔{'═' * (width - 2)}╗")
    print(f"║ {title:<{width - 4}} ║")
    print(f"╠{'═' * (width - 2)}╣")
    
    for line in content:
        print(f"║ {line:<{width - 4}} ║")
    
    print(f"╚{'═' * (width - 2)}╝\n")


def print_success(message):
    """Print success message"""
    print(f"[✓] {message}")


def print_error(message):
    """Print error message"""
    print(f"[✗] {message}")


def print_warning(message):
    """Print warning message"""
    print(f"[!] {message}")


def print_info(message):
    """Print info message"""
    print(f"[i] {message}")


def clear_line():
    """Clear current line"""
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()