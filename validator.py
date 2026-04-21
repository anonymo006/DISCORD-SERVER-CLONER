import os
import requests
from animations import print_error, print_warning, print_success, ProgressBar


def validate_tasks_csv(tasks_df):
    """
    Validate tasks.csv for common errors
    Returns: (is_valid, errors, warnings, valid_count)
    """
    errors = []
    warnings = []
    valid_rows = 0
    
    required_columns = ['account_token_id', 'channel_id', 'webhook_url', 'delay', 'incognito_mode']
    
    # Check if required columns exist
    for col in required_columns:
        if col not in tasks_df.columns:
            errors.append(f"Missing required column: {col}")
            return False, errors, warnings, 0
    
    # Validate each row
    for idx, row in tasks_df.iterrows():
        row_num = idx + 2  # +2 because pandas is 0-indexed and CSV has header
        row_valid = True
        
        # Check account_token_id
        if not row['account_token_id'] or str(row['account_token_id']).strip() == '':
            errors.append(f"Row {row_num}: Missing account_token_id")
            row_valid = False
        
        # Check channel_id
        try:
            channel_id = str(row['channel_id']).strip()
            if not channel_id or not channel_id.isdigit():
                errors.append(f"Row {row_num}: Invalid channel_id (must be numeric)")
                row_valid = False
        except:
            errors.append(f"Row {row_num}: Invalid channel_id")
            row_valid = False
        
        # Check webhook_url
        webhook = str(row['webhook_url']).strip()
        if not webhook or not webhook.startswith('https://discord.com/api/webhooks/'):
            errors.append(f"Row {row_num}: Invalid webhook_url")
            row_valid = False
        
        # Check delay
        try:
            delay = float(row['delay'])
            if delay < 5:
                warnings.append(f"Row {row_num}: Delay < 5s may cause rate limits")
            elif delay > 120:
                warnings.append(f"Row {row_num}: Delay > 120s may miss messages")
        except:
            errors.append(f"Row {row_num}: Delay must be a number")
            row_valid = False
        
        # Check incognito_mode
        incognito = str(row['incognito_mode']).lower()
        if incognito not in ['true', 'false', '1', '0']:
            errors.append(f"Row {row_num}: incognito_mode must be True/False")
            row_valid = False
        
        if row_valid:
            valid_rows += 1
    
    return len(errors) == 0, errors, warnings, valid_rows


def verify_webhooks(tasks_list, progress_callback=None):
    """
    Verify that all webhooks are accessible
    Returns: (working_count, failed_webhooks)
    """
    working = 0
    failed = []
    
    total = len(tasks_list)
    
    # Handle both DataFrame and list
    if hasattr(tasks_list, 'iterrows'):
        # It's a DataFrame
        items = list(tasks_list.iterrows())
    else:
        # It's a list of dicts
        items = list(enumerate(tasks_list))
    
    for idx, row in items:
        if progress_callback:
            progress_callback(idx + 1, total)
        
        # Handle both DataFrame row and dict
        if hasattr(row, 'get'):
            webhook_url = row.get('webhook_url')
            channel_id = row.get('channel_id')
        else:
            webhook_url = row['webhook_url']
            channel_id = row['channel_id']
        
        try:
            response = requests.get(webhook_url, timeout=10)
            
            if response.status_code == 200:
                working += 1
            else:
                failed.append({
                    'channel_id': channel_id,
                    'status_code': response.status_code,
                    'reason': 'HTTP Error'
                })
        except requests.exceptions.Timeout:
            failed.append({
                'channel_id': channel_id,
                'status_code': 'Timeout',
                'reason': 'Connection timeout'
            })
        except Exception as e:
            failed.append({
                'channel_id': channel_id,
                'status_code': 'Error',
                'reason': str(e)[:50]
            })
    
    return working, failed


def validate_proxy_file(proxy_file):
    """
    Validate proxy file exists and has valid format
    Returns: (is_valid, proxy_count, errors)
    """
    if not os.path.exists(proxy_file):
        return False, 0, [f"Proxy file not found: {proxy_file}"]
    
    errors = []
    valid_proxies = 0
    
    try:
        with open(proxy_file, 'r') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split(':')
            if len(parts) == 2:
                # IP:PORT format
                ip, port = parts
                if not port.isdigit():
                    errors.append(f"Line {line_num}: Invalid port number")
                else:
                    valid_proxies += 1
            elif len(parts) == 4:
                # IP:PORT:USER:PASS format
                ip, port, user, password = parts
                if not port.isdigit():
                    errors.append(f"Line {line_num}: Invalid port number")
                else:
                    valid_proxies += 1
            else:
                errors.append(f"Line {line_num}: Invalid proxy format (use IP:PORT or IP:PORT:USER:PASS)")
        
        if valid_proxies == 0:
            errors.append("No valid proxies found in file")
            return False, 0, errors
        
        return True, valid_proxies, errors
        
    except Exception as e:
        return False, 0, [f"Error reading proxy file: {e}"]