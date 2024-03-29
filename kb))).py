import socket
import struct
import time
import keyboard

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


last_keys = []
while True:
    keys = []
    if keyboard.is_pressed('w'):
        keys.append("w")
    if keyboard.is_pressed('a'):
        keys.append("a")
    if keyboard.is_pressed('s'):
        keys.append("s")
    if keyboard.is_pressed('d'):
        keys.append("d")

    if keys != last_keys:
        if "w" in keys:
            if "a" in keys:
                move(0, 100)
            elif "d" in keys:
                move(100, 0)
            else:
                move(100, 100)
        elif "s" in keys:
            if "a" in keys:
                move(0, -100)
            elif "d" in keys:
                move(-100, 0)
            else:
                move(-100, -100)
        elif "a" in keys:
            move(-70, 70)
        elif "d" in keys:
            move(70, -70)
        else:
            move(0, 0)
    last_keys = keys.copy()
    time.sleep(0.1)
