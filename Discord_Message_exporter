# 1. IMPORTS
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
from typing import Optional, Tuple, List, Literal
import aiohttp
import logging
from discord import app_commands
from discord.ext import commands
import signal

# 2. VERSION
VERSION = "1.0.0"

# 3. ENVIRONMENT SETUP
def check_env_file():
    """Check if token is available"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: Discord token not found!")
        print("Make sure DISCORD_TOKEN is set in your environment variables")
        sys.exit(1)
    return token

# Load environment variables
load_dotenv(override=True)
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    TOKEN = check_env_file()
print("Token loaded successfully (token hidden for security)")

# 4. LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_exporter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 5. CLASS DEFINITIONS
class ProgressTracker:
    def __init__(self, message, total=None):
        self.message = message
        self.count = 0
        self.total = total
        self.last_update = time.time()
        self.update_interval = 2
        self.batch_size = 100

    def _generate_progress_bar(self, progress):
        length = 20
        filled = int(length * progress / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f'[{bar}]'

    async def update(self, force=False):
        try:
            self.count += 1
            current_time = time.time()
            should_update = force or (
                self.count % self.batch_size == 0 and 
                current_time - self.last_update >= self.update_interval
            )
            
            if should_update:
                self.last_update = current_time
                try:
                    if self.total:
                        progress = (self.count / self.total) * 100
                        bar = self._generate_progress_bar(progress)
                        await self.message.edit(
                            content=f"Progress: {self.count:,}/{self.total:,} messages {bar} ({progress:.1f}%)"
                        )
                    else:
                        await self.message.edit(
                            content=f"Progress: {self.count:,} messages processed..."
                        )
                except discord.errors.HTTPException as e:
                    logger.error(f"Failed to update progress: {e}")
        except Exception as e:
            logger.error(f"Progress update error: {e}")

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
        self._export_cooldown = 5
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

# 6. UTILITY FUNCTIONS
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

# 7. DECORATORS
def handle_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except discord.errors.Forbidden as e:
            logger.error(f"Permission error: {e}")
            if hasattr(args[0], 'channel'):
                await args[0].channel.send("❌ I don't have the required permissions!")
        except discord.errors.HTTPException as e:
            logger.error(f"Discord API error: {e}")
            if hasattr(args[0], 'channel'):
                await args[0].channel.send("❌ Discord API error. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if hasattr(args[0], 'channel'):
                await args[0].channel.send(f"❌ An error occurred: {str(e)}")
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

def command_cooldown(cooldown_seconds=5):
    def decorator(func):
        last_used = {}
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            user_id = interaction.user.id
            current_time = time.time()
            if user_id in last_used and current_time - last_used[user_id] < cooldown_seconds:
                remaining = int(cooldown_seconds - (current_time - last_used[user_id]))
                await interaction.response.send_message(
                    f"⏳ Please wait {remaining} seconds before using this command again.",
                    ephemeral=True
                )
                return
            last_used[user_id] = current_time
            return await func(interaction, *args, **kwargs)
        return wrapper
    return decorator

# 8. HELPER FUNCTIONS
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

async def create_message_data(msg, data_options):
    """Create message data with selected options"""
    try:
        message_data = {
            'Author': str(msg.author),
            'Content': msg.content,
            'Timestamp': msg.created_at.isoformat()
        }

        if data_options:
            options = [int(x.strip()) for x in data_options.split(',') if x.strip().isdigit() and 0 < int(x.strip()) < 7]
            
            if 1 in options:  # Attachments
                message_data['Attachments'] = ', '.join([a.url for a in msg.attachments])
            
            if 2 in options:  # Reactions
                reactions = [f"{r.emoji}: {r.count}" for r in msg.reactions]
                message_data['Reactions'] = ', '.join(reactions)
            
            if 3 in options:  # Reply References
                if msg.reference and isinstance(msg.reference.resolved, discord.Message):
                    message_data['Replying_To'] = f"{msg.reference.resolved.author}: {msg.reference.resolved.content[:100]}..."
                else:
                    message_data['Replying_To'] = ''
            
            if 4 in options:  # Edits
                message_data['Edited_At'] = msg.edited_at.isoformat() if msg.edited_at else ''
            
            if 5 in options:  # Embeds
                embeds_data = []
                for embed in msg.embeds:
                    embed_info = {
                        'title': embed.title,
                        'description': embed.description,
                        'url': embed.url
                    }
                    embeds_data.append(str(embed_info))
                message_data['Embeds'] = ' | '.join(embeds_data) if embeds_data else ''
            
            if 6 in options:  # Pinned
                message_data['Pinned'] = str(msg.pinned)

        return message_data
    except Exception as e:
        logger.error(f"Message data creation error: {e}")
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
async def save_and_send_messages(messages, channel_name, suffix, is_csv, chunk_size, original_message):
    with SafeBuffer() as safe_buffer:
        try:
            if not messages:
                return

            # Add file size check before processing
            estimated_size = len(str(messages)) / 1024  # Rough size estimate in KB
            if estimated_size > 7000:  # Close to Discord's 8MB limit
                await original_message.channel.send("⚠️ Large file detected, using compression...")
            
            # Clean message data
            cleaned_messages = []
            for msg in messages:
                try:
                    # Remove invalid characters and normalize data
                    msg['Content'] = msg['Content'].replace('\x00', '').strip()
                    msg['Author'] = msg['Author'].replace('\x00', '').strip()
                    cleaned_messages.append(msg)
                except Exception as e:
                    logger.error(f"Message cleaning error: {e}")
                    continue

            file_extension = 'csv' if is_csv else 'xlsx'
            base_filename = f'{channel_name}_messages_{suffix}.{file_extension}'
            zip_filename = f'{channel_name}_messages_{suffix}.zip'
            
            # Create ZIP file in memory with error handling
            zip_buffer = safe_buffer.create_buffer()
            try:
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    df = pd.DataFrame(cleaned_messages)
                    if is_csv:
                        csv_buffer = safe_buffer.create_buffer(io.StringIO)
                        df.to_csv(csv_buffer, index=False, encoding='utf-8', errors='replace')
                        zip_file.writestr(base_filename, csv_buffer.getvalue())
                    else:
                        excel_buffer = safe_buffer.create_buffer(io.BytesIO)
                        df.to_excel(excel_buffer, index=False, engine='openpyxl')
                        zip_file.writestr(base_filename, excel_buffer.getvalue())
            except Exception as e:
                logger.error(f"Compression error: {e}")
                raise

            # Check file size before sending
            zip_buffer.seek(0, os.SEEK_END)
            size = zip_buffer.tell()
            zip_buffer.seek(0)
            
            if size > 8 * 1024 * 1024:  # 8MB
                raise ValueError("File too large for Discord upload")

            await original_message.channel.send(
                f'Extracted {len(cleaned_messages)} messages from "{channel_name}" (compressed).',
                file=discord.File(zip_buffer, filename=zip_filename)
            )
            
        except discord.errors.HTTPException as e:
            error_msg = "File too large. Try reducing the chunk size or using CSV format." if e.code == 40005 else f"Discord error: {str(e)}"
            await original_message.channel.send(f"❌ {error_msg}")
            logger.error(f"HTTP error: {e}")
        except Exception as e:
            await original_message.channel.send(f"❌ Error saving/sending file: {str(e)}")
            logger.error(f"Save/send error: {e}", exc_info=True)
            raise

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
        
        # Estimate total based on sample
        total_seconds = (before or datetime.now()) - (after or channel.created_at)
        sample_seconds = timedelta(days=7)
        ratio = total_seconds / sample_seconds
        estimated_total = int(count * ratio)
        return min(estimated_total, 1000000)  # Cap at 1M for safety
    except Exception as e:
        logger.error(f"Error estimating messages: {e}")
        return None

# 9. BOT INITIALIZATION
client = None

# Initialize bot after all definitions
async def initialize():
    """Async initialization"""
    try:
        client = ExporterBot()
        BotInstance.set_instance(client)
        
        # Initialize any async resources
        client._session = aiohttp.ClientSession()
        
        return client
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

# 10. EVENT HANDLERS
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

# 11. SLASH COMMANDS
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
    try:
        # Create export task and track user
        task = asyncio.current_task()
        task.user_id = interaction.user.id
        task.start_time = time.time()  # Add timing
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
        
        # Initialize progress tracker
        progress = ProgressTracker(message)
        
        # Initialize chunker
        chunker = MessageChunker(chunk_size)
        
        # Process messages
        async for msg in channel.history(limit=None):
            await progress.update()
            
            if not await process_message_filters(msg, role, category, channel, search, date_from, date_to):
                continue

            message_data = await create_message_data(msg, data_options)
            if message_data:
                await chunker.add_message(message_data, channel.name, format == "csv", message)

        # Save any remaining messages
        await chunker.finish(channel.name, format == "csv", message)

    except Exception as e:
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
        BotInstance.set_instance(new_client)
        
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
    if not client:
        await interaction.response.send_message("❌ Bot not initialized")
        return

    try:
        if not client._active_exports:
            await interaction.response.send_message("No active exports")
            return
            
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
    if not client:
        await interaction.response.send_message("❌ Bot not initialized")
        return

    try:
        if not client._active_exports:
            await interaction.response.send_message("📭 Export queue is empty")
            return
            
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

# Add after bot initialization
def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutdown signal received")
    if client:
        logger.info("Cleaning up...")
        asyncio.run_coroutine_threadsafe(client.close(), client.loop)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 12. RUN BOT
if __name__ == "__main__":
    try:
        # Initialize bot
        client = asyncio.run(initialize())
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run bot
        client.run(TOKEN)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)
