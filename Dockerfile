# Usa una imagen base liviana de Python
FROM python:3.11-slim

# Establece el directorio dentro del contenedor
WORKDIR /app

# Copia todo el contenido del proyecto al contenedor
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando de entrada por defecto
CMD ["python", "src/index.py"]
