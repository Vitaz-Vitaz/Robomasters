import sys
import os
import time
import numpy as np
import base64
import math
import itertools
import socket
import struct
from nto.final import Task
import cv2

import networkx as nx
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import base64
import math
import itertools


## Здесь должно работать ваше решение
def solve(task: Task):
    ## Загружаем изображение из задачи
    # сцена отправляется с определенной частотй
    # для этого смотри в документацию к задаче

    UDP_IP = '10.128.73.121'
    # UDP_IP = '192.168.45.231'
    UDP_PORT = 11105
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    try:
        sock.connect((UDP_IP, UDP_PORT))
    except Exception as e:
        print(e)

    my_ip = list(map(lambda x: x.to_bytes(1, "little"), map(int, sock.getsockname()[0].split("."))))
    my_ip = my_ip[0] + my_ip[1] + my_ip[2] + my_ip[3]
    my_port = sock.getsockname()[1].to_bytes(2, "little")

    # print(my_ip, my_port, sock.getsockname())

    def send(mes):
        sock.send(mes)

    wheel_radius = 4.3 / 2  # см
    base_radius = 12.3 / 2  # см
    steps_in_turn = 695
    pi = 3.14159265359
    wheel_len = 2 * pi * wheel_radius

    def wait():
        sock.settimeout(None)
        sock.recvfrom(1024)

    def move(lpower, rpower):
        mes = b'\x00'
        mes += struct.pack('f', lpower)
        mes += struct.pack('f', rpower)
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

    def get_lines(lines, near_distance):
        ret = []
        count = 0
        while len(lines) > 0:
            count += 1

            new = [lines[0]]
            main_cur = lines[0]
            cur = main_cur
            lines.pop(0)

            cur_i = 0
            while True:
                mn = 9999
                el = 0
                for ind, i in enumerate(lines):
                    l = min(math.dist(cur[cur_i], i[0]), math.dist(cur[cur_i], i[1]))
                    if l < mn:
                        mn = l
                        el = ind
                if mn > near_distance:
                    # print(el, mn)
                    break
                if math.dist(cur[cur_i], lines[el][0]) > math.dist(cur[cur_i], lines[el][1]):
                    new.append((lines[el][1], lines[el][0]))
                else:
                    new.append(lines[el])
                cur = new[-1]
                lines.pop(el)

            # new.reverse()

            if math.dist(new[0][1], new[1][0]) > math.dist(new[0][0], new[1][0]):
                new[0] = (new[0][1], new[0][0])
                # print("---------------------------------------------------------------------------------")

            cur = main_cur

            cur_i = 1
            while True:
                mn = 9999
                el = 0
                for ind, i in enumerate(lines):
                    l = min(math.dist(cur[cur_i], i[0]), math.dist(cur[cur_i], i[1]))
                    if l < mn:
                        mn = l
                        el = ind
                if mn > near_distance:
                    # print(el, mn)
                    break
                if math.dist(cur[cur_i], lines[el][1]) > math.dist(cur[cur_i], lines[el][0]):
                    new.insert(0, (lines[el][1], lines[el][0]))
                else:
                    new.insert(0, lines[el])
                cur = new[0]
                lines.pop(el)

            ret.append(new.copy())
        return ret

    def get_graph(lines, qrCods, lines_x, lines_y, cross_near, coordrob):
        crosses_x = 1699
        crosses_y = 1080
        crosses = """219 162
    364 117
    1105 105
    323 212
    613 359
    1029 383
    1130 409
    1545 548
    105 574
    380 605
    833 686
    1084 767
    1377 913
    1265 930
    707 423""".split("\n")
        for ind, i in enumerate(crosses):
            cross = list(map(int, i.split()))
            crosses[ind] = (cross[0] / crosses_x * lines_x, cross[1] / crosses_y * lines_y)
        markers = """187 343
    253 536
    406 449
    102 897
    150 945
    173 735
    283 879
    388 894
    797 911
    1454 683
    1196 282
    1563 147
    1480 99
    1048 516
    891 290
    769 139
    636 145
    721 564
    549 510""".split("\n")
        for ind, i in enumerate(markers):
            marker = list(map(int, i.split()))
            markers[ind] = (marker[0] / crosses_x * lines_x, marker[1] / crosses_y * lines_y)

        graph = nx.MultiDiGraph()
        for line in lines:
            for i in line:
                graph.add_node(i[0])
                graph.add_node(i[1])
        for cross in crosses:
            graph.add_node(cross)
        for line in lines:
            for ind in range(1, len(line)):
                graph.add_edge(line[ind - 1][0], line[ind - 1][1], weight=math.dist(line[ind - 1][0], line[ind - 1][1]))
                graph.add_edge(line[ind - 1][1], line[ind][0], weight=math.dist(line[ind - 1][1], line[ind][0]))
            graph.add_edge(line[len(line) - 1][0], line[len(line) - 1][1],
                           weight=math.dist(line[len(line) - 1][0], line[len(line) - 1][1]))

        for i in range(len(crosses)):
            for j in range(i + 1, len(crosses)):
                cross1 = (crosses[i][0] / lines_x * crosses_x, crosses[i][1] / lines_y * crosses_y)
                cross2 = (crosses[j][0] / lines_x * crosses_x, crosses[j][1] / lines_y * crosses_y)
                if math.dist(cross1, cross2) < cross_near:
                    cross1 = (cross1[0] / crosses_x * lines_x, cross1[1] / crosses_y * lines_y)
                    cross2 = (cross2[0] / crosses_x * lines_x, cross2[1] / crosses_y * lines_y)
                    graph.add_edge(cross1, cross2, weight=math.dist(cross1, cross2))
        for line in lines:
            end = line[0]
            mn = max(lines_x, lines_y)
            el = (0, 0)
            for cross in crosses:
                if math.dist(end[0], cross) < mn:
                    mn = math.dist(end[0], cross)
                    el = cross
            graph.add_edge(end[0], el, weight=mn)

            end = line[-1]
            mn = max(lines_x, lines_y)
            el = (0, 0)
            for cross in crosses:
                if math.dist(end[1], cross) < mn:
                    mn = math.dist(end[1], cross)
                    el = cross
            graph.add_edge(end[1], el, weight=mn)

        nodes = list(graph.nodes())
        markers.append(coordrob)
        for marker in markers:
            mn = 999999
            el = 0
            for ind, node in enumerate(nodes):
                if math.dist(marker, (int(node[0]), int(node[1]))) < mn:
                    mn = math.dist(marker, (int(node[0]), int(node[1])))
                    el = ind
            print(nodes[el])
            graph.add_edge(nodes[el], marker, weight=math.dist(nodes[el], marker))

        for i in range(len(qrCods)):
            mi = 99999
            x1, y1 = qrCods[i][0], qrCods[i][1]
            q1 = (0, 0)
            q2 = (0, 0)
            for j in range(len(markers)):
                x2, y2 = markers[j][0], markers[j][1]
                if math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < mi:
                    mi = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    q1 = (x1, y1)
                    q2 = (x2, y2)
            print(q2, q1)
            graph.add_edge(q2, q1, weight=mi)

        return graph

    def navigator(img, coordrob, spoints):
        graph = nx.MultiDiGraph()
        ans = []
        # Преобразование изображения в оттенки серого
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Бинаризация изображения (порог можно настроить под ваш конкретный случай)
        # _, binary_image = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        binary_image = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 255, 0)
        cv2.imshow("Image1", binary_image)
        cv2.waitKey(0)
        allBigContrs = []
        # Поиск контура
        contours, hi = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        linecent = []
        biggestContur = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                allBigContrs.append(contour)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 25000:
                biggestContur = contour

        # Перебираем все контуры на изображении
        i = 0
        oner = True
        for contour in contours:
            cv2.drawContours(img, [contour], -1, (200, 200, 200), 2)
            area = cv2.contourArea(contour)

            c, dim, ang = cv2.minAreaRect(contour)
            box = cv2.boxPoints((c, dim, ang))
            box = np.intp(box)
            x, y, w, h = cv2.boundingRect(contour)
            f1 = True
            f2 = True
            # for point in contour:
            #
            #     distance = cv2.pointPolygonTest(biggestContur, (int(point[0][0]), int(point[0][1])), False)
            #     if distance > 0:
            #         f2 = False
            #     print(distance, "ppppp")
            # print("start", contour[0][0][1], "finish")
            if x < 40 or x > 1150:
                f2 = False
            if area > 25000:
                cv2.putText(img, "skididistyyy", (int(box[0][0]), int(box[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
                            (255, 0, 255), 0, cv2.LINE_AA)
                cv2.drawContours(img, [contour], -1, (300, 100, 50), 2)
                f1 = False
            elif area > 1000:
                # print(box[0], "skibidi dop dop yes yes")
                cv2.putText(img, "skibidi dop dop yes yes", (int(box[0][0]), int(box[0][1])), cv2.FONT_HERSHEY_SIMPLEX,
                            0.3,
                            (255, 0, 255), 0, cv2.LINE_AA)
                cv2.drawContours(img, [contour], -1, (200, 200, 200), 2)
                f1 = False
            elif area > 10:
                cv2.drawContours(img, [contour], -1, 0, 2)
                for qq in allBigContrs:
                    for h in qq:
                        M = cv2.moments(contour)
                        # Нахождение центра масс контура
                        if M['m00'] != 0:
                            cx = int(M['m10'] / M['m00'])
                            cy = int(M['m01'] / M['m00'])
                            # print(h, "qwertyuf")
                            if math.sqrt((cx - int(h[0][0])) ** 2 + ((cy - int(h[0][1])) ** 2)) < 25:
                                f1 = False
            # cv2.putText(img, f'{box[0]}, {box[1]}, {box[2]}, {box[3]}', (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 255),0,cv2.LINE_AA)
            #
            # print(x, y, w, h, 'erty')
            if 10 < area < 200 and f1 and f2:
                xP = abs(box[0][0] - box[2][0])
                yP = abs(box[0][1] - box[2][1])
                cv2.putText(img, f'{xP}, {yP}', (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 255), 0,
                            cv2.LINE_AA)
                q1 = (box[0][0], box[0][1])
                q2 = (box[1][0], box[1][1])
                q3 = (box[2][0], box[2][1])
                q4 = (box[3][0], box[3][1])
                r1 = math.sqrt((q1[0] - q3[0]) ** 2 + (q1[1] - q3[1]) ** 2)
                r2 = math.sqrt((q2[0] - q4[0]) ** 2 + (q2[1] - q4[1]) ** 2)
                if r1 > r2:
                    ans.append((q1, q3))
                else:
                    ans.append((q2, q4))
                # print(q1, "ANS")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.imwrite(f'photo4.jpg', sceneImg)
        # print(ans, "ANS")
        aa = get_lines(ans, 70)

        # print(aa, 1)
        # for hh in aa:
        #     for i in range(len(hh) - 1):
        #         # k = o % 2
        #         # k2 = 1 - k
        #         # print(hh[o][k2])
        #         cv2.line(img, hh[i][1], hh[i + 1][0], (150, 0, 150), 2)
        #     cv2.circle(img, hh[0][0], 8, (0, 0, 255))
        #     cv2.circle(img, hh[-1][1], 4, (0, 255, 0))

        print(aa)

        graphFinal = get_graph(aa, spoints, (img.shape[0], img.shape[1]), 200, coordrob)
        pos = graphFinal.edges()
        pos2 = graphFinal.nodes()  # vershina
        print(pos, 1234567890)
        print(pos2)
        # for q in pos2:
        #     c1 = int(q[0])
        #     c2 = int(q[1])
        #     cv2.circle(img, (c1, c2), 12, (78, 200, 25))

        for q in pos:
            try:
                c1 = q[0]
                c2 = q[1]
                z1, z2 = int(c1[0]), int(c1[1])
                v1, v2 = int(c2[0]), int(c2[1])
                cv2.line(img, (z1, z2), (v1, v2), (150, 150, 150), 2)
            except:
                print(q, "ErrorMain")

        cv2.imshow("Image", img)
        cv2.waitKey(0)

    def clip_img(IMG1, IMG2):
        camera_matrix1 = np.array([[2.85040816e+03, 0.00000000e+00, 6.38881112e+02],
                                   [0.00000000e+00, 3.05444657e+03, 3.93160316e+02],
                                   [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
        dist_coefs1 = np.array([[-2.85704778e+00, -7.66000137e+00, 1.08976277e-01,
                                 9.40554799e-04, 1.93092989e+02]])

        camera_matrix2 = np.array([[936.13046684, 0, 649.31171323],
                                   [0, 936.95657529, 405.33544041],
                                   [0, 0, 1]])
        dist_coefs2 = np.array([[-0.32549398, 0.18280344, 0.00143496, 0.00035975, -0.07752816]])

        w, h = IMG1.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix1, dist_coefs1, (w, h), 1, (w, h))
        x, y, w, h = roi
        dst1 = cv2.undistort(IMG1, camera_matrix1, dist_coefs1, None, newcameramtx)

        w, h = IMG2.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix2, dist_coefs2, (w, h), 1, (w, h))
        x, y, w, h = roi
        dst2 = cv2.undistort(IMG2, camera_matrix2, dist_coefs2, None, newcameramtx)

        dst1 = dst1[200:dst1.shape[0], 200:dst1.shape[1] - 200]

        dst2 = dst2[100:-235, 200:dst2.shape[1] - 200]
        dst2 = cv2.resize(dst2, (980, 500))

        dst2 = dst2[0:dst2.shape[0], 70:dst2.shape[1] - 30]

        IMG = cv2.vconcat([dst2, dst1])
        IMG = cv2.rotate(IMG, cv2.ROTATE_90_COUNTERCLOCKWISE)
        imgray = cv2.cvtColor(IMG, cv2.COLOR_BGR2GRAY)
        adimg = cv2.adaptiveThreshold(imgray, 205, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 17, 2)

        contours, hi = cv2.findContours(adimg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cimarkers = []
        for i, cnt in enumerate(contours):
            perimeter = cv2.arcLength(cnt, True)
            cnt = cv2.approxPolyDP(cnt, 0.03 * perimeter,
                                   True)  # Попробуйте различные коэффициенты для получения более или менее углов
            if cv2.contourArea(cnt) > 850000 or cv2.contourArea(cnt) < 700000:
                continue
            # cv2.drawContours(IMG, [cnt], -1, 200, 2)
            # cv2.imshow('adimg',adimg)
            # cv2.waitKey(0)
            # print(cnt)
            # cv2.imshow('IMG2',IMG)
            # cv2.waitKey(0)

            c, dim, ang = cv2.minAreaRect(cnt)
            box = cv2.boxPoints((c, dim, ang))
            cv2.circle(IMG, (int(box[0][0]), int(box[0][1])), 2, (0, 0, 255), -1)
            cv2.circle(IMG, (int(box[1][0]), int(box[1][1])), 2, (0, 0, 255), -1)
            cv2.circle(IMG, (int(box[2][0]), int(box[2][1])), 2, (0, 0, 255), -1)
            cv2.circle(IMG, (int(box[3][0]), int(box[3][1])), 2, (0, 0, 255), -1)

            dst = np.float32([[0, IMG.shape[0]],
                              [IMG.shape[1], IMG.shape[0]],
                              [IMG.shape[1], 0],
                              [0, 0]])
            '''
            src = np.float32([box[0],
                            box[3],
                            box[2],
                            box[1]])
            '''
            src = np.float32([cnt[3],
                              cnt[2],
                              cnt[1],
                              cnt[0]])
            # src = np.float32([[1065, 82],
            #                  [42, 46],
            #                  [42,  785],
            #                  [1051,  788]])

            M = cv2.getPerspectiveTransform(src, dst)
            mask = cv2.warpPerspective(IMG, M, (IMG.shape[1], IMG.shape[0]), flags=cv2.INTER_LINEAR)
            return mask

    video1 = True
    video2 = True
    if video1 == True:
        cap1 = cv2.VideoCapture('http://student:nto2024@10.128.73.31/mjpg/video.mjpg')
        if cap1.isOpened() == False:
            print("Cannot open input video1")
            video1 = False
            IMG1 = cv2.imread('cam1.jpg')
        else:
            _, IMG1 = cap1.read()
    else:
        IMG1 = cv2.imread('cam1.jpg')
    if video2 == True:
        cap2 = cv2.VideoCapture('http://student:nto2024@10.128.73.38/mjpg/video.mjpg')
        if cap2.isOpened() == False:
            print("Cannot open input video2")
            video2 = False
            IMG2 = cv2.imread('cam2.jpg')
        else:
            _, IMG2 = cap2.read()
    else:
        IMG2 = cv2.imread('cam2.jpg')

    sceneImg = clip_img(IMG1, IMG2)  # cv2.imread('photo3.jpg')#
    mapImage = sceneImg.copy()

    # taskInfo = str([{'name': 'p_0', 'coordinates': [764, 600]}])
    '''
    taskInfo = str([{"name": "p_1", "marker_id": 1},
                    {"name": "p_2", "marker_id": 2},
                    {"name": "p_3", "coordinates": [64, 1080, 1]},
                    {"name": "p_5", "coordinates": [200, 150, 2]},
                    {"name": "p_4", "marker_id": 25}])
    '''
    taskInfo = task.getTask()
    print('taskInfo:', taskInfo)

    robotsSize = 15

    if taskInfo != None:
        points = eval(taskInfo)
    else:
        points = list()

    r90_idx = [6, 3, 0, 7, 4, 1, 8, 5, 2]
    r180_idx = [8, 7, 6, 5, 4, 3, 2, 1, 0]
    r270_idx = [2, 5, 8, 1, 4, 7, 0, 3, 6]

    aruco_3x3_dict = {
        1: [0, 0, 0, 0, 0, 0, 0, 0, 1],
        2: [0, 0, 0, 0, 0, 0, 0, 1, 0],
        3: [0, 0, 0, 0, 0, 0, 0, 1, 1],
        5: [0, 0, 0, 0, 0, 0, 1, 0, 1],
        6: [0, 0, 0, 0, 0, 0, 1, 1, 0],
        7: [0, 0, 0, 0, 0, 0, 1, 1, 1],
        10: [0, 0, 0, 0, 0, 1, 0, 1, 0],
        11: [0, 0, 0, 0, 0, 1, 0, 1, 1],
        12: [0, 0, 0, 0, 0, 1, 1, 0, 0],
        13: [0, 0, 0, 0, 0, 1, 1, 0, 1],
        14: [0, 0, 0, 0, 0, 1, 1, 1, 0],
        15: [0, 0, 0, 0, 0, 1, 1, 1, 1],
        17: [0, 0, 0, 0, 1, 0, 0, 0, 1],
        18: [0, 0, 0, 0, 1, 0, 0, 1, 0],
        19: [0, 0, 0, 0, 1, 0, 0, 1, 1],
        21: [0, 0, 0, 0, 1, 0, 1, 0, 1],
        22: [0, 0, 0, 0, 1, 0, 1, 1, 0],
        23: [0, 0, 0, 0, 1, 0, 1, 1, 1],
        26: [0, 0, 0, 0, 1, 1, 0, 1, 0],
        27: [0, 0, 0, 0, 1, 1, 0, 1, 1],
        28: [0, 0, 0, 0, 1, 1, 1, 0, 0],
        29: [0, 0, 0, 0, 1, 1, 1, 0, 1],
        30: [0, 0, 0, 0, 1, 1, 1, 1, 0],
        31: [0, 0, 0, 0, 1, 1, 1, 1, 1],
        33: [0, 0, 0, 1, 0, 0, 0, 0, 1],
        35: [0, 0, 0, 1, 0, 0, 0, 1, 1],
        37: [0, 0, 0, 1, 0, 0, 1, 0, 1],
        39: [0, 0, 0, 1, 0, 0, 1, 1, 1],
        41: [0, 0, 0, 1, 0, 1, 0, 0, 1],
        42: [0, 0, 0, 1, 0, 1, 0, 1, 0],
        43: [0, 0, 0, 1, 0, 1, 0, 1, 1],
        44: [0, 0, 0, 1, 0, 1, 1, 0, 0],
        45: [0, 0, 0, 1, 0, 1, 1, 0, 1],
        46: [0, 0, 0, 1, 0, 1, 1, 1, 0],
        47: [0, 0, 0, 1, 0, 1, 1, 1, 1],
        49: [0, 0, 0, 1, 1, 0, 0, 0, 1],
        51: [0, 0, 0, 1, 1, 0, 0, 1, 1],
        53: [0, 0, 0, 1, 1, 0, 1, 0, 1],
        55: [0, 0, 0, 1, 1, 0, 1, 1, 1],
        57: [0, 0, 0, 1, 1, 1, 0, 0, 1],
        58: [0, 0, 0, 1, 1, 1, 0, 1, 0],
        59: [0, 0, 0, 1, 1, 1, 0, 1, 1],
        60: [0, 0, 0, 1, 1, 1, 1, 0, 0],
        61: [0, 0, 0, 1, 1, 1, 1, 0, 1],
        62: [0, 0, 0, 1, 1, 1, 1, 1, 0],
        63: [0, 0, 0, 1, 1, 1, 1, 1, 1],
        69: [0, 0, 1, 0, 0, 0, 1, 0, 1],
        70: [0, 0, 1, 0, 0, 0, 1, 1, 0],
        71: [0, 0, 1, 0, 0, 0, 1, 1, 1],
        76: [0, 0, 1, 0, 0, 1, 1, 0, 0],
        77: [0, 0, 1, 0, 0, 1, 1, 0, 1],
        78: [0, 0, 1, 0, 0, 1, 1, 1, 0],
        79: [0, 0, 1, 0, 0, 1, 1, 1, 1],
        85: [0, 0, 1, 0, 1, 0, 1, 0, 1],
        86: [0, 0, 1, 0, 1, 0, 1, 1, 0],
        87: [0, 0, 1, 0, 1, 0, 1, 1, 1],
        92: [0, 0, 1, 0, 1, 1, 1, 0, 0],
        93: [0, 0, 1, 0, 1, 1, 1, 0, 1],
        94: [0, 0, 1, 0, 1, 1, 1, 1, 0],
        95: [0, 0, 1, 0, 1, 1, 1, 1, 1],
        97: [0, 0, 1, 1, 0, 0, 0, 0, 1],
        98: [0, 0, 1, 1, 0, 0, 0, 1, 0],
        99: [0, 0, 1, 1, 0, 0, 0, 1, 1],
        101: [0, 0, 1, 1, 0, 0, 1, 0, 1],
        102: [0, 0, 1, 1, 0, 0, 1, 1, 0],
        103: [0, 0, 1, 1, 0, 0, 1, 1, 1],
        105: [0, 0, 1, 1, 0, 1, 0, 0, 1],
        106: [0, 0, 1, 1, 0, 1, 0, 1, 0],
        107: [0, 0, 1, 1, 0, 1, 0, 1, 1],
        109: [0, 0, 1, 1, 0, 1, 1, 0, 1],
        110: [0, 0, 1, 1, 0, 1, 1, 1, 0],
        111: [0, 0, 1, 1, 0, 1, 1, 1, 1],
        113: [0, 0, 1, 1, 1, 0, 0, 0, 1],
        114: [0, 0, 1, 1, 1, 0, 0, 1, 0],
        115: [0, 0, 1, 1, 1, 0, 0, 1, 1],
        117: [0, 0, 1, 1, 1, 0, 1, 0, 1],
        118: [0, 0, 1, 1, 1, 0, 1, 1, 0],
        119: [0, 0, 1, 1, 1, 0, 1, 1, 1],
        121: [0, 0, 1, 1, 1, 1, 0, 0, 1],
        122: [0, 0, 1, 1, 1, 1, 0, 1, 0],
        123: [0, 0, 1, 1, 1, 1, 0, 1, 1],
        125: [0, 0, 1, 1, 1, 1, 1, 0, 1],
        126: [0, 0, 1, 1, 1, 1, 1, 1, 0],
        127: [0, 0, 1, 1, 1, 1, 1, 1, 1],
        141: [0, 1, 0, 0, 0, 1, 1, 0, 1],
        142: [0, 1, 0, 0, 0, 1, 1, 1, 0],
        143: [0, 1, 0, 0, 0, 1, 1, 1, 1],
        157: [0, 1, 0, 0, 1, 1, 1, 0, 1],
        158: [0, 1, 0, 0, 1, 1, 1, 1, 0],
        159: [0, 1, 0, 0, 1, 1, 1, 1, 1],
        171: [0, 1, 0, 1, 0, 1, 0, 1, 1],
        173: [0, 1, 0, 1, 0, 1, 1, 0, 1],
        175: [0, 1, 0, 1, 0, 1, 1, 1, 1],
        187: [0, 1, 0, 1, 1, 1, 0, 1, 1],
        189: [0, 1, 0, 1, 1, 1, 1, 0, 1],
        191: [0, 1, 0, 1, 1, 1, 1, 1, 1],
        197: [0, 1, 1, 0, 0, 0, 1, 0, 1],
        199: [0, 1, 1, 0, 0, 0, 1, 1, 1],
        205: [0, 1, 1, 0, 0, 1, 1, 0, 1],
        206: [0, 1, 1, 0, 0, 1, 1, 1, 0],
        207: [0, 1, 1, 0, 0, 1, 1, 1, 1],
        213: [0, 1, 1, 0, 1, 0, 1, 0, 1],
        215: [0, 1, 1, 0, 1, 0, 1, 1, 1],
        221: [0, 1, 1, 0, 1, 1, 1, 0, 1],
        222: [0, 1, 1, 0, 1, 1, 1, 1, 0],
        223: [0, 1, 1, 0, 1, 1, 1, 1, 1],
        229: [0, 1, 1, 1, 0, 0, 1, 0, 1],
        231: [0, 1, 1, 1, 0, 0, 1, 1, 1],
        237: [0, 1, 1, 1, 0, 1, 1, 0, 1],
        239: [0, 1, 1, 1, 0, 1, 1, 1, 1],
        245: [0, 1, 1, 1, 1, 0, 1, 0, 1],
        247: [0, 1, 1, 1, 1, 0, 1, 1, 1],
        253: [0, 1, 1, 1, 1, 1, 1, 0, 1],
        255: [0, 1, 1, 1, 1, 1, 1, 1, 1],
        327: [1, 0, 1, 0, 0, 0, 1, 1, 1],
        335: [1, 0, 1, 0, 0, 1, 1, 1, 1],
        343: [1, 0, 1, 0, 1, 0, 1, 1, 1],
        351: [1, 0, 1, 0, 1, 1, 1, 1, 1],
        367: [1, 0, 1, 1, 0, 1, 1, 1, 1],
        383: [1, 0, 1, 1, 1, 1, 1, 1, 1]
    }

    def bin2dec(binarray):
        marker_id = 0
        n = len(binarray)
        for i in range(n - 1, -1, -1):
            marker_id += binarray[i] * 2 ** (n - i - 1)
        if marker_id in aruco_3x3_dict.keys():
            return marker_id
        else:
            return -1

    def update_binarray(binarray, order):
        new_binarray = []
        for i in order:
            new_binarray.append(binarray[i])
        return new_binarray

    def get_mask_binarray(mask):

        N = 5
        cell_width = mask.shape[1] / N
        cell_height = mask.shape[0] / N
        cell_cx = cell_width / 2
        cell_cy = cell_height / 2

        binarray = []
        is_boder = True

        for i in range(N):
            for j in range(N):
                y = round(i * cell_width + cell_cx)
                x = round(j * cell_height + cell_cy)
                color = round(np.average(mask[y - 1:y + 1, x - 1:x + 1]) / 255)
                if (i == 0 or i == N - 1) or (j == 0 or j == N - 1):
                    is_boder = is_boder and (color == 0)
                    continue
                binarray.append(color)
                cv2.circle(mask, (x, y), 1, (255, 0, 0), -1)

        cv2.imshow("m", mask)
        # print(binarray)
        # cv2.waitKey(0)
        if not is_boder:
            return []

        return binarray

    imgray = cv2.cvtColor(mapImage, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 29, 7)

    contours, hi = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    cimarkers = []
    for i, cnt in enumerate(contours):
        if 10000 < cv2.contourArea(cnt) or cv2.contourArea(cnt) < 1000:
            # if cv2.contourArea(cnt)<10000:
            continue

        if hi[0][i][2] == -1 or hi[0][i][3] == -1:
            continue

        c, dim, ang = cv2.minAreaRect(cnt)
        box = cv2.boxPoints((c, dim, ang))
        print(box)
        cv2.circle(imgray, (int(box[0][0]), int(box[0][1])), 2, 255, -1)
        cv2.circle(imgray, (int(box[1][0]), int(box[1][1])), 2, 200, -1)
        cv2.circle(imgray, (int(box[2][0]), int(box[2][1])), 2, 150, -1)
        cv2.circle(imgray, (int(box[3][0]), int(box[3][1])), 2, 100, -1)
        # if box[0][1]>box[2][1]:
        #    print('True')
        '''
        boxs=[]
        ctock=box[0]

        for i2 in box:
            if i2[0]<ctock[0]:
                ctock=i2
            elif i2[0]==ctock[0]:
                if i2[1]>ctock[1]:
                    ctock=i2
        boxs.append(ctock)
        for i2 in box:
            if i2[1]>ctock[1]:
                ctock=i2
            elif i2[1]==ctock[1]:
                if i2[0]<ctock[0]:
                    ctock=i2


        boxs.append(ctock)
        for i2 in box:
            if i2[0]>ctock[0]:
                ctock=i2
            elif i2[0]==ctock[0]:
                if i2[1]<ctock[1]:
                    ctock=i2
        boxs.append(ctock)

        for i2 in box:
            if i2[1]<ctock[1]:
                ctock=i2
            elif i2[1]==ctock[1]:
                if i2[0]>ctock[0]:
                    ctock=i2
        boxs.append(ctock)

        print('1:', box)
        print('2:', boxs)
        '''

        box = np.intp(box)

        if max(dim) < 5:
            continue
        # if min(dim)/max(dim)<0.85:
        #    continue
        cv2.drawContours(thresh, [cnt], -1, 0, 2)
        x, y, w, h = cv2.boundingRect(cnt)

        '''
        margin=5
        x,y,w,h=cv2.boundingRect(cnt)
        mask=thresh[y-margin:y+h+margin, x-margin:x+w+margin]

        M=cv2.getRotationMatrix2D((mask.shape[0]/2, mask.shape[1]/2), ang, 1)

        if mask.shape[0] > 0 and mask.shape[1] > 0:
            mask = cv2.warpAffine(mask, M, (mask.shape[0], mask.shape[1]))
        else:
            print("Invalid mask image dimensions")

        clip=[round((mask.shape[0]-dim[1])/2), round((mask.shape[1]-dim[0])/2)]
        mask=mask[clip[0]:-clip[0], clip[1]:-clip[1]]
        if mask is not None and not mask.size == 0:
            mask = cv2.resize(mask, (200, 200))
        else:
            continue
        '''

        dst = np.float32([[0, 200],
                          [200, 200],
                          [200, 0],
                          [0, 0]])

        src = np.float32([box[0],
                          box[3],
                          box[2],
                          box[1]])

        M = cv2.getPerspectiveTransform(src, dst)
        mask = cv2.warpPerspective(thresh, M, (200, 200), flags=cv2.INTER_LINEAR)

        binarray = get_mask_binarray(mask)
        if len(binarray) == 0:
            continue

        marker_id = -1
        marker_ang = 0
        idx = [
            bin2dec(binarray),
            bin2dec(update_binarray(binarray, r90_idx)),
            bin2dec(update_binarray(binarray, r180_idx)),
            bin2dec(update_binarray(binarray, r270_idx))
        ]

        for i, id in enumerate(idx):
            if id > -1:
                marker_id = id
                marker_ang = i * 90 - ang
                if marker_ang > 180:
                    marker_ang -= 360
                if marker_ang < -180:
                    marker_ang += 360
                break

        if marker_id == -1:
            continue
        cimarkers.append([[int(x + w / 2), int(y + h / 2), marker_ang], marker_id])
        cv2.circle(imgray, (int(x + w / 2), int(y + h / 2)), 2, (255, 0, 0), -1)
        cv2.putText(imgray, f'{id}, ({int(x + w / 2)}, {int(y + h / 2)})', (int(x + w / 2 + 5), int(y + h / 2)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, 230, 0, cv2.LINE_AA)

    cv2.imshow("thresh", thresh)
    cv2.imshow("imgray", imgray)
    print(f"cimarkers: {cimarkers}")
    cv2.waitKey(1)

    spoints = []
    markers_name = []
    # points=[{'name': 'p_0', 'coordinates': [764, 600, -90]}, {'name': 'p_1', 'marker_id': '12'}, {'name': 'p_2', 'coordinates': [1371, 126, 0]}, {'name': 'p_3', 'marker_id': '99'}, {'name': 'p_4', 'marker_id': '199'}, {'name': 'p_5', 'coordinates': [130, 141, 180]}, {'name': 'p_6', 'coordinates': [423, 871, -30]}, {'name': 'p_7', 'marker_id': '105'}, {'name': 'p_8', 'coordinates': [144, 286, 30]}, {'name': 'p_9', 'coordinates': [1475, 520, 90]}, {'name': 'p_10', 'marker_id': '26'}]
    print(f"points: {points}")

    for i in range(len(points)):
        markers_name.append(points[i]["name"])
        try:
            vrem = points[i]["coordinates"]
            # spoints.append(["coordinates"])
            if vrem[2] == 1:
                cv2.circle(IMG1, (vrem[0], vrem[1]), 0, (0, 175, 175), -1)
            elif vrem[2] == 2:
                cv2.circle(IMG2, (vrem[0], vrem[1]), 0, (0, 175, 175), -1)
        except:
            for i2 in cimarkers:
                if int(points[i]["marker_id"]) == i2[1]:
                    spoints.append(i2[0])
                    points[i]["coordinates"] = i2[0]

    print(f"spoints: {spoints}")
    sceneImg = clip_img(IMG1, IMG2)
    mapImage = sceneImg.copy()

    def coorrob(img):
        image = img.copy()
        blurred = cv2.GaussianBlur(img, (3, 3), 0)
        cv2.imshow("blurred", blurred)

        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (146, 20, 20), (240, 240, 255))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=0)
        cv2.imshow("maskr", mask)

        # contours, hi = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=5, param1=30, param2=5, minRadius=3,
                                   maxRadius=10)

        if circles is not None and circles.size > 0:
            contr = []
            for i in circles[0, :]:
                if 3 < (math.pi * (i[2] ** 2)) < 200:
                    contr.append((i[0], i[1]))
                    cv2.circle(image, (int(i[0]), int(i[1])), int(i[2]), (0, 0, 255))
        else:
            contr = [(1, 1)]

        cx1 = 1
        cy1 = 1
        cx2 = 1
        cy2 = 1
        # print(contr)
        if len(contr) >= 1:
            cx1 = int(contr[0][0])
            cy1 = int(contr[0][1])
            if len(contr) >= 2:
                cx2 = int(contr[1][0])
                cy2 = int(contr[1][1])
            else:
                cx2 = cx1
                cy2 = cy1
                # print(cx1, cy1, cx2, cy2)
        blurred = cv2.GaussianBlur(blurred, (3, 3), 0)
        # rrob=30

        # blurred = blurred[int((cy1+cy2)/2-rrob):int((cy1+cy2)/2+rrob), int((cx1+cx2)/2-rrob):int((cx1+cx2)/2+rrob)]#min((cy1, cy2))-5:max((cy1, cy2))+5, min((cx1, cx2))-5:max((cx1, cx2))+5]

        cv2.imshow("blurred2", blurred)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (75, 102, 102), (97, 176, 179))  # blurred -> hsv

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=0)

        cv2.imshow("maskg", mask)

        # contours, hi = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, dp=1, minDist=15, param1=60, param2=8, minRadius=3,
                                   maxRadius=15)

        if circles is not None and circles.size > 0:
            contr = []
            for i in circles[0, :]:
                if 3 < (math.pi * (i[2] ** 2)) < 120:
                    if math.dist(((cx1 + cx2) / 2, (cy1 + cy2) / 2), (i[0], i[1])) < 40:
                        contr.append((i[0], i[1]))
                        cv2.circle(image, (int(i[0]), int(i[1])), int(i[2]), (0, 255, 0))
        else:
            contr = [(1, 1)]

        cx3 = 1
        cy3 = 1
        cx4 = 1
        cy4 = 1
        # print(contr)
        if len(contr) >= 1:
            cx3 = int(contr[0][0])
            cy3 = int(contr[0][1])
            if len(contr) >= 2:
                cx4 = int(contr[1][0])
                cy4 = int(contr[1][1])
            else:
                cx4 = cx3
                cy4 = cy3

        # print((cx3, cy3),(cx4, cy4))
        cv2.circle(image, (cx1, cy1), 1, (0, 10, 255))
        cv2.circle(image, (cx2, cy2), 1, (0, 10, 255))
        cv2.circle(image, (cx3, cy3), 1, (0, 255, 0))
        cv2.circle(image, (cx4, cy4), 1, (0, 255, 0))
        # cv2.drawContours(image, largest_contours, -1, (0, 255, 0), 0)
        di = float('inf')
        per = None
        for i in itertools.combinations([(cx1, cy1), (cx2, cy2), (cx3, cy3), (cx4, cy4)], 2):
            if math.dist(*i) < di:
                di = math.dist(*i)
                per = i
        for i in per:
            cv2.circle(image, i, 2, (0, 0, 255))

        poiper = (int((per[0][0] + per[1][0]) / 2), int((per[0][1] + per[1][1]) / 2))
        cv2.circle(image, poiper, 1, (0, 0, 255))

        centr = (int((cx1 + cx2 + cx3 + cx4) / 4), int((cy1 + cy2 + cy3 + cy4) / 4))
        cv2.circle(image, centr, 3, (0, 0, 255))

        robang = math.atan2(poiper[0] - centr[0], poiper[1] - centr[1])
        cv2.putText(image, str(math.degrees(robang)), (centr[0] + 5, centr[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    (0, 0, 0), 0)

        cv2.imshow("image", image)
        return centr, robang

    '''
    def orrob(sceneImg):
        global robcoord
        global robang
        imhsv = cv2.cvtColor(sceneImg, cv2.COLOR_BGR2HSV)
        blue_mask = cv2.inRange(imhsv, (100, 50, 50), (130, 255, 255))

        circles = cv2.HoughCircles(blue_mask, cv2.HOUGH_GRADIENT, 1, 10,
                      param1=30,
                      param2=10,
                      minRadius=3,
                      maxRadius=30)
        robcoord=(0, 0)
        robang=0
        if circles is not None:
            circles = np.uint16(np.around(circles))
            if len(circles[0,:])==3:
                pr1=(circles[0,:][0][0], circles[0,:][0][1])
                pr2=(circles[0,:][1][0], circles[0,:][1][1])
                pr3=(circles[0,:][2][0], circles[0,:][2][1])
                if 35<math.dist(pr1, pr2)<50:
                    robcoord=((pr1[0] + pr2[0])/2, (pr1[1] + pr2[1])/2)
                    robang=math.atan2(pr3[0]-robcoord[0], pr3[1]-robcoord[1])
                if 35<math.dist(pr2, pr3)<50:
                    robcoord=((pr2[0] + pr3[0])/2, (pr2[1] + pr3[1])/2)
                    robang=math.atan2(pr1[0]-robcoord[0], pr1[1]-robcoord[1])
                if 35<math.dist(pr1, pr3)<50:
                    robcoord=((pr1[0] + pr3[0])/2, (pr1[1] + pr3[1])/2)
                    robang=math.atan2(pr2[0]-robcoord[0], pr2[1]-robcoord[1])
    '''

    robcoord, robang = coorrob(sceneImg)
    G = navigator(sceneImg, robcoord, spoints)
    put = nx.shortest_path(G, robcoord, spoints[0], weight='weight')

    move(0, 0)
    print(robcoord)
    numpoint = 0
    numdo = None
    povfil = False
    while numpoint < len(put):
        if video1 == True:
            cap1 = cv2.VideoCapture('http://student:nto2024@10.128.73.31/mjpg/video.mjpg')
            if cap1.isOpened() == False:
                print("Cannot open input video1")
                video1 = False
                IMG1 = cv2.imread('cam1.jpg')
            else:
                _, IMG1 = cap1.read()
        else:
            IMG1 = cv2.imread('cam1.jpg')
        if video2 == True:
            cap2 = cv2.VideoCapture('http://student:nto2024@10.128.73.38/mjpg/video.mjpg')
            if cap2.isOpened() == False:
                print("Cannot open input video2")
                video2 = False
                IMG2 = cv2.imread('cam2.jpg')
            else:
                _, IMG2 = cap2.read()
        else:
            IMG2 = cv2.imread('cam2.jpg')

        sceneImg = clip_img(IMG1, IMG2)  #

        robcoord, robang = coorrob(sceneImg)

        dang = math.atan2(robcoord[0] - spoints[numpoint][0], robcoord[1] - spoints[numpoint][1])
        drm = math.dist((robcoord[0], robcoord[1]), (spoints[numpoint][0], spoints[numpoint][1]))
        rdang = robang - dang
        if rdang > math.pi:
            rdang = math.pi - rdang
        elif rdang < -math.pi:
            rdang = -math.pi - rdang
        # print(rdang)
        if povfil == False:
            if drm > 10:
                if rdang > 0.2:
                    if numdo != 'r':
                        move(75, 0)
                        numdo = 'r'
                        print('r')
                elif rdang < -0.2:
                    if numdo != 'l':
                        move(0, 75)
                        numdo = 'l'
                        print('l')
                else:
                    if numdo != 's':
                        move(75, 75)
                        numdo = 's'
                        print('s')
            else:
                '''
                if numdo!='f':
                    move(65, -65)
                    numdo='f'
                    print('f')
                '''
                if spoints[numpoint][2] != None:
                    rpang = robang - math.radians(spoints[numpoint][2])
                    # if rpang>math.pi:
                    #    rpang=math.pi-rpang
                    # elif rpang<-math.pi:
                    #    rpang=-math.pi-rpang
                    if rpang > 0.040:
                        if numdo != 'rn':
                            move(60, -60)
                            numdo = 'rn'
                            print('rn')
                    elif rpang < -0.040:
                        if numdo != 'ln':
                            move(-60, 60)
                            numdo = 'ln'
                            print('ln')
                    else:
                        print(f"nmark: {numpoint}")
                        if spoints[numpoint][2] != None:
                            print(f"angmark: {math.radians(spoints[numpoint][2])}")
                        else:
                            print(f"angmark: {spoints[numpoint][2]}")
                        print(f"out: {markers_name[numpoint]} OK")

                        move(0, 0)
                        time.sleep(1)
                        numpoint += 1
                else:
                    print(f"nmark: {numpoint}")
                    if spoints[numpoint][2] != None:
                        print(f"angmark: {math.radians(spoints[numpoint][2])}")
                    else:
                        print(f"angmark: {spoints[numpoint][2]}")
                    print(f"out: {markers_name[numpoint]} OK")

                    move(0, 0)
                    time.sleep(1)
                    numpoint += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite(f'photo4.jpg', sceneImg)
        # print('task.setMotorVoltage(0, v)')
        cv2.imshow('Scene', sceneImg)
        cv2.waitKey(3)  # мс
        # time.sleep(1)
    turn_steps(90, 360)
    move(0, 0)
    wait()
    task.stop()


if __name__ == '__main__':
    os.environ["TASK_ID"] = '36'
    os.environ["SERVER_ADDRESS"] = '10.128.73.40'
    os.environ["SERVER_PORT"] = '8000'
    os.environ["CAMERA_1"] = '0'
    os.environ["CAMERA_2"] = '0'

    ## Запуск задания и таймера (внутри задания)
    task = Task()
    print('1')
    try:
        task.start()
        task.getTask()
    except Exception as e:
        print(e)
    print('1')

    solve(task)
    '''
    try:
        solve(task)
    except Exception as e:
        print(e)
    '''

