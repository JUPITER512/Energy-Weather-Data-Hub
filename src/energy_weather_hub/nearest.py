import numpy as np
import pandas as pd
import json



STATIONS="./stations.csv"
# The Haversine distance is the shortest distance between two points on the surface of a sphere, measured along the sphere's surface rather than through its interior.

# For example, if you know the latitude and longitude of Berlin and Paris, you can use the Haversine formula to calculate the approximate distance between them along the Earth's surface.
'''
Why do we need it?
Locations on Earth are given by geographic coordinates:
- Latitude: how far north or south a point is from the equator.
- Longitude: how far east or west a point is from the prime meridian.
Because the Earth is approximately spherical, you cannot calculate the surface distance simply by subtracting the latitudes and longitudes. Longitude distances also vary with latitude.
The Haversine formula accounts for the Earth's curvature and calculates the great-circle distance between two locations.
'''

def haversine_distance(lon1,lat1,lon2,lat2):
    RADIUS=6371.0
    # Convert each coordinate separately (not as one np.radians([...]) list) so this
    # also works when one side is a scalar and the other is an array of many stations.
    lat1=np.radians(lat1)
    lon1=np.radians(lon1)
    lat2=np.radians(lat2)
    lon2=np.radians(lon2)
    delta_lon=lon2-lon1
    delta_lat=lat2-lat1
    a=(
        np.sin(delta_lat/2)**2 +
        np.cos(lat1)*np.cos(lat2) *
        np.sin(delta_lon/2)**2
    )


    # Protect against floating-point rounding errors
    a = np.clip(a, 0.0, 1.0)
    d=2*np.arcsin(np.sqrt(a))
    return RADIUS*d


def load_stations(path=STATIONS):
    return pd.read_csv(path)


def distances_from(station_id, stations_df):
    """Distance in km from one station to every station in stations_df (vectorized)."""
    target = stations_df.loc[stations_df["STATIONS_ID"] == station_id].iloc[0]
    return haversine_distance(
        target["LONGITUDE"], target["LATITUDE"],
        stations_df["LONGITUDE"].to_numpy(), stations_df["LATITUDE"].to_numpy()
    )


def nearest_stations(station_id, n=3, stations_df=None):
    """The n closest station ids to station_id, as [(station_id, distance_km), ...], nearest first."""
    if stations_df is None:
        stations_df = load_stations()
    distances = distances_from(station_id, stations_df)
    order = np.argsort(distances)

    ids = stations_df["STATIONS_ID"].to_numpy()[order]
    dists = distances[order]

    keep = ids != station_id  # drop the station itself (distance 0)
    return list(zip(ids[keep][:n], dists[keep][:n]))


def main():
    # Coordinates in (latitude, longitude) order
    aachen = (50.7827, 6.0941)
    grossenkneten = (52.9336, 8.25)

    # Function arguments are (longitude, latitude)
    distance = haversine_distance(
        aachen[1], aachen[0],
        grossenkneten[1], grossenkneten[0]
    )

    print(f"Distance: {distance:.2f} km")

    # Aachen is station 3 in stations.csv
    stations_df = load_stations()
    print("\nNearest stations to Aachen (id 3):")
    for station_id, dist in nearest_stations(3, n=3, stations_df=stations_df):
        name = stations_df.loc[stations_df.STATIONS_ID == station_id, "STATION_NAME"].values[0]
        print(f"  {station_id}: {name} -> {dist:.2f} km")


if __name__=="__main__":
    main()