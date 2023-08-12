import enum
import math
import pandas as pd
import requests
import streamlit as st


class DayType(enum.Enum):
    WORKING_DAY = 1
    THURSEDAY = 3
    FRIDAY = 4


def haversine_distance(lat_1: float, lon_1: float, lat_2: float, lon_2: float):
    # Earth radius in kilometers
    earth_radius = 6371

    # Convert latitude and longitude coordinates from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat_1, lon_1, lat_2, lon_2])

    # Calculate the differences between the latitudes and longitudes
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Calculate the square of half the chord length between the points
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )

    # Calculate the angular distance in radians
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate the distance in kilometers
    distance = earth_radius * c

    return distance


st.title("Nostradamus")


cols = st.columns(2)

with cols[0]:
    origin = st.text_input("Origin", placeholder="37.271408, 49.504597")

    if not origin:
        st.error("no origin entered")
        # stop this run, please note that the main application is still running
        # and we only stop this specific run.
        st.stop()

    origin_lat, origin_lng = map(float, origin.split(","))

with cols[1]:
    dest = st.text_input("Destination", placeholder="37.27284, 49.54639")

    if not dest:
        st.error("no destination entered")
        # stop this run, please note that the main application is still running
        # and we only stop this specific run.
        st.stop()

    dest_lat, dest_lng = map(float, dest.split(","))

day_type = st.selectbox("Day Type", [dt.name for dt in DayType])

dep_time = st.time_input("Departure time")

points = pd.DataFrame(
    {
        "lat": [origin_lat, dest_lat],
        "lon": [origin_lng, dest_lng],
    },
)

st.map(points)

hd = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)

st.text(f"Haversine distance: {hd}")

if (not dep_time) or (not day_type):
    st.error("day/time information required")
    # stop this run, please note that the main application is still running
    # and we only stop this specific run.
    st.stop()

assert day_type is not None

resp = requests.post(
    "http://172.21.88.59:1378/predict",
    json={
        "origin_lat": origin_lat,
        "origin_lng": origin_lng,
        "destination_lat": dest_lat,
        "destination_lng": dest_lng,
        "hour": dep_time.hour,
        "haversine_distance": hd,
        "day_type": DayType[day_type].value,
    },
)

st.text(f"{resp.json()}")
