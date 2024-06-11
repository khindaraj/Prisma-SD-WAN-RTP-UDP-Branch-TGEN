import subprocess
import os
import time
from scapy.all import sniff, get_if_list  # Requires scapy library (install using pip3 install scapy)

# Define Git repository URL
script_repo_url = "https://github.com/khindaraj/Prisma-SD-WAN-RTP-UDP-Branch-TGEN.git"

# Set working directory (replace with your actual directory)
working_directory = "/home/lab-user/scripts"

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
    """Downloads the traffic generator scripts from the Git repository."""
    script_directory = get_script_directory()
    if not os.path.exists(script_directory):
        os.makedirs(script_directory)  # Create the directory if it doesn't exist
    subprocess.run(["git", "-C", script_directory, "pull"])  # Update existing directory
    if not os.path.isdir(script_directory):
        subprocess.run(["git", "clone", script_repo_url, script_directory])
    print("Scripts downloaded successfully.")


# Install Python libraries (if not already installed)
def install_dependencies():
    if not os.path.exists("/usr/bin/python3"):
        subprocess.run(["apt", "get", "install", "-y", "python3"])
    if not os.path.exists("/usr/bin/pip3"):
        subprocess.run(["apt", "get", "install", "-y", "python3-pip"])
    subprocess.run(["pip3", "install", "scapy", "curl"])  # Install scapy and curl


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
    script_directory = get_script_directory()
    service_content = f"""[Unit]
Description=Check webpos.sasedemo.net entry in /etc/hosts
Requires=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'if ! grep -q "webpos.sasedemo.net" /etc/hosts; then exit 1; fi'
StandardOutput=syslog
StandardError=syslog
SyslogLevel=info

[Install]
WantedBy=multi-user.target
"""
    with open(f"{script_directory}/check_hosts_entry.service", "w") as f:
        f.write(service_content)
    subprocess.run(["systemctl", "daemon-reload"])


def create_rtp_service(script_dir, target_host, username="your_username"):
  """
  Creates a systemd service file for RTP traffic generation with logging.

  Args:
      script_dir (str): Path to the directory containing the script (rtp.sh).
      target_host (str): Target host for the RTP traffic.
      username (str, optional): Username to run the service as. Defaults to "your_username".
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
Requires=network-online.target
After=check_hosts_entry.service

[Service]
Type=simple
User={username}
WorkingDirectory={script_dir}
ExecStart=/bin/bash -c '{script_path} {target_host} &'
StandardOutput=syslog
StandardError=syslog
SyslogLevel=info

[Install]
WantedBy=multi-user.target
"""

  # Create the service file
  service_file = os.path.join(script_dir, "rtp.service")
  with open(service_file, "w") as f:
    f.write(service_content)

  # Reload systemd daemon (assuming appropriate permissions)
  subprocess.run(["systemctl", "daemon-reload"])

def create_webpos_service(script_dir, target_host):
  """
  Creates a systemd service file for custom app traffic generation with logging.

  Args:
      script_dir (str): Path to the directory containing the script (webpos.sh).
      target_host (str): Target host for the custom app traffic.
      username (str, optional): Username to run the service as. Defaults to "your_username".
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
Requires=network-online.target
After=check_hosts_entry.service

[Service]
Type=simple
WorkingDirectory={script_dir}
ExecStart=/bin/bash -c '{script_path} {target_host} &'
StandardOutput=syslog
StandardError=syslog
SyslogLevel=info

[Install]
WantedBy=multi-user.target
"""

  # Create the service file
  service_file = os.path.join(script_dir, "webpos.service")
  with open(service_file, "w") as f:
    f.write(service_content)

  # Reload systemd daemon (assuming appropriate permissions)
  subprocess.run(["systemctl", "daemon-reload"])


def main():
    """Main function for script execution."""
    
    script_directory = get_script_directory()

    target_host = "webpos.sadedemo.net"
    

    # Download scripts (replace with your actual implementation)
    download_scripts()

    # Install dependencies (replace with your actual implementation)
    install_dependencies()
    
    os.chdir(working_directory)  # Change the current working directory

    # Make downloaded scripts executable in all subdirectories
    make_scripts_executable(working_directory)  

    # Create systemd service files
    create_check_hosts_service()
    create_rtp_service(script_directory, target_host)
    create_webpos_service(script_directory, target_host)

    # Enable and start systemd services
    subprocess.run(["systemctl", "enable", "check_hosts_entry.service"])
    subprocess.run(["systemctl", "start", "check_hosts_entry.service"])

    # Wait for 'webpos.sadedemo.net' entry to be missing in /etc/hosts
    #while check_hosts_entry("webpos.sasedemo.net"):
        #print("Waiting for 'webpos.sadedemo.net' entry to be removed from /etc/hosts...")
        #time.sleep(10)  # Adjust wait time as needed (seconds)

    # Start traffic generator services after successful check
    subprocess.run(["systemctl", "start", "rtp.service"])
    subprocess.run(["systemctl", "start", "webpos.service"])

    print("Scripts downloaded, dependencies installed, and systemd services started.")

if __name__ == "__main__":
    main()