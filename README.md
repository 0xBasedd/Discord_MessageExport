# Discord Message Exporter Bot

A powerful Discord bot for exporting channel messages with advanced filtering, formatting, and data management capabilities. Based on the original code by Lezbrahh.

## 🚀 Features

### Core Functionality
- Export messages to Excel/CSV format
- Advanced message filtering
- Progress tracking with visual bar
- Automatic file chunking
- Memory usage monitoring
- Secure state management

### Export Options
- Role-based filtering
- Category filtering
- Date range selection
- Search term filtering
- Customizable chunk sizes
- Multiple data field options

### Data Fields
1. Attachments URLs
2. Message Reactions
3. Reply References
4. Message Edits
5. Message Embeds
6. Pinned Status

## 📋 Requirements

- Python 3.8+
- Required packages:
  ```
  discord.py>=2.0.0
  pandas>=1.3.0
  python-dotenv>=0.19.0
  psutil>=5.8.0
  aiohttp>=3.8.0
  openpyxl>=3.0.0
  typing-extensions>=4.0.0
  ```

## 🚀 Installation Guide

### Local Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/Discord_Message_exporter.git
   cd Discord_Message_exporter
   ```

2. **Set Up Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # Create .env file
   echo "DISCORD_TOKEN=your_token_here" > .env
   ```

5. **Run Locally**
   ```bash
   python Discord_Message_exporter.py
   ```

### Railway.app Deployment

1. **Fork the Repository**
   - Fork this repository to your GitHub account

2. **Set Up Railway Project**
   - Go to [Railway.app](https://railway.app/)
   - Create new project from GitHub
   - Select your forked repository

3. **Configure Environment Variables**
   - Add `DISCORD_TOKEN` in Railway's variables section
   - Value: Your Discord bot token

4. **Deploy**
   - Railway will automatically deploy your bot
   - Check deployment logs for any issues

### Required Files for Railway

1. **Procfile**
   ```
   worker: python Discord_Message_exporter.py
   ```

2. **runtime.txt**
   ```
   python-3.9.16
   ```

3. **railway.toml**
   ```toml
   [build]
   builder = "NIXPACKS"
   buildCommand = "pip install -r requirements.txt"

   [deploy]
   startCommand = "python Discord_Message_exporter.py"
   restartPolicyType = "ON_FAILURE"
   restartPolicyMaxRetries = 10
   ```

### Railway.app Limitations
- Free tier: 500 hours/month
- Memory: 512MB RAM
- Shared CPU
- No persistent storage

## 💻 Commands

### User Commands
- `/export` - Export messages with filtering options
- `/help` - Show detailed help information
- `/version` - Display bot version and system info

### Admin Commands
- `/logs` - View recent log entries
- `/detailed-stats` - Show detailed bot statistics
- `/maintenance` - Toggle maintenance mode
- `/cleanup` - Force cleanup of resources
- `/restart` - Restart the bot

## 🔧 Usage Examples

### Basic Export
```
/export format:csv channel:#general role:@Member
```

### Advanced Export
```
/export format:excel channel:#announcements role:@Mod category:Important search:update date_from:2023-01-01 date_to:2023-12-31 chunk_size:5000 data_options:1,2,3
```

## ⚙️ Configuration

The bot uses a configuration system with these key components:
- Data directory structure (`data/`)
- Log rotation and management
- State persistence
- Memory monitoring
- Security permissions

## 🔒 Security Features

- Secure file permissions (700 for directories, 600 for files)
- State file backups
- Atomic writes
- Rate limiting protection
- Error handling and logging

## 📊 Performance & Limitations

### Export Sizes
1. **File Size Considerations**
   - Excel: Up to 100,000 messages
   - CSV: Up to 500,000 messages
   - Auto-splits larger exports
   - Compression for large files

2. **Performance Factors**
   - Number of messages
   - Selected data options
   - Server response time
   - Rate limits
   - Large exports may take several minutes

3. **Data Type Limitations**
   - System messages may not export perfectly
   - Slash commands may have limited data
   - Complex embeds might be simplified
   - Custom emoji show as IDs

### Memory Management
- Automatic monitoring
- Proactive cleanup
- Warning system
- Memory usage increases with message count

## 🔧 Manual Operations & Maintenance

### Daily Maintenance
1. **Log Management**
   - Location: `data/logs/discord_exporter.log`
   - Automatic rotation: 5MB max size
   - Keeps 5 backup files
   - 30-day retention

2. **Health Checks**
   ```bash
   /detailed-stats    # Shows current status
   /cleanup          # Forces garbage collection
   /maintenance on   # Enables maintenance mode
   ```

### Emergency Procedures
1. **Export Issues**
   - Use smaller date ranges
   - Switch to CSV format
   - Reduce chunk size
   - Check permissions

2. **Recovery Steps**
   - Check logs for errors
   - Clear temp files
   - Restart bot if needed
   - Verify token validity

## 🚨 Troubleshooting

### Common Issues
1. **Permission Errors**
   - Bot needs 'View Channel' and 'Read Message History'
   - File system needs write permissions
   - Check role hierarchy

2. **Memory Warnings**
   - Reduce chunk size
   - Use CSV for large exports
   - Enable maintenance mode
   - Clear temp files

3. **Rate Limits**
   - Increase delay between requests
   - Reduce concurrent exports
   - Wait for cooldowns

4. **Export Failures**
   - Check file permissions
   - Verify channel access
   - Confirm role permissions
   - Review date formats

### Debug Mode
Add to `.env` file for additional logging:
```
DEBUG=True
```

## 📝 License

MIT License

## 🙏 Credits

Based on the original code by Lezbrahh
