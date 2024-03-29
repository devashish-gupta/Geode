import unittest
import numpy as np
from functional_experts import *  
from model_experts import *  
import torch

# class TestImputationExpert(unittest.TestCase):
#     def test_imputation_expert(self):
#         patch = generate_test_patch()
#         patch_with_nan = introduce_nans(patch, 10)
#         print(f'A: {patch_with_nan.raster_data}\n')        
#         imputed_patch = imputation_expert(patch_with_nan)
#         print(imputed_patch.raster_data)
#         self.assertFalse(np.isnan(imputed_patch.get_raster_data()).any())


class TestElaborateExpert(unittest.TestCase):
    def test_elaborate_expert(self):
        question = 'Which country has the larger area, Greenland or Russia?'
        answer = 'Russia'
        context = ['Russia area = 6.602 million sq mi', 'Greenland area = 836.3 thousand sq mi']

        explanation = elaborate_expert(question, answer, context)

        # Assert that the explanation is not empty
        print(f'\nElaborated answer:\n\n{explanation.strip()}\n\n')
        self.assertTrue(explanation.strip())


# def generate_test_patch():
#     # Generate a dummy patch for testing
#     gp = GeoPatch(bounds=None, type=0, raster_data=torch.rand((3, 6)).numpy())
#     return gp  # Implement GeoPatch creation according to your code

# def introduce_nans(patch: GeoPatch, num_nans: int):
#     if num_nans <= 0:
#         return patch
#     rows, cols = patch.raster_data.shape
#     nan_indices = np.random.choice(rows * cols, num_nans, replace=False)
#     patch.raster_data.ravel()[nan_indices] = np.nan
#     return patch


if __name__ == '__main__':
    unittest.main()