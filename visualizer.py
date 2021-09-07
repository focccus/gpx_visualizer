# %%

import gpxpy
import gpxpy.gpx
import pandas as pd
from math import sqrt
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime


def distance(a, b):
    return sqrt((a.latitude - b.latitude) ** 2 + (a.longitude - b.longitude) ** 2)


def point_line_distance(point, start, end):
    if start == end:
        return distance(point, start)
    else:
        n = abs(
            (end.latitude - start.latitude) * (start.longitude - point.longitude)
            - (start.latitude - point.latitude) * (end.longitude - start.longitude)
        )
        d = sqrt(
            (end.latitude - start.latitude) ** 2
            + (end.longitude - start.longitude) ** 2
        )
        return n / d


# Ramer-Douglas-Peucker
# https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
def rdp(points, epsilon):
    dmax = 0.0
    index = 0
    i = 1
    for i in range(1, len(points) - 1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d

    if dmax >= epsilon:
        results = rdp(points[: index + 1], epsilon)[:-1] + rdp(points[index:], epsilon)
    else:
        results = [points[0], points[-1]]
    return results


def writeas(name, img):
    with open(name, "w") as f:
        img.save(f)


# %%

center = (51.0, 10.0)
size = 500
maxOffset = 0.10459313449999921  # 0.10932199999999881
longitudeFactor = 0.5855


# %%
totallength = 0
total = 1
previmg = Image.new("RGB", (size * 2, size * 2), (0, 0, 0))
font = ImageFont.truetype("arial.ttf", 20)

# Get all GPX Files
files = list(filter(lambda x: x.endswith(".gpx"), os.listdir("gpx")))
files.sort(key=lambda name: datetime.strptime(name, "%d.%m.%Y_%H_%M_%S.gpx"))

for file in files:
    with open("gpx/" + file, "r") as src:
        gpx = gpxpy.parse(src)

        # reduce points using Ramer-Douglas-Peucker
        points = rdp(gpx.tracks[0].segments[0].points, 0.00002)
        print(
            "Reduced from {} to {}".format(
                len(gpx.tracks[0].segments[0].points), len(points)
            ),
        )

        draw = ImageDraw.Draw(previmg)
        length = gpx.length_2d() / 1000

        draw.rectangle([(10, 10), (250, 110)], fill="black")
        draw.multiline_text(
            (10, 10),
            "Tour: {} \nLength: {:04.2f}km \nDuration: {:.0f}h {:.0f}min".format(
                gpx.name,
                length,
                gpx.get_duration() // 3600,
                (gpx.get_duration() % 3600) / 60,
            ),
            font=font,
            fill=(255, 255, 255),
        )
        idraw.rectangle([(10, 2 * size - 10), (170, 2 * size - 30)], fill="black")
        draw.text(
            (10, 2 * size - 30), "Total: {:.2f}km".format(totallength), font=font,
        )

        prev = previmg.copy()

        computed = []

        for i in range(0, len(points)):
            computed.append(
                (
                    (points[i].longitude - center[1]) / maxOffset * size * longitudeFactor
                    + size,
                    (points[i].latitude - center[0]) / maxOffset * size + size,
                )
            )
            totallength += length / len(points)
            if i != 0 and i % 5 == 0:
                writeas("./output/GeoAnimation {}.jpeg".format(total), prev)

                total += 1
                im = prev.copy()
                idraw = ImageDraw.Draw(im)
                color = distance(points[i - 1], points[i]) * 500

                idraw.line(
                    computed[i - 5 : i + 1],
                    fill=(
                        min(255, round(510 * color)),
                        min(255, round(510 * (1 - color))),
                        0,
                    ),
                )
                # Total Counter
                idraw.rectangle(
                    [(10, 2 * size - 10), (170, 2 * size - 30)], fill="black"
                )
                idraw.text(
                    (10, 2 * size - 30),
                    "Total: {:.2f}km".format(totallength),
                    font=font,
                )
                prev = im
        # draw full line
        draw.line(computed, fill=(255, 255, 255))
        writeas("./output/GeoAnimation {}.jpeg".format(total), previmg)
        prev = previmg.copy()
        total += 1
# for i in range(6):
#     for color in ["red", "magenta", "blue", "cyan", "green", "yellow", "white"]:
#         t.color(color)
#         t.circle(100)
#         t.left(10)

# images[0].save(
#     "./pillow_imagedraw.gif",
#     save_all=True,
#     append_images=images[1:],
#     optimize=False,
#     duration=40,
#     loop=0,
# )


# %%
