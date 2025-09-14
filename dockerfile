FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requirements e instala las dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación
COPY . .

# Concede permisos de ejecución al binario de Stockfish
RUN chmod +x ./bin/stockfish

# Comando para ejecutar tu aplicación Streamlit
CMD ["streamlit", "run", "streamlit.app.py"]
