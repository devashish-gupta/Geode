'''
This is where the base classes are defined, which the API interacts with
'''
import sys
sys.path.append('../')

import numpy as np
from PIL import Image
from typing import List, Union, Dict
from enum import Enum
from shapely.geometry.polygon import Polygon, Point
from scipy.interpolate import Rbf
import random
from pprint import pformat


class PatchType(Enum):
    raster_only = 0
    vector_only = 1
    dual = 2

class RasterType(Enum):
    color = 0
    non_color = 1
    binary = 2

class DataPoint():
    def __init__(self, x, y, name: str, data: float = None):
        self.point = Point(x, y)
        self.name = name
        self.data = data


class GeoPatch():
    '''
    Primary class that represents a geospatial patch with vector/raster data
    '''
    def __init__(
            self, 
            type: PatchType,
            raster_data: Union[Image.Image, np.ndarray] = None, 
            vector_data: Dict = None) -> None:
              
        self.type = type
        self.raster_data = raster_data
        self.vector_data = vector_data

        '''
        sample vector data:
        self.vector_data = {
            'location': [float, float], # compulsory
            'bbox': List[float], # [min_lat, max_lat, min_lon, max_lon], compulsory
            'points': List[DataPoint], # optional
            'boundary': List[Polygon] # optional
        }

        sample raster data:
        self.raster_data = {
            'name': str, 
            'type': RasterType,
            'colormap': str, # optional
            'data': np.ndarray
        }
        '''

    def __str__(self):
        return f"GeoPatch(\n\ttype = {self.type},\n\traster_data = {pformat(self.raster_data)},\n\tvector_data = {pformat(self.vector_data)}\n)"

    def get_type(self) -> PatchType:
        return self.type

    def set_type(self, type: PatchType):
        self.type = type

    # raster data related methods
    def get_raster_data(self) -> Dict:
        if self.raster_data is not None:
            return self.raster_data
        
    def set_raster_data(self, raster_data: Dict) -> None:
        self.raster_data = raster_data

    def set_raster_data_from_points(self, points: List[List[float]], name=None, type=None, colormap='gray') -> None:
        # performing RBF interpolation
        coordinates = np.array([[point[0], point[1]] for point in points])
        values = np.array([point[2] for point in points])

        # define grid for raster data
        latitudes = np.linspace(np.min(coordinates[:, 0]), np.max(coordinates[:, 0]), 100)
        longitudes = np.linspace(np.min(coordinates[:, 1]), np.max(coordinates[:, 1]), 100)
        grid_lat, grid_lon = np.meshgrid(latitudes, longitudes)
        grid_coordinates = np.vstack([grid_lat.ravel(), grid_lon.ravel()]).T

        # perform RBF interpolation
        rbf = Rbf(coordinates[:, 0], coordinates[:, 1], values, function='linear')
        interpolated_values = rbf(grid_coordinates[:, 0], grid_coordinates[:, 1])

        # reshape interpolated values to match grid shape
        data = np.flip(np.transpose(interpolated_values.reshape(grid_lat.shape)), axis=0)
        self.raster_data = {
            'name': name, 
            'type': type,
            'colormap': colormap,
            'data': data
        }

    def sample_random_points(self, num_points: int = 10) -> List:
        # returns randomly sampled points within the patch's bounding box
        min_lat, max_lat, min_lon, max_lon = self.vector_data['bbox']
        random_points = []
        for _ in range(num_points):
            # Generate random latitude and longitude within the bounds
            random_lat = random.uniform(min_lat, max_lat)
            random_lon = random.uniform(min_lon, max_lon)
            random_points.append([random_lat, random_lon])
        return random_points


    # vector data related methods
    def get_vector_data(self) -> Dict:
        return self.vector_data
    
    def set_vector_data(self, vector_data) -> None:
        self.vector_data = vector_data

    def get_boundary(self) -> List[Polygon]:
        return self.vector_data['boundary']

    def set_boundary(self, boundary: List[Polygon]) -> None:
        self.vector_data['boundary'] = boundary

    def get_bbox(self) -> List[float]:
        if 'bbox' in self.vector_data:
            return self.vector_data['bbox']
        
    def set_bbox(self, bbox: List[float]) -> None:
        self.vector_data['bbox'] = bbox

    def get_location(self) -> List[float]:
        if 'location' in self.vector_data:
            return self.vector_data['location']
        return None
    
    def set_location(self, location: List[float]) -> None:
        self.vector_data['location'] = location


    