import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# =============================
# CONFIGURACIÓN DE PÁGINA
# =============================
st.set_page_config(
    page_title="BAE Sensor Monitor 🍼",
    page_icon="🧸",
    layout="centered"
)

# =============================
# VARIABLES DE SESIÓN
# =============================
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# =============================
# FUNCIÓN MQTT
# =============================
def get_mqtt_message(broker, port, topic, client_id):
    """Obtiene un mensaje MQTT desde un broker."""
    message_received = {"received": False, "payload": None}

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True

    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()

        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)

        client.loop_stop()
        client.disconnect()
        return message_received["payload"]

    except Exception as e:
        return {"error": str(e)}

# =============================
# ESTILO BAE PASTEL
# =============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

    body, .stApp {
        background: linear-gradient(180deg, #FFF9EC, #FFFDF7);
        color: #3E3E3E;
        font-family: 'Poppins', sans-serif;
    }

    /* Encabezado principal */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        color: #2F3E46;
        margin-bottom: 0.3rem;
        animation: fadeInDown 1.5s ease;
    }

    .subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #52796F;
        margin-bottom: 2rem;
        animation: fadeInUp 2s ease;
    }

    /* Contenedores */
    .bae-box {
        background: #FFF8EB;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        border: 2px solid #F4A261;
        animation: fadeIn 2s ease;
    }

    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #F6C667, #F4A261);
        color: #2F3E46;
        font-weight: 700;
        border: none;
        border-radius: 15px;
        padding: 0.8rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(244,162,97,0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 18px rgba(246,198,103,0.5);
    }

    /* Expander */
    .st-expander {
        border-radius: 15px !important;
        border: 1px solid #FFD89C !important;
        background-color: #FFF9EC !important;
    }

    /* Métricas */
    [data-testid="stMetricValue"] {
        color: #2F3E46;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #52796F;
    }

    /* Animaciones */
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(10px);}
        to {opacity: 1; transform: translateY(0);}
    }
    @keyframes fadeInDown {
        from {opacity: 0; transform: translateY(-20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    @keyframes fadeInUp {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
</style>
""", unsafe_allow_html=True)

# =============================
# INTERFAZ PRINCIPAL
# =============================
st.markdown('<div class="main-title">📡 BAE Sensor Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Monitorea los datos de tus sensores con un toque suave y pastel 💛</div>', unsafe_allow_html=True)

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.subheader('⚙️ Configuración de Conexión')
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com')
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535)
    topic = st.text_input('Tópico', value='sensor_bae')
    client_id = st.text_input('ID del Cliente', value='cliente_bae')

# =============================
# INFO Y ACCIONES
# =============================
with st.expander('🍼 ¿Cómo usar esta app?', expanded=False):
    st.markdown("""
    1. Ingresa el **Broker MQTT** y el **tópico**.  
    2. Haz clic en **Obtener Datos** para recibir la última lectura.  
    3. Verás los datos representados de manera visual y amigable 🌈  
    """)

st.markdown('<div class="bae-box">', unsafe_allow_html=True)

if st.button('🔄 Obtener Datos del Sensor'):
    with st.spinner('🩵 Conectando al broker y recibiendo datos...'):
        data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = data

if st.session_state.sensor_data:
    data = st.session_state.sensor_data
    st.markdown("### 📊 Datos Recibidos")
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success("✅ Datos recibidos correctamente")
        if isinstance(data, dict):
            cols = st.columns(len(data))
            for i, (k, v) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=k, value=v)
            with st.expander('Ver JSON completo'):
                st.json(data)
        else:
            st.code(data)
else:
    st.info("🌸 Aún no se han recibido datos, intenta obtenerlos arriba.")

st.markdown('</div>', unsafe_allow_html=True)

# =============================
# PIE
# =============================
st.markdown("""
<div style='text-align:center; margin-top:2rem; color:#52796F; font-size:0.9rem;'>
Hecho con 💛 por <b>BAE</b> | Sensores conectados con ternura 🌿
</div>
""", unsafe_allow_html=True)

