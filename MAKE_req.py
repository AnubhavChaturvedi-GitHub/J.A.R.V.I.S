import subprocess

def list_installed_packages():
    try:
        # Get the list of installed packages
        installed_packages = subprocess.check_output(['pip', 'freeze']).decode('utf-8')
        
        # Write the list to requirements.txt
        with open('requirements.txt', 'w') as file:
            file.write(installed_packages)
            
        print("The installed packages have been listed in requirements.txt")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while listing the packages: {e}")

if __name__ == "__main__":
    list_installed_packages()