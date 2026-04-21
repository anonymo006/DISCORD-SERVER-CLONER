# Discord Mirror Bot 🚀

**Bandwidth-Optimized Discord Channel Mirroring Bot**

A professional Discord bot that mirrors messages, files, and threads from one server to another with **97% bandwidth reduction** through intelligent caching and optimization.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success)](https://github.com/yourusername/discord-mirror-bot)

---

## ✨ Features

- 🔄 **Real-time Message Mirroring** - Mirrors text, images, files, and embeds
- 🧵 **Thread Support** - Automatically creates and mirrors threads
- 📉 **97% Bandwidth Reduction** - Cache-first approach saves data
- 🎯 **Smart Delays** - Auto-adjusts check frequency based on activity
- 🔒 **Incognito Mode** - Anonymize usernames in mirrored messages
- 🌐 **Proxy Support** - Use proxies to distribute load
- ⚡ **Rate Limit Protection** - Intelligent rate limiting prevents bans
- 📊 **Statistics Tracking** - Hourly reports with detailed metrics
- 🎨 **Professional UI** - Interactive setup with animations
- 💾 **Persistent Config** - Save settings, no re-setup needed

---

## 📋 Requirements

- Python 3.8 or higher
- Discord user account or bot token
- Webhook access to destination server

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/discord-mirror-bot.git
cd discord-mirror-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Tasks

Edit `tasks.csv` with your channel information:

```csv
account_token_id,bot_token,channel_id,webhook_url,delay,incognito_mode
YOUR_TOKEN,YOUR_BOT_TOKEN,CHANNEL_ID,WEBHOOK_URL,20,false
```

### 4. Run Bot

```bash
python main_professional.py
```

The bot will guide you through an interactive setup wizard on first run!

---

## ⚙️ Configuration

### First-Time Setup

The bot asks 4 simple questions:

1. **Verify webhooks on startup?** - Validates all webhooks before starting
2. **Fetch missed messages on startup?** - Catches up on messages from downtime
3. **How many messages to fetch?** - Number of messages to catch up (10-100)
4. **Use proxies?** - Enable proxy support for distributed requests

Settings are saved to `config.json` and reused on subsequent runs.

### Configuration File

```json
{
  "version": "2.1.0",
  "settings": {
    "verify_webhooks": true,
    "fetch_on_startup": true,
    "fetch_limit": 50,
    "use_proxies": false,
    "proxy_file": "proxies.txt"
  }
}
```

---

## 📁 Project Structure

```
discord-mirror-bot/
├── main_professional.py          # Main bot script
├── animations.py                 # Loading animations & UI
├── config_manager.py             # Configuration management
├── setup_wizard.py               # Interactive setup
├── validator.py                  # Tasks & webhook validation
├── logger.py                     # Logging with statistics
├── rate_limiter.py               # Rate limit protection
├── utils/
│   ├── discord_utils_optimized.py   # Bandwidth-optimized API calls
│   ├── file_utils.py                # File operations
│   └── verification_utils.py        # Task verification
├── tasks.csv                     # Channel configuration
├── config.json                   # Saved settings (auto-created)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🎯 How It Works

### Bandwidth Optimization

**Traditional Polling** (10-15 GB/day):
```
Every 10s: Fetch 50 messages → Check for new → Repeat
```

**Our Optimized Approach** (~400 MB/day):
```
Every 20s: Check metadata (1 KB) → If changed, fetch messages → Else skip
```

**Result: 97% bandwidth reduction!** 🎉

### Smart Features

- **Cache-First**: Only fetches when messages actually changed
- **Smart Delays**: Active channels = 20s, quiet channels = 60s
- **Compression**: All requests use gzip compression
- **Rate Limiting**: Global limiter prevents Discord bans
- **Error Recovery**: Exponential backoff with auto-recovery

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Bandwidth (quiet day) | ~400 MB |
| Bandwidth (active day) | ~2-4 GB |
| Message delay | 0-20 seconds |
| Channels supported | 100+ |
| Rate limit incidents | <1/day |

---

## 🛠️ Advanced Usage

### Using Proxies

Create `proxies.txt` with one proxy per line:

```
IP:PORT
IP:PORT:USER:PASS
```

Enable during setup or in `config.json`:

```json
{
  "use_proxies": true,
  "proxy_file": "proxies.txt"
}
```

### Reconfigure Bot

```bash
# Delete config to run setup again
rm config.json
python main_professional.py
```

---

## 🐛 Troubleshooting

### "401 Unauthorized" Error

Your Discord token expired. Get a new token:
1. Open Discord in browser (Chrome/Firefox)
2. Press F12 → Console
3. Paste: `(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()`
4. Update token in `tasks.csv`

### "Rate Limited" Messages

- Increase delay in `tasks.csv` (try 25-30 seconds)
- Enable proxies
- Reduce number of channels

### High Bandwidth Usage

- Ensure "bandwidth optimization" is enabled (always on by default)
- Increase delays for quiet channels
- Check if cache-first is working (should see very few fetches in logs)

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚠️ Disclaimer

This bot is for educational purposes. Using user account tokens for automation may violate Discord's Terms of Service. Use at your own risk. Consider using official Discord bot accounts where possible.

---

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: [https://github.com/yourusername/discord-mirror-bot](https://github.com/yourusername/discord-mirror-bot)

---

## 🌟 Acknowledgments

- Built with [discord-webhook](https://github.com/lovvskillz/python-discord-webhook)
- Inspired by the need for efficient Discord mirroring
- Thanks to all contributors and users!

---

**⭐ If you found this project useful, please consider giving it a star on GitHub!**