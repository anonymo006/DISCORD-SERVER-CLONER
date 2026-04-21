import websocket
import json
import time
import threading
from logger import console_output

class DiscordGatewayClient:
    """
    Discord Gateway WebSocket client for real-time message monitoring
    """
    
    def __init__(self, token, on_message_callback, on_thread_create_callback=None):
        self.token = token
        self.on_message_callback = on_message_callback
        self.on_thread_create_callback = on_thread_create_callback
        
        self.gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.ws = None
        self.heartbeat_interval = None
        self.session_id = None
        self.sequence = None
        self.heartbeat_thread = None
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def send_heartbeat(self):
        """Send periodic heartbeats to keep connection alive"""
        while self.running:
            time.sleep(self.heartbeat_interval / 1000)
            if self.ws and self.running:
                heartbeat_payload = {
                    "op": 1,
                    "d": self.sequence
                }
                try:
                    self.ws.send(json.dumps(heartbeat_payload))
                except Exception as e:
                    console_output(f"Heartbeat failed: {e}", msg_type="WARNING")
                    break
    
    def on_ws_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            op = data.get('op')
            event_data = data.get('d')
            event_type = data.get('t')
            
            if data.get('s'):
                self.sequence = data['s']
            
            # Op 10: Hello
            if op == 10:
                self.heartbeat_interval = event_data['heartbeat_interval']
                
                self.heartbeat_thread = threading.Thread(
                    target=self.send_heartbeat,
                    daemon=True
                )
                self.heartbeat_thread.start()
                
                # Identify
                identify_payload = {
                    "op": 2,
                    "d": {
                        "token": self.token,
                        "properties": {
                            "$os": "windows",
                            "$browser": "chrome",
                            "$device": "pc"
                        },
                        "intents": 33281  # GUILDS + GUILD_MESSAGES + MESSAGE_CONTENT
                    }
                }
                self.ws.send(json.dumps(identify_payload))
            
            # Op 0: Dispatch events
            elif op == 0:
                if event_type == "READY":
                    self.session_id = event_data.get('session_id')
                    user = event_data.get('user', {})
                    console_output(f"Gateway connected as {user.get('username')}", msg_type="SUCCESS")
                    self.reconnect_attempts = 0
                
                elif event_type == "MESSAGE_CREATE":
                    # New message event
                    if self.on_message_callback:
                        self.on_message_callback(event_data)
                
                elif event_type == "THREAD_CREATE":
                    # New thread event
                    if self.on_thread_create_callback:
                        self.on_thread_create_callback(event_data)
            
            # Op 7: Reconnect
            elif op == 7:
                console_output("Reconnect requested by Discord", msg_type="WARNING")
                self.reconnect()
            
            # Op 9: Invalid session
            elif op == 9:
                console_output("Invalid session, reconnecting...", msg_type="WARNING")
                time.sleep(5)
                self.reconnect()
                
        except Exception as e:
            console_output(f"Error processing gateway message: {e}", msg_type="ERROR")
    
    def on_ws_error(self, ws, error):
        """Handle WebSocket errors"""
        console_output(f"Gateway error: {error}", msg_type="ERROR")
    
    def on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket closure"""
        console_output(f"Gateway connection closed (code: {close_status_code})", msg_type="WARNING")
        
        if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect()
    
    def on_ws_open(self, ws):
        """Handle WebSocket opening"""
        console_output("Gateway connection established", msg_type="INFO")
    
    def connect(self):
        """Establish WebSocket connection to Discord Gateway"""
        self.running = True
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts > 1:
            wait_time = min(self.reconnect_attempts * 2, 30)
            console_output(f"Reconnecting in {wait_time}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})", msg_type="INFO")
            time.sleep(wait_time)
        
        self.ws = websocket.WebSocketApp(
            self.gateway_url,
            on_message=self.on_ws_message,
            on_error=self.on_ws_error,
            on_close=self.on_ws_close,
            on_open=self.on_ws_open
        )
        
        # Run in separate thread
        ws_thread = threading.Thread(
            target=self.ws.run_forever,
            daemon=True
        )
        ws_thread.start()
    
    def reconnect(self):
        """Reconnect to Gateway"""
        if self.ws:
            self.ws.close()
        time.sleep(2)
        self.connect()
    
    def disconnect(self):
        """Gracefully disconnect from Gateway"""
        self.running = False
        if self.ws:
            self.ws.close()
        console_output("Gateway disconnected", msg_type="INFO")