'''
This script facilitates local hosting for the code generation model
'''
from flask import Flask, request, jsonify
from generator import Generator 
import random

codes = [
'''def solve_query():
    return f"I found {st.session_state.latest_query} on the map and plotted the boundary and location on the map for you", patch_location_expert(st.session_state.latest_query)
result = solve_query()''',
'''def solve_query():
    return f"I found {st.session_state.latest_query} on the map and plotted the boundary and location on the map for you", point_location_expert(st.session_state.latest_query)
result = solve_query()''',
'''def solve_query():
    patch=threshold_expert(
        precipitation_expert(
            point_location_expert(
                st.session_state.latest_query
            )
        ),
        threshold=0.6
    )
    return f"I found the locations where over 60 percent precipitation of {st.session_state.latest_query} happens, check out the map output!", patch
result = solve_query()''',
'''def solve_query():
    patch=air_quality_expert(
        patch_location_expert(st.session_state.latest_query),
        parameter='co2'
    )
    return f"I found the CO2 levels throughtout {st.session_state.latest_query}, check it out on the map!", patch
result = solve_query()'''
]

app = Flask(__name__)
generator = Generator() 

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        data = request.get_json()
        user_query = data.get('user_query')

        if user_query:
            generated_code = generator.generate(user_query) # call the generator
            # generated_code = random.choice(codes).replace('st.session_state.latest_query', f"'{user_query}'") # mocking the code generation
            # generated_code = '''raise RuntimeError('This is an error in the code')'''
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
