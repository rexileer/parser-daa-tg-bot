import os
import sys
import argparse

def main():
    """
    Run the Redis to DB synchronization task
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run Redis to DB synchronization task')
    parser.add_argument('--cleanup-days', type=int, default=7,
                        help='Number of days to keep ads before deletion (default: 7)')
    parser.add_argument('--interval', type=int, default=60,
                        help='Interval in seconds between task runs (default: 60)')
    args = parser.parse_args()
    
    print(f"Starting Redis to DB synchronization task with cleanup_days={args.cleanup_days}, interval={args.interval}s...")
    
    # Activate the virtual environment if needed
    if os.name == 'nt':  # Windows
        activate_script = os.path.join('.venv', 'Scripts', 'activate')
    else:  # Unix/Linux
        activate_script = os.path.join('.venv', 'bin', 'activate')
    
    # Run the Redis to DB synchronization task
    if os.name == 'nt':  # Windows
        os.system(f"{activate_script} && python manage.py run_ads_tasks --cleanup-days={args.cleanup_days} --interval={args.interval}")
    else:  # Unix/Linux
        os.system(f"source {activate_script} && python manage.py run_ads_tasks --cleanup-days={args.cleanup_days} --interval={args.interval}")
    
if __name__ == "__main__":
    main() 