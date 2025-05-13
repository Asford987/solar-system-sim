import streamlit as st
import json
import os
import time


def load_scene_data(filename):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(path, 'r') as f:
        return json.load(f)

def save_scene_data(filename, data):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
def add_moon_to_planet(scene_data, planet_name):
    for i, obj in enumerate(scene_data.copy()["children"]):
        if obj["name"] == planet_name:
            if "children" not in obj:
                obj["children"] = []
            new_moon = {
                "name": f"New Moon {len(obj['children']) + 1}",
                "type": "moon",
                "radius": 0.1,
                "orbit_radius": 2.0,
                "orbit_speed": 20.0,
                "rotation_speed": 10.0,
                "inclination": 0.5,
                "texture": "assets/textures/moon.jpg"
            }
            scene_data["children"][i]["children"].append(new_moon)
            return scene_data
    return scene_data

scene_file = "scene.json"
scene_data = load_scene_data(scene_file)

st.markdown(
    """
    <style>
    /* Fundo futurista */
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Roboto', sans-serif;
    }
    /* Caixa de seleção estilizada */
    .stSelectbox {
        background-color: #1e293b;
        color: white;
        border-radius: 10px;
        padding: 10px;
    }
    /* Botão estilizado */
    .stButton button {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2575fc, #6a11cb);
    }
    /* Títulos */
    h1, h2, h3 {
        text-align: center;
        color: #00d4ff;
        text-shadow: 0px 0px 10px #00d4ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌌 Gerenciador do Sistema Solar")
st.subheader("🪐 Adicionar Lua a um Planeta")

planet_names = [obj["name"] for obj in scene_data["children"] if obj["type"] == "planet"]

selected_planet = st.selectbox("Escolha um planeta:", planet_names)


if "scene_data" not in st.session_state:
    st.session_state.scene_data = load_scene_data(scene_file)

if st.button("Adicionar Lua"):
    new_json = add_moon_to_planet(st.session_state.scene_data, selected_planet)
    save_scene_data(scene_file, new_json)
    time.sleep(0.5)
    st.session_state.scene_data = load_scene_data(scene_file)

    moons = []
    for obj in st.session_state.scene_data["children"]:
        if obj["name"] == selected_planet and "children" in obj:
            moons = [child["name"] for child in obj["children"] if child["type"] == "moon"]
            break

    st.success(f"🌕 Uma nova lua foi adicionada a {selected_planet}!")
    if moons:
        st.subheader(f"🌙 Luas atuais de {selected_planet}:")
        for moon in moons:
            st.write(f"• {moon}")
    else:
        st.info("Este planeta ainda não possui luas.")

