import time
import argparse
import random
import logging
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.layers.rtp import RTP
from scapy.packet import Raw
from scapy.sendrecv import send, sendp
from socket import gethostbyname  # Import for hostname resolution

# Set log level to benefit from Scapy warnings
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

    # Create the payload for UDP packets, in Python 3 bytes must be used
    udp_payload = []
    for i in range(200):
        # Generating random byte data for the payload
        tmp = random.randrange(0, 255).to_bytes(1, byteorder='big')
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

    # Pull arguments for packet count
    min_count = args['min_count']
    max_count = args['max_count']
    count = random.randrange(min_count, max_count)
    print(f"sending: {count} packets")

    source_port = random.randrange(10000, 65535)  # Randomize source port

    # Begin sending packets
    for i in range(1, count + 1):
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

        # Creating RTP packet
        packet = packet / UDP(sport=source_port, dport=args['destination_port'], len=220)
        packet = packet / RTP(version=2, payload_type=8, sequence=i, sourcesync=1, timestamp=int(time.time()))
        packet = packet / Raw(load=b"".join(udp_payload))  # Ensuring payload is bytes

        # Remove checksums to allow Scapy to recalculate them
        if args['source_interface'] is not None:
            del packet[Ether].chksum
        del packet[IP].chksum
        del packet[UDP].chksum

        # Send packet using appropriate method
        if args['source_interface'] is None:
            output = send(packet, verbose=False)
        else:
            output = sendp(packet, iface=args['source_interface'], verbose=False)

        # Introduce delay between packet transmissions
        time.sleep(0.03)

    # Uncomment for debugging output
    # print(packet.show())
    # print(f"Sending the above packet on interface {args['source_interface']}")
