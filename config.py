"""Configuration settings for Discord Message Exporter Bot"""

# Bot Settings
VERSION = "1.0.0"
COMMAND_PREFIX = "/"
DEFAULT_CHUNK_SIZE = 10000
EXPORT_COOLDOWN = 5  # seconds between exports
MAINTENANCE_MODE = False

# Memory Settings
MEMORY_WARNING_THRESHOLD = 70  # percentage
MEMORY_CRITICAL_THRESHOLD = 85  # percentage
MEMORY_CHECK_INTERVAL = 60  # seconds
MEMORY_TREND_SAMPLES = 5

# File Settings
DATA_DIR = "data"
LOG_FILE = "discord_exporter.log"
STATE_FILE = "bot_state.json"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 5
LOG_RETENTION_DAYS = 30

# Export Settings
MAX_MESSAGES_EXCEL = 100000
MAX_MESSAGES_CSV = 500000
RATE_LIMIT_DELAY = 0.25  # seconds
MAX_RETRIES = 5
TIMEOUT = 30.0  # seconds

# Security Settings
DIR_PERMISSION = 0o700
FILE_PERMISSION = 0o600 