import socket
import time

UDP_IP = '10.128.73.98'
UDP_PORT = 11105
print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.connect((UDP_IP, UDP_PORT))
my_ip = list(map(lambda x: x.to_bytes(1, "little"), map(int, sock.getsockname()[0].split("."))))
my_ip = my_ip[0] + my_ip[1] + my_ip[2] + my_ip[3]
my_port = sock.getsockname()[1].to_bytes(2, "little")
print(my_ip, my_port, sock.getsockname())

sock.send(my_ip + my_port)
# sock.sendto(my_ip, (UDP_IP, UDP_PORT))
sock.settimeout(1)
while True:
    a = sock.recv(1024)
    print("mm", a)
    time.sleep(0.1)
