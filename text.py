import subprocess

def save_installed_packages(file_path='requirements.txt'):
    try:
        # Get the list of installed packages
        result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE)
        installed_packages = result.stdout.decode('utf-8')

        # Save the list to the requirements.txt file
        with open(file_path, 'w') as file:
            file.write(installed_packages)

        print(f"Installed packages have been saved to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
save_installed_packages()
