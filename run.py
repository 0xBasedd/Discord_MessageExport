#!/usr/bin/env python3
import os
import sys

def main():
    # Check if we're running on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("\n=== Railway Startup ===")
        print(f"Working directory: {os.getcwd()}")
        print(f"Files available: {os.listdir()}")
        
        # Ensure the bot file exists
        if not os.path.exists('Discord_Message_exporter.py'):
            print("ERROR: Discord_Message_exporter.py not found!")
            sys.exit(1)
        
        # Import and run the bot
        try:
            import Discord_Message_exporter
        except Exception as e:
            print(f"ERROR: Failed to import bot: {e}")
            sys.exit(1)
    else:
        # Local development
        import Discord_Message_exporter

if __name__ == "__main__":
    main() 