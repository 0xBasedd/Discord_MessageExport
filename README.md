# Discord Message Exporter Bot

A powerful Discord bot for exporting channel messages with advanced filtering and formatting options.

## Features

- Export messages to Excel or CSV format
- Advanced filtering options (role, category, search terms, date range)
- Additional data options (attachments, reactions, replies, edits, embeds, pins)
- Progress tracking with visual progress bar
- Memory usage monitoring
- Automatic file chunking for large exports
- Secure state management
- Admin-only commands for maintenance

## Quick Start

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Discord bot token:
```
DISCORD_TOKEN=your_token_here
```

3. Run the bot:
```bash
python Discord_Message_exporter.py
```

## Commands

- `/export` - Export messages with various filtering options
- `/help` - Show detailed help information
- `/version` - Show bot version and system info
- `/logs` - Show recent log entries (Admin only)
- `/detailed-stats` - Show detailed bot statistics (Admin only)
- `/maintenance` - Toggle maintenance mode (Admin only)
- `/cleanup` - Force cleanup of resources (Admin only)
- `/restart` - Restart the bot (Admin only)

## Data Options

When exporting, you can include additional data using numbers 1-6:
1. Attachments URLs
2. Message Reactions
3. Reply References
4. Message Edits
5. Message Embeds
6. Pinned Status

Example: Use `1,2,4` to include attachments, reactions, and edits.

## Security Features

- Secure file permissions (700 for directories, 600 for files)
- State file backups
- Atomic writes for state saving
- Memory usage monitoring
- Rate limiting protection
- Error handling and logging

## Requirements

- Python 3.8+
- discord.py
- pandas
- python-dotenv
- psutil
- aiohttp
- openpyxl
- typing-extensions

## License

MIT License

## Advanced Features

### Smart Export Options

1. **Compression** 🗜️
   - ZIP format compression for all exports
   - Reduces file sizes by 60-80%
   - Perfect for large exports

2. **Parallel Processing** ⚡
   - Uses multiple CPU cores
   - Automatically splits workload
   - Great for 1000+ messages

3. **Smart Chunking** 📊
   - Weekly chunks for very active channels
   - Bi-weekly for moderate activity
   - Monthly for quiet channels

4. **Memory Optimization** 💾
   - One message at a time processing
   - Minimal RAM usage
   - Perfect for large servers

### Quick Tips for Large Exports

1. **Best Practices** 🎯
   - Use CSV for >100k messages
   - Enable compression
   - Use date ranges
   - Pick only needed data

2. **File Sizes** 📁
   - Excel: Up to 100k messages
   - CSV: Up to 500k messages
   - Auto-splits larger exports

3. **Speed Tips** ⚡
   - Use date ranges for huge exports
   - Skip unnecessary data options
   - Let the bot handle chunking

### Example Commands

**Large Server Export:**
```
!extractcsv
[Pick channel]
[Enter roles]
2022-01-01 2022-12-31  # Date range
5000  # Messages per file
```

**Quick Export:**
```
!extractcsv
[Pick channel]
[Enter role]
[Skip optional filters]
1 2  # Just attachments and reactions
```

### Export Size Handling

1. **Automatic File Splitting**
   - Customizable chunk size (default: 10,000 messages)
   - Automatically splits large exports
   - Compressed ZIP files for each chunk
   - Progress tracking per chunk

2. **Date-Based Pagination**
   - Smart date range splitting
   - Automatic density calculation
   - Optimized chunk sizes
   - Rate limit handling

### Performance Tips

1. **Optimal Export Settings**
   - For large channels (>100k messages):
     * Use CSV format
     * Enable compression
     * Use date ranges
     * Select only needed data options

2. **Memory Usage**
   - Default chunk size: 10,000 messages
   - Recommended limits:
     * Excel: 100,000 messages per file
     * CSV: 500,000 messages per file
   - Compression reduces file size by ~60-80%

3. **Processing Speed**
   - Parallel processing for large exports
   - Automatic rate limit handling
   - Smart chunking based on channel activity
   - Progress updates every 100 messages

### Example Advanced Usage

1. **Large Channel Export**
   ```
   !extractcsv
   [Select channel]
   [Enter roles]
   [Select category]
   [Enter search terms]
   [Select data options]
   2022-01-01 2022-12-31
   5000  # smaller chunks for better handling
   ```

2. **Memory-Efficient Export**
   ```
   !extractcsv
   [Select channel]
   [Enter roles]
   [Skip category]
   [Skip search]
   1 2  # minimal data options
   2023-01-01 2023-01-31  # monthly chunks
   10000
   ```

### Technical Details

1. **Compression**
   - Uses ZIP_DEFLATED compression
   - In-memory compression
   - No temporary files
   - Automatic cleanup

2. **Parallel Processing**
   - ProcessPoolExecutor for CPU-bound tasks
   - Automatic core detection
   - Configurable chunk sizes
   - Memory-aware processing

3. **Message Processing**
   - Generator-based iteration
   - Minimal memory footprint
   - Efficient data structure
   - Optimized filtering

## Installation

### Local Installation

1. **Prerequisites**
   ```bash
   # Install Python 3.8 or higher
   python -m pip install --upgrade pip
   
   # For Windows
   # Download Python from python.org
   # Make sure to check "Add Python to PATH" during installation
   
   # For Linux/Mac
   # Python usually comes pre-installed
   # Verify with: python3 --version
   ```

2. **Clone the Repository**
   ```bash
   git clone [your-repository-url]
   cd discord-message-exporter
   
   # Or download directly from GitHub:
   # 1. Click "Code" button
   # 2. Select "Download ZIP"
   # 3. Extract the ZIP file
   # 4. Open terminal in extracted folder
   ```

3. **Install Dependencies**
   ```bash
   # Windows
   pip install discord.py pandas python-dotenv openpyxl
   
   # Linux/Mac
   python3 -m pip install discord.py pandas python-dotenv openpyxl
   
   # If you get permissions errors on Linux/Mac:
   sudo python3 -m pip install discord.py pandas python-dotenv openpyxl
   ```

4. **Set Up Environment Variables**
   ```bash
   # Create .env file
   # Windows
   echo DISCORD_TOKEN=your_token_here > .env
   
   # Linux/Mac
   touch .env
   echo "DISCORD_TOKEN=your_token_here" > .env
   
   # Or create manually:
   # 1. Create new file named exactly ".env"
   # 2. Add line: DISCORD_TOKEN=your_token_here
   # 3. Save in same folder as bot
   ```

### Railway.app Deployment

1. **Prerequisites**
   - Create a [Railway.app](https://railway.app) account
     - Sign up with GitHub for easier deployment
     - Free tier includes 500 hours/month
     - Verify email address
   - Install Railway CLI (optional)
     ```bash
     # Windows
     scoop install railway
     
     # Mac
     brew install railway
     
     # Linux
     curl -fsSL https://railway.app/install.sh | sh
     ```
   - Create Discord bot and get token (see Bot Setup section)

2. **Detailed Deployment Steps**
   1. Fork this repository
      - Go to GitHub repository
      - Click "Fork" button
      - Wait for fork to complete
   
   2. Railway.app Setup
      - Log in to Railway.app
      - Click "New Project"
      - Select "Deploy from GitHub repo"
      - Choose your forked repository
      - Wait for initial deployment
   
   3. Environment Configuration
      - Click "Variables" tab
      - Add new variable:
        - Key: `DISCORD_TOKEN`
        - Value: Your Discord bot token
      - Click "Add"
   
   4. Deployment Settings
      - Click "Settings" tab
      - Set build command: `pip install -r requirements.txt`
      - Set start command: `python Discord_Message_exporter.py`
   
   5. Monitor Deployment
      - Check "Deployments" tab
      - Wait for build to complete
      - Check logs for successful startup

3. **Verify Deployment**
   - Check Railway.app logs
     - Look for "Bot connected as [bot-name]"
     - Check for any error messages
   - Test in Discord
     - Type `!test` in server
     - Bot should respond "Bot is working!"
   - Monitor resource usage in Railway dashboard

## Bot Setup

1. **Detailed Discord Bot Creation**
   1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
      - Log in with Discord account
      - Click "New Application"
      - Enter name for your bot
   
   2. Basic Configuration
      - Click "Bot" in left sidebar
      - Click "Add Bot"
      - Set bot username
      - Upload avatar (optional)
      - Uncheck "Public Bot" if private use
   
   3. Token Management
      - Click "Reset Token"
      - Copy new token
      - Store securely
      - Never share or commit token
   
   4. Intent Configuration
      - Under "Privileged Gateway Intents"
      - Enable all three toggles:
        - Presence Intent
        - Server Members Intent
        - Message Content Intent
   
   5. OAuth2 Setup
      - Click "OAuth2" in sidebar
      - Select "bot" under "Scopes"
      - Select required permissions:
        - Read Messages/View Channels
        - Read Message History
        - Send Messages
        - Attach Files
      - Copy generated URL
      - Use URL to invite bot

2. **Required Bot Permissions Explained**
   - Read Messages/View Channels
     - Needed to see channels and messages
     - Required for basic functionality
   
   - Read Message History
     - Allows accessing past messages
     - Essential for export function
   
   - Send Messages
     - Enables bot responses
     - Required for user interaction
   
   - Attach Files
     - Needed to send export files
     - Required for main functionality

## Commands

### Slash Commands
- `/export` - Export messages to Excel
- `/exportcsv` - Export messages to CSV
- `/test` - Check if bot is working

### Legacy Commands (Text Based)
- `!extract` - Export messages to Excel
- `!extractcsv` - Export messages to CSV
- `!test` - Check if bot is working

### Using Slash Commands vs Text Commands

1. **Slash Commands** `/export`
   - Better mobile experience
   - Auto-complete support
   - Clear command visibility
   - Modern Discord integration

2. **Text Commands** `!extract`
   - Works in older Discord clients
   - Faster for power users
   - No special permissions needed
   - Legacy support

## Usage

### Basic Commands
- `!test` - Check if bot is working
- `!help` - Show help message
- `!extract` - Export to Excel
- `!extractcsv` - Export to CSV

### Export Process

1. **Start Export**
   ```
   !extract
   ```
   or
   ```
   !extractcsv
   ```

2. **Channel Selection**
   - Bot shows numbered list of channels
   - Enter channel number

3. **Role Selection**
   - Enter primary role name
   - Optionally add more roles (comma-separated)
   Example: `Moderator, Admin, Staff`

4. **Category Filter (Optional)**
   - Select category number or press Enter to skip

5. **Content Search (Optional)**
   - Enter search terms or press Enter to skip
   - Case-insensitive search

6. **Additional Data Selection**
   Enter numbers for desired data:
   1. Attachments URLs
   2. Message Reactions
   3. Reply References
   4. Message Edits
   5. Message Embeds
   6. Pinned Status
   Example: `1 2 4` to select options 1, 2, and 4

7. **Date Range (Optional)**
   - Format: YYYY-MM-DD YYYY-MM-DD
   - Example: `2023-01-01 2023-12-31`
   - Press Enter to skip

### Example Usage

## Troubleshooting

### Common Issues and Solutions

1. **Bot Not Starting**
   ```
   Error: Discord token not found in .env file!
   ```
   - Check .env file exists
   - Verify token is correct
   - No quotes around token
   - No extra spaces
   
   ```
   Error: Cannot connect to Discord
   ```
   - Check internet connection
   - Verify token is valid
   - Check if bot is disabled

2. **Permission Issues**
   ```
   discord.errors.Forbidden: 403 Forbidden
   ```
   - Check bot role permissions
   - Verify channel permissions
   - Ensure bot role is high enough in hierarchy

3. **Export Problems**
   - No messages found
     - Verify role names exactly
     - Check date range format
     - Confirm channel access
   
   - File too large
     - Use CSV instead of Excel
     - Export smaller date ranges
     - Check Discord file limits

### Best Practices

1. **Security**
   - Rotate bot token regularly
   - Never share .env file
   - Use minimum required permissions
   - Monitor bot access logs

2. **Performance**
   - Export in smaller chunks
   - Use CSV for large exports
   - Filter unnecessary data
   - Consider time zones in dates

3. **Maintenance**
   - Regular token rotation
   - Update dependencies
   - Monitor Railway usage
   - Backup configuration

## Support

Need help? Try these resources:
1. Check common issues above
2. Review Railway.app documentation
3. Discord.py documentation
4. Open an issue on GitHub

## Contributing

1. Fork repository
2. Create feature branch
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Commit changes
   ```bash
   git commit -m "Add YourFeature"
   ```
4. Push to branch
   ```bash
   git push origin feature/YourFeature
   ```
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Limitations

### Discord Limitations
1. **Message History**
   - Discord API allows fetching up to 100 messages per request
   - No hard limit on total messages, but exports get slower with more messages
   - Messages older than 14 days might require additional API calls

2. **File Size Limits**
   - Discord has file upload limits:
     - 8MB for regular servers
     - 50MB for servers with Nitro boost level 2
     - 100MB for servers with Nitro boost level 3
   - Bot automatically splits files over 10,000 messages
   - Use CSV format for larger exports (smaller file size than Excel)

3. **Rate Limits**
   - Discord API has rate limiting
   - Bot automatically handles rate limits but may slow down for large exports
   - Typical rate limits:
     - 50 requests per second
     - Additional limits per endpoint

### Bot Limitations
1. **Export Size**
   - Memory usage increases with message count
   - Recommended maximum per export:
     - Excel: 100,000 messages
     - CSV: 500,000 messages
   - Use date ranges for larger exports

2. **Performance**
   - Export speed depends on:
     - Number of messages
     - Selected data options
     - Server response time
     - Rate limits
   - Large exports may take several minutes

3. **Data Types**
   - Some message types may not export perfectly:
     - System messages
     - Slash commands
     - Complex embeds
     - Custom emoji might show as IDs

### Railway.app Limitations
1. **Free Tier**
   - 500 hours per month
   - 512MB RAM
   - Shared CPU
   - Consider upgrading for heavy usage

2. **Storage**
   - Temporary files only
   - No persistent storage
   - Files deleted after sending

## Manual Operations & Maintenance

### Memory Management 🧹

1. **Manual Cleanup**
   ```bash
   # If bot becomes slow:
   !cleanup  # Forces garbage collection
   !restart  # Restarts the bot (if configured)
   ```

2. **Log Management**
   - Location: `discord_exporter.log`
   - Recommended: Rotate logs weekly
   - Max size: 100MB per log file

### Emergency Controls 🚨

1. **Export Interruption**
   - Use `Ctrl+C` in console to stop bot
   - Type `!cancel` to stop current export
   - Wait 5 minutes before restarting

2. **Rate Limit Recovery**
   ```bash
   # If bot hits rate limits:
   !pause    # Pauses all operations
   !resume   # Resumes operations
   ```

### Maintenance Schedule 📅

1. **Daily Tasks**
   - Check log files
   - Monitor memory usage
   - Clear temp files

2. **Weekly Tasks**
   - Rotate log files
   - Check Railway.app usage
   - Update bot token

3. **Monthly Tasks**
   - Update dependencies
   - Check Discord API changes
   - Backup configurations

### Health Checks 🏥

1. **Memory Status**
   ```bash
   !status    # Shows current memory usage
   !health    # Full diagnostic report
   ```

2. **Performance Monitoring**
   - Watch for slow responses
   - Monitor file compression times
   - Check export speeds

### Recovery Procedures 🔄

1. **If Bot Crashes**
   - Check logs for errors
   - Clear temp files
   - Restart bot service
   - Verify token validity

2. **If Exports Fail**
   - Try smaller date ranges
   - Use CSV instead of Excel
   - Reduce chunk size
   - Check permissions

## Environment Setup

### Local Environment
1. Create `.env` file in project root:
   ```
   DISCORD_TOKEN=your_token_here
   ```

### Railway.app Environment
1. Add environment variable:
   - Key: `DISCORD_TOKEN`
   - Value: Your bot token
2. No `.env` file needed on Railway

## Deployment

### Railway.app Setup Files
Required files in repository:
```
requirements.txt    # Dependencies
Procfile           # Start command
runtime.txt        # Python version
railway.toml       # Build config
```

### Common Deployment Issues

1. **Build Errors**
   ```
   Could not generate build plan
   ```
   - Check all required files exist
   - Verify file names are exact
   - Ensure files are in root directory

2. **Token Errors**
   ```
   Discord token not found
   ```
   - Check environment variable on Railway
   - Verify token is valid
   - Check for extra spaces

3. **Startup Issues**
   ```
   Error: No module named 'discord'
   ```
   - Verify requirements.txt is complete
   - Check Python version in runtime.txt
   - Review build logs

### Required Files Content

1. **requirements.txt**
   ```
   discord.py>=2.0.0
   pandas>=1.3.0
   python-dotenv>=0.19.0
   psutil>=5.8.0
   aiohttp>=3.8.0
   openpyxl>=3.0.0
   typing-extensions>=4.0.0
   ```

2. **Procfile**
   ```
   worker: python Discord_Message_exporter
   ```

3. **runtime.txt**
   ```
   python-3.9.16
   ```

4. **railway.toml**
   ```toml
   [build]
   builder = "NIXPACKS"
   buildCommand = "pip install -r requirements.txt"

   [deploy]
   startCommand = "python Discord_Message_exporter"
   restartPolicyType = "ON_FAILURE"
   restartPolicyMaxRetries = 10
   ```

## Command Usage

### Slash Commands

1. **`/export`**
   ```
   Required Options:
   • format: [excel/csv] - Choose export format
   • channel: [#channel] - Channel to export from
   • role: [@role] - Primary role to filter by

   Optional Options:
   • category: [category] - Filter by channel category
   • search: [text] - Search terms in messages
   • date_from: [YYYY-MM-DD] - Start date
   • date_to: [YYYY-MM-DD] - End date
   • chunk_size: [number] - Messages per file (default: 10000)
   ```

2. **`/help`**
   - Shows detailed command usage information
   - Lists all available options
   - Explains data export options

3. **`/test`**
   - Simple command to verify bot is working
   - Returns confirmation message

### Slash Command Advantages
- **Auto-complete** - Options show available choices
- **Validation** - Prevents invalid inputs
- **Visual UI** - Clear option selection
- **Mobile Friendly** - Better touch interface

### Example Slash Command Usage
```
/export format:csv channel:#general role:@Member date_from:2023-01-01 date_to:2023-12-31 chunk_size:5000
```

### Additional Data Selection
After using `/export`, you'll be prompted to select additional data:
1. Attachments URLs
2. Message Reactions
3. Reply References
4. Message Edits
5. Message Embeds
6. Pinned Status

### Legacy Commands
The traditional `!` commands are still available:
- `!extract` - Classic Excel export
- `!extractcsv` - Classic CSV export
- `!test` - Basic bot check