import streamlit as st
import chess
import chess.engine
import os
from io import BytesIO
import chess.svg
import cairosvg # Importa la librería para convertir SVG a PNG

# --- CONFIGURACIÓN PARA STOCKFISH EN STREAMLIT CLOUD ---
# En Streamlit Cloud, el repositorio se clona en /app.
# Asegúrate de que el binario de Stockfish para Linux esté en la raíz de tu repositorio
# y se llame simplemente 'stockfish'.
STOCKFISH_PATH = "/app/stockfish" 

# --- FUNCIÓN PARA INICIALIZAR EL MOTOR STOCKFISH ---
# Usa st.cache_resource para que el motor se inicialice solo una vez por despliegue.
@st.cache_resource
def init_stockfish_engine(path):
    st.info("Intentando iniciar Stockfish...")
    
    # Verificar si el archivo Stockfish existe en la ruta especificada
    if not os.path.exists(path):
        st.error(f"Error: No se encontró el archivo ejecutable de Stockfish en '{path}'.")
        st.stop() # Detiene la aplicación si el binario no está

    try:
        # Intenta iniciar el motor Stockfish usando la interfaz UCI
        engine = chess.engine.popen_uci(path)
        st.success("Stockfish iniciado correctamente.")
        return engine
    except Exception as e:
        # Captura cualquier error durante la inicialización de Stockfish
        st.error(f"Error al iniciar Stockfish desde '{path}': {e}. "
                 "Asegúrate de que el archivo es un ejecutable válido para Linux y tiene permisos. "
                 "Verifica que el 'pre_run_script' en .streamlit/config.toml sea correcto.")
        st.stop() # Detiene la aplicación si el motor no se puede iniciar

# --- FUNCIÓN PARA GENERAR LA IMAGEN DEL TABLERO ---
# Convierte el estado actual del tablero de ajedrez a una imagen PNG en bytes.
def get_board_image(board):
    # Genera el tablero como una cadena SVG
    board_svg = chess.svg.board(board=board)
    
    # Convierte la cadena SVG a un objeto BytesIO que contiene la imagen PNG
    # Esto es necesario porque st.image espera un formato de imagen rasterizado (como PNG),
    # no un SVG directo.
    png_output = BytesIO()
    cairosvg.svg2png(bytestring=board_svg.encode("utf-8"), write_to=png_output)
    png_output.seek(0) # Vuelve al inicio del stream de bytes para que st.image lo lea correctamente
    return png_output

# --- TÍTULO DE LA APLICACIÓN ---
st.title("Ajedrez con Asistente de IA")

# --- INICIALIZAR EL MOTOR STOCKFISH ---
# Llama a la función para inicializar el motor Stockfish.
# Esto se ejecuta solo una vez al iniciar la aplicación.
engine = init_stockfish_engine(STOCKFISH_PATH)

# --- INICIALIZAR EL ESTADO DE LA PARTIDA ---
# 'st.session_state' se usa para que el estado del tablero persista entre las interacciones.
if 'board' not in st.session_state:
    st.session_state.board = chess.Board() # Crea un nuevo tablero al inicio

# --- MOSTRAR EL TABLERO ---
# Obtiene la imagen del tablero actual y la muestra en la aplicación.
png_bytes = get_board_image(st.session_state.board)
# 'use_container_width=True' hace que la imagen se ajuste al ancho disponible.
st.image(png_bytes, use_container_width=True) 

# --- LÓGICA PARA LOS MOVIMIENTOS DEL JUGADOR ---
st.subheader("Tu Turno")
player_move_uci = st.text_input("Ingresa tu movimiento (formato UCI, ej. e2e4):", key="player_move_input")

if st.button("Hacer Movimiento del Jugador"):
    if player_move_uci:
        try:
            # Intenta crear un objeto Move a partir del string UCI
            move = chess.Move.from_uci(player_move_uci)
            # Verifica si el movimiento es legal en el tablero actual
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move) # Realiza el movimiento
                st.info(f"Has movido: {move.uci()}")
                st.rerun() # Vuelve a ejecutar la aplicación para actualizar el tablero
            else:
                st.error("Movimiento ilegal. Por favor, intenta un movimiento válido.")
        except ValueError:
            st.error("Formato de movimiento incorrecto. Usa formato UCI (ej. e2e4).")
    else:
        st.warning("Por favor, ingresa un movimiento.")

# --- LÓGICA PARA EL MOVIMIENTO DE LA IA (STOCKFISH) ---
st.subheader("Turno de la IA")
if st.button("Hacer Movimiento de la IA"):
    # Verifica si la partida ha terminado antes de pedir un movimiento a la IA
    if not st.session_state.board.is_game_over():
        with st.spinner("La IA está pensando..."):
            # Define el límite de tiempo o profundidad para el cálculo de Stockfish.
            # Mayor tiempo/profundidad = IA más fuerte pero más lenta.
            limit = chess.engine.Limit(time=0.5) # La IA piensa por 0.5 segundos
            
            # Obtiene el mejor movimiento de Stockfish
            result = engine.play(st.session_state.board, limit=limit)
            st.session_state.board.push(result.move) # Realiza el movimiento de la IA
            st.success(f"La IA movió: {result.move.uci()}")
            st.rerun() # Vuelve a ejecutar la aplicación para actualizar el tablero
    else:
        st.info("La partida ha terminado. No se pueden hacer más movimientos.")

# --- DETECCIÓN DE FIN DE PARTIDA ---
st.subheader("Estado de la Partida")
if st.session_state.board.is_checkmate():
    st.success("¡Jaque Mate! La partida ha terminado.")
elif st.session_state.board.is_stalemate():
    st.info("¡Tablas por ahogado! La partida ha terminado.")
elif st.session_state.board.is_insufficient_material():
    st.info("¡Tablas por material insuficiente! La partida ha terminado.")
elif st.session_state.board.is_seventyfive_moves():
    st.info("¡Tablas por regla de los 75 movimientos! La partida ha terminado.")
elif st.session_state.board.is_fivefold_repetition():
    st.info("¡Tablas por repetición quíntuple! La partida ha terminado.")
else:
    st.info("La partida está en progreso.")

# --- BOTÓN PARA REINICIAR LA PARTIDA ---
if st.button("Reiniciar Partida"):
    st.session_state.board = chess.Board() # Crea un tablero nuevo
    st.success("Partida reiniciada.")
    st.rerun() # Vuelve a ejecutar la aplicación para mostrar el tablero inicial