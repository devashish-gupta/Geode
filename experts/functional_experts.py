import copy
import numpy as np

from .base import GeoPatch, RasterType
from scipy.interpolate import griddata
import folium
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
import matplotlib.pyplot as plt
from textwrap import wrap



def imputation_expert(patch: GeoPatch) -> GeoPatch:
    '''
    Impute missing values in a patch using interpolation.

    Parameters:
        patch (GeoPatch): Input patch with missing values represented as NaN.

    Returns:
        GeoPatch: Patch with missing values imputed.
    '''
    # edge case
    if patch is None:
        return None
    
    data = patch.get_raster_data()['data']

    # mask nan values
    mask = ~np.isnan(data)

    # check if there are any known coordinates available
    if np.any(mask):
        x, y = np.meshgrid(np.arange(data.shape[1]), np.arange(data.shape[0]))

        # coordinates of known values
        known_coords = np.column_stack((x[mask], y[mask]))

        # values at known coordinates
        known_values = data[mask]

        # coordinates where values need to be imputed
        impute_coords = np.column_stack((x[~mask], y[~mask]))

        # perform interpolation
        imputed_values = griddata(known_coords, known_values, impute_coords, method='nearest')

        # reshape imputed values to match original image shape
        imputed_data = np.copy(data)
        imputed_data[~mask] = imputed_values
    else:
        # if entire matrix is nans, fill with default value or handle as needed
        default_value = 0.0
        imputed_data = np.full_like(data, default_value)

    out_patch = copy.deepcopy(patch)
    out_patch.set_raster_data({
        'data': imputed_data, 
        'type': patch.raster_data['type'], 
        'colormap': patch.raster_data['colormap']
    })

    return out_patch


def correlation_expert(patch1: GeoPatch, patch2: GeoPatch) -> float:
    '''
    Cross-correlate the raster data within two input patches.

    Parameters:
        patch1 (GeoPatch): First patch.
        patch2 (GeoPatch): Second patch.

    Returns:
        float: Value of correlation between the raster data in patch1 and patch2
    '''

    # edge case
    if patch1.get_bbox() != patch2.get_bbox():
        return 0

    data1 = patch1.get_raster_data()['data']
    data2 = patch2.get_raster_data()['data']

    # edge case
    if data1 is None or data2 is None:
        return 0

    corr = np.corrcoef(data1.flatten(), data2.flatten())[0, 1]
    return float(corr)


def data_to_text_expert(data: any) -> str:
    '''
    Computes the string representation for any input data.

    Parameters:
        data (any): Input data which is to be represented as a string.

    Returns:
        str: String representation of the input data.
    '''
    str_repr = str(data)
    return str_repr


def patch_visualization_expert(patch: GeoPatch) -> None:
    '''
    Visualize the vector and raster data within GeoPatch on a map. Use for showcasing final results.

    Parameters:
        patch (Union[GeoPatch, None]): A GeoPatch with vector/raster data to be visualized.

    Returns:
        None
    '''
    if patch is not None:
        bbox = patch.vector_data['bbox']

        m = folium.Map(
            name='Geode map output',
            location=patch.vector_data['location'],
            zoom_start=12,  # set an initial zoom level
        )

        # add raster data layer if available
        if patch.raster_data['data'] is not None:
            raster_type = patch.raster_data['type']
            if raster_type == RasterType.color: # color data
                # creating image overlay
                img = folium.raster_layers.ImageOverlay(
                    image=patch.raster_data['data'],
                    bounds=[[bbox[1], bbox[3]], [bbox[0], bbox[2]]],  # assuming bbox is in [min_lat, max_lat, min_lon, max_lon] format
                    opacity=0.6,
                    name=patch.raster_data['name']
                )

            else: # non-color data or binary
                data = patch.raster_data['data']
                if len(data.shape) == 3:
                    data = data[:,:,0] # removing channel dim
                
                # min-max normalization
                min_, max_ = np.nanmin(data), np.nanmax(data)
                norm_data = (data - min_)/(max_ - min_ + 1e-7) 

                # applying the colormap
                colormap = plt.get_cmap('gray' if patch.raster_data['colormap'] is None else patch.raster_data['colormap']) # fallback colormap
                norm_data = colormap(norm_data)

                # creating image overlay
                img = folium.raster_layers.ImageOverlay(
                    image=norm_data,
                    bounds=[[bbox[1], bbox[3]], [bbox[0], bbox[2]]],  # assuming bbox is in [min_lat, max_lat, min_lon, max_lon] format
                    opacity=0.6,
                    name=patch.raster_data['name'])

                # adding colorbar if non-color
                if raster_type == RasterType.non_color:
                    bar = folium.LinearColormap([colormap(i) for i in range(colormap.N)], vmin=min_, vmax=max_, max_labels=5)
                    bar.caption = patch.raster_data['name']
                    bar.width = 200
                    svg_style = '<style>svg#legend {background-color: white;}</style>'
                    m.get_root().add_child(folium.Element(svg_style))
                    bar.add_to(m)
                elif raster_type == RasterType.binary:
                    bar = folium.LinearColormap([colormap(0), colormap(colormap.N)], vmin=0.0, vmax=255.0, max_labels=2)
                    bar.caption = patch.raster_data['name']
                    bar.width = 200
                    svg_style = '<style>svg#legend {background-color: white;}</style>'
                    m.get_root().add_child(folium.Element(svg_style))
                    bar.add_to(m)

            img.add_to(m)

        # add vector data layer if available
        if patch.vector_data is not None:
            # add boundary polygons
            if 'boundary' in patch.vector_data and patch.vector_data['boundary'] is not None:
                boundary_fg = folium.FeatureGroup(name='Boundary')
                for boundary in patch.vector_data['boundary']:
                    folium.GeoJson(
                        boundary.__geo_interface__,
                        name='Boundary',
                        style_function=lambda _: {'fillColor': '#4254f5', 'color': '#4254f5'}
                    ).add_to(boundary_fg) 
                boundary_fg.add_to(m)

            # add points
            if 'points' in patch.vector_data and patch.vector_data['points'] is not None:
                points_fg = folium.FeatureGroup(name='Data markers')
                for point in patch.vector_data['points']:
                    folium.Marker(
                        location=(point.point.x, point.point.y),
                        # icon=folium.Icon(color='blue', icon='info-sign')
                        tooltip=point.name,
                        popup=point.data
                    ).add_to(points_fg)
                points_fg.add_to(m)

        # set the view box based on the bounding box
        m.fit_bounds([[bbox[1], bbox[3]], [bbox[0], bbox[2]]])

    else: # fallback
        m = folium.Map(
            name='Geode map output',
            location=[0, 0],
            zoom_start=0,
        )

    # add fullscreen button
    Fullscreen().add_to(m)
    folium.LayerControl(name='Map output').add_to(m)

    # display the map
    folium_static(m, width=470, height=200)


def threshold_expert(patch: GeoPatch, threshold: float, mode: str = 'greater', relative=True) -> GeoPatch:
    '''
    Threshold the raster data within a GeoPatch by a percent threshold.

    Parameters:
        patch (GeoPatch): A GeoPatch whose raster data is to be thresholded.
        threshold (float): Value between 0.0 and 1.0, the percent threshold.
        mode (str): ('greater', 'less') Mode specifying the truth of a pixel value when compared to the threshold.
        relative (bool): Whether to use a percent or absolute threshold.

    Returns:
        GeoPatch: Patch with thresholded raster data, RasterType of the GeoPatch.raster_data changes to RasterType.binary
    '''
    # edge cases
    if patch is None:
        return None
    if patch.raster_data['type'] != RasterType.non_color:
        return patch
    
    data = patch.get_raster_data()['data']
    min_, max_ = np.nanmin(data), np.nanmax(data)
    threshold_val = min_ + threshold * (max_ - min_) if relative is True else threshold

    # apply thresholding based on mode
    if mode == 'greater':
        thresholded_data = np.where(data > threshold_val, data, np.nan)
    elif mode == 'less':
        thresholded_data = np.where(data < threshold_val, data, np.nan)
    else:
        raise ValueError("Invalid mode. Mode must be either 'greater' or 'less'.")
    
    # create a new GeoPatch with thresholded image data
    thresholded_patch = copy.deepcopy(patch)
    thresholded_patch.set_raster_data({
        'name': f"{patch.raster_data['name']} {'>' if mode == 'greater' else '<'} {threshold_val:.2f}",
        'data': thresholded_data,
        'type': RasterType.binary,
        'colormap': patch.raster_data['colormap'] # invert if needed
    })
    
    return thresholded_patch


def intersection_expert(patch1: GeoPatch, patch2: GeoPatch, mode='raster') -> GeoPatch:
    '''
    Perform intersection between the vector or raster data within two geographical patches. 
    If raster intersection is to be performed, both patches should have RasterType.binary and cover identical geographical regions.

    Parameters:
        patch1 (GeoPatch): First patch
        patch2 (GeoPatch): Second patch
        mode (str): Intersection mode, either 'vector' or 'raster'

    Returns:
        GeoPatch: with required intersection present within vector or raster data.
    '''
    # edge cases
    if patch1 is None and patch2 is None:
        return None
    elif patch1 is None and patch2 is not None:
        return patch2
    elif patch1 is not None and patch2 is None:
        return patch1
    
    intersect_patch = copy.deepcopy(patch1)

    if mode == 'vector':
        data1 = patch1.get_vector_data()['boundary'][0] # shapely.geometry.Polygon
        data2 = patch2.get_vector_data()['boundary'][0]

        # computing intersection of boundary
        intersection_boundary = data1.intersection(data2)

        # recomputing bbox
        bbox = intersection_boundary.bounds

        # recomputing location
        lat1, lon1 = patch1.vector_data['location']
        lat2, lon2 = patch2.vector_data['location']

        # finding union of points in the intersection boundary
        data_points1 = patch1.vector_data['points']
        data_points2 = patch2.vector_data['points']

        if data_points1 is None:
            data_points = data_points2 if data_points2 is not None else None
        else:
            data_points = data_points1 if data_points2 is None else (data_points1 + data_points2, data1 + data2)
        if data_points is not None:
            data_points = [data_point for data_point in data_points if intersection_boundary.contains(data_point.point)]
  
        # setting the vector data of the intersection patch
        intersect_patch.set_vector_data({
            'location': [0.5*(lat1 + lat2), 0.5*(lon1 + lon2)],
            'bbox': bbox, # [min_lat, max_lat, min_lon, max_lon]
            'points': data_points, 
            'boundary': [intersection_boundary]
        })

    elif mode == 'raster':
        data1 = patch1.get_raster_data()['data']
        data2 = patch2.get_raster_data()['data']

        intersection_mask = np.logical_and(np.logical_not(np.isnan(data1)), np.logical_not(np.isnan(data2)))
        intersection_data = np.zeros_like(data1, dtype=float)
        # intersection_data[:] = np.nan
        intersection_data[intersection_mask] = 255.0

        intersect_patch.set_raster_data({
            'name': f"{patch1.raster_data['name']} AND {patch2.raster_data['name']}",
            'type': RasterType.binary,
            'data': intersection_data,
            'colormap': 'gray'
        })

    return intersect_patch



    
    