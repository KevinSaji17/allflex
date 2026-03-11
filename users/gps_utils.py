"""
GPS Utilities for Location Verification
----------------------------------------
Haversine formula for distance calculation and proximity verification.
"""
import math
from typing import Tuple, Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on earth (specified in decimal degrees).
    Returns distance in meters.
    
    Args:
        lat1: Latitude of point 1
        lon1: Longitude of point 1
        lat2: Latitude of point 2
        lon2: Longitude of point 2
    
    Returns:
        Distance in meters
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r


def is_within_proximity(
    user_lat: float, 
    user_lon: float, 
    gym_lat: float, 
    gym_lon: float, 
    max_distance_meters: float = 100.0
) -> Tuple[bool, float]:
    """
    Check if user is within acceptable proximity of gym location.
    
    Args:
        user_lat: User's current latitude
        user_lon: User's current longitude
        gym_lat: Gym's latitude
        gym_lon: Gym's longitude
        max_distance_meters: Maximum allowed distance in meters (default: 100m)
    
    Returns:
        Tuple of (is_within_range: bool, actual_distance: float)
    """
    distance = haversine_distance(user_lat, user_lon, gym_lat, gym_lon)
    is_close = distance <= max_distance_meters
    return (is_close, distance)


def validate_gps_coordinates(lat: Optional[float], lon: Optional[float]) -> bool:
    """
    Validate GPS coordinates are within valid ranges.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        True if coordinates are valid, False otherwise
    """
    if lat is None or lon is None:
        return False
    
    # Latitude must be between -90 and 90
    # Longitude must be between -180 and 180
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lon <= 180):
        return False
    
    return True


def format_distance(meters: float) -> str:
    """
    Format distance in human-readable format.
    
    Args:
        meters: Distance in meters
    
    Returns:
        Formatted string (e.g., "50m", "1.2km")
    """
    if meters < 1000:
        return f"{int(meters)}m"
    else:
        km = meters / 1000
        return f"{km:.1f}km"
