import os
import sys
import subprocess

def main():
    """
    Run the Redis to DB synchronization task
    """
    print("Starting Redis to DB synchronization task...")
    
    # Activate the virtual environment if needed
    if os.name == 'nt':  # Windows
        activate_script = os.path.join('.venv', 'Scripts', 'activate')
    else:  # Unix/Linux
        activate_script = os.path.join('.venv', 'bin', 'activate')
    
    # Run the Redis to DB synchronization task
    if os.name == 'nt':  # Windows
        os.system(f"{activate_script} && python manage.py run_ads_tasks")
    else:  # Unix/Linux
        os.system(f"source {activate_script} && python manage.py run_ads_tasks")
    
if __name__ == "__main__":
    main() 