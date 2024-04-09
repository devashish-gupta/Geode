'''
This is where the base classes are defined, which the API interacts with
'''
import sys
sys.path.append('../')

import numpy as np
from PIL import Image
from typing import List, Union, Dict
from enum import Enum
from shapely.geometry.polygon import Polygon


class PatchType(Enum):
    raster_only = 0
    vector_only = 1
    dual = 2

class RasterType(Enum):
    color = 0
    non_color = 1
    binary = 2

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
            'points': List[Point], # optional
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
        return f"GeoPatch(\n\ttype = {self.type},\n\traster_data = {self.raster_data},\n\tvector_data = {self.vector_data}\n)"

    def get_type(self) -> PatchType:
        return self.type

    def set_type(self, type: PatchType):
        self.type = type

    # raster data related methods
    def get_raster_data(self) -> Dict:
        if self.raster_data is not None:
            return self.raster_data
        
    def set_raster_data(self, raster_data) -> None:
        self.raster_data = raster_data

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



    