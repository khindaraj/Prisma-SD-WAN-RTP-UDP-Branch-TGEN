import subprocess
import os
import time

# Define Git repository URL
script_repo_url = "http://github.com/khindaraj/Prisma-SD-WAN-RTP-UDP-Branch-TGEN.git"

# Set working directory (replace with your actual directory)
working_directory = "/home/lab-user/scripts"

def run_command(command):
    """Runs a shell command and handles errors."""
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e.stderr.decode()}")
        exit(1)

def make_scripts_executable(directory):
    """
    Makes downloaded .sh and .py files in the specified directory and its subdirectories executable.

    Args:
        directory: The directory to check for downloaded files.
    """
    for root, _, files in os.walk(directory):
        for filename in files:
            # Get the full path of the file
            filepath = os.path.join(root, filename)
            # Check if it's a file and the extension is .sh or .py
            if os.path.isfile(filepath) and (filename.endswith(".sh") or filename.endswith(".py")):
                # Make the file executable
                os.chmod(filepath, 0o755)  # Grant execute permission for owner, group, and others
                print(f"Made '{filepath}' executable")

# Manage script repository directory based on Git URL
def get_script_directory():
    """Returns the script directory based on the Git repository URL."""
    script_directory = os.path.join(working_directory, script_repo_url.split("/")[-1].split(".")[0])
    return script_directory

# Download or update scripts from the Git repository
def download_scripts():
    """Downloads the traffic generator scripts from the Git repository.

    This function first checks if the script directory exists. If not, it creates it.
    Then, it attempts to update an existing Git repository in the directory using `git pull`.
    If there's no local repository, it clones the repository from the provided URL using `git clone`.

    Raises:
        RuntimeError: If there's an error during download or cloning.
    """
    script_directory = get_script_directory()
    
    if not os.path.exists(script_directory):
        os.makedirs(script_directory)  # Create the directory if it doesn't exist

    try:
        # Attempt to update existing repository (if present)
        subprocess.run(["git", "-C", script_directory, "pull"], check=True)
        print("Scripts updated successfully.")
    except subprocess.CalledProcessError:
        # If update fails, assume no repository exists and clone
        print("No local repository found. Cloning scripts...")
        try:
            subprocess.run(["git", "clone", script_repo_url, script_directory], check=True)
            print("Scripts downloaded successfully.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error downloading scripts: {e}") from e

# Install Python libraries (if not already installed)
def install_dependencies():
    if not os.path.exists("/usr/bin/python3"):
        run_command("sudo apt-get install -y python3")
    if not os.path.exists("/usr/bin/pip3"):
        run_command("sudo apt-get install -y python3-pip")
    run_command("sudo pip3 install scapy --break-system-packages")  # Install scapy and curl

# Check if webpos.sasedemo.net entry exists in /etc/hosts
def check_hosts_entry(hostname):
    gateway = "192.168.1.204"  # Assuming you have the gateway IP
    entry = f"{gateway} {hostname}\n"
    hosts_file = "/etc/hosts"
    with open(hosts_file, "r") as f:
        lines = f.readlines()
    return entry not in lines  # Return True if entry is missing

# Create systemd service file for check_hosts_entry
def create_check_hosts_service():
    service_content = f"""[Unit]
Description=Check webpos.sasedemo.net entry in /etc/hosts
Requires=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'until grep -q "webpos.sasedemo.net" /etc/hosts; do sleep 10; done'
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogLevel=info

[Install]
WantedBy=multi-user.target
"""
    with open(f"/etc/systemd/system/check_hosts_entry.service", "w") as f:
        f.write(service_content)
    run_command("sudo systemctl daemon-reload")

def create_rtp_service(script_dir, target_host, username="lab-user"):
    """
    Creates a systemd service file for RTP traffic generation with logging.

    Args:
        script_dir (str): Path to the directory containing the script (rtp.sh).
        target_host (str): Target host for the RTP traffic.
        username (str, optional): Username to run the service as. Defaults to "lab-user".
    """

    # Check if script directory exists
    if not os.path.isdir(script_dir):
        raise ValueError(f"Script directory '{script_dir}' does not exist.")

    # Construct the full path to the script
    script_path = os.path.join(script_dir, "rtp.sh")

    # Check if script exists
    if not os.path.isfile(script_path):
        raise ValueError(f"Script '{script_path}' not found.")

    # Service content with f-strings and variable interpolation
    service_content = f"""[Unit]
Description=RTP Traffic Generator - Target: {target_host}
Requires=check_hosts_entry.service
After=check_hosts_entry.service

[Service]
Type=simple
User={username}
ExecStart=/bin/bash -c 'until systemctl is-active --quiet check_hosts_entry.service; do sleep 10; done && {script_path} {target_host} &'
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogLevel=info

[Install]
WantedBy=multi-user.target
"""

    # Create the service file
    service_file = f"/etc/systemd/system/rtp.service"
    with open(service_file, "w") as f:
        f.write(service_content)

    # Reload systemd daemon
    run_command("sudo systemctl daemon-reload")

def create_webpos_service(script_dir, target_host, username="lab-user"):
    """
    Creates a systemd service file for custom app traffic generation with logging.

    Args:
        script_dir (str): Path to the directory containing the script (webpos.sh).
        target_host (str): Target host for the custom app traffic.
        username (str, optional): Username to run the service as. Defaults to "lab-user".
    """

    # Check if script directory exists
    if not os.path.isdir(script_dir):
        raise ValueError(f"Script directory '{script_dir}' does not exist.")

    # Construct the full path to the script
    script_path = os.path.join(script_dir, "webpos.sh")

    # Check if script exists
    if not os.path.isfile(script_path):
        raise ValueError(f"Script '{script_path}' not found.")

    # Service content with f-strings and variable interpolation
    service_content = f"""[Unit]
Description=Custom App Traffic Generator - Target: {target_host}
Requires=check_hosts_entry.service
After=check_hosts_entry.service

[Service]
Type=simple
User={username}
ExecStart=/bin/bash -c 'until systemctl is-active --quiet check_hosts_entry.service; do sleep 10; done && {script_path} {target_host} &'
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogLevel=info

[Install]
WantedBy=multi-user.target
"""

    # Create the service file
    service_file = f"/etc/systemd/system/webpos.service"
    with open(service_file, "w") as f:
        f.write(service_content)

    # Reload systemd daemon
    run_command("sudo systemctl daemon-reload")

def check_service_status(service_name):
    """Checks the status of a systemd service."""
    print(f"Checking status of service '{service_name}'...")
    try:
        result = subprocess.run(f"sudo systemctl status {service_name}", check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error checking service status: {service_name}\n{e.stderr.decode()}")

def main():
    """Main function for script execution."""

    if os.geteuid() != 0:
        print("This script must be run as root. Please use 'sudo'.")
        exit(1)
    
    script_directory = get_script_directory()

    target_host = "webpos.sasedemo.net"
    
    # Download scripts
    download_scripts()

    # Install dependencies
    install_dependencies()
    
    os.chdir(working_directory)  # Change the current working directory

    # Make downloaded scripts executable in all subdirectories
    make_scripts_executable(working_directory)  

    # Create systemd service files
    create_check_hosts_service()
    create_rtp_service(script_directory, target_host)
    create_webpos_service(script_directory, target_host)

    # Enable and start systemd services
    run_command("sudo systemctl enable check_hosts_entry.service")
    run_command("sudo systemctl start check_hosts_entry.service")

    # Wait for 'webpos.sadedemo.net' entry to be missing in /etc/hosts
    time.sleep(5)  # Allow some time for the check_hosts_entry.service to run

    # Start traffic generator services after successful check
    if subprocess.run("systemctl is-active --quiet check_hosts_entry.service", shell=True).returncode == 0:
        print("check_hosts_entry.service is active, starting other services...")
        run_command("sudo systemctl enable rtp.service")
        run_command("sudo systemctl start rtp.service")
        run_command("sudo systemctl enable webpos.service")
        run_command("sudo systemctl start webpos.service")
    else:
        print("check_hosts_entry.service failed, not starting other services.")

    # Check the status of the services
    check_service_status("check_hosts_entry.service")
    check_service_status("rtp.service")
    check_service_status("webpos.service")

    print("Scripts downloaded, dependencies installed, and systemd services started.")

if __name__ == "__main__":
    main()
