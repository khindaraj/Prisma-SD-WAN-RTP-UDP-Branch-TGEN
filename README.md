# Prisma SD-WAN Branch Traffic Generator

This set of scripts are used to generate traffic for Prisma SD-WAN on any branch client 

#### Synopsis

Set of scripts and config files required to do client side traffic generation of the following type. 

webpos.sh = traffic to a "custom application" hosted on the tgen-ns2 server

rtp.sh = shell script wrapper for the python script rtp.py that does RTP traffic generation toward any host specified (that host must be running the corresponding udp_echo.py script).

#### Requirements

* Ubuntu 18.04 or similar
* Python3
* Python modules:
  * scapy
* curl 


#### License

MIT
