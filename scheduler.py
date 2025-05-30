#!/usr/bin/env python3
"""
Scheduler for Bislett monitor - runs checks 10 times per day
"""

import time
import schedule
import subprocess
import sys
import os
from datetime import datetime

def run_monitor():
    """Run the monitoring script"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running Bislett monitor...")
    try:
        result = subprocess.run([sys.executable, "bislett_monitor.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Monitor script failed: {result.stderr}")
        else:
            print(f"Monitor completed successfully")
    except Exception as e:
        print(f"Error running monitor: {e}")

def main():
    """Set up schedule to run 10 times per day"""
    print("Setting up Bislett 24-hour monitor schedule...")
    print("Will check 10 times per day at:")
    
    # Schedule 10 times throughout the day
    times = ["06:00", "08:30", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00", "23:30"]
    
    for time_str in times:
        schedule.every().day.at(time_str).do(run_monitor)
        print(f"  - {time_str}")
    
    print("\nScheduler started. Press Ctrl+C to stop.")
    print("Monitor logs will be saved to bislett_monitor.log")
    
    # Run once immediately to test
    print("\nRunning initial check...")
    run_monitor()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped.")

if __name__ == "__main__":
    main()