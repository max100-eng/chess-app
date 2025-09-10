import streamlit as st
import chess
import chess.engine
import os
from io import BytesIO
import chess.svg # Necesario para dibujar el tablero

# --- Configuración del motor Stockfish ---
STOCKFISH_PATH = "./stockfish" # Apunta directamente al archivo binario renombrado

# Función para inicializar Stockfish
@st.cache_resource
def init_stockfish_engine(path):
    st.info("Intentando iniciar Stockfish...")
    if not os.path.exists(path):
        st.error(f"Error: No se encontró el archivo ejecutable de Stockfish en '{path}'.")
        st.stop() # Detener la app si no se encuentra
    
    try:
        # Aquí se inicia el motor
        engine = chess.engine.popen_uci(path)
        st.success("Stockfish iniciado correctamente.")
        return engine
    except Exception as e:
        st.error(f"Error al iniciar Stockfish desde '{path}': {e}. "
                 "Asegúrate de que el archivo es un ejecutable válido para Linux y tiene permisos.")
        st.stop()

# --- Función para dibujar el tablero (solución NameError: png_bytes) ---
def get_board_image(board):
    # Genera el SVG del tablero
    board_svg = chess.svg.board(board=board)
    # Convierte el SVG a bytes, esto es lo que st.image espera
    return BytesIO(board_svg.encode("utf-8"))

# --- Lógica principal de la aplicación ---
st.title("Ajedrez con Asistente de IA")

# Inicializar el motor Stockfish al inicio de la app
engine = init_stockfish_engine(STOCKFISH_PATH)

# Inicializar el estado de la partida
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()

# Mostrar el tablero
png_bytes = get_board_image(st.session_state.board)
st.image(png_bytes, use_column_width=True)

# Lógica para los movimientos del jugador
player_move_uci = st.text_input("Tu movimiento (ej. e2e4):")
if st.button("Hacer Movimiento del Jugador"):
    if player_move_uci:
        try:
            move = chess.Move.from_uci(player_move_uci)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.rerun() # Volver a ejecutar para actualizar el tablero
            else:
                st.error("Movimiento ilegal. Intenta de nuevo.")
        except ValueError:
            st.error("Formato de movimiento incorrecto (ej. e2e4).")

# Lógica para el movimiento de la IA (Stockfish)
if st.button("Movimiento de la IA"):
    if not st.session_state.board.is_game_over():
        with st.spinner("La IA está pensando..."):
            # Configura la dificultad (puedes hacer esto una opción de usuario)
            limit = chess.engine.Limit(time=0.5) # La IA piensa por 0.5 segundos
            
            result = engine.play(st.session_state.board, limit=limit)
            st.session_state.board.push(result.move)
            st.success(f"La IA movió: {result.move.uci()}")
            st.rerun()
    else:
        st.info("La partida ha terminado.")

# Detectar fin de partida
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

# Botón para reiniciar la partida
if st.button("Reiniciar Partida"):
    st.session_state.board = chess.Board()
    st.success("Partida reiniciada.")
    st.rerun()