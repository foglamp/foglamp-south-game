
from abc import ABC, abstractmethod
import http.client
import json
import datetime
import sys

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host="pi0-mark.local"
port=8081

last_processed = None
max_red = None
max_green = None
max_blue = None
max_lateral = None
max_linear = None
max_flip = None

red_points = 0
green_points = 0
blue_points = 0
linear_points = 0
lateral_points = 0
flip_points = 0

fmt = "%Y-%m-%d %H:%M:%S.%f"

conn = http.client.HTTPConnection("{0}:{1}".format(host, port))

while 1:
    points = 0
    conn.request('GET', url='/fledge/asset/points%2Fred/points')
    r = conn.getresponse()
    res = r.read().decode()
    red = json.loads(res)
    conn.request('GET', url='/fledge/asset/points%2Fgreen/points')
    r = conn.getresponse()
    res = r.read().decode()
    green = json.loads(res)
    conn.request('GET', url='/fledge/asset/points%2Fblue/points')
    r = conn.getresponse()
    res = r.read().decode()
    blue = json.loads(res)
    conn.request('GET', url='/fledge/asset/points%2Faccelerometer/points?limit=50')
    r = conn.getresponse()
    res = r.read().decode()
    linear = json.loads(res)
    conn.request('GET', url='/fledge/asset/points%2Flateral/points?limit=50')
    r = conn.getresponse()
    res = r.read().decode()
    lateral = json.loads(res)
    conn.request('GET', url='/fledge/asset/points%2Fflip/points')
    r = conn.getresponse()
    res = r.read().decode()
    flip = json.loads(res)

    for i in red:
        red_time = datetime.datetime.strptime(i["timestamp"], fmt)
        if last_processed is None or red_time > last_processed:
            red_points += i["points"]
        if max_red is None or red_time > max_red:
            max_red = red_time

    for i in green:
        green_time = datetime.datetime.strptime(i["timestamp"], fmt)
        if last_processed is None or green_time > last_processed:
            green_points += i["points"]
        if max_green is None or green_time > max_green:
            max_green = green_time

    for i in blue:
        blue_time = datetime.datetime.strptime(i["timestamp"], fmt)
        if last_processed is None or blue_time > last_processed:
            blue_points += i["points"]
        if max_blue is None or blue_time > max_blue:
            max_blue = blue_time

    for i in linear:
        linear_time = datetime.datetime.strptime(i["timestamp"], fmt)
        if last_processed is None or linear_time > last_processed:
            linear_points += i["points"]
        if max_linear is None or linear_time > max_linear:
            max_linear = linear_time

    for i in lateral:
        lateral_time = datetime.datetime.strptime(i["timestamp"], fmt)
        if last_processed is None or lateral_time > last_processed:
            lateral_points += i["points"]
        if max_lateral is None or lateral_time > max_lateral:
            max_lateral = lateral_time

    for i in flip:
        flip_time = datetime.datetime.strptime(i["timestamp"], fmt)
        if last_processed is None or flip_time > last_processed:
            flip_points += i["points"]
        if max_flip is None or flip_time > max_red:
            max_flip = flip_time

    if last_processed is None:
        last_processed = max_red
    elif max_red is not None and max_red > last_processed:
        last_processed = max_red
    if last_processed is None:
        last_processed = max_green
    elif max_green is not None and max_green > last_processed:
        last_processed = max_green
    if last_processed is None:
        last_processed = max_blue
    elif max_blue is not None and max_blue > last_processed:
        last_processed = max_blue
    if last_processed is None:
        last_processed = max_linear
    elif max_linear is not None and max_linear > last_processed:
        last_processed = max_linear
    if last_processed is None:
        last_processed = max_lateral
    elif max_lateral is not None and max_lateral > last_processed:
        last_processed = max_lateral
    if last_processed is None:
        last_processed = max_flip
    elif max_flip is not None and max_flip > last_processed:
        last_processed = max_flip

    points = red_points + green_points + blue_points + linear_points + lateral_points + flip_points;

    # print("Red: ", red_points, " Green: ", green_points, " Blue: ", blue_points, " Linear Acceleration: ", round(linear_points, 1), " Lateral Acceleration: ", round(lateral_points, 1), " Flip: ", flip_points, " Total: ", round(points, 1));
    print(red_points, green_points, blue_points, round(linear_points, 1), round(lateral_points, 1), flip_points, round(points,1))

conn.close()
