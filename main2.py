import socket
import struct
import time

UDP_IP = '10.128.73.121'
# UDP_IP = '192.168.45.231'
UDP_PORT = 11105
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
sock.connect((UDP_IP, UDP_PORT))
my_ip = list(map(lambda x: x.to_bytes(1, "little"), map(int, sock.getsockname()[0].split("."))))
my_ip = my_ip[0] + my_ip[1] + my_ip[2] + my_ip[3]
my_port = sock.getsockname()[1].to_bytes(2, "little")
print(my_ip, my_port, sock.getsockname())


def send(mes):
    sock.send(mes)


wheel_radius = 4.3 / 2  # см
base_radius = 12.3 / 2  # см
steps_in_turn = 695
pi = 3.14159265359
wheel_len = 2 * pi * wheel_radius


def move(lpower, rpower):
    mes = b'\x00'
    mes += struct.pack('f', lpower)
    mes += struct.pack('f', rpower)
    print(mes)
    send(mes)


def move_step(lpower, rpower, steps, wait=False):
    mes = b'\x01'
    mes += struct.pack('f', lpower)
    mes += struct.pack('f', rpower)
    mes += struct.pack('f', steps)
    mes += my_ip
    mes += my_port
    send(mes)
    if wait:
        sock.settimeout(None)
        sock.recvfrom(1024)


def turn_steps(power, degree, wait=False):
    """power: - по часовой + против часовой"""
    circle_len = (2 * pi * base_radius) * (abs(degree) / 360)
    steps = (circle_len / wheel_len) * steps_in_turn
    move_step(-power, power, abs(steps), wait=wait)


def wait():
    sock.settimeout(None)
    sock.recvfrom(1024)

move(100, 100)

# turn_steps(70, 360, wait=True)
# move(80, -80)
#
# while True:
#     move(90, 60)
#     time.sleep(5)
#     move(-90, -60)
#     time.sleep(5)

# while True:
#     move_step(70, 70, 2000,  wait=True)
#     turn_steps(70, 90, wait=True)
#
# while True:
#     turn_steps(70, 360, wait=True)
#     print(1)
#     turn_steps(-70, 360, wait=True)
#     print(2)
    # move(0, 0)
    # time.sleep(2)



# while True:
#     a, b = map(float, input().split())
#     move(a, b)
