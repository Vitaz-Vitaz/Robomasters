import socket
from time import sleep

UDP_IP = '10.128.73.75'
UDP_PORT = 11105

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)

sock = socket.socket(socket.AF_INET, -socket.SOCK_DGRAM) # UDP
mes = b'mem'
sock.sendto(mes, (UDP_IP, UDP_PORT))
exit(0)
