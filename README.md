# Discord Message Exporter Bot

A powerful Discord bot that exports messages from channels to Excel or CSV files with extensive filtering and data collection options.

## Features

### Core Features
- Export messages to Excel (.xlsx) or CSV format
- Multiple filtering options:
  - Filter by one or multiple roles
  - Filter by channel category
  - Filter by date range
  - Search message content
- Progress tracking for large exports
- Automatic file splitting for large exports (>10,000 messages)
- Secure token handling

### Export Data Options
1. **Basic Message Data**
   - Author
   - Content
   - Timestamp

2. **Additional Data Options**
   - Attachments URLs
   - Message Reactions (emoji and count)
   - Reply References
   - Message Edit History
   - Message Embeds
   - Pinned Status

## Installation

### Local Installation

1. **Prerequisites**
   ```bash
   # Install Python 3.8 or higher
   python -m pip install --upgrade pip
   ```

2. **Clone the Repository**
   ```bash
   git clone [your-repository-url]
   cd discord-message-exporter
   ```

3. **Install Dependencies**
   ```bash
   pip install discord.py pandas python-dotenv openpyxl
   ```

4. **Set Up Environment Variables**
   - Create a file named `.env` in the project directory
   - Add your Discord bot token:
     ```
     DISCORD_TOKEN=your_token_here
     ```

### Railway.app Deployment

1. **Prerequisites**
   - Create a [Railway.app](https://railway.app) account
   - Install Railway CLI (optional)
   - Create a Discord bot and get the token

2. **Deployment Steps**
   1. Fork this repository to your GitHub account
   2. Log in to Railway.app
   3. Click "New Project"
   4. Select "Deploy from GitHub repo"
   5. Choose your forked repository
   6. Add Environment Variable:
      - Key: `DISCORD_TOKEN`
      - Value: Your Discord bot token
   7. Deploy the project

3. **Verify Deployment**
   - Check Railway.app logs for successful startup
   - Test the bot with `!test` command in Discord

## Bot Setup

1. **Create Discord Bot**
   1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
   2. Click "New Application"
   3. Go to "Bot" section
   4. Click "Add Bot"
   5. Enable these Privileged Gateway Intents:
      - Message Content Intent
      - Server Members Intent
      - Presence Intent

2. **Bot Permissions**
   - Required permissions:
     - Read Messages/View Channels
     - Read Message History
     - Send Messages
     - Attach Files
   - Invite URL: Generate from OAuth2 → URL Generator
     - Select "bot" scope
     - Select required permissions
     - Use generated URL to invite bot

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