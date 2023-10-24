import datetime
import enum
import math
import pandas as pd
import requests
import streamlit as st


class DayType(enum.Enum):
    WORKING_DAY = 1
    THURSEDAY = 3
    FRIDAY = 4


def haversine_distance(
    lat_1: float, lon_1: float, lat_2: float, lon_2: float
) -> float:
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
    query_params = st.experimental_get_query_params()
    origin_lat: float | None = None
    origin_lng: float | None = None

    origin: str = ""
    if "origin" in query_params:
        origin_lat, origin_lng = (
            float(item) if item != "" else None
            for item in query_params.get("origin", ["", ""])
        )
        origin = (
            f"{origin_lat},{origin_lng}"
            if origin_lat is not None and origin_lng is not None
            else ""
        )

    origin = st.text_input(
        "Origin", placeholder="37.271408, 49.504597", value=origin
    )

    if not origin or "," not in origin:
        st.error("no origin entered")
        st.stop()

    origin_lat, origin_lng = map(float, origin.split(","))

    query_params = st.experimental_get_query_params()
    query_params["origin"] = [str(origin_lat), str(origin_lng)]
    st.experimental_set_query_params(**query_params)

with cols[1]:
    query_params = st.experimental_get_query_params()
    dest_lat: float | None = None
    dest_lng: float | None = None

    dest: str = ""
    if "dest" in query_params:
        dest_lat, dest_lng = (
            float(item) if item != "" else None
            for item in query_params.get("dest", ["", ""])
        )
        dest = (
            f"{dest_lat},{dest_lng}"
            if dest_lat is not None and dest_lng is not None
            else ""
        )

    dest = st.text_input(
        "Destination", placeholder="37.27284, 49.54639", value=dest
    )

    if not dest or "," not in dest:
        st.error("no destination entered")
        st.stop()

    dest_lat, dest_lng = map(float, dest.split(","))

    query_params = st.experimental_get_query_params()
    query_params["dest"] = [str(dest_lat), str(dest_lng)]
    st.experimental_set_query_params(**query_params)

points = pd.DataFrame(
    {
        "lat": [origin_lat, dest_lat],
        "lon": [origin_lng, dest_lng],
    },
)

st.map(points)

hd = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)

st.text(f"Haversine distance: {hd}")


cols = st.columns(2)

with cols[0]:
    query_params = st.experimental_get_query_params()
    day_type_index: int | None = None
    if "day_type" in query_params:
        day_type_index = next(
            index
            for index, dt in enumerate(DayType)
            if dt.name == query_params.get("day_type", ["-"])[0]
        )

    day_type = st.selectbox(
        "Day Type",
        [dt.name for dt in DayType],
        index=day_type_index,
    )

    if day_type is None:
        st.error("no day_type entered")
        st.stop()

    assert day_type is not None

    query_params = st.experimental_get_query_params()
    query_params["day_type"] = [day_type]
    st.experimental_set_query_params(**query_params)

with cols[1]:
    query_params = st.experimental_get_query_params()
    dep_time: datetime.time | None = None
    if "dep_time" in query_params:
        try:
            dep_time = datetime.time.fromisoformat(
                query_params.get("dep_time", [""])[0]
            )
        except ValueError:
            dep_time = None

    dep_time = st.time_input("Departure time", value=dep_time)

    if dep_time is None:
        st.error("day/time information required")
        st.stop()

    assert dep_time is not None

    query_params = st.experimental_get_query_params()
    query_params["dep_time"] = [dep_time.isoformat()]
    st.experimental_set_query_params(**query_params)

with st.spinner("Wait for ETA..."):
    resp = requests.post(
        "http://172.21.88.100:1378/predict",
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
