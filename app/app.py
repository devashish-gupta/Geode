import streamlit as st
import folium
import geopandas as gpd
from streamlit_folium import folium_static
import random # temporary

codes = ['''def compute_answer(question):
                nearby_cities = proximity_expert('Atlanta', level='city', count=10)
                no_rain_cities = []
                for city in cities:
                    prob = rain_prob_expert(point_location_expert(city), date='today')
                    if prob < 0.05:
                        no_rain_cities.append(city)

                answer_text = elaborate_expert(question=question, 
                    answer=data_to_text_expert(no_rain_cities))
                return answer_text
                answer_text = elaborate_expert(question=question, 
                    answer=data_to_text_expert(no_rain_cities))
                return answer_text
                answer_text = elaborate_expert(question=question, 
                    answer=data_to_text_expert(no_rain_cities))
                return answer_text
                answer_text = elaborate_expert(question=question, 
                    answer=data_to_text_expert(no_rain_cities))
                return answer_text
''',
'''
def compute_answer(question):
                answer_text = elaborate_expert(question=question, 
                    answer=data_to_text_expert(no_rain_cities))
                return answer_text
''']

st.set_page_config(page_title="Geode", layout="wide", page_icon="🪨")

# setting up session states
if "generated_code" not in st.session_state:
    st.session_state["generated_code"] = [
        {'content': '# No code generated yet'}
    ]
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Ask me anything geospatial!"}
    ]

# global styling
st.markdown(
    '''
    <style>
        .block-container {
            margin-top: 0rem;
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }
        .reportview-container {
            margin-top: -2em;
        }
        header {
            visibility: hidden;
        }  
        .stCodeBlock {
            height: 300px;
            width: 100%;
            overflow-x: hidden;
        }
        pre code {
            font-size: 0.9em;
            white-space: pre-wrap !important;
        }     
        iframe {
            width: 100%;
            border-radius: 8px;
        }
        .stChatMessage {
            cursor: pointer; 
            border: 1px solid transparent;
            transition: all 200ms ease-in-out;
        }
        .stChatMessage:hover {
            border: 1px solid #555555;
            transition: all 200ms ease-in-out;
        }
        .stChatMessage.selected {
            border: 1px solid #888888;
            transition: all 100ms ease-in-out;
        }
    </style>
    ''',
    unsafe_allow_html=True,
)

# Read GeoJSON file containing country borders
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

def visualize_geojson(geojson_data):
    '''
    Function to visualize GeoJSON data on a map
    '''
    # Create a Folium map centered at the mean latitude and longitude
    m = folium.Map(
        location=[0, 0],
        zoom_start=0,
    )
    # add GeoJSON layer to the map
    folium.GeoJson(geojson_data).add_to(m)
    folium_static(m, width=470, height=200)

def reset_chat():
    for key in st.session_state.keys():
        del st.session_state[key]


def main():
    '''
    Main layout
    '''
    left_column, right_column = st.columns([3, 2])  # Adjust column widths here

    with left_column:
        st.markdown("### __Geode__")

        # displaying entire conversation
        conversation = st.container(height=520)
        for answer in st.session_state.messages:
            conversation.chat_message(answer["role"], avatar='🪨' if answer['role'] == 'assistant' else '🧑').write(answer["content"])

        button_col, input_col = st.columns([1, 6.4])
        button_col.button('New chat', on_click=reset_chat)
        query = input_col.chat_input(key="input")

        if query:
            # reading the user prompt
            st.session_state.messages.append({"role": "user", "content": query})
            conversation.chat_message("user", avatar='🧑').write(query)

            # generating code to solve the query
            answer = "Hello from Geode"
            # generated_code, answer = codegen(base_prompt + prompt)

            # displaying the answer and generated code, saving it
            st.session_state.generated_code.append({'content': random.choice(codes)}) # put generated code here
            st.session_state.messages.append({"role": "assistant", "content": answer}) # put generated answer here
            conversation.chat_message("assistant", avatar='🪨').write(answer)

    with right_column:
        st.markdown('<div style="padding-top:18px;padding-bottom:15px;">Map output</div>', unsafe_allow_html=True)
        country_data = world[world.name == "Canada"]
        visualize_geojson(country_data)

        st.markdown("Generated code")
        st.markdown(
            f"""```python
            {st.session_state.generated_code[-1]['content']}
            """
        )


if __name__ == "__main__":
    main()
