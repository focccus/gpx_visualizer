# %%
import glob
import gpxpy
import gpxpy.gpx
import pandas as pd
import os

#%%
longitudeFactor = 0.5855
maxLong = 0
minLong = float("inf")
maxLat = 0
minLat = float("inf")

m = None
n = None
for file in [f for f in os.listdir("gpx") if ".gpx" in f]:
    with open("gpx/" + file, "r") as f:
        gpx = gpxpy.parse(f)
        # print(gpx.name)
        for p in gpx.tracks[0].segments[0].points:
            if p.longitude > maxLong:
                maxLong = p.longitude
            if p.latitude > maxLat:
                maxLat = p.latitude
                n = gpx
            if p.longitude < minLong:
                minLong = p.longitude
            if p.latitude < minLat:
                minLat = p.latitude
                m = gpx


# %%
print("Min: ({},{}), Max: ({},{})".format(minLong, minLat, maxLong, maxLat))
center = (51.0, 10.0)

maxd = max(
    (maxLong - center[1]) * longitudeFactor, 
    (center[1] - minLong) * longitudeFactor, 
    maxLat - center[0], 
    center[0] - minLat
)
print(maxd)

# %%
