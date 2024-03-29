from base import GeoPatch
import numpy as np
import copy
from scipy.interpolate import griddata

def imputation_expert(patch: GeoPatch) -> GeoPatch:
    '''
    Impute missing values in a patch using interpolation.

    Parameters:
        patch (GeoPatch): Input patch with missing values represented as NaN.

    Returns:
        GeoPatch: Patch with missing values imputed.
    '''
    image = patch.get_raster_data()

    # Mask NaN values
    mask = ~np.isnan(image)

    # Check if there are any known coordinates available
    if np.any(mask):
        x, y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))

        # Coordinates of known values
        known_coords = np.column_stack((x[mask], y[mask]))

        # Values at known coordinates
        known_values = image[mask]

        # Coordinates where values need to be imputed
        impute_coords = np.column_stack((x[~mask], y[~mask]))

        # Perform interpolation
        imputed_values = griddata(known_coords, known_values, impute_coords, method='nearest')

        # Reshape imputed values to match original image shape
        imputed_image = np.copy(image)
        imputed_image[~mask] = imputed_values
    else:
        # If entire matrix is NaNs, fill with default value or handle as needed
        default_value = 0.0
        imputed_image = np.full_like(image, default_value)

    out_patch = copy.deepcopy(patch)
    out_patch.set_raster_data(imputed_image)

    return out_patch
    