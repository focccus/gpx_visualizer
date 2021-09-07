# %%
import glob
import gpxpy
import gpxpy.gpx
import pandas as pd
import os

# %%


def format_distance(d):
    return (round(d, 2),)


def format_speed(s):
    return round(s * 3600.0 / 1000.0, 2)


def get_data(gpx):

    uphill, downhill = gpx.get_uphill_downhill()
    start_time, end_time = gpx.get_time_bounds()

    res = {
        "name": gpx.name,
        "waypoints": len(gpx.waypoints),
        "routes": len(gpx.routes),
        "length": round(gpx.length_2d(), 2),
        "uphill": round(uphill, 2),
        "downhill": round(downhill, 2),
        "start": start_time,
        "end": end_time,
    }

    if end_time:
        res["duration"] = end_time - start_time

    moving = gpx.get_moving_data()

    if moving:
        duration = res["duration"].seconds if "duration" in res else moving.moving_time
        if duration == 0:
            return res
        res["max_speed"] = format_speed(moving.max_speed)
        res["avg_speed"] = format_speed(res["length"] / duration)
        res["avg_moving_speed"] = format_speed(
            moving.moving_distance / moving.moving_time
        )
        res["moving"] = moving.moving_time / duration
    return res


# %%
routes = []
for file in [f for f in os.listdir("gpx") if ".gpx" in f]:
    with open("gpx/" + file, "r") as f:
        gpx = gpxpy.parse(f)
        routes.append(get_data(gpx))


# %%
df = pd.DataFrame(routes).sort_values("start").set_index("start")
df.index = df.index + pd.Timedelta(hours=2)
df.end = df.end + pd.Timedelta(hours=2)
df.index = pd.to_datetime(df.index)
df.end = pd.to_datetime(df.end)
df.to_csv("output.csv")

# %%
