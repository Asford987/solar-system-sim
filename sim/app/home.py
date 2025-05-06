import streamlit as st
import json
import os
import asyncio
import websockets
import time

# Função para carregar os dados da cena
def load_scene_data(filename):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(path, 'r') as f:
        return json.load(f)

# Função para salvar os dados da cena
def save_scene_data(filename, data):
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# Função para enviar mensagem via WebSocket
async def send_websocket_message(action, planet_name):
    async with websockets.connect("ws://localhost:8765") as websocket:
        message = {"action": action, "planet": planet_name}
        await websocket.send(json.dumps(message))

# Carregar os dados da cena
scene_file = "scene.json"
scene_data = load_scene_data(scene_file)

# Adicionar estilo futurista
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

# Interface do Streamlit
st.title("🌌 Gerenciador do Sistema Solar")
st.subheader("🪐 Adicionar Lua a um Planeta")

# Lista de planetas disponíveis
planet_names = [obj["name"] for obj in scene_data["children"] if obj["type"] == "planet"]

# Selecionar o planeta
selected_planet = st.selectbox("Escolha um planeta:", planet_names)

# Botão para adicionar a lua


if st.button("Adicionar Lua"):
    asyncio.run(send_websocket_message("add_moon", selected_planet))
    time.sleep(0.5)  # Aguarda o servidor processar a alteração
    scene_data = load_scene_data(scene_file)  # Recarrega o arquivo atualizado

    # Encontra o planeta selecionado e lista as luas
    moons = []
    for obj in scene_data["children"]:
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
