import os
import sys
import subprocess

def main():
    """
    Run the Django development server
    """
    print("Starting Django development server...")
    
    # Activate the virtual environment if needed
    if os.name == 'nt':  # Windows
        activate_script = os.path.join('.venv', 'Scripts', 'activate')
    else:  # Unix/Linux
        activate_script = os.path.join('.venv', 'bin', 'activate')
    
    # Run the Django development server
    if os.name == 'nt':  # Windows
        os.system(f"{activate_script} && python manage.py runserver")
    else:  # Unix/Linux
        os.system(f"source {activate_script} && python manage.py runserver")
    
if __name__ == "__main__":
    main() 