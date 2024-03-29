import cv2
import base64
import numpy as np
import math
import networkx as nx
from PIL import Image
import matplotlib.pyplot as plt
import itertools

# imageString = input()

# buffer = base64.b64decode(imageString)
# array = np.frombuffer(buffer, dtype=np.uint8)
# img = cv2.imdecode(array, flags=1)
imageFinal = Image.open('photo3.jpg')
img = cv2.imread('photo3.jpg')
# Проверка, успешно ли загрузилось изображение
if img is not None:
    print("Изображение загружено успешно!")
else:
    print("Ошибка: Изображение не загружено. Проверьте путь к файлу.")

coordrob = (930, 690)
# coordrob=tuple([int(x) for x in input().split()])
npoint = int(2)
# npoint=int(input())
# points=eval(input())

points = [{"name": "p_2", "marker_id": "63"}, {"name": "p_3",
                                               "marker_id": "55"}]  # , {"name": "p_7", "coordinates": [633, 368]}, {"name": "p_21", "coordinates": [219, 715]}, {"name": "p_1", "marker_id": "245"}, {"name": "p_5", "marker_id": "97"}, {"name": "p_18", "coordinates": [217, 76]}, {"name": "p_17", "coordinates": [397, 281]}, {"name": "p_19", "coordinates": [155, 611]}, {"name": "p_6", "coordinates": [564, 437]}, {"name": "p_10", "coordinates": [155, 76]}, {"name": "p_14", "coordinates": [540, 524]}, {"name": "p_12", "coordinates": [938, 699]}, {"name": "p_4", "marker_id": "86"}, {"name": "p_11", "coordinates": [390, 194]}, {"name": "p_22", "coordinates": [624, 523]}, {"name": "p_16", "coordinates": [150, 925]}, {"name": "p_23", "coordinates": [731, 246]}, {"name": "p_15", "coordinates": [268, 401]}, {"name": "p_8", "coordinates": [888, 824]}]

'''
points=[{"name": "p_5", "coordinates": [1232, 320]}, {"name": "p_23", "coordinates": [1070, 173]}, {"name": "p_17", "coordinates": [331, 229]},
        {"name": "p_2", "coordinates": [615, 176]}, {"name": "p_7", "coordinates": [609, 509]}, {"name": "p_9", "coordinates": [1019, 193]},
        {"name": "p_4", "coordinates": [1342, 253]}, {"name": "p_10", "coordinates": [1412, 301]}, {"name": "p_12", "coordinates": [398, 143]},
        {"name": "p_8", "coordinates": [823, 366]}, {"name": "p_6", "coordinates": [566, 320]}, {"name": "p_3", "coordinates": [1466, 439]},
        {"name": "p_13", "coordinates": [801, 279]}, {"name": "p_1", "coordinates": [105, 189]}, {"name": "p_15", "coordinates": [1402, 559]},
        {"name": "p_18", "coordinates": [1304, 321]}, {"name": "p_20", "coordinates": [807, 530]}, {"name": "p_11", "coordinates": [890, 301]},
        {"name": "p_16", "coordinates": [1136, 147]}, {"name": "p_14", "coordinates": [87, 343]}, {"name": "p_19", "coordinates": [422, 320]},
        {"name": "p_21", "coordinates": [1525, 528]}, {"name": "p_22", "coordinates": [494, 301]}]
'''
'''
imageString = input()

buffer = base64.b64decode(imageString)
array = np.frombuffer(buffer, dtype=np.uint8)
img = cv2.imdecode(array, flags=1)


coordrob=tuple(input())
npoint=int(input())

points=list(input())
'''
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



def get_graph(lines, qrCods, lines_x, lines_y, cross_near):
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
        graph.add_edge(line[len(line) - 1][0], line[len(line) - 1][1], weight=math.dist(line[len(line) - 1][0], line[len(line) - 1][1]))

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
    if not is_boder:
        return []

    return binarray


imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 201, 13)

contours, hi = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

cimarkers = []
for i, cnt in enumerate(contours):
    if cv2.contourArea(cnt) > 3000:
        # if cv2.contourArea(cnt)<10000:
        continue
    if hi[0][i][2] == -1 or hi[0][i][3] == -1:
        continue

    c, dim, ang = cv2.minAreaRect(cnt)
    box = cv2.boxPoints((c, dim, ang))
    box = np.intp(box)

    if max(dim) < 50:
        continue
    if min(dim) / max(dim) < 0.95:
        continue

    margin = 10
    x, y, w, h = cv2.boundingRect(cnt)
    mask = thresh[y - margin:y + h + margin, x - margin:x + w + margin]

    M = cv2.getRotationMatrix2D((mask.shape[0] / 2, mask.shape[1] / 2), ang, 1)
    mask = cv2.warpAffine(mask, M, (mask.shape[0], mask.shape[1]))

    clip = [round((mask.shape[0] - dim[1]) / 2), round((mask.shape[1] - dim[0]) / 2)]
    mask = mask[clip[0]:-clip[0], clip[1]:-clip[1]]

    binarray = get_mask_binarray(mask)
    if len(binarray) == 0:
        continue

    marker_id = -1
    marker_ang = 0
    idx = {
        bin2dec(binarray),
        bin2dec(update_binarray(binarray, r90_idx)),
        bin2dec(update_binarray(binarray, r180_idx)),
        bin2dec(update_binarray(binarray, r270_idx))
    }

    for i, id in enumerate(idx):
        if id > -1:
            marker_id = id
            marker_ang = i * 90 - ang
            break

    if marker_id == -1:
        continue
    cimarkers.append([[int(x + w / 2), int(y + h / 2)], id])
    # cv2.circle(img, (int(x+w/2), int(y+h/2)), 2, (255, 0, 0), -1)
    # cv2.putText(img, f'{id}, ({int(x+w/2)}, {int(y+h/2)})', (int(x+w/2+5), int(y+h/2+10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,0,255), 0, cv2.LINE_AA)
print('cimarkers')
print(cimarkers)

spoints = []
# tspoints=[]
for i in range(len(points)):
    try:
        spoints.append(points[i]["coordinates"])
    except:
        for i2 in cimarkers:

            if int(points[i]["marker_id"]) == i2[1]:
                spoints.append(i2[0])
                points[i]["coordinates"] = i2[0]

print('spoints')
print(spoints)


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
            cv2.putText(img, "skibidi dop dop yes yes", (int(box[0][0]), int(box[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,
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
    print(imageFinal.width, 10000)
    print(aa)
    je = [(662, 351), (440, 155)]
    graphFinal = get_graph(aa, je, imageFinal.width, imageFinal.height, 200)
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


navigator(img, coordrob, spoints)
cv2.destroyAllWindows()

isWritten = cv2.imwrite("photo3.jpg", img)
