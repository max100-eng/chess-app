import streamlit as st
import chess
from stockfish import Stockfish
import chess.svg
import io
import cairosvg # Asegúrate de que esta librería esté instalada

# Título de la aplicación
st.title("Ajedrez con Asistente de IA")

# Inicializar Stockfish si no está ya en la sesión
if "stockfish" not in st.session_state:
    try:
        # Usar el ejecutable de Linux que subiste
        st.session_state.stockfish = Stockfish(path="stockfish-ubuntu-x86-64-avx2")
    except FileNotFoundError:
        # Mensaje de error corregido
        st.error("Error: No se encontró el archivo ejecutable de Stockfish. Asegúrate de que 'stockfish-ubuntu-x86-64-avx2' esté en la misma carpeta.")
        st.session_state.stockfish = None

# Inicializar el tablero de ajedrez
if "board" not in st.session_state:
    st.session_state.board = chess.Board()

# --- Funciones del tablero y movimientos ---

def reset_board():
    """Reinicia el tablero a su posición inicial."""
    st.session_state.board = chess.Board()

def show_board_as_image(board):
    """Genera el tablero como una imagen PNG a partir de los datos SVG."""
    # Genera el SVG como una cadena de texto
    board_svg = chess.svg.board(board=board)
    
    # Convierte la cadena SVG a bytes PNG usando cairosvg
    png_bytes = cairosvg.svg2png(bytestring=board_svg.encode("utf-8"))
    
    # Muestra los bytes PNG en Streamlit
    st.image(png_bytes, use_container_width=True)

def make_stockfish_move():
    """Ejecuta el mejor movimiento sugerido por Stockfish."""
    if st.session_state.stockfish:
        best_move_uci = st.session_state.stockfish.get_best_move_time(1000)
        best_move = chess.Move.from_uci(best_move_uci)
        if best_move in st.session_state.board.legal_moves:
            st.session_state.board.push(best_move)
            st.success(f"Stockfish movió: {best_move_uci}")
        else:
            st.warning("Stockfish sugirió un movimiento ilegal. Vuelve a intentarlo.")
    else:
        st.error("Stockfish no está disponible.")

# --- Interfaz de Streamlit ---

# Muestra el tablero de ajedrez como una imagen SVG
show_board_as_image(st.session_state.board)

# Botones de acción
col1, col2 = st.columns(2)
with col1:
    st.button("Reiniciar Tablero", on_click=reset_board, key="reset_board_button")
with col2:
    st.button("Mover con Stockfish", on_click=make_stockfish_move, key="stockfish_move_button")

# Pedir sugerencia a Stockfish
if st.session_state.stockfish:
    st.text("Análisis de la posición por Stockfish:")
    st.session_state.stockfish.set_fen_position(st.session_state.board.fen())
    best_move_suggestion = st.session_state.stockfish.get_best_move_time(1000) # 1 segundo de análisis
    st.info(f"El mejor movimiento sugerido es: {best_move_suggestion}")
