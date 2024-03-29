'''
This is where the base classes are defined, which the API interacts with
'''
import numpy as np
from PIL import Image
from typing import List, Union
from enum import Enum

class PatchType(Enum):
    points = 0
    raster_only = 1
    vector_only = 2
    dual = 3

class GeoPatch():
    '''
    Primary class that represents a geospatial patch with vector/raster data
    '''
    def __init__(
            self, 
            bounds: List[List[int]],
            type: PatchType,
            raster_data: Union[Image.Image, np.ndarray]=None, 
            vector_data=None) -> None:
              
        self.bounds = bounds
        self.type = type
        self.raster_data = raster_data
        self.vector_data = vector_data

    def set_raster_data(self, raster_data) -> None:
        self.raster_data = raster_data

    def sample_raster_data(self) -> None:
        pass

    def get_raster_data(self) -> Union[Image.Image, np.ndarray]:
        if self.raster_data is not None:
            return self.raster_data
        else:
            self.sample_raster_data()
            return self.raster_data

    def set_vector_data(self, vector_data) -> None:
        self.vector_data = vector_data

    def get_bounds(self):
        return self.bounds


    