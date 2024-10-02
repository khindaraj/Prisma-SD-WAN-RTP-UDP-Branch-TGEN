"""
This Python script generates and transmits RTP traffic streams to a specified destination. 

**Key Features:**

* **Hostname Resolution:** Accepts a hostname or IP address for the destination and attempts to resolve the hostname if necessary.
* **Configurable Traffic Parameters:** Allows customization of source and destination ports, minimum and maximum packet count, and source IP address (if desired).
* **Random Payload Generation:** Generates random data for the UDP payload within each RTP packet.
* **Scapy Library Integration:** Leverages the Scapy library for efficient packet crafting and transmission.

"""

#!/usr/bin/env python3

import time
import argparse
import random
import logging
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.layers.rtp import RTP
from scapy.packet import Raw
from scapy.sendrecv import send, sendp
from socket import gethostbyname

logging.getLogger("scapy").setLevel(1)

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser()

    # Allow Controller modification and debug level sets.
    binding_group = parser.add_argument_group('Binding', 'These options change how traffic is bound/sent')
    binding_group.add_argument("--destination-host", "-dh", "-H", help="Destination hostname or IP for the RTP stream",
                               required=True)
    binding_group.add_argument("--destination-port", "-dport",
                               help="Destination port for the RTP stream (Default 6100)", type=int,
                               default=6100)
    binding_group.add_argument("--source-ip", "-sip", "-S", help="Source IP for the RTP stream. If not specified, "
                                                                 "the kernel will auto-select.",
                               type=str, default=None)
    binding_group.add_argument("--source-port", "-sport",
                               help="Source port for the RTP stream. If not specified, "
                                    "the kernel will auto-select.", type=int,
                               default=0)
    binding_group.add_argument("--source-interface",
                               help="Source interface RTP stream. If not specified, "
                                    "the kernel will auto-select.", type=str,
                               default=None)
    options_group = parser.add_argument_group('Options', "Configurable options for traffic sending.")
    options_group.add_argument("--min-count", "-C", help="Minimum number of packets to send (Default 4500)",
                               type=int, default=4500)
    options_group.add_argument("--max-count", help="Maximum number of packets to send (Default 90000)",
                               type=int, default=90000)

    args = vars(parser.parse_args())

    print("Setting up RTP Packets")
    udp_payload = []
    # 212 = 240 - IP headler len  - UDP header len - RTP header length ==> 240 - 20 - 8 - 12
    for i in range(200):
        #tmp = bytes("{:02x}".format(random.randrange(0, 255)))
        #tmp = tmp.decode("hex")
        tmp = bytes.fromhex("{:02x}".format(random.randrange(0, 255)))
        udp_payload.append(tmp)

    # Resolve destination IP from hostname (if provided)
    destination_host = args['destination_host']
    if not destination_host.isdigit():
        try:
            args['destination_ip'] = gethostbyname(destination_host)
            print(f"Resolved destination hostname '{destination_host}' to IP: {args['destination_ip']}")
        except socket.gaierror as e:
            print(f"Error resolving hostname '{destination_host}': {e}")
            exit(1)
    else:
        args['destination_ip'] = destination_host  # Use provided IP address

    print("Setting up RTP Packets")
    udp_payload = []
    # 212 = 240 - IP headler len  - UDP header len - RTP header length ==> 240 - 20 - 8 - 12
    for i in range(200):
        #tmp = bytes("{:02x}".format(random.randrange(0, 255)))
        #tmp = tmp.decode("hex")
        tmp = bytes.fromhex("{:02x}".format(random.randrange(0, 255)))
        udp_payload.append(tmp)

    # pull args for count.
    min_count = args['min_count']
    max_count = args['max_count']
    count = random.randrange(min_count, max_count)
    print("sending: {0} packets".format(count))

    source_port = random.randrange(10000, 65535)
    # delete IP and UDP checksum so that they can be re computed.
    for i in range(1, count, 1):

        if args['source_interface'] is None:
            if args['source_ip'] is None:
                packet = IP(dst=args['destination_ip'], proto=17, len=240)
            else:
                packet = IP(dst=args['destination_ip'], src=args['source_ip'], proto=17, len=240)
        else:
            packet = Ether()
            if args['source_ip'] is None:
                packet = IP(dst=args['destination_ip'], proto=17, len=240)
            else:
                packet = IP(dst=args['destination_ip'], src=args['source_ip'], proto=17, len=240)
        # do this for all streams
        packet = packet/UDP(sport=source_port, dport=args['destination_port'], len=220)
        packet = packet/RTP(version=2, payload_type=8, sequence=i, sourcesync=1, timestamp=time.time())
        packet = packet/Raw(load="".join(udp_payload))

        if args['source_interface'] is not None:
            del packet[Ether].chksum
        del packet[IP].chksum
        del packet[UDP].chksum

        if args['source_interface'] is None:
            output = send(packet, verbose=False)
        else:
            output = sendp(packet, iface=args['source_interface'], verbose=False)
        # output = send(packet, verbose=False)
        time.sleep(0.03)

    # enable these for additional debugs
    # print(packet.show())
    # print("Sending the above packet on interface {0}".format(args['source_interface']))
