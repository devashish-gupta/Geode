from .base import GeoPatch, PatchType, RasterType, DataPoint
from shapely.geometry.polygon import Polygon
from geopy.geocoders import Nominatim
from typing import Union, Tuple
from dotenv import load_dotenv
import os
import requests as req
import copy


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
                                      'points': [DataPoint(location.latitude, location.longitude, name='Location')],
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
                                      'boundary': boundary_polygons,
                                      'points': None})
        return patch
    else: 
        return None
    

def humidity_expert(patch: GeoPatch, mode: str = 'patch') -> Union[GeoPatch, Tuple[float, GeoPatch]]:
    '''
    Retrieves humidity (%) values throughout a geographical patch as raster data, or at the central location of a patch based on mode.

    Parameters:
        patch (GeoPatch): Geographical patch for which the humidity is to be retrieved.
        mode (str): Possible values: ['patch', 'point']. To specify whether to retrieve humidity data for the entire patch or a single point.

    Returns:
        GeoPatch: patch with average precipitation in ml as raster data. (if mode == 'patch')
        float, GeoPatch: value of the humidity and the GeoPatch with a data point added for visualization, with the humidity value (if mode == 'point')
    '''
    # edge case
    if patch is None or 'location' not in patch.vector_data:
        return None
    
    # preparing http request
    load_dotenv()
    key = os.environ['WEATHER_API_KEY']

    if mode == 'patch':
        # sampling random points within the patch bounding box
        points = patch.sample_random_points(num_points=20)

        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q=bulk"
        headers = {'Content-Type': 'application/json'}
        data = {'locations': [{'q': f'{point[0]},{point[1]}'} for point in points]}

        # sending the request to WeatherAPI.com
        try:
            response = req.post(url, headers=headers, json=data)
            response.raise_for_status()
            data = response.json()['bulk']
            
            values = [] # air quality parameter values
            for loc in data:
                values.append(loc['query']['current']['humidity'])
            data_points = [[point[0], point[1], value] for value, point in zip(values, points)]

            out_patch = copy.deepcopy(patch)
            out_patch.set_raster_data_from_points(data_points, name='Humidity (%)', type=RasterType.non_color, colormap='Greys') # rbf regression
            return out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
        
    elif mode == 'point':
        loc = patch.vector_data['location']
        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={loc[0]},{loc[1]}"

        # sending the request to WeatherAPI.com
        try:
            response = req.get(url=url)
            response.raise_for_status()
            data = response.json()
            value = data['current']['humidity']

            out_patch = copy.deepcopy(patch)
            out_patch.vector_data['points'] = [DataPoint(loc[0], loc[1], name='Humidity (%)', data=value)]
            return value, out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
    else:
        raise ValueError('Unknown mode specified for humidity expert.')


def precipitation_expert(patch: GeoPatch, mode: str = 'patch') -> Union[GeoPatch, Tuple[float, GeoPatch]]:
    '''
    Retrieves precipitation values in mm throughout a geographical patch as raster data, or at the central location of a patch based on mode.

    Parameters:
        patch (GeoPatch): Geographical patch for which the precipitation is to be retrieved.
        mode (str): Possible values: ['patch', 'point']. To specify whether to retrieve precipitation data for the entire patch or a single point.

    Returns:
        GeoPatch: patch with precipitation as raster data.
        float, GeoPatch: value of the precipitation and the GeoPatch with a data point added for visualization, with the precipitation value (if mode == 'point')
    '''
    # edge case
    if patch is None or 'location' not in patch.vector_data:
        return None
    
    # preparing http request
    load_dotenv()
    key = os.environ['WEATHER_API_KEY']

    if mode == 'patch':
        # sampling random points within the patch bounding box
        points = patch.sample_random_points(num_points=20)

        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q=bulk"
        headers = {'Content-Type': 'application/json'}
        data = {'locations': [{'q': f'{point[0]},{point[1]}'} for point in points]}

        # sending the request to WeatherAPI.com
        try:
            response = req.post(url, headers=headers, json=data)
            response.raise_for_status()
            data = response.json()['bulk']
            
            values = [] # air quality parameter values
            for loc in data:
                values.append(loc['query']['current']['precip_mm'])
            data_points = [[point[0], point[1], value] for value, point in zip(values, points)]

            out_patch = copy.deepcopy(patch)
            out_patch.set_raster_data_from_points(data_points, name='Precipitation (mm)', type=RasterType.non_color, colormap='Blues') # rbf regression
            return out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
        
    elif mode == 'point':
        loc = patch.vector_data['location']
        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={loc[0]},{loc[1]}"

        # sending the request to WeatherAPI.com
        try:
            response = req.get(url=url)
            response.raise_for_status()
            data = response.json()
            value = data['current']['precip_mm']

            out_patch = copy.deepcopy(patch)
            out_patch.vector_data['points'] = [DataPoint(loc[0], loc[1], name='Precipitation (mm)', data=value)]
            return value, out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
    else:
        raise ValueError('Unknown mode specified for precipitation expert.')
    

def temperature_expert(patch: GeoPatch, mode: str = 'patch') -> Union[GeoPatch, Tuple[float, GeoPatch]]:
    '''
    Retrieves temperature values (Celcius) throughout a geographical patch as raster data, or at the central location of a patch based on mode.

    Parameters:
        patch (GeoPatch): Geographical patch for which the temperature is to be retrieved.
        mode (str): Possible values: ['patch', 'point']. To specify whether to retrieve temperature data for the entire patch or a single point.

    Returns:
        GeoPatch: patch with temperature as raster data.
        float, GeoPatch: value of the temperature and the GeoPatch with a data point added for visualization, with the temperature value (if mode == 'point')
    '''
    # edge case
    if patch is None or 'location' not in patch.vector_data:
        return None
    
    # preparing http request
    load_dotenv()
    key = os.environ['WEATHER_API_KEY']

    if mode == 'patch':
        # sampling random points within the patch bounding box
        points = patch.sample_random_points(num_points=20)

        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q=bulk"
        headers = {'Content-Type': 'application/json'}
        data = {'locations': [{'q': f'{point[0]},{point[1]}'} for point in points]}

        # sending the request to WeatherAPI.com
        try:
            response = req.post(url, headers=headers, json=data)
            response.raise_for_status()
            data = response.json()['bulk']
            
            values = [] # temperature values
            for loc in data:
                values.append(loc['query']['current']['temp_c'])
            data_points = [[point[0], point[1], value] for value, point in zip(values, points)]

            out_patch = copy.deepcopy(patch)
            out_patch.set_raster_data_from_points(data_points, name='Temperature (°C)', type=RasterType.non_color, colormap='magma') # rbf regression
            return out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
        
    elif mode == 'point':
        loc = patch.vector_data['location']
        url = f"http://api.weatherapi.com/v1/current.json?key={key}&q={loc[0]},{loc[1]}"

        # sending the request to WeatherAPI.com
        try:
            response = req.get(url=url)
            response.raise_for_status()
            data = response.json()
            value = data['current']['precip_mm']

            out_patch = copy.deepcopy(patch)
            out_patch.vector_data['points'] = [DataPoint(loc[0], loc[1], name='Temperature (°C)', data=value)]
            return value, out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
    else:
        raise ValueError('Unknown mode specified for precipitation expert.')


def air_quality_expert(patch: GeoPatch, parameter: str = 'pm2_5', mode: str = 'patch') -> Union[GeoPatch, Tuple[float, GeoPatch]]:
    '''
    Retrieves a particular air quality parameter throughout a geographical patch as raster data, or at the central location of a patch based on mode.

    Parameters:
        patch (GeoPatch): Geographical patch for which the air quality index is to be evaluated. patch has latitude and longitude information.
        parameter (str): The air quality parameter to be retrieved. Possible values: ['co', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'us-epa-index']
        mode (str): Possible values: ['patch', 'point']. To specify whether to retrieve air quality data for the entire patch or a single point.

    Returns:
        GeoPatch: patch with the chosen air quality parameter plotted as raster data accessible as GeoPatch.raster_data['data'] (if mode == 'patch')
        float, GeoPatch: value of the air quality parameter and the GeoPatch with a data point added for visualization, with the air quality parameter value (if mode == 'point')
    '''
    param_info = {
        'co': ('Carbon Monoxide (μg/m3)', 'Greys'),
        'no2': ('Nitrogen dioxide (μg/m3)', 'Oranges'),
        'o3': ('Ozone (μg/m3)', 'Blues'),
        'so2': ('Sulfur Dioxide (μg/m3)', 'YlOrBr'),
        'pm2_5': ('PM2.5 (μg/m3)', 'magma'),
        'pm10': ('PM10 (μg/m3)', 'magma'),
        'us-epa-index': ('US - EPA Index', 'magma')
    }

    # edge cases
    if patch is None or parameter not in param_info.keys():
        return None

    # preparing http request
    load_dotenv()
    key = os.environ['WEATHER_API_KEY']

    if mode == 'patch':
        # sampling random points within the patch bounding box
        points = patch.sample_random_points(num_points=20)

        url = f"http://api.weatherapi.com/v1/current.json?key={key}&aqi=yes&q=bulk"
        headers = {'Content-Type': 'application/json'}
        data = {'locations': [{'q': f'{point[0]},{point[1]}'} for point in points]}

        # sending the request to WeatherAPI.com
        try:
            response = req.post(url, headers=headers, json=data)
            response.raise_for_status()
            data = response.json()['bulk']
            print(data)
            
            values = [] # air quality parameter values
            for loc in data:
                values.append(loc['query']['current']['air_quality'][parameter])

            data_points = [[point[0], point[1], value] for value, point in zip(values, points)]

            out_patch = copy.deepcopy(patch)
            info = param_info[parameter]
            out_patch.set_raster_data_from_points(data_points, name=info[0], type=RasterType.non_color, colormap=info[1]) # rbf regression
            return out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
        
    elif mode == 'point':
        loc = patch.vector_data['location']
        url = f"http://api.weatherapi.com/v1/current.json?key={key}&aqi=yes&q={loc[0]},{loc[1]}"

        # sending the request to WeatherAPI.com
        try:
            response = req.get(url=url)
            response.raise_for_status()
            data = response.json()
            value = data['current']['air_quality'][parameter]

            out_patch = copy.deepcopy(patch)
            info = param_info[parameter]
            out_patch.vector_data['points'] = [DataPoint(loc[0], loc[1], name=info[0], data=value)]
            return value, out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
    else:
        raise ValueError('Unknown mode specified for air quality expert.')


def elevation_expert(patch: GeoPatch, mode: str = 'patch') -> Union[GeoPatch, Tuple[float, GeoPatch]]:
    '''
    Retrieves elevation values throughout a geographical patch as raster data, or at the central location of a patch based on mode.

    Parameters:
        patch (GeoPatch): Geographical patch for which the elevation is to be retrieved.
        mode (str): Possible values: ['patch', 'point']. To specify whether to retrieve elevation data for the entire patch or a single point.

    Returns:
        GeoPatch: patch with elevation (m) as raster data. (if mode == 'patch')
        float, GeoPatch: value of the elevation and the GeoPatch with a data point added for visualization, with the elevation value (if mode == 'point')
    '''
    # edge case
    if patch is None or 'location' not in patch.vector_data:
        return None
    
    # preparing http request
    if mode == 'patch':
        # sampling random points within the patch bounding box
        points = patch.sample_random_points(num_points=100)
        
        lats = ','.join([str(f'{point[0]:.2f}') for point in points])
        lons = ','.join([str(f'{point[1]:.2f}') for point in points])
        url = f'https://api.open-meteo.com/v1/elevation?latitude={lats}&longitude={lons}'

        # sending the request to open-meteo.com
        try:
            response = req.get(url)
            response.raise_for_status()
            data = response.json()
            values = data['elevation'] # elevation values
            
            data_points = [[point[0], point[1], value] for value, point in zip(values, points)]
            out_patch = copy.deepcopy(patch)
            out_patch.set_raster_data_from_points(data_points, name='Elevation (m)', type=RasterType.non_color, colormap='terrain') # rbf regression
            return out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
        
    elif mode == 'point':
        loc = patch.vector_data['location']
        url = f'https://api.open-meteo.com/v1/elevation?latitude={loc[0]}&longitude={loc[1]}'

        # sending the request to open-meteo.com
        try:
            response = req.get(url)
            response.raise_for_status()
            data = response.json()
            value = data['elevation']

            out_patch = copy.deepcopy(patch)
            out_patch.vector_data['points'] = [DataPoint(loc[0], loc[1], name='Elevation (m)', data=value)]
            return value, out_patch

        except req.exceptions.RequestException as e:
            print("Error:", e)
            return None
    else:
        raise ValueError('Unknown mode specified for elevation expert.')

    