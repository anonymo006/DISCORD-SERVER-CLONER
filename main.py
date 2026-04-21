import time
import threading
import traceback
import random
import datetime
import sys

# Import our modules
from logger import console_output
from utils import discord_utils_optimized as discord_utils
from utils import file_utils, verification_utils
from rate_limiter import rate_limiter

# Import new professional modules
from animations import (
    print_banner, print_box, print_success, print_error, 
    print_warning, print_info, Spinner, ProgressBar
)
from config_manager import (
    config_exists, load_config, save_config, create_new_config,
    get_setting, display_config_summary
)
from setup_wizard import run_setup_wizard, show_existing_config_prompt
from validator import validate_tasks_csv, verify_webhooks

VERSION = "2.1.0"
AUTHOR = "Your Name"  # Change this!

# Global state
active_thread_ids = set()
thread_map = {}
thread_map_lock = threading.Lock()
last_message_cache = {}
cache_lock = threading.Lock()
channel_activity = {}
activity_lock = threading.Lock()


def hide_discord_username(username: str, incognito_names: dict) -> str:
    if username not in incognito_names:
        incognito_names[username] = f'user{len(incognito_names) + 1}'
        file_utils.save_custom_names(custom_names=incognito_names)
    return incognito_names[username]


def extract_embedded_data(embedded_list: list):
    for embed in embedded_list:
        embed_type    = embed.get('type')
        title         = embed.get('title')
        url           = embed.get('url')
        description   = embed.get('description')
        fields        = embed.get('fields')
        thumbnail_url = embed.get('thumbnail', {}).get('url')
        return embed_type, title, url, description, fields, thumbnail_url
    return None, None, None, None, None, None


def process_attachments(message: dict) -> list:
    attachments = []
    for att in message.get('attachments', []):
        attachments.append({
            "url":      att.get('url'),
            "filename": att.get('filename'),
            "size":     att.get('size'),
        })
    return attachments


def update_channel_activity(channel_id, has_new_message):
    """Track channel activity for smart delays"""
    with activity_lock:
        if channel_id not in channel_activity:
            channel_activity[channel_id] = {
                'last_message_time': time.time() if has_new_message else 0,
                'message_count': 1 if has_new_message else 0
            }
        elif has_new_message:
            channel_activity[channel_id]['last_message_time'] = time.time()
            channel_activity[channel_id]['message_count'] += 1


def get_smart_delay(channel_id, base_delay):
    """Calculate smart delay based on channel activity"""
    with activity_lock:
        activity = channel_activity.get(channel_id)
        
        if not activity:
            return base_delay
        
        time_since_last = time.time() - activity['last_message_time']
        
        if time_since_last < 300:
            return base_delay
        elif time_since_last < 3600:
            return base_delay * 2
        else:
            return base_delay * 3


def monitor_discord_api(
    delay: float,
    account_token_id: str,
    source_channel_id: str,
    webhook_url: str,
    incognito_mode: bool = False,
    bot_token: str = None,
    thread_name: str = None
):
    global active_thread_ids, thread_map, thread_map_lock, last_message_cache, cache_lock

    time.sleep(random.uniform(0, delay * 2))

    dest_channel_id = discord_utils.get_channel_from_webhook(webhook_url)
    no_message_cycle = 0
    consecutive_errors = 0
    current_delay = delay

    try:
        while True:
            try:
                actual_delay = get_smart_delay(source_channel_id, current_delay)
                
                if thread_name:
                    rate_limiter.wait_if_needed()
                    meta = discord_utils.fetch_channel_metadata(account_token_id, source_channel_id)
                    
                    if meta.get('archived', False):
                        with thread_map_lock:
                            clone_thread_id = thread_map.get(source_channel_id)
                        
                        if clone_thread_id and bot_token:
                            discord_utils.sync_thread_archive_status(
                                bot_token=bot_token,
                                clone_thread_id=clone_thread_id,
                                is_archived=True
                            )
                        
                        console_output(f"Thread '{thread_name}' archived - Stopping monitor", msg_type="INFO")
                        return
                
                rate_limiter.wait_if_needed()
                current_last_id = discord_utils.get_last_message_id(account_token_id, source_channel_id)
                
                should_fetch = False
                with cache_lock:
                    cached_id = last_message_cache.get(source_channel_id)
                    
                    if cached_id is None:
                        should_fetch = True
                    elif cached_id != current_last_id:
                        should_fetch = True
                    
                    last_message_cache[source_channel_id] = current_last_id
                
                if not should_fetch:
                    no_message_cycle += 1
                    update_channel_activity(source_channel_id, False)
                    time.sleep(actual_delay)
                    continue
                
                rate_limiter.wait_if_needed()
                messages = discord_utils.fetch_discord_channel_messages(account_token_id, source_channel_id)
                messages = sorted(messages, key=lambda msg: int(msg['id'])) if messages else []
                incognito_names = file_utils.load_custom_names_from_json()
                new_message_found = False

                if messages:
                    for message in messages:
                        message_id = message.get('id')
                        is_new = file_utils.record_new_message_id(
                            id_value=message_id,
                            filename='ids.txt'
                        )

                        if thread_name is None:
                            thread_info = message.get('thread')
                            if thread_info:
                                tid   = thread_info.get('id')
                                tname = thread_info.get('name')
                                
                                should_start_monitor = False
                                with thread_map_lock:
                                    if tid and tid not in active_thread_ids:
                                        active_thread_ids.add(tid)
                                        should_start_monitor = True
                                
                                if should_start_monitor:
                                    console_output(f"New thread detected: '{tname}'", msg_type="INFO")

                                    if bot_token and dest_channel_id:
                                        with thread_map_lock:
                                            if tid not in thread_map:
                                                rate_limiter.wait_if_needed()
                                                new_thread = discord_utils.create_thread(bot_token, dest_channel_id, tname)
                                                if new_thread:
                                                    thread_map[tid] = new_thread['id']
                                                    file_utils.save_thread_map(thread_map)

                                    threading.Thread(
                                        target=monitor_discord_api,
                                        args=(current_delay, account_token_id, tid, webhook_url, incognito_mode, bot_token, tname),
                                        daemon=True
                                    ).start()

                        if not is_new:
                            continue

                        new_message_found = True
                        update_channel_activity(source_channel_id, True)
                        
                        message_timestamp = int(message_id) >> 22
                        message_time = datetime.datetime.fromtimestamp(message_timestamp / 1000)
                        current_time = datetime.datetime.now()
                        message_age_seconds = (current_time - message_time).total_seconds()

                        if message_age_seconds > 300:
                            time.sleep(2)

                        author      = message.get('author', {})
                        username    = author.get('username')
                        msg_txt     = message.get('content', '')
                        embeds      = message.get('embeds', [])
                        attachments = process_attachments(message)

                        ref = message.get('referenced_message')
                        if ref:
                            orig_author = ref.get('author', {}).get('username', 'unknown')
                            orig_text   = ref.get('content', '')
                            snippet     = (orig_text[:100] + '…') if len(orig_text) > 100 else orig_text
                            msg_txt     = f"> **Reply to {orig_author}:** {snippet}\n{msg_txt}"

                        if incognito_mode:
                            username   = hide_discord_username(username, incognito_names)
                            avatar_url = None
                        else:
                            avatar_hash = author.get('avatar')
                            auth_id     = author.get('id')
                            avatar_url  = (
                                f"https://cdn.discordapp.com/avatars/{auth_id}/{avatar_hash}.png"
                                if avatar_hash else None
                            )

                        with thread_map_lock:
                            dest_thread_id = thread_map.get(source_channel_id)

                        rate_limiter.wait_if_needed()
                        
                        if embeds:
                            etype, title, url, desc, fields, thumb = extract_embedded_data(embeds)
                            thread_footer = f"Thread: {thread_name}" if thread_name and etype == 'rich' else None

                            if etype == 'rich':
                                discord_utils.send_discord_webhook(
                                    message_id, username, avatar_url, webhook_url, title, url,
                                    desc, fields or [], thumb, attachments, thread_footer,
                                    dest_thread_id, True
                                )
                            else:
                                discord_utils.send_discord_webhook(
                                    message_id, username, avatar_url, webhook_url,
                                    is_bot=False, message_content=msg_txt,
                                    attachments=attachments, thread_id=dest_thread_id, reupload_files=True
                                )
                        else:
                            discord_utils.send_discord_webhook(
                                message_id, username, avatar_url, webhook_url,
                                is_bot=False, message_content=msg_txt,
                                attachments=attachments, thread_id=dest_thread_id, reupload_files=True
                            )

                if not new_message_found:
                    no_message_cycle += 1
                else:
                    no_message_cycle = 0

                consecutive_errors = 0
                current_delay = delay
                time.sleep(actual_delay)

            except Exception as ex:
                consecutive_errors += 1
                console_output(
                    f"Error in monitor [{source_channel_id}]: {str(ex)[:100]}",
                    msg_type="ERROR",
                    suppress_duplicates=True
                )
                
                backoff_delay = min(delay * (2 ** consecutive_errors), 300)
                time.sleep(backoff_delay)
                
                if consecutive_errors >= 5:
                    consecutive_errors = 0
                    current_delay = delay

    finally:
        if thread_name and source_channel_id in active_thread_ids:
            active_thread_ids.discard(source_channel_id)


if __name__ == '__main__':
    # Print banner
    print_banner(VERSION, AUTHOR)
    
    # STEP 1: Configuration
    spinner = Spinner("Loading configuration")
    spinner.start()
    time.sleep(1)
    
    if config_exists():
        spinner.stop("[✓] Configuration file found")
        config = load_config()
        
        if config:
            use_existing = show_existing_config_prompt(config)
            
            if not use_existing:
                settings = run_setup_wizard()
                config = create_new_config(settings)
                save_config(config)
        else:
            spinner.stop("[✗] Failed to load config")
            print_error("Config file is corrupted. Running setup wizard...")
            settings = run_setup_wizard()
            config = create_new_config(settings)
            save_config(config)
    else:
        spinner.stop("[i] No configuration found")
        settings = run_setup_wizard()
        config = create_new_config(settings)
        save_config(config)
        print_success("Configuration saved!")
    
    # STEP 2: Load tasks
    print()
    spinner = Spinner("Loading tasks from tasks.csv")
    spinner.start()
    time.sleep(1)
    
    try:
        tasks = file_utils.open_or_create_task_csv()
        spinner.stop(f"[✓] Loaded tasks.csv")
    except Exception as e:
        spinner.stop(f"[✗] Failed to load tasks.csv")
        print_error(f"Error: {e}")
        sys.exit(1)
    
    # STEP 3: Validate tasks
    spinner = Spinner("Validating tasks")
    spinner.start()
    time.sleep(0.5)
    
    is_valid, errors, warnings, valid_count = validate_tasks_csv(tasks)
    
    if not is_valid:
        spinner.stop("[✗] Validation failed")
        print()
        print_error("Found errors in tasks.csv:")
        for error in errors[:10]:
            print(f"  • {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
        
        print()
        cont = input("[?] Continue with valid rows only? (y/n): ").strip().lower()
        if cont != 'y':
            print_info("Exiting...")
            sys.exit(1)
    else:
        spinner.stop(f"[✓] All {valid_count} channels validated")
    
    if warnings:
        print()
        print_warning(f"Found {len(warnings)} warnings:")
        for warning in warnings[:5]:
            print(f"  • {warning}")
    
    # Filter valid tasks
    tasks_to_run = verification_utils.verify_and_filter_tasks(task_file=tasks)
    
    # STEP 4: Verify webhooks (if enabled)
    if get_setting(config, 'verify_webhooks'):
        print()
        print_info("Verifying webhooks...")
        
        progress = ProgressBar(len(tasks_to_run), prefix="Testing webhooks")
        
        def progress_callback(current, total):
            progress.update(current)
        
        working, failed = verify_webhooks(tasks_to_run, progress_callback)
        progress.finish()
        
        if failed:
            print()
            print_warning(f"{len(failed)} webhook(s) failed:")
            for fail in failed[:5]:
                print(f"  • Channel {fail['channel_id']}: {fail['reason']}")
            
            cont = input("\n[?] Continue anyway? (y/n): ").strip().lower()
            if cont != 'y':
                print_info("Exiting...")
                sys.exit(1)
    
    # STEP 5: Start bot
    print()
    print_box("STARTING BOT", [
        f"Mode: Bandwidth Optimized",
        f"Channels: {len(tasks_to_run)}",
        f"Catch-up: {'Enabled' if get_setting(config, 'fetch_on_startup') else 'Disabled'}",
        f"Proxies: {'Enabled' if get_setting(config, 'use_proxies') else 'Disabled'}",
        f"Smart delays: Enabled",
        f"",
        f"Press Ctrl+C to stop"
    ])
    
    console_output("Starting monitors...", msg_type="INFO")
    
    # Load thread map
    thread_map = file_utils.load_thread_map()
    
    # Start monitoring threads
    threads = []
    for task in tasks_to_run:
        account_token_id = task.get('account_token_id')
        bot_token        = task.get('bot_token')
        channel_id       = str(task.get('channel_id'))
        webhook_url      = task.get('webhook_url')
        delay            = task.get('delay')
        incognito_mode   = task.get('incognito_mode')

        thread = threading.Thread(
            target=monitor_discord_api,
            args=(delay, account_token_id, channel_id, webhook_url, incognito_mode, bot_token)
        )
        threads.append(thread)
        thread.start()
    
    console_output(f"All {len(threads)} monitors active!", msg_type="SUCCESS")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print()
        console_output("Shutting down gracefully...", msg_type="WARNING")
        print_success("Goodbye! ✨")