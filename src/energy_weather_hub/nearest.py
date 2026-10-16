import numpy as np
import pandas as pd
import json

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
    # First, convert all coordinates from degrees to radians.
    lat1,lon1,lat2,lon2=np.radians([lat1,lon1,lat2,lon2])
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


if __name__=="__main__":
    main()