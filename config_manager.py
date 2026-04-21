import json
import os
from datetime import datetime

CONFIG_FILE = "config.json"
VERSION = "2.1.0"

DEFAULT_CONFIG = {
    "version": VERSION,
    "created_at": "",
    "last_modified": "",
    "settings": {
        "verify_webhooks": True,
        "fetch_on_startup": True,
        "fetch_limit": 50,
        "use_proxies": False,
        "proxy_file": "proxies.txt"
    }
}


def config_exists():
    """Check if config file exists"""
    return os.path.exists(CONFIG_FILE)


def load_config():
    """Load configuration from file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"[✗] Error loading config: {e}")
        return None


def save_config(config):
    """Save configuration to file"""
    try:
        config['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create backup
        try:
            with open(CONFIG_FILE + '.backup', 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
        
        return True
    except Exception as e:
        print(f"[✗] Error saving config: {e}")
        return False


def create_new_config(settings):
    """Create new configuration"""
    config = DEFAULT_CONFIG.copy()
    config['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    config['settings'] = settings
    return config


def get_setting(config, key, default=None):
    """Get setting value from config"""
    try:
        return config['settings'].get(key, default)
    except:
        return default


def display_config_summary(config):
    """Display configuration summary"""
    settings = config.get('settings', {})
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║  CURRENT CONFIGURATION                                     ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  • Webhook verification: {'✓ Enabled' if settings.get('verify_webhooks') else '✗ Disabled':<42}║")
    print(f"║  • Startup catch-up: {'✓ Enabled' if settings.get('fetch_on_startup') else '✗ Disabled':<46}║")
    
    if settings.get('fetch_on_startup'):
        fetch_limit = settings.get('fetch_limit', 50)
        print(f"║    └─ Fetch limit: {fetch_limit} messages{' ' * (32 - len(str(fetch_limit)))}║")
    
    print(f"║  • Proxy usage: {'✓ Enabled' if settings.get('use_proxies') else '✗ Disabled':<49}║")
    
    if settings.get('use_proxies'):
        proxy_file = settings.get('proxy_file', 'proxies.txt')
        display_file = proxy_file if len(proxy_file) <= 35 else proxy_file[:32] + '...'
        print(f"║    └─ Proxy file: {display_file:<39}║")
    
    print(f"║  • Bandwidth optimization: ✓ Always Enabled{' ' * 17}║")
    print(f"║  • Smart delays: ✓ Always Enabled{' ' * 25}║")
    print("╚════════════════════════════════════════════════════════════╝\n")