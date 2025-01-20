import asyncio
import signal
import sys
import logging

# Add at the very start of the file, after imports
def check_requirements():
    """Check if all required packages are installed"""
    try:
        import discord
        import pandas
        import dotenv
        import openpyxl
        import psutil
        import aiohttp
        print("✅ All required packages found")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {str(e)}")
        print("Please run: pip install -r requirements.txt")
        return False

# Add in the main block
if __name__ == "__main__":
    try:
        if not check_requirements():
            sys.exit(1)
            
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