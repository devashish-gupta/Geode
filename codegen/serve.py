'''
This script facilitates local hosting for the code generation model
'''
from flask import Flask, request, jsonify
from generator import Generator 
import random

codes = [
'''patch_visualization_expert(
    patch=patch_location_expert(st.session_state.latest_query)
)''',
'''patch_visualization_expert(
    patch=point_location_expert(st.session_state.latest_query)
)''',
'''patch_visualization_expert(
    patch=threshold_expert(
        precipitation_expert(
            point_location_expert(
                st.session_state.latest_query
            )
        ),
        threshold=0.6
    )
)''',
'''patch_visualization_expert(
    patch=air_quality_expert(
        patch_location_expert(st.session_state.latest_query),
        parameter='us-epa-index'
    )
)''',
'''patch_visualization_expert(
    patch=threshold_expert(
        air_quality_expert(
            patch_location_expert(st.session_state.latest_query)
        ), threshold=0.5, mode='greater')
)''',
'''patch_visualization_expert(patch=air_quality_expert(point_location_expert(st.session_state.latest_query), mode='point')[1])''',
'''patch_visualization_expert(patch=precipitation_expert(patch_location_expert(st.session_state.latest_query)))''',
'''patch_visualization_expert(patch=humidity_expert(patch_location_expert(st.session_state.latest_query))) # todo inferring the mode automatically''',
'''patch_visualization_expert(patch=elevation_expert(patch_location_expert(st.session_state.latest_query)))'''
]

app = Flask(__name__)
# generator = Generator() 

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        data = request.get_json()
        user_query = data.get('user_query')

        if user_query:
            # generated_code = generator.generate(user_query) # call the generator
            generated_code = random.choice(codes).replace('st.session_state.latest_query', f"'{user_query}'") # mocking the code generation
            return jsonify({'generated_code': str(generated_code)}), 200
        else:
            return jsonify({'error': 'User query is missing'}), 400
    else:
        return jsonify({'error': 'Only POST requests are allowed'}), 405
    
@app.route('/active', methods=['GET'])
def is_active():
    if request.method == 'GET':
        return jsonify(None), 200

if __name__ == '__main__':
    app.run(debug=True)