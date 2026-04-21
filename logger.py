import logging
import uuid
import sys
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)


class MessageStats:
    """Track statistics for hourly reports"""
    def __init__(self):
        self.messages_mirrored = 0
        self.messages_failed = 0
        self.files_uploaded = 0
        self.total_file_size = 0
        self.rate_limit_incidents = 0
        self.rate_limit_total_time = 0
        self.start_time = datetime.now()
        self.last_hour_reset = datetime.now()
    
    def reset_hourly(self):
        """Reset hourly counters"""
        self.messages_mirrored = 0
        self.messages_failed = 0
        self.files_uploaded = 0
        self.total_file_size = 0
        self.rate_limit_incidents = 0
        self.rate_limit_total_time = 0
        self.last_hour_reset = datetime.now()
    
    def get_uptime(self):
        """Get uptime in human readable format"""
        delta = datetime.now() - self.start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        days = delta.days
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m"


stats = MessageStats()


class ErrorSuppressor:
    """Suppress duplicate consecutive errors"""
    def __init__(self):
        self.last_error = None
        self.error_count = 0
    
    def should_log(self, error_msg):
        """Returns True if should log, False if duplicate"""
        if error_msg == self.last_error:
            self.error_count += 1
            return False
        else:
            if self.error_count > 0:
                self.last_error = None
                self.error_count = 0
            self.last_error = error_msg
            self.error_count = 1
            return True
    
    def get_suppressed_count(self):
        """Get count of suppressed messages"""
        if self.error_count > 1:
            count = self.error_count
            self.error_count = 0
            self.last_error = None
            return count
        return 0


error_suppressor = ErrorSuppressor()


def get_color_for_type(msg_type):
    """Get color based on message type"""
    colors = {
        "SUCCESS": Fore.GREEN,
        "INFO": Fore.CYAN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.MAGENTA
    }
    return colors.get(msg_type, Fore.WHITE)


def get_emoji_for_type(msg_type):
    """Get emoji based on message type"""
    emojis = {
        "SUCCESS": "✅",
        "INFO": "ℹ️ ",
        "WARNING": "⚠️ ",
        "ERROR": "❌",
        "CRITICAL": "🔴"
    }
    return emojis.get(msg_type, "  ")


def console_output(text, msg_type="INFO", suppress_duplicates=False):
    """
    Enhanced console output with colors and statistics tracking
    
    Args:
        text: Message to display
        msg_type: Type of message (SUCCESS, INFO, WARNING, ERROR)
        suppress_duplicates: Whether to suppress duplicate consecutive messages
    """
    global stats, error_suppressor
    
    if suppress_duplicates and msg_type in ["WARNING", "ERROR"]:
        if not error_suppressor.should_log(text):
            return
    
    suppressed = error_suppressor.get_suppressed_count()
    if suppressed > 1:
        suffix_msg = f"(repeated {suppressed-1} more times)"
        color = get_color_for_type(msg_type)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {color}{suffix_msg}{Style.RESET_ALL}")
    
    color = get_color_for_type(msg_type)
    emoji = get_emoji_for_type(msg_type)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"[{timestamp}] {color}{emoji} {text}{Style.RESET_ALL}"
    print(message)
    
    check_hourly_report()


def track_message_mirrored(file_count=0, total_size=0):
    """Track successful message mirror"""
    global stats
    stats.messages_mirrored += 1
    stats.files_uploaded += file_count
    stats.total_file_size += total_size


def track_message_failed():
    """Track failed message"""
    global stats
    stats.messages_failed += 1


def track_rate_limit(duration):
    """Track rate limit incident"""
    global stats
    stats.rate_limit_incidents += 1
    stats.rate_limit_total_time += duration


def format_file_size(bytes_size):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def print_hourly_report():
    """Print hourly statistics report"""
    global stats
    
    print("\n" + "="*70)
    print(f"{Fore.CYAN}📊 HOURLY STATISTICS REPORT{Style.RESET_ALL}")
    print("="*70)
    print(f"{Fore.GREEN}Messages Mirrored:{Style.RESET_ALL} {stats.messages_mirrored}")
    
    if stats.messages_failed > 0:
        print(f"{Fore.RED}Messages Failed:{Style.RESET_ALL} {stats.messages_failed}")
    
    if stats.files_uploaded > 0:
        size_str = format_file_size(stats.total_file_size)
        print(f"{Fore.CYAN}Files Uploaded:{Style.RESET_ALL} {stats.files_uploaded} ({size_str} total)")
    
    if stats.rate_limit_incidents > 0:
        avg_time = stats.rate_limit_total_time / stats.rate_limit_incidents
        print(f"{Fore.YELLOW}Rate Limit Incidents:{Style.RESET_ALL} {stats.rate_limit_incidents} (avg {avg_time:.0f}s pause)")
    
    print(f"{Fore.MAGENTA}Uptime:{Style.RESET_ALL} {stats.get_uptime()}")
    print("="*70 + "\n")
    
    stats.reset_hourly()


def check_hourly_report():
    """Check if an hour has passed and print report"""
    global stats
    now = datetime.now()
    time_diff = (now - stats.last_hour_reset).total_seconds()
    
    if time_diff >= 3600:
        print_hourly_report()


def console_output_uuid(text, msg_type="INFO"):
    """Legacy function for backward compatibility - redirects to console_output"""
    console_output(text, msg_type)