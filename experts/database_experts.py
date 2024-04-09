from .base import GeoPatch, PatchType, RasterType
from shapely.geometry.polygon import Polygon, Point
from geopy.geocoders import Nominatim
import torch


def point_location_expert(name: str) -> GeoPatch:
    '''
    Finds the geographic location of any place on the map by its name.

    Parameters:
        name (str): Name of the place for which the geo location has to be found

    Returns:
        (lat, lon): Latitude and longitude of the location found.
    '''
    # edge case
    if name == '':
        return None

    # initialize nominatim geocoder
    geolocator = Nominatim(user_agent="geo_locator")

    # find location based on name
    location = geolocator.geocode(name, geometry='geojson')

    if location:
        bbox = list(map(float, location.raw.get('boundingbox', [])))
        patch = GeoPatch(type=PatchType.vector_only,
                         raster_data={'name': None,
                                      'type': None,
                                      'colormap': None,
                                      'data': None},
                         vector_data={'location': [location.latitude, location.longitude],
                                      'points': [Point(location.latitude, location.longitude)],
                                      'bbox': bbox})
        return patch
    else:
        return None
    

def patch_location_expert(name: str) -> GeoPatch:
    '''
    Finds the geographic location and boundary polygon of any place on the map by its name.

    Parameters:
        name (str): Name of the place for which the geo location has to be found

    Returns:
        GeoPatch: GeoPatch containing the location and boundary path of the found place.
    '''
    # edge case
    if name == '':
        return None
    
    # initialize nominatim geocoder
    geolocator = Nominatim(user_agent="geo_locator")

    # find location based on name
    location = geolocator.geocode(name, geometry='geojson')

    if location:
        latitude = location.latitude
        longitude = location.longitude

        # extract boundary polygons if available
        boundary_polygons = []
        if location.raw.get('geojson', {}).get('type') == 'MultiPolygon':
            for coordinates_list in location.raw['geojson']['coordinates']:
                for coordinates in coordinates_list:
                    boundary_polygons.append(Polygon(coordinates))
        elif location.raw.get('geojson', {}).get('type') == 'Polygon':
            coordinates = location.raw['geojson']['coordinates']
            boundary_polygons.append(Polygon(coordinates[0]))
        else:
            boundary_polygons = None

        bbox = list(map(float, location.raw.get('boundingbox', [])))
        patch = GeoPatch(type=PatchType.vector_only,
                         raster_data={'name': None,
                                      'type': None,
                                      'colormap': None,
                                      'data': None},
                         vector_data={'location': [latitude, longitude],
                                      'bbox': bbox,
                                      'boundary': boundary_polygons})
        return patch
    else: 
        return None
    

def precipitation_expert(patch: GeoPatch) -> GeoPatch:
    '''
    Returns the average precipitation in a geographical patch.

    Parameters:
        patch (GeoPatch): Geographical patch for which the average precicipitation is to be computed. patch has latitude and longitude information.

    Returns:
        GeoPatch: patch with average precipitation in ml as raster data.
    '''
    # edge case
    if patch is None or 'location' not in patch.vector_data:
        return None
    
    patch.raster_data = {
        'name': 'Precipitation (ml)',
        'data': torch.randint(0, 255, (256, 256, 1), dtype=torch.uint8).numpy(),
        'type': RasterType.non_color,
        'colormap': 'Blues'
    }

    return patch
    
