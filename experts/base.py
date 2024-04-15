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

    def __str__(self):
        return f'DataPoint(name={self.name},\n\tPoint={self.point},\n\tdata={self.data}\n)'


class GeoPatch():
    '''
    Primary class representing a geospatial patch with vector/raster data.

    Attributes
    ----------
    type: PatchType
        Type of geographical patch based on the data it contains.
    raster_data: dict
        Stores raster data and related information.
        - 'name' (str): Name of the raster data stored. (mandatory)
        - 'type' (RasterType): Type of raster data stored, whether color, non_color, or binary (mandatory)
        - 'colormap' (str): String representing a color name. (optional)
        - 'data' (np.ndarray): NumPy array containing the raster data. (mandatory)
    vector_data: dict
        Stores vector data and related information.
        - 'location' ([float, float]): Latitude and longitude of the location that the patch represents (mandatory).
        - 'bbox' (List[float]): Bounding box coordinates of the boundary of the patch [min_lat, max_lat, min_lon, max_lon] (mandatory).
        - 'points' (List[DataPoint]): Data points corresponding to the patch, displayed on the map (optional).
        - 'boundary' (List[shapely.geometry.Polygon]): Boundary polygon of the patch (mandatory).
    '''
    def __init__(
            self, 
            type: PatchType = PatchType.dual,
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
        return f"GeoPatch(\n\ttype = {self.type},\n\traster_data = {pformat(self.raster_data, indent=2)},\n\tvector_data = {pformat(self.vector_data, indent=2)}\n)"

    # raster data related methods
    def get_raster_data(self) -> Dict:
        if self.raster_data is not None:
            return self.raster_data
        
    def set_raster_data(self, raster_data: Dict) -> None:
        '''
        Set the raster data for the GeoPatch.
        
        Parameters
        ----------
        raster_data : Dict
            Raster data and related information.
        '''
        self.raster_data = raster_data

    def set_raster_data_from_points(self, points: List[List[float]], name=None, type=None, colormap='gray') -> None:
        '''
        Sets the raster data across the patch from a list of points
        
        Parameters
        ----------
        points : List[List[float]]
            List of points of the form [[lat0, lon0, value0], ...]
        name : str, optional
            Name of the raster data.
        type : RasterType, optional
            Type of the raster data. Possible values: [RasterType.color, RasterType.non_color, RasterType.binary]
        colormap : str, optional
            Colormap for the raster data.
        '''
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
        '''
        Get the vector data stored in the GeoPatch, potentially containing 'points', 'boundary', 'location', 'bbox'.
        '''
        return self.vector_data
    
    def set_vector_data(self, vector_data) -> None:
        self.vector_data = vector_data

    def get_boundary_polygons(self) -> List[Polygon]:
        '''
        Get the boundary polygon of the geographic location represented by the patch.
        
        Returns
        -------
        List[Polygon]
            List of shapely.geometry.Polygon representing the boundary.
        '''
        return self.vector_data['boundary']
    
    def get_area(self) -> float:
        '''
        Gets boundary area for the patch in million sq km.

        Returns
        -------
        float: Area of the patch in million sq km.
        '''
        area = 0
        for poly in self.get_boundary_polygons():
            area += poly.area

        return area

    def set_boundary_polygons(self, boundary: List[Polygon]) -> None:
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

    def get_data_points(self) -> List[DataPoint]:
        '''
        Get the data points associated with the locations within the patch.

        Returns
        -------
        List[DataPoint]: list of data points containing latitude, longitude, name and data.
        '''
        if 'points' in self.vector_data:
            return self.vector_data['points']


    