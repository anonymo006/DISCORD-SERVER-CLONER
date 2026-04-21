import os
from animations import print_box, print_success, print_error, print_warning, print_info
from validator import validate_proxy_file


def ask_yes_no(question, default=True):
    """Ask yes/no question"""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"[?] {question} ({default_str}): ").strip().lower()
        
        if response == '':
            return default
        elif response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print_error("Please enter 'y' or 'n'")


def ask_number(question, min_val, max_val, default):
    """Ask for a number within range"""
    while True:
        response = input(f"[?] {question} ({min_val}-{max_val}, default {default}): ").strip()
        
        if response == '':
            return default
        
        try:
            value = int(response)
            if min_val <= value <= max_val:
                return value
            else:
                print_error(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print_error("Please enter a valid number")


def ask_proxy_setup():
    """Ask about proxy configuration"""
    print_info("Proxy Configuration")
    print_info("If you don't use proxies, your real IP will be used")
    
    use_proxies = ask_yes_no("Do you want to use proxies?", default=False)
    
    if not use_proxies:
        return False, ""
    
    # Ask for proxy file path
    print()
    print_info("Enter proxy file path (or press Enter for default 'proxies.txt')")
    proxy_file = input("[?] Proxy file path: ").strip()
    
    if proxy_file == '' or proxy_file.lower() == 'n':
        proxy_file = "proxies.txt"
    
    # Validate proxy file
    is_valid, proxy_count, errors = validate_proxy_file(proxy_file)
    
    if not is_valid:
        print()
        print_error("Proxy file validation failed:")
        for error in errors:
            print(f"    • {error}")
        
        retry = ask_yes_no("Continue without proxies?", default=True)
        if retry:
            return False, ""
        else:
            print_error("Setup cancelled. Please fix proxy file and try again.")
            exit(1)
    else:
        print_success(f"Found {proxy_count} valid proxies in {proxy_file}")
        return True, proxy_file


def run_setup_wizard():
    """Run the interactive setup wizard"""
    print()
    print_box("FIRST TIME SETUP", [
        "Welcome! Let's configure your Discord Mirror Bot.",
        "",
        "This wizard will ask you 4 quick questions.",
        "You can change these settings anytime."
    ])
    
    settings = {}
    
    # Question 1: Verify webhooks
    print()
    print_info("Question 1/4: Webhook Verification")
    print_info("This checks if all webhooks are valid before starting")
    settings['verify_webhooks'] = ask_yes_no("Verify webhooks on startup?", default=True)
    
    # Question 2: Fetch on startup
    print()
    print_info("Question 2/4: Startup Catch-Up")
    print_info("This fetches missed messages sent while bot was offline")
    settings['fetch_on_startup'] = ask_yes_no("Fetch missed messages on startup?", default=True)
    
    # Question 3: Fetch limit (only if fetch_on_startup is True)
    if settings['fetch_on_startup']:
        print()
        print_info("Question 3/4: Message Fetch Limit")
        print_info("Higher = more catch-up, but uses more bandwidth")
        settings['fetch_limit'] = ask_number(
            "How many messages to fetch per channel?",
            min_val=10,
            max_val=100,
            default=50
        )
    else:
        settings['fetch_limit'] = 50  # Default even if not used
    
    # Question 4: Proxy setup
    print()
    print_info("Question 4/4: Proxy Configuration")
    settings['use_proxies'], settings['proxy_file'] = ask_proxy_setup()
    
    # Summary
    print()
    print_success("Configuration complete!")
    print()
    print_box("YOUR SETTINGS", [
        f"• Webhook verification: {'Enabled' if settings['verify_webhooks'] else 'Disabled'}",
        f"• Startup catch-up: {'Enabled' if settings['fetch_on_startup'] else 'Disabled'}",
        f"• Fetch limit: {settings['fetch_limit']} messages" if settings['fetch_on_startup'] else "",
        f"• Proxies: {'Enabled (' + settings['proxy_file'] + ')' if settings['use_proxies'] else 'Disabled'}",
        f"• Bandwidth optimization: Always Enabled",
        f"• Smart delays: Always Enabled"
    ])
    
    confirm = ask_yes_no("Save configuration and start bot?", default=True)
    
    if not confirm:
        print_error("Setup cancelled")
        exit(0)
    
    return settings


def show_existing_config_prompt(config):
    """Show existing config and ask if user wants to use it"""
    from config_manager import display_config_summary
    
    print()
    display_config_summary(config)
    
    use_existing = ask_yes_no("Use existing configuration?", default=True)
    
    if use_existing:
        return True
    else:
        # Ask what to do
        print()
        print_box("CONFIGURATION MENU", [
            "1. Run setup wizard again (create new config)",
            "2. Exit (no changes)"
        ])
        
        choice = input("[?] Choose option (1-2): ").strip()
        
        if choice == '1':
            return False  # Run wizard
        else:
            print_info("Exiting...")
            exit(0)