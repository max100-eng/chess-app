import streamlit as st
import chess
import chess.engine
import os
from io import BytesIO
import chess.svg
import cairosvg 
from stockfish import Stockfish

# Define la ruta relativa al ejecutable dentro de tu repositorio
# Reemplaza 'bin/stockfish' con la ruta correcta si la colocaste en otro lugar
ruta_stockfish = "./bin/stockfish"

# Inicializa el motor de Stockfish
engine = Stockfish(path=ruta_stockfish)
# --- FUNCIÓN PARA INICIALIZAR EL MOTOR STOCKFISH ---
@st.cache_resource
def init_stockfish_engine():
    # your function code here
    try:
        # Define la ruta relativa al ejecutable dentro de tu repositorio
        # Reemplaza './stockfish' si el archivo está en una ubicación diferente
        ruta_stockfish = "./bin/stockfish"
        
        st.info("Intentando iniciar Stockfish...")
        
        # Crea una instancia de Stockfish.
        stockfish_engine = Stockfish(path=ruta_stockfish)
        
        # Opcional: Establecer un nivel de fuerza (valor entre 1 y 20)
        stockfish_engine.set_skill_level(10)
        
        st.success("Stockfish iniciado correctamente.")
        return stockfish_engine  # Devuelve el objeto Stockfish
    except FileNotFoundError:
        st.error(f"Error: El ejecutable de Stockfish no se encuentra en la ruta: '{ruta_stockfish}'."
                 " Asegúrate de haberlo subido a tu repositorio y de que la ruta sea correcta.")
        st.stop()
    except Exception as e:
        st.error(f"Error al iniciar Stockfish: {e}.")
        st.stop()

# Inicializa el motor al inicio de la aplicación
# La función se ejecuta una sola vez gracias a @st.cache_resource
engine = init_stockfish_engine()

# --- FUNCIÓN PARA GENERAR LA IMAGEN DEL TABLERO ---
def get_board_image(board):
    board_svg = chess.svg.board(board=board)
    png_output = BytesIO()
    cairosvg.svg2png(bytestring=board_svg.encode("utf-8"), write_to=png_output)
    png_output.seek(0)
    return png_output

# --- TÍTULO DE LA APLICACIÓN ---
st.title("Ajedrez con Asistente de IA")

# --- INICIALIZAR EL MOTOR STOCKFISH ---
engine = init_stockfish_engine()

# --- INICIALIZAR EL ESTADO DE LA PARTIDA ---
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()

# --- MOSTRAR EL TABLERO ---
png_bytes = get_board_image(st.session_state.board)
st.image(png_bytes, use_container_width=True) 

# --- LÓGICA PARA LOS MOVIMIENTOS DEL JUGADOR ---
st.subheader("Tu Turno")
player_move_uci = st.text_input("Ingresa tu movimiento (formato UCI, ej. e2e4):", key="player_move_input")

if st.button("Hacer Movimiento del Jugador"):
    if player_move_uci:
        try:
            move = chess.Move.from_uci(player_move_uci)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.info(f"Has movido: {move.uci()}")
                st.rerun()
            else:
                st.error("Movimiento ilegal. Por favor, intenta un movimiento válido.")
        except ValueError:
            st.error("Formato de movimiento incorrecto. Usa formato UCI (ej. e2e4).")
    else:
        st.warning("Por favor, ingresa un movimiento.")

# --- LÓGICA PARA EL MOVIMIENTO DE LA IA (STOCKFISH) ---
st.subheader("Turno de la IA")
if st.button("Hacer Movimiento de la IA"):
    if not st.session_state.board.is_game_over():
        with st.spinner("La IA está pensando..."):
            # Obtiene el mejor movimiento de Stockfish
            best_move = engine.get_best_move()
            if best_move:
                move = chess.Move.from_uci(best_move)
                st.session_state.board.push(move)
                st.success(f"La IA movió: {move.uci()}")
                st.rerun()
            else:
                st.warning("La IA no pudo encontrar un movimiento válido.")
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
    st.session_state.board = chess.Board()
    st.success("Partida reiniciada.")
    st.rerun()
