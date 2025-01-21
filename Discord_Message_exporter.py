#!/usr/bin/env python3
"""
Discord Message Exporter Bot
Copyright (c) 2024 info-infoweb
Based on the Python code created by @lezbrahh

This bot allows exporting Discord channel messages with advanced filtering,
formatting, and data management capabilities.

Licensed under MIT License
"""

# 1. BASIC IMPORTS
import os
import sys
from dotenv import load_dotenv
import time  # Add this import

# 2. CONFIGURATION
VERSION = "1.0.0"
COMMAND_PREFIX = "/"
DEFAULT_CHUNK_SIZE = 10000
EXPORT_COOLDOWN = 5
MAINTENANCE_MODE = False
MEMORY_WARNING_THRESHOLD = 70
MEMORY_CRITICAL_THRESHOLD = 85
MEMORY_CHECK_INTERVAL = 60
MEMORY_TREND_SAMPLES = 5
DATA_DIR = "data"
LOG_FILE = "discord_exporter.log"
STATE_FILE = "bot_state.json"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5
LOG_RETENTION_DAYS = 30
MAX_MESSAGES_EXCEL = 100000
MAX_MESSAGES_CSV = 500000
RATE_LIMIT_DELAY = 0.25
MAX_RETRIES = 5
TIMEOUT = 30.0
DIR_PERMISSION = 0o700
FILE_PERMISSION = 0o600

# 2.1 BOT STATE CLASS
class BotState:
    def __init__(self):
        self.start_time = time.time()
        self.total_exports = 0
        self.successful_exports = 0
        self.failed_exports = 0
        self.total_messages_processed = 0
        self.last_error = None
        self.is_maintenance_mode = MAINTENANCE_MODE
        self.state_manager = None  # Will be initialized after DataDirectory

    def save_state(self):
        """Save state to file"""
        if not self.state_manager:
            return False
        state = {
            'total_exports': self.total_exports,
            'successful_exports': self.successful_exports,
            'failed_exports': self.failed_exports,
            'total_messages_processed': self.total_messages_processed,
            'is_maintenance_mode': self.is_maintenance_mode
        }
        return True

    def load_state(self):
        """Load state from file"""
        pass  # Will be implemented after DataDirectory is available

    def record_export(self, success: bool, messages_processed: int = 0):
        """Record export statistics"""
        self.total_exports += 1
        if success:
            self.successful_exports += 1
        else:
            self.failed_exports += 1
        self.total_messages_processed += messages_processed

    def get_stats(self) -> dict:
        """Get current statistics"""
        uptime = time.time() - self.start_time
        days = int(uptime // (24 * 3600))
        hours = int((uptime % (24 * 3600)) // 3600)
        minutes = int((uptime % 3600) // 60)
        
        return {
            'uptime': f"{days}d {hours}h {minutes}m",
            'total_exports': self.total_exports,
            'successful_exports': self.successful_exports,
            'failed_exports': self.failed_exports,
            'success_rate': f"{(self.successful_exports / self.total_exports * 100):.1f}%" if self.total_exports > 0 else "N/A",
            'total_messages': self.total_messages_processed,
            'last_error': str(self.last_error) if self.last_error else None,
            'maintenance_mode': self.is_maintenance_mode
        }

    def set_maintenance_mode(self, enabled: bool):
        """Set maintenance mode"""
        self.is_maintenance_mode = enabled

# 2.1 ENVIRONMENT SETUP
# Load environment variables (skip on Railway)
if not os.getenv('RAILWAY_ENVIRONMENT'):
    load_dotenv(override=True)

# Get token from environment
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("Error: Discord token not found!")
    print("Make sure DISCORD_TOKEN is set in your environment variables")
    sys.exit(1)
print("Token loaded successfully (token hidden for security)")

# Initialize bot state early
bot_state = BotState()

# 3. RAILWAY CHECK
RAILWAY_MODE = bool(os.getenv('RAILWAY_ENVIRONMENT'))
if RAILWAY_MODE:
    try:
        print("\n=== Railway Startup Check ===")
        print(f"Python executable: {sys.executable}")
        print(f"Script path: {__file__}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Available files: {os.listdir()}")
        
        # Verify we're running from the correct location
        if not os.path.exists('/app/bot.py'):
            print("ERROR: Bot file not found in /app directory!")
            print("Files in /app:", os.listdir('/app'))
            sys.exit(1)
            
        # Check write permissions
        try:
            test_file = "/app/write_test"
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("Write permissions OK")
        except Exception as e:
            print(f"Warning: Write permission test failed: {e}")
            
        print("===========================\n")
    except Exception as e:
        print(f"Railway startup check failed: {e}")
        sys.exit(1)

# 4. REST OF IMPORTS
import discord
import os
import pandas as pd
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import math
import asyncio
import zipfile
import io
import concurrent.futures
import functools
import traceback
import psutil
import time
from typing import Optional, Tuple, List, Literal, Any, Dict
import aiohttp
import logging
from discord import app_commands
from discord.ext import commands
import signal
import atexit
from logging.handlers import RotatingFileHandler
import json
import glob
from functools import wraps

# Add after imports
RAILWAY_MODE = bool(os.getenv('RAILWAY_ENVIRONMENT'))
if RAILWAY_MODE:
    print("\n=== Railway Environment Details ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Available directories: {os.listdir()}")
    print(f"Environment variables: {[k for k in os.environ.keys() if not k.startswith('PATH')]}")
    print(f"Discord.py version: {discord.__version__}")
    print(f"Memory: {psutil.virtual_memory()}")
    print("================================\n")

    # Additional Railway-specific checks
    try:
        import pwd
        print("\n=== Railway User Details ===")
        print(f"Current user: {pwd.getpwuid(os.getuid()).pw_name}")
        print(f"User home: {os.path.expanduser('~')}")
        print(f"User permissions: {oct(os.stat('.').st_mode)[-3:]}")
        print("===========================\n")
    except ImportError:
        print("pwd module not available")

    # Check write permissions
    try:
        print("\n=== Railway Write Test ===")
        test_file = "/tmp/write_test"
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("Write test successful")
        print("========================\n")
    except Exception as e:
        print(f"Write test failed: {e}")
        print("Attempting fallback to user directory...")
        try:
            test_file = os.path.expanduser("~/write_test")
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("Fallback write test successful")
        except Exception as e2:
            print(f"Fallback write test failed: {e2}")
            print("WARNING: Bot may have limited functionality")

# 6. DATA DIRECTORY SETUP
class RailwayFileHandler:
    """Handle file operations for Railway environment"""
    @staticmethod
    def get_writable_dir():
        """Get a writable directory path for Railway"""
        if not os.getenv('RAILWAY_ENVIRONMENT'):
            return None
            
        # Try different possible writable locations
        test_paths = [
            '/tmp',
            os.path.expanduser('~'),
            os.getcwd(),
            '/app/data'
        ]
        
        for path in test_paths:
            try:
                test_file = os.path.join(path, 'write_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"Found writable directory: {path}")
                return path
            except Exception as e:
                print(f"Cannot write to {path}: {e}")
        
        print("WARNING: No writable directory found!")
        return '/tmp'  # Fallback to /tmp even if test failed

class DataDirectory:
    """Manage bot data directory structure"""
    def __init__(self, base_dir: str = DATA_DIR):
        if os.getenv('RAILWAY_ENVIRONMENT'):
            writable_dir = RailwayFileHandler.get_writable_dir()
            self.base_dir = os.path.join(writable_dir, 'discord_exporter')
            print(f"\n=== Railway Directory Setup ===")
            print(f"Using Railway directory: {self.base_dir}")
            if not os.path.exists(self.base_dir):
                try:
                    os.makedirs(self.base_dir, exist_ok=True)
                    print(f"Created Railway directory: {self.base_dir}")
                except Exception as e:
                    print(f"Error creating Railway directory: {e}")
            print(f"Directory contents: {os.listdir(self.base_dir) if os.path.exists(self.base_dir) else 'not created'}")
            print("==============================\n")
        else:
            self.base_dir = base_dir
        
        self.state_dir = os.path.join(self.base_dir, "state")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.temp_dir = os.path.join(self.base_dir, "temp")
        self._ensure_directories()

    def _ensure_directories(self):
        """Create directory structure with proper permissions"""
        for directory in [self.base_dir, self.state_dir, self.logs_dir, self.temp_dir]:
            try:
                if not os.path.exists(directory):
                    os.makedirs(directory, mode=DIR_PERMISSION)
                else:
                    os.chmod(directory, DIR_PERMISSION)
            except Exception as e:
                logger.error(f"Error creating directory {directory}: {e}")
                # On Railway, try without permissions
                if os.getenv('RAILWAY_ENVIRONMENT'):
                    os.makedirs(directory, exist_ok=True)

    def get_state_file(self, filename: str) -> str:
        """Get path for state file"""
        return os.path.join(self.state_dir, filename)

    def get_log_file(self, filename: str) -> str:
        """Get path for log file"""
        return os.path.join(self.logs_dir, filename)

    def get_temp_file(self, filename: str) -> str:
        """Get path for temporary file"""
        return os.path.join(self.temp_dir, filename)

    def cleanup_temp(self, max_age: int = 24):
        """Clean up old temporary files"""
        try:
            now = time.time()
            for filename in os.listdir(self.temp_dir):
                filepath = os.path.join(self.temp_dir, filename)
                if os.path.getmtime(filepath) < now - (max_age * 3600):
                    os.remove(filepath)
        except Exception as e:
            logger.error(f"Error cleaning temp directory: {e}")

    def check_permissions(self):
        """Check and fix directory permissions"""
        try:
            # Check base directories
            for directory in [self.base_dir, self.state_dir, self.logs_dir, self.temp_dir]:
                if os.path.exists(directory):
                    current_mode = oct(os.stat(directory).st_mode)[-3:]
                    if current_mode != oct(DIR_PERMISSION)[-3:]:  # Compare with config value
                        logger.warning(f"Fixing permissions for {directory}")
                        os.chmod(directory, DIR_PERMISSION)

            # Check state files
            for file in glob.glob(os.path.join(self.state_dir, '*')):
                if os.path.isfile(file):
                    current_mode = oct(os.stat(file).st_mode)[-3:]
                    if current_mode != oct(FILE_PERMISSION)[-3:]:  # Compare with config value
                        logger.warning(f"Fixing permissions for {file}")
                        os.chmod(file, FILE_PERMISSION)

            # Check log files
            for file in glob.glob(os.path.join(self.logs_dir, '*')):
                if os.path.isfile(file):
                    current_mode = oct(os.stat(file).st_mode)[-3:]
                    if current_mode != oct(FILE_PERMISSION)[-3:]:  # Compare with config value
                        logger.warning(f"Fixing permissions for {file}")
                        os.chmod(file, FILE_PERMISSION)

            return True
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False

def cleanup_old_logs():
    """Clean up old log files"""
    try:
        # Clean up logs directory
        data_dir.cleanup_temp()  # Clean temp files first
        
        now = datetime.now()
        log_pattern = os.path.join(data_dir.logs_dir, LOG_FILE + '*')  # Use config LOG_FILE
        
        for log_file in glob.glob(log_pattern):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                if now - mtime > timedelta(days=LOG_RETENTION_DAYS):  # Use config value
                    os.remove(log_file)
                    logger.info(f"Removed old log file: {log_file}")
            except Exception as e:
                logger.error(f"Error cleaning up log file {log_file}: {e}")
                
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}")

# Initialize data directory first
data_dir = DataDirectory()

# Clean up old logs at startup
cleanup_old_logs()

# 7. VERSION
VERSION = VERSION  # Using imported VERSION instead of config.VERSION

# 8. LOGGING CONFIGURATION
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler with rotation
file_handler = RotatingFileHandler(
    data_dir.get_log_file(LOG_FILE),  # Using imported LOG_FILE
    maxBytes=LOG_MAX_SIZE,  # Using imported LOG_MAX_SIZE
    backupCount=LOG_BACKUP_COUNT,  # Using imported LOG_BACKUP_COUNT
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Remove any existing handlers to prevent duplicates
for handler in logger.handlers[:]:
    if not isinstance(handler, (RotatingFileHandler, logging.StreamHandler)):
        logger.removeHandler(handler)

# 9. CLASS DEFINITIONS
class ProgressTracker:
    def __init__(self, message, total=None):
        self.message = message
        self.count = 0
        self.filtered_count = 0
        self.total = total
        self.last_update = time.time()
        self.update_interval = 2
        self.batch_size = 100
        self.last_message = None  # Track last message to prevent duplicates

    def _generate_progress_bar(self, progress):
        length = 20
        filled = int(length * progress / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f'[{bar}]'

    async def update(self, force=False, filtered=False, batch_mode=False):
        """
        Update progress
        batch_mode: True if updating for a batch of messages (don't increment count)
        """
        try:
            if not batch_mode:
                self.count += 1
                if filtered:
                    self.filtered_count += 1
            
            current_time = time.time()
            should_update = force or (
                self.count % self.batch_size == 0 and 
                current_time - self.last_update >= self.update_interval
            )
            
            if should_update:
                self.last_update = current_time
                try:
                    message = self._generate_progress_message()
                    if message != self.last_message:  # Only update if message changed
                        await self.message.edit(content=message)
                        self.last_message = message
                except discord.errors.HTTPException as e:
                    logger.error(f"Failed to update progress: {e}")
        except Exception as e:
            logger.error(f"Progress update error: {e}")

    def _generate_progress_message(self):
        """Generate progress message string"""
        if self.total and self.total > 0:
            progress = min((self.count / self.total) * 100, 100)
            bar = self._generate_progress_bar(progress)
            filtered_info = f" ({self.filtered_count:,} matched)" if self.filtered_count else ""
            return f"Progress: {self.count:,}/{self.total:,} messages {bar} ({progress:.1f}%){filtered_info}"
        else:
            filtered_info = f" ({self.filtered_count:,} matched)" if self.filtered_count else ""
            return f"Progress: {self.count:,} messages processed...{filtered_info}"

class ExporterBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._last_export_time = 0
        self._export_cooldown = EXPORT_COOLDOWN  # Using imported EXPORT_COOLDOWN
        self._session = None
        self._active_exports = set()
        self._start_time = time.time()

    async def setup_hook(self):
        self._session = aiohttp.ClientSession()
        await self.tree.sync()

    async def can_export(self):
        current_time = time.time()
        if current_time - self._last_export_time < self._export_cooldown:
            return False
        self._last_export_time = current_time
        return True

    async def check_memory(self):
        """Check available memory and warn if low"""
        available_memory = psutil.virtual_memory().available / (1024 * 1024)
        return available_memory >= 100  # Return True if more than 100MB available

    async def cleanup(self):
        """Async cleanup tasks"""
        try:
            # Cancel active exports
            for task in self._active_exports:
                task.cancel()
            self._active_exports.clear()

            # Cancel other tasks
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Clear memory
            clear_memory()
            
            # Close session
            if self._session:
                await self._session.close()
                self._session = None
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def close(self):
        """Clean shutdown"""
        try:
            await self.cleanup()
        finally:
            await super().close()

class MessageChunker:
    """Helper for managing message chunks"""
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.current_chunk = []
        self.chunk_number = 0

    async def add_message(self, message_data, channel_name, is_csv, original_message):
        if message_data:
            self.current_chunk.append(message_data)
            
        if len(self.current_chunk) >= self.chunk_size:
            await self._save_chunk(channel_name, is_csv, original_message)

    async def _save_chunk(self, channel_name, is_csv, original_message):
        if self.current_chunk:
            self.chunk_number += 1
            await save_and_send_messages(
                self.current_chunk,
                channel_name,
                f"part{self.chunk_number}",
                is_csv,
                self.chunk_size,
                original_message
            )
            self.current_chunk = []

    async def finish(self, channel_name, is_csv, original_message):
        if self.current_chunk:
            await self._save_chunk(channel_name, is_csv, original_message)

class ExportCleanup:
    """Context manager for export cleanup"""
    def __init__(self, client, task):
        self.client = client
        self.task = task
        self.start_time = time.time()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            duration = time.time() - self.start_time
            logger.info(f"Export completed in {duration:.1f}s")
            
            # Force garbage collection
            clear_memory()
            
            # Remove task from active exports
            self.client._active_exports.discard(self.task)
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# 10. UTILITY FUNCTIONS
def clear_memory():
    """Force garbage collection"""
    import gc
    gc.collect()

# Replace global client with a proper singleton pattern
class BotInstance:
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def set_instance(cls, bot):
        cls._instance = bot

# Replace client references with BotInstance
async def check_memory_usage(message_count, message):
    """Check memory usage periodically"""
    if message_count % 1000 == 0:
        clear_memory()
        client = BotInstance.get_instance()
        if client and not await client.check_memory():
            await message.channel.send("⚠️ Warning: Memory usage high, consider using smaller chunks")

# 11. DECORATORS
def handle_errors(func):
    """Error handling decorator for event handlers"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
    return wrapper

def retry_on_error(retries=3, delay=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except (discord.errors.HTTPException, aiohttp.ClientError) as e:
                    if attempt == retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

def command_cooldown(seconds: int):
    """Cooldown decorator for commands"""
    def decorator(func):
        last_used = {}  # Store last use time per user
        
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            user_id = interaction.user.id
            current_time = time.time()
            
            # Check cooldown
            if user_id in last_used:
                time_since_last = current_time - last_used[user_id]
                if time_since_last < seconds:
                    remaining = int(seconds - time_since_last)
                    await interaction.response.send_message(
                        f"⏳ Please wait {remaining} seconds before using this command again.",
                        ephemeral=True
                    )
                    return
            
            # Update last use time
            last_used[user_id] = current_time
            
            # Clean up old entries periodically
            if len(last_used) > 1000:  # Prevent memory leak
                cutoff = current_time - (seconds * 2)
                last_used.clear()
            
            # Execute command
            return await func(interaction, *args, **kwargs)
            
        return wrapper
    return decorator

# 12. HELPER FUNCTIONS
async def process_message_filters(msg, role, category, channel, search, date_from, date_to):
    """Process all message filters"""
    try:
        # Role check
        member = msg.guild.get_member(msg.author.id)
        if not member or role not in member.roles:
            return False

        # Category check
        if category and channel not in category.channels:
            return False

        # Search check
        if search and search.lower() not in msg.content.lower():
            return False

        # Date check
        if date_from and date_to:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d')
                end_date = datetime.strptime(date_to, '%Y-%m-%d')
                if not (start_date <= msg.created_at.replace(tzinfo=None) <= end_date):
                    return False
            except ValueError:
                logger.error("Date parsing error")
                return False

        return True
    except Exception as e:
        logger.error(f"Filter error: {e}")
        return False

async def create_message_data(message: discord.Message, data_options: Optional[str] = None) -> Optional[dict]:
    """Create message data dictionary with optional data fields"""
    try:
        # Parse data options
        options = set(map(int, data_options.split(','))) if data_options else set()
        
        # Base message data
        data = {
            'Message ID': str(message.id),
            'Author': str(message.author),
            'Content': message.content,
            'Channel': message.channel.name,
            'Timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Optional data based on options
        if 1 in options:  # Attachments
            data['Attachments'] = ', '.join([a.url for a in message.attachments])
            
        if 2 in options:  # Reactions
            data['Reactions'] = ', '.join([f"{r.emoji}:{r.count}" for r in message.reactions])
            
        if 3 in options:  # Reply References
            data['Reply To'] = str(message.reference.message_id) if message.reference else ''
            
        if 4 in options:  # Message Edits
            data['Edited'] = message.edited_at.strftime('%Y-%m-%d %H:%M:%S') if message.edited_at else ''
            
        if 5 in options:  # Embeds
            data['Embeds'] = len(message.embeds)
            
        if 6 in options:  # Pinned Status
            data['Pinned'] = message.pinned
            
        return data
    except Exception as e:
        logger.error(f"Error creating message data: {e}")
        return None

class SafeBuffer:
    """Context manager for safe buffer handling"""
    def __init__(self):
        self.buffers = []

    def create_buffer(self, buffer_type=io.BytesIO):
        buffer = buffer_type()
        self.buffers.append(buffer)
        return buffer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for buffer in self.buffers:
            try:
                buffer.close()
            except:
                pass

# Use in save_and_send_messages
async def save_and_send_messages(messages: List[dict], channel_name: str, suffix: str, is_csv: bool, chunk_size: int, message: discord.Message):
    """Save messages to file and send to channel"""
    try:
        # Create DataFrame
        df = pd.DataFrame(messages)
        
        # Prepare filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{channel_name}_{timestamp}_{suffix}"
        
        # Save to temp file
        temp_path = data_dir.get_temp_file(filename)
        if is_csv:
            df.to_csv(f"{temp_path}.csv", index=False, encoding='utf-8-sig')
            file_path = f"{temp_path}.csv"
        else:
            df.to_excel(f"{temp_path}.xlsx", index=False)
            file_path = f"{temp_path}.xlsx"
        
        # Send file
        await message.channel.send(
            f"📊 Export part ({len(messages):,} messages)",
            file=discord.File(file_path)
        )
        
        # Cleanup temp file
        try:
            os.remove(file_path)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error saving messages: {e}")
        await message.channel.send(f"❌ Error saving messages: {str(e)}")

# Add to helper functions
async def estimate_message_count(channel: discord.TextChannel, role=None, after=None, before=None) -> int:
    """Estimate total messages for progress tracking"""
    try:
        count = 0
        sample_size = 1000
        async for msg in channel.history(limit=sample_size):
            if role and not any(role == r for r in msg.author.roles):
                continue
            if after and msg.created_at < after:
                continue
            if before and msg.created_at > before:
                continue
            count += 1
        
        if count == 0:
            return 1000  # Default estimate if no messages found in sample
            
        # Estimate total based on sample
        total_seconds = (before or datetime.now()) - (after or channel.created_at)
        sample_seconds = timedelta(days=7)
        ratio = total_seconds / sample_seconds
        estimated_total = max(int(count * ratio), count)  # Never estimate less than what we counted
        return min(estimated_total, 1000000)  # Cap at 1M for safety
    except Exception as e:
        logger.error(f"Error estimating messages: {e}")
        return 1000  # Default fallback estimate

# Add this helper function to handle pagination
async def fetch_messages_with_pagination(channel, progress_tracker=None, max_retries=MAX_RETRIES, timeout=TIMEOUT):
    messages = []
    last_message_id = None
    batch_count = 0
    retry_count = 0
    
    while True:
        try:
            async with asyncio.timeout(timeout):
                batch = await channel.history(
                    limit=100,
                    before=last_message_id and discord.Object(id=last_message_id)
                ).flatten()
            
            retry_count = 0
            
            if not batch:
                break
                
            messages.extend(batch)
            batch_count += 1
            
            if progress_tracker:
                # Update progress for the batch
                progress_tracker.count += len(batch)
                await progress_tracker.update(force=True, batch_mode=True)
            
            last_message_id = batch[-1].id
            await asyncio.sleep(min(2.0, RATE_LIMIT_DELAY * batch_count))
            
        except (asyncio.TimeoutError, discord.errors.HTTPException, aiohttp.ClientError) as e:
            retry_count += 1
            if retry_count >= max_retries:
                if isinstance(e, asyncio.TimeoutError):
                    raise ValueError(f"Operation timed out after {max_retries} retries")
                elif isinstance(e, discord.errors.HTTPException):
                    if e.code in [50001, 50013]:
                        raise ValueError(f"Permission error: {str(e)}")
                    elif e.code == 429:
                        raise ValueError(f"Too many rate limits hit after {max_retries} retries")
                raise ValueError(f"Error after {max_retries} retries: {str(e)}")
            
            wait_time = retry_count * 2 if isinstance(e, asyncio.TimeoutError) else retry_count
            if isinstance(e, discord.errors.HTTPException) and e.code == 429:
                wait_time = e.retry_after if hasattr(e, 'retry_after') else 5
            
            logger.warning(f"Error (attempt {retry_count}/{max_retries}), waiting {wait_time}s: {str(e)}")
            await asyncio.sleep(wait_time)
    
    return messages

# 13. BOT INITIALIZATION
client = ExporterBot()  # Initialize immediately instead of setting to None
BotInstance.set_instance(client)

# 14. EVENT HANDLERS
@client.event
@handle_errors
async def on_ready():
    print(f'Bot connected as {client.user}')

@client.tree.error
async def on_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Command is on cooldown. Try again in {error.retry_after:.1f}s",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
    else:
        logger.error(f"Command error: {error}")
        await interaction.response.send_message(
            "❌ An error occurred while processing the command.",
            ephemeral=True
        )

# 15. SLASH COMMANDS
@client.tree.command(name="export", description="Export messages to Excel/CSV format")
@app_commands.describe(
    format="Choose export format (Excel or CSV)",
    channel="Select channel to export from",
    role="Primary role to filter messages",
    category="Optional: Filter by channel category",
    search="Optional: Search terms in messages",
    date_from="Optional: Start date (YYYY-MM-DD)",
    date_to="Optional: End date (YYYY-MM-DD)",
    chunk_size="Optional: Messages per file (default: 10000)",
    data_options="Optional: Additional data options (comma-separated numbers 1-6)"
)
@app_commands.choices(format=[
    app_commands.Choice(name="Excel", value="excel"),
    app_commands.Choice(name="CSV", value="csv")
])
@command_cooldown(10)  # 10 second cooldown
async def export(
    interaction: discord.Interaction,
    format: Literal["excel", "csv"],
    channel: discord.TextChannel,
    role: discord.Role,
    category: Optional[discord.CategoryChannel] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    chunk_size: Optional[int] = 10000,
    data_options: Optional[str] = None
):
    if bot_state.is_maintenance_mode:
        await interaction.response.send_message("🔧 Bot is currently in maintenance mode. Please try again later.")
        return

    task = asyncio.current_task()
    
    async with ExportCleanup(client, task):
        try:
            task.user_id = interaction.user.id
            task.start_time = time.time()
            client._active_exports.add(task)
            
            # Memory and cooldown checks
            if not await client.check_memory():
                await interaction.response.send_message("⚠️ Low memory available. Try smaller chunk size.")
                return

            if not await client.can_export():
                await interaction.response.send_message("⏳ Please wait a few seconds between exports.")
                return

            await interaction.response.send_message("Processing your request...")
            message = await interaction.original_response()
            
            # Parse dates safely
            start_date = None
            end_date = None
            if date_from:
                try:
                    start_date = datetime.strptime(date_from, '%Y-%m-%d')
                except ValueError:
                    await interaction.response.send_message("❌ Invalid start date format. Use YYYY-MM-DD")
                    return
                
            if date_to:
                try:
                    end_date = datetime.strptime(date_to, '%Y-%m-%d')
                except ValueError:
                    await interaction.response.send_message("❌ Invalid end date format. Use YYYY-MM-DD")
                    return
            
            if start_date and end_date and start_date > end_date:
                await interaction.response.send_message("❌ Start date must be before end date")
                return
            
            # Initialize progress tracker with estimated count
            estimated_count = await estimate_message_count(channel, role, start_date, end_date)
            progress = ProgressTracker(message, total=estimated_count or 1000)  # Fallback estimate
            
            # Initialize chunker
            chunker = MessageChunker(chunk_size)
            processed_count = 0
            
            try:
                # Fetch all messages with pagination
                messages = await fetch_messages_with_pagination(channel, progress)
                total_messages = len(messages)
                
                if total_messages == 0:
                    await message.edit(content="❌ No messages found in channel")
                    return
                
                await message.edit(content=f"Processing {total_messages:,} messages...")
                
                # Process the fetched messages
                for msg in messages:
                    # Check memory periodically
                    is_ok, warning_message = memory_monitor.check()
                    if not is_ok:
                        await warning_message.channel.send(warning_message)
                        return
                    elif warning_message:  # Warning message
                        await warning_message.channel.send(warning_message)
                    
                    if not await process_message_filters(msg, role, category, channel, search, date_from, date_to):
                        await progress.update(filtered=False)
                        continue

                    message_data = await create_message_data(msg, data_options)
                    if message_data:
                        await chunker.add_message(message_data, channel.name, format == "csv", message)
                        processed_count += 1
                        await progress.update(filtered=True)
                    else:
                        await progress.update(filtered=False)
                
                if processed_count == 0:
                    await message.edit(content="❌ No messages matched the filters")
                    return
                
                # Record successful export
                bot_state.record_export(True, processed_count)
                await message.edit(content=f"✅ Processed {processed_count:,} out of {total_messages:,} messages")
                
                # Save any remaining messages
                await chunker.finish(channel.name, format == "csv", message)

            except ValueError as e:
                bot_state.last_error = str(e)
                bot_state.record_export(False)
                await message.channel.send(f"❌ Error: {str(e)}")
                return

        except Exception as e:
            bot_state.last_error = str(e)
            bot_state.record_export(False)
            await message.channel.send(f"❌ Export failed: {str(e)}")
            logger.error(f"Export error: {e}", exc_info=True)
        finally:
            client._active_exports.discard(task)

@client.tree.command(name="help", description="Show detailed help information")
async def help(interaction: discord.Interaction):
    """Show detailed help information"""
    try:
        embed = discord.Embed(
            title="Discord Message Exporter Help",
            description="Detailed guide on how to use the bot",
            color=discord.Color.blue()
        )
        
        # Export Options
        embed.add_field(
            name="Export Options",
            value="""
            **Required:**
            • `format` - Choose 'excel' or 'csv'
            • `channel` - Channel to export from
            • `role` - Role to filter messages by
            
            **Optional:**
            • `category` - Filter by category
            • `search` - Search in messages
            • `date_from` - Start date (YYYY-MM-DD)
            • `date_to` - End date (YYYY-MM-DD)
            • `chunk_size` - Messages per file
            """,
            inline=False
        )
        
        # Data Options
        embed.add_field(
            name="Additional Data Options",
            value="""
            Use numbers 1-6 separated by commas:
            1. Attachments URLs
            2. Message Reactions
            3. Reply References
            4. Message Edits
            5. Message Embeds
            6. Pinned Status
            
            Example: `1,2,4` for attachments, reactions, and edits
            """,
            inline=False
        )
        
        # Examples
        embed.add_field(
            name="Example Usage",
            value="""
            Basic export:
            `/export format:csv channel:#general role:@Member`
            
            Advanced export:
            `/export format:excel channel:#announcements role:@Mod category:Important search:update date_from:2023-01-01 date_to:2023-12-31 chunk_size:5000 data_options:1,2,3`
            """,
            inline=False
        )
        
        embed.set_footer(text="Use /commands to see all available commands")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.error(f"Help error: {e}")
        await interaction.response.send_message("❌ Error showing help information")

@client.tree.command(name="test", description="Check if bot is working")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Bot is working!")

@client.tree.command(name="status", description="Show bot status")
async def status(interaction: discord.Interaction):
    client = BotInstance.get_instance()
    if not client:
        await interaction.response.send_message("❌ Bot not initialized")
        return

    memory = psutil.virtual_memory()
    active_exports = len(client._active_exports)
    
    status_text = f"""
    **Bot Status**
    Memory Usage: {memory.percent}%
    Active Exports: {active_exports}
    Uptime: {time.time() - client._start_time:.0f} seconds
    """
    await interaction.response.send_message(status_text)

@client.tree.command(name="cancel", description="Cancel ongoing exports")
@command_cooldown(5)
async def cancel(interaction: discord.Interaction):
    """Cancel all active exports for the user"""
    client = BotInstance.get_instance()
    if not client:
        await interaction.response.send_message("❌ Bot not initialized")
        return

    cancelled = 0
    for task in client._active_exports.copy():
        if hasattr(task, 'user_id') and task.user_id == interaction.user.id:
            task.cancel()
            client._active_exports.discard(task)
            cancelled += 1

    if cancelled:
        await interaction.response.send_message(f"✅ Cancelled {cancelled} active export(s)")
    else:
        await interaction.response.send_message("❌ No active exports found")

@client.tree.command(name="cleanup", description="Force cleanup (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def cleanup(interaction: discord.Interaction):
    """Force cleanup of resources"""
    client = BotInstance.get_instance()
    if not client:
        await interaction.response.send_message("❌ Bot not initialized")
        return

    try:
        await interaction.response.send_message("🧹 Starting cleanup...")
        message = await interaction.original_response()
        
        # Cancel all exports
        export_count = len(client._active_exports)
        for task in client._active_exports.copy():
            task.cancel()
        client._active_exports.clear()
        
        # Force garbage collection
        clear_memory()
        
        memory_before = psutil.virtual_memory().percent
        memory_after = psutil.virtual_memory().percent
        
        await message.edit(content=f"""
        ✅ Cleanup complete:
        • Cancelled exports: {export_count}
        • Memory usage: {memory_before}% → {memory_after}%
        """)
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        await interaction.followup.send("❌ Error during cleanup")

@client.tree.command(name="restart", description="Restart the bot (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def restart(interaction: discord.Interaction):
    """Restart the bot"""
    try:
        await interaction.response.send_message("🔄 Restarting bot...")
        client = BotInstance.get_instance()
        if client:
            await client.cleanup()
            await client.close()
        
        # Re-initialize
        new_client = await initialize()
        
        await interaction.followup.send("✅ Bot restarted successfully")
    except Exception as e:
        logger.error(f"Restart error: {e}")
        await interaction.followup.send("❌ Error during restart")

@client.tree.command(name="stats", description="Show export statistics")
async def stats(interaction: discord.Interaction):
    """Show export statistics"""
    client = BotInstance.get_instance()
    if not client:
        await interaction.response.send_message("❌ Bot not initialized")
        return

    try:
        # Get stats
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent()
        active_exports = len(client._active_exports)
        uptime = time.time() - client._start_time
        
        # Format uptime
        days = int(uptime // (24 * 3600))
        hours = int((uptime % (24 * 3600)) // 3600)
        minutes = int((uptime % 3600) // 60)
        
        stats_text = f"""
        **Bot Statistics**
        🕒 Uptime: {days}d {hours}h {minutes}m
        💾 Memory Usage: {memory.percent}%
        💻 CPU Usage: {cpu_percent}%
        📤 Active Exports: {active_exports}
        """
        await interaction.response.send_message(stats_text)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await interaction.response.send_message("❌ Error getting statistics")

@client.tree.command(name="about", description="Show bot information")
async def about(interaction: discord.Interaction):
    """Show bot information"""
    try:
        embed = discord.Embed(
            title="Discord Message Exporter",
            description="A powerful bot for exporting Discord messages",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Features",
            value="• Excel/CSV export\n• Role filtering\n• Date range\n• Search\n• Attachments\n• Reactions",
            inline=False
        )
        
        embed.add_field(
            name="Commands",
            value="/help - Show commands\n/export - Export messages\n/status - Show status",
            inline=False
        )
        
        embed.set_footer(text="Use /help for detailed command usage")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.error(f"About error: {e}")
        await interaction.response.send_message("❌ Error showing bot information")

@client.tree.command(name="progress", description="Show current export progress")
async def progress(interaction: discord.Interaction):
    """Show progress of current exports"""
    client = BotInstance.get_instance()
    if not client._active_exports:
        await interaction.response.send_message("No active exports")
        return

    try:
        progress_text = "**Active Exports**\n"
        for task in client._active_exports:
            if hasattr(task, 'user_id'):
                user = interaction.guild.get_member(task.user_id)
                user_name = user.display_name if user else "Unknown"
                progress_text += f"• Export by {user_name}\n"
        
        await interaction.response.send_message(progress_text)
    except Exception as e:
        logger.error(f"Progress error: {e}")
        await interaction.response.send_message("❌ Error showing progress")

@client.tree.command(name="commands", description="List all available commands")
async def commands(interaction: discord.Interaction):
    """Show all available commands with descriptions"""
    try:
        embed = discord.Embed(
            title="Available Commands",
            description="All available bot commands and their descriptions",
            color=discord.Color.green()
        )
        
        # Basic Commands
        embed.add_field(
            name="Basic Commands",
            value="""
            `/help` - Show detailed help
            `/test` - Check if bot is working
            `/about` - Show bot information
            `/commands` - Show this list
            """,
            inline=False
        )
        
        # Export Commands
        embed.add_field(
            name="Export Commands",
            value="""
            `/export` - Export messages (with options)
            `/progress` - Show export progress
            `/cancel` - Cancel your exports
            """,
            inline=False
        )
        
        # Status Commands
        embed.add_field(
            name="Status Commands",
            value="""
            `/status` - Show bot status
            `/stats` - Show detailed statistics
            """,
            inline=False
        )
        
        # Admin Commands
        embed.add_field(
            name="Admin Commands",
            value="""
            `/cleanup` - Force cleanup (Admin)
            `/restart` - Restart bot (Admin)
            """,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.error(f"Commands list error: {e}")
        await interaction.response.send_message("❌ Error showing commands list")

@client.tree.command(name="queue", description="Show export queue status")
async def queue(interaction: discord.Interaction):
    """Show current export queue status"""
    client = BotInstance.get_instance()
    if not client._active_exports:
        await interaction.response.send_message("📭 Export queue is empty")
        return

    try:
        queue_text = "**Export Queue Status**\n"
        for i, task in enumerate(client._active_exports, 1):
            if hasattr(task, 'user_id'):
                user = interaction.guild.get_member(task.user_id)
                user_name = user.display_name if user else "Unknown"
                started_time = getattr(task, 'start_time', time.time())
                duration = time.time() - started_time
                queue_text += f"{i}. {user_name} - Running for {int(duration)}s\n"
        
        await interaction.response.send_message(queue_text)
    except Exception as e:
        logger.error(f"Queue error: {e}")
        await interaction.response.send_message("❌ Error showing queue")

@client.tree.command(name="version", description="Show bot version")
async def version(interaction: discord.Interaction):
    """Show bot version information"""
    try:
        embed = discord.Embed(
            title="Discord Message Exporter",
            description=f"Version {VERSION}",
            color=discord.Color.blue()
        )
        
        # System Info
        py_version = sys.version.split()[0]
        discord_version = discord.__version__
        
        embed.add_field(
            name="System Information",
            value=f"""
            • Python: {py_version}
            • Discord.py: {discord_version}
            • OS: {os.name}
            • Platform: {sys.platform}
            """,
            inline=False
        )
        
        # Runtime Info
        memory = psutil.virtual_memory()
        embed.add_field(
            name="Runtime Information",
            value=f"""
            • Memory Usage: {memory.percent}%
            • CPU Cores: {psutil.cpu_count()}
            • Process ID: {os.getpid()}
            """,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.error(f"Version error: {e}")
        await interaction.response.send_message("❌ Error showing version info")

@client.tree.command(name="logs", description="Show recent log entries (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def logs(
    interaction: discord.Interaction, 
    lines: Optional[int] = 10,
    level: Optional[Literal["INFO", "WARNING", "ERROR"]] = "ERROR"
):
    """Show recent log entries"""
    try:
        await interaction.response.defer()
        
        # Read last N*2 lines (to account for filtering)
        log_file = data_dir.get_log_file(LOG_FILE)  # Use data directory path
        log_entries = tail_file(log_file, lines * 2)
        
        if not log_entries:
            await interaction.followup.send("❌ No log file found or file is empty")
            return
            
        # Filter by level
        filtered_lines = [
            line for line in log_entries 
            if f" - {level} - " in line
        ][-lines:]  # Take last N after filtering
        
        if not filtered_lines:
            await interaction.followup.send(f"No {level} level logs found")
            return
            
        # Format and send logs
        formatted_logs = "```\n" + "".join(filtered_lines) + "```"
        
        if len(formatted_logs) > 1900:
            chunks = [formatted_logs[i:i+1900] for i in range(0, len(formatted_logs), 1900)]
            for chunk in chunks:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(formatted_logs)
            
    except Exception as e:
        logger.error(f"Log view error: {e}")
        await interaction.followup.send("❌ Error showing logs")

@client.tree.command(name="detailed-stats", description="Show detailed bot statistics")
@app_commands.checks.has_permissions(administrator=True)
async def detailed_stats(interaction: discord.Interaction):
    """Show detailed bot statistics"""
    try:
        stats = bot_state.get_stats()
        
        embed = discord.Embed(
            title="Bot Statistics",
            description=f"Uptime: {stats['uptime']}",
            color=discord.Color.blue()
        )
        
        # Export Stats
        embed.add_field(
            name="Export Statistics",
            value=f"""
            Total Exports: {stats['total_exports']}
            Successful: {stats['successful_exports']}
            Failed: {stats['failed_exports']}
            Success Rate: {stats['success_rate']}
            Messages Processed: {stats['total_messages']:,}
            """,
            inline=False
        )
        
        # System Status
        memory = psutil.virtual_memory()
        embed.add_field(
            name="System Status",
            value=f"""
            Memory Usage: {memory.percent}%
            Active Exports: {len(client._active_exports)}
            Maintenance Mode: {'🔧 Enabled' if stats['maintenance_mode'] else '✅ Disabled'}
            """,
            inline=False
        )
        
        # Last Error
        if stats['last_error']:
            embed.add_field(
                name="Last Error",
                value=f"```\n{stats['last_error']}\n```",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        await interaction.response.send_message("❌ Error showing statistics")

@client.tree.command(name="maintenance", description="Toggle maintenance mode (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def maintenance(
    interaction: discord.Interaction,
    enable: bool
):
    """Toggle maintenance mode"""
    try:
        bot_state.set_maintenance_mode(enable)
        status = "🔧 enabled" if enable else "✅ disabled"  # Fixed emoji encoding
        
        if enable:
            # Cancel all active exports
            for task in client._active_exports.copy():
                try:
                    task.cancel()
                    logger.info(f"Cancelled export task for user {getattr(task, 'user_id', 'unknown')}")
                except Exception as e:
                    logger.error(f"Error cancelling task: {e}")
            client._active_exports.clear()
            
            # Force cleanup
            clear_memory()
            
        await interaction.response.send_message(f"Maintenance mode {status}")
        logger.info(f"Maintenance mode {status}")
    except Exception as e:
        logger.error(f"Maintenance mode error: {e}")
        await interaction.response.send_message("❌ Error toggling maintenance mode")

# Add after bot initialization
def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    try:
        # Try to get the running loop
        try:
            loop = asyncio.get_running_loop()
            # Schedule shutdown in the running loop
            if not loop.is_closed():
                loop.create_task(shutdown_handler())
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(shutdown_handler())
            loop.close()
    except Exception as e:
        logger.error(f"Error in shutdown handler: {e}")
    finally:
        os._exit(0)

async def shutdown_handler():
    """Handle graceful shutdown"""
    try:
        logger.info("Shutting down bot...")
        client = BotInstance.get_instance()
        if client:
            # Save state first
            bot_state.save_state()
            logger.info("Bot state saved")
            
            # Close session
            if hasattr(client, '_session') and client._session and not client._session.closed:
                await client._session.close()
            
            # Close client
            if not client.is_closed():
                await client.close()
            
            logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

# Update the atexit registration
def cleanup_on_exit():
    """Clean exit handler"""
    try:
        # Try to get the running loop
        try:
            loop = asyncio.get_running_loop()
            if not loop.is_closed():
                loop.run_until_complete(shutdown_handler())
        except RuntimeError:
            # No running loop, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(shutdown_handler())
            loop.close()
    except Exception as e:
        logger.error(f"Exit cleanup error: {e}")
    finally:
        os._exit(0)

atexit.register(cleanup_on_exit)

# 16. RUN BOT
if __name__ == "__main__":
    try:
        # Clean up old logs
        cleanup_old_logs()
        
        # Check directory permissions
        if not data_dir.check_permissions():
            logger.error("Failed to verify directory permissions")
            sys.exit(1)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run bot
        client.run(TOKEN)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)

# Add to utility functions
class MemoryMonitor:
    """Monitor memory usage and trigger cleanup when needed"""
    def __init__(self, 
                 warning_threshold=MEMORY_WARNING_THRESHOLD,
                 critical_threshold=MEMORY_CRITICAL_THRESHOLD,
                 trend_samples=MEMORY_TREND_SAMPLES):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.last_check = time.time()
        self.check_interval = MEMORY_CHECK_INTERVAL  # Use config value
        self.trend_samples = trend_samples
        self.memory_history = []

    def check(self) -> tuple[bool, str]:
        """
        Check memory usage and track trends
        Returns: (is_ok, message)
        """
        current_time = time.time()
        if current_time - self.last_check < self.check_interval:
            return True, ""
            
        self.last_check = current_time
        memory = psutil.virtual_memory()
        
        # Add to history and keep last N samples
        self.memory_history.append(memory.percent)
        if len(self.memory_history) > self.trend_samples:
            self.memory_history.pop(0)
        
        # Calculate trend
        trend_increasing = len(self.memory_history) > 1 and all(
            self.memory_history[i] < self.memory_history[i+1] 
            for i in range(len(self.memory_history)-1)
        )
        
        message = ""
        if memory.percent >= self.critical_threshold:
            clear_memory()
            message = f"❌ Critical memory usage: {memory.percent}%"
            return False, message
        elif memory.percent >= self.warning_threshold:
            message = f"⚠️ High memory usage: {memory.percent}%"
            if trend_increasing:
                message += " (Trending up ↗️)"
                clear_memory()  # Preemptive cleanup
            return True, message
        elif trend_increasing and memory.percent >= self.warning_threshold * 0.8:
            message = f"ℹ️ Memory usage trending up: {memory.percent}%"
            
        return True, message

# Initialize memory monitor
memory_monitor = MemoryMonitor()

# Add to utility functions
def tail_file(filename: str, n: int) -> List[str]:
    """Read last n lines from file efficiently"""
    try:
        with open(filename, 'rb') as f:
            # Get file size
            f.seek(0, 2)
            size = f.tell()
            
            # Empty file
            if size == 0:
                return []
                
            # Read blocks from end
            block_size = 1024
            block_count = -1
            lines = []
            
            while len(lines) < n:
                seek_size = block_count * block_size
                if -seek_size > size:
                    # Reached start of file
                    f.seek(0)
                    lines = f.readlines()[-n:]
                    break
                    
                f.seek(seek_size, 2)
                lines = f.readlines()
                block_count -= 1
            
            return [line.decode('utf-8', errors='replace') for line in lines[-n:]]
            
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return []

# Add to utility functions
class StateFileManager:
    """Manage bot state file with proper permissions and backup"""
    def __init__(self, filename: str, backup_count: int = 3):
        self.filename = filename
        self.backup_count = backup_count
        self.backup_suffix = '.backup'
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure state directory exists with proper permissions"""
        directory = os.path.dirname(self.filename) or '.'
        if not os.path.exists(directory):
            os.makedirs(directory, mode=DIR_PERMISSION)  # Use config value
        else:
            os.chmod(directory, DIR_PERMISSION)  # Use config value

    def _create_backup(self):
        """Create backup of state file"""
        if os.path.exists(self.filename):
            # Rotate backups
            for i in range(self.backup_count - 1, 0, -1):
                old = f"{self.filename}{self.backup_suffix}.{i}"
                new = f"{self.filename}{self.backup_suffix}.{i+1}"
                if os.path.exists(old):
                    if os.path.exists(new):
                        os.remove(new)
                    os.rename(old, new)
            
            # Create new backup
            backup = f"{self.filename}{self.backup_suffix}.1"
            if os.path.exists(backup):
                os.remove(backup)
            import shutil
            shutil.copy2(self.filename, backup)

    def save(self, data: dict):
        """Save data to state file with backup"""
        try:
            self._create_backup()
            temp_file = f"{self.filename}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, self.filename)  # Atomic write
            os.chmod(self.filename, FILE_PERMISSION)  # Use config value
            return True
        except Exception as e:
            logger.error(f"Error saving state file: {e}")
            return False

    def load(self) -> Optional[dict]:
        """Load data from state file or latest backup"""
        files_to_try = [
            self.filename,
            *[f"{self.filename}{self.backup_suffix}.{i}" 
              for i in range(1, self.backup_count + 1)]
        ]
        for file in files_to_try:
            try:
                if os.path.exists(file):
                    with open(file, 'r') as f:
                        data = json.load(f)
                    if file != self.filename:
                        logger.warning(f"Loaded state from backup: {file}")
                    return data
            except Exception as e:
                logger.error(f"Error loading state from {file}: {e}")
        
        return None

async def initialize():
    """Initialize bot with fresh state"""
    try:
        client = ExporterBot()
        BotInstance.set_instance(client)
        
        # Initialize any async resources
        client._session = aiohttp.ClientSession()
        
        # Clear memory and check permissions
        clear_memory()
        if not data_dir.check_permissions():
            raise ValueError("Failed to verify directory permissions")
            
        return client
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

# Add after imports
def handle_railway_error(error_msg: str):
    """Handle Railway-specific errors"""
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("\n=== Railway Error ===")
        print(error_msg)
        print("Current environment:")
        print(f"- Python: {sys.version}")
        print(f"- Working dir: {os.getcwd()}")
        print(f"- Files: {os.listdir()}")
        print("===================\n")
    sys.exit(1)
