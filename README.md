# **Geode**

A zero-shot geospatial question answering agent with precise spatiotemporal retrieval and explicit reasoning capabilities!

![Geode home](/assets/home.png)

## Capabilities

Geode is capable of answering geospatial queries that require complex reasoning and algorithmic computation. Here are a few examples of how Geode leverages its expert pool to answer geospatial queries.

🔍 **Query: Which one of the following countries is larger, Russia or Greenland?**

🪨 **Generated code**:
```python
def compute_answer(query: str):
    # Find the geographic locations and boundaries of Russia and Greenland
    russia_patch = patch_location_expert("Russia")
    greenland_patch = patch_location_expert("Greenland")

    # Calculate the areas of Russia and Greenland patches
    russia_area = sum(p.area for p in russia_patch.get_boundary())
    greenland_area = sum(p.area for p in greenland_patch.get_boundary())

    # Determine which country is larger
    if russia_area > greenland_area:
        answer = "Russia is larger than Greenland."
        patch = russia_patch
    elif russia_area < greenland_area:
        answer = "Greenland is larger than Russia."
        patch = greenland_patch
    else:
        answer = "Russia and Greenland are of equal size."
        # Return one of the patches for visualization, in this case, Russia
        patch = russia_patch

    return answer, patch 

result = compute_answer(query)
```

🔍 **Query: What is air quality like in the city that is known for the Eiffel tower?**

🪨 **Generated code**:
```python
def compute_answer(query: str):
    # Find the geographic location and boundary of the city known for the Eiffel Tower
    city_patch = patch_location_expert("Paris")
    
    # Retrieve air quality information for the entire city
    air_quality, air_quality_patch = air_quality_expert(city_patch, mode='point', parameter='us-epa-index')
    
    # Represent air quality as text
    air_quality_text = data_to_text_expert(air_quality)
    
    # Returning the textual answer and the GeoPatch object for visualization
    return f"The air quality in the city known for the Eiffel Tower is {air_quality_text}.", air_quality_patch

result = compute_answer(query)
```

🔍 **Query: Which state in the United states has the highest average humidity?**

🪨 **Generated code**:
```python
def compute_answer(query: str):
    # List of all state names in the United States
    state_names = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
        "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
        "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
        "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
        "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
        "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    ]

    # Initialize variables to store the maximum humidity and corresponding state patch
    max_humidity = 0
    max_humidity_state_patch = None

    # Iterate over each state to find the one with the highest humidity
    for state_name in state_names:
        # Finding the geographic location and boundary polygon of the state
        state_patch = patch_location_expert(state_name)

        # Retrieving humidity data for the entire state patch
        humidity_patch = humidity_expert(state_patch, mode='patch')

        # Getting the maximum humidity value for the current state
        state_max_humidity = humidity_patch.raster_data['data'].max()

        # Checking if the current state has higher humidity than the previous maximum
        if state_max_humidity > max_humidity:
            max_humidity = state_max_humidity
            max_humidity_state_patch = state_patch

    # Elaborating the answer with computation steps
    answer = "The state in the United States with the highest humidity is not determined solely by the presence of a single maximum value. Humidity levels can vary significantly across different regions and time periods. An in-depth analysis considering spatial and temporal variations would be necessary to identify the state with consistently high humidity levels."

    # Returning the textual answer and the GeoPatch object for visualization
    return answer, max_humidity_state_patch

result = compute_answer(query) # make sure you call the compute_answer function at the end and store the output in a variable called result
```

🔍 **Query: If we were to mark Smyrna, Sandy Springs and Norcross as points on the map, would they form a triangle?**

🪨 **Generated code**:
```python
def compute_answer(query: str):
    # Find the geographic locations of Smyrna, Sandy Springs, and Norcross
    smyrna_patch = point_location_expert("Smyrna")
    sandy_springs_patch = point_location_expert("Sandy Springs")
    norcross_patch = point_location_expert("Norcross")

    # Check if all points are found
    if smyrna_patch is None or sandy_springs_patch is None or norcross_patch is None:
        return "One or more locations not found", None

    # Create a list of the points for triangle formation check
    points = [smyrna_patch, sandy_springs_patch, norcross_patch]

    # Check if the points form a triangle
    triangle_formed = check_triangle_formation(points)

    # Return the textual answer and the most salient GeoPatch object for visualization
    answer = "Yes, the points form a triangle." if triangle_formed else "No, the points do not form a triangle."
    return answer, points

def check_triangle_formation(points):
    '''
    Check if three points form a triangle.
    '''
    # Get the locations of the points
    locations = [point.get_location() for point in points]

    # Check if any two points have the same location
    if len(set(locations)) < len(locations):
        return False

    # Check if the three points form a triangle using cross product
    x1, y1 = locations[0]
    x2, y2 = locations[1]
    x3, y3 = locations[2]

    cross_product = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)

    # If cross product is not zero, points form a triangle
    return cross_product != 0

result = compute_answer(query)
```

🔍 **Query: Can you return an adjacency matrix representing the adjacency of state borders, for states in the US?**

🪨 **Generated code**:
```python
def compute_answer(query: str):
    # Finding the geographic location and boundary polygons of US states
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
              "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
              "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
              "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
              "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
              "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
              "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

    state_patches = [patch_location_expert(state) for state in states]

    # Constructing the adjacency matrix
    adjacency_matrix = []
    for i, state1 in enumerate(states):
        row = []
        for j, state2 in enumerate(states):
            # Check if the boundary of state1 intersects with the boundary of state2
            intersection_patch = intersection_expert(state_patches[i], state_patches[j], mode='vector')
            if intersection_patch:
                row.append(1)
            else:
                row.append(0)
        adjacency_matrix.append(row)

    # Textual answer incorporating adjacency matrix
    answer = "Adjacency matrix representing the adjacency of state borders for states in the US:\n"
    for i, state in enumerate(states):
        answer += state + ": " + str(adjacency_matrix[i]) + "\n"

    # GeoPatch object for visualization (using the first state patch)
    patch = state_patches[0]

    return answer, patch

result = compute_answer(query)
```

## Architecture

![System architecture](/assets/architecture.png)


