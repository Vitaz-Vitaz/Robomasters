import socket
import struct
import time


UDP_IP = '10.128.73.75'
UDP_PORT = 11105
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP


def send(mes):
    sock.sendto(mes, (UDP_IP, UDP_PORT))


wheel_radius = 1  # см
base_radius = 1  # см
steps_in_turn = 695
pi = 3.14159265359


# raw
def move(lpower, rpower, accel, start_power, finish_power):
    mes = b'\x00'
    mes += struct.pack('f', lpower)
    mes += struct.pack('f', rpower)
    mes += struct.pack('f', accel)
    mes += struct.pack('f', start_power)
    mes += struct.pack('f', finish_power)
    send(mes)
move(1.1, 2.12, 3.123, 4.1234, 5.54321)


def move_steps(lpower, rpower, accel, start_power, finish_power, steps):
    mes = b'\x01'
    mes += struct.pack('f', lpower)
    mes += struct.pack('f', rpower)
    mes += struct.pack('f', accel)
    mes += struct.pack('f', start_power)
    mes += struct.pack('f', finish_power)
    mes += struct.pack('f', steps)
    send(mes)


# simple
def set_power(lpower, rpower):
    move(lpower, rpower, 0, min(lpower, rpower), max(lpower, rpower))


def set_power_steps(lpower, rpower, steps):
    move_steps(lpower, rpower, 0, min(lpower, rpower), max(lpower, rpower), steps)


# straight
def straight(power):
    set_power(power, power)


def straight_accel(power, start_power, max_power, accel):
    move(power, power, accel, start_power, max_power)


def straight_steps(power, steps):
    set_power_steps(power, power, steps)


def straight_step_accel(power, start_power, max_power, finish_power, accel, step):
    new_max = ((2 * abs(accel) * step + start_power ** 2 + finish_power ** 2) / 2) ** 0.5
    if new_max < max_power:
        max_power = new_max
    step1 = (max_power ** 2 - start_power ** 2) / (2 * accel)
    step2 = step - step1
    move_steps(power, power, accel, start_power, max_power, step1)
    move_steps(power, power, -accel, max_power, finish_power, step2)


# turn
def turn(power):
    """power: + по часовой - против часовой"""
    set_power(power, -power)


def turn_accel(power, start_power, max_power, accel):
    """power: + по часовой - против часовой"""
    move(power, -power, accel, start_power, max_power)


def turn_steps(power, degree):
    """power or degree: + по часовой - против часовой"""
    circle_len = (2 * pi * base_radius) * (abs(degree) / 360)
    wheel_len = 2 * pi * base_radius
    steps = (circle_len / wheel_len) * steps_in_turn
    set_power_steps(power, -power, steps)


# def turn_step_accel(power, start_power, max_power, finish_power, accel, degree):
#     """power: + по часовой - против часовой"""
#     move(power, -power, accel, start_power, max_power)


# arc
def arc(power, radius):
    """power: для медленного мотора, + по часовой - против часовой
    radius: от центра базы, + справа - слева"""
    lwheel_len = (2 * pi * (abs(radius) + base_radius)) * (abs(degree) / 360)
    rwheel_len = (2 * pi * (abs(radius) - base_radius)) * (abs(degree) / 360)
    if radius < 0:
        lwheel_len, rwheel_len = rwheel_len, lwheel_len
    max_power = power * (max(lwheel_len, rwheel_len) / min(lwheel_len, rwheel_len))
    move(lwheel_len, rwheel_len, 0, power, max_power)


def arc_steps(power, radius, degree):
    """power: для медленного мотора
    radius: от центра базы, + справа - слева
    power or degree: + по часовой - против часовой"""
    lwheel_len = (2 * pi * (abs(radius) + base_radius)) * (abs(degree) / 360)
    rwheel_len = (2 * pi * (abs(radius) - base_radius)) * (abs(degree) / 360)
    if radius < 0:
        lwheel_len, rwheel_len = rwheel_len, lwheel_len
    wheel_len = 2 * pi * base_radius
    steps = (max(lwheel_len, rwheel_len) / wheel_len) * steps_in_turn
    max_power = power * (max(lwheel_len, rwheel_len) / min(lwheel_len, rwheel_len))
    move_steps(lwheel_len, rwheel_len, 0, power, max_power, steps)


# straight_step_accel(-1, 0, -80, 0, 1, 50000)


