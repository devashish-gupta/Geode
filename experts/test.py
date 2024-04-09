import unittest
import numpy as np
from functional_experts import *  
from model_experts import *  
from database_experts import *  
import torch

# class TestImputationExpert(unittest.TestCase):
#     def test_imputation_expert(self):
#         patch = generate_test_patch()
#         patch_with_nan = introduce_nans(patch, 10)
#         print(f'A: {patch_with_nan.raster_data}\n')        
#         imputed_patch = imputation_expert(patch_with_nan)
#         print(imputed_patch.raster_data)
#         self.assertFalse(np.isnan(imputed_patch.get_raster_data()).any())

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


# class TestElaborateExpert(unittest.TestCase):
#     def test_elaborate_expert(self):
#         question = 'Which country has the larger area, Greenland or Russia?'
#         answer = 'Russia'
#         context = ['Russia area = 6.602 million sq mi', 'Greenland area = 836.3 thousand sq mi']

#         explanation = elaborate_expert(question, answer, context)

#         # Assert that the explanation is not empty
#         print(f'\nElaborated answer:\n\n{explanation.strip()}\n\n')
#         self.assertTrue(explanation.strip())


# class TestPointLocationExpert(unittest.TestCase):
#     def test_point_location_expert(self):
#         # test for a known location
#         name = "Statue of Liberty"
#         expected_latitude = 40.6892534
#         expected_longitude = -74.0445485

#         latitude, longitude = point_location_expert(name)
#         print(latitude, longitude)

#         self.assertAlmostEqual(latitude, expected_latitude, places=4)
#         self.assertAlmostEqual(longitude, expected_longitude, places=4)

class TestPatchLocationExpert(unittest.TestCase):
    # def test_patch_location_expert_existing(self):
    #     # test for an existing location
    #     name = "Golden gate bridge"

    #     patch = patch_location_expert(name)
    #     print(patch)

    #     # check if patch is not None
    #     self.assertIsNotNone(patch)

    #     # check if patch has location and boundary polygons
    #     self.assertIn('location', patch.vector_data)
    #     self.assertIn('boundary', patch.vector_data)

    #     # check if location is a list of two elements
    #     location = patch.vector_data['location']
    #     self.assertIsInstance(location, list)
    #     self.assertEqual(len(location), 2)

    #     # check if boundary is a list of Polygon objects
    #     boundary = patch.vector_data['boundary']
    #     for polygon in boundary:
    #         self.assertIsInstance(polygon, Polygon)

    #     # check if bounding box is present
    #     self.assertIn('bbox', patch.vector_data)

    # def test_patch_location_expert_nonexisting(self):
    #     # Test for a non-existing location
    #     name = "Nonexistent Place"

    #     patch = patch_location_expert(name)

    #     # Check if patch is None
    #     self.assertIsNone(patch)

    def test_patch_location_expert_multiple_polygons(self):
        # Test for a location with multiple polygons (e.g., country with multiple islands)
        name = "Indonesia"

        patch = patch_location_expert(name)
        print(f'Multi island patch:\n{patch}')

        # Check if patch is not None
        self.assertIsNotNone(patch)

        # Check if patch has location and boundary polygons
        self.assertIn('location', patch.vector_data)
        self.assertIn('boundary', patch.vector_data)

        # Check if location is a list of two elements
        location = patch.vector_data['location']
        self.assertIsInstance(location, list)
        self.assertEqual(len(location), 2)

        # Check if boundary is a list of Polygon objects
        boundary = patch.vector_data['boundary']
        self.assertIsInstance(boundary, list)
        print(f'num islands: {len(boundary)}')
        for polygon in boundary:
            self.assertIsInstance(polygon, Polygon)

        # Check if bounding box is present
        self.assertIn('bbox', patch.vector_data)


if __name__ == '__main__':
    unittest.main()