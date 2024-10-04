#!/usr/bin/env python3
import os
import subprocess
import sys

netplan_file = "/etc/netplan/50-cloud-init.yaml"

def update_netplan_config():
    """Updates the netplan configuration to disable route assignments via DHCP."""
    netplan_content = """
network:
  ethernets:
    ens192:
      addresses: []
      dhcp-identifier: mac
      dhcp4: true
      dhcp4-overrides:
        use-routes: false
    ens224:
      addresses: []
      dhcp-identifier: mac
      dhcp4: true
  version: 2
"""
    try:
        # Backup the current netplan file
        if os.path.exists(netplan_file):
            backup_file = netplan_file + ".bak"
            os.rename(netplan_file, backup_file)
            print(f"Backup created: {backup_file}")

        # Write the new netplan configuration
        with open(netplan_file, "w") as f:
            f.write(netplan_content)
        print(f"Netplan configuration updated: {netplan_file}")

        # Apply the new netplan configuration
        subprocess.run(["sudo", "netplan", "apply"], check=True)
        print("Netplan configuration applied successfully.")
    except Exception as e:
        print(f"Failed to update or apply netplan configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_netplan_config()
