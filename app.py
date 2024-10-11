from flask import Flask, jsonify, request
from classArtMind import ArtMind
import json
import os
import firebase_admin
from firebase_admin import credentials, storage
import re

app = Flask(__name__)

# Configurar Firebase Admin SDK para desplegarla en Render
firebase_cred_json = os.getenv("FIREBASE_ADMIN_SDK")
firebase_cred = json.loads(firebase_cred_json)
cred = credentials.Certificate(firebase_cred)  # Ruta del archivo de credenciales JSON
firebase_admin.initialize_app(cred, {
    'storageBucket': 'artmind-9f80a.appspot.com'  # Tu bucket de Firebase
})

# Crear una instancia de la clase ArtMind con configuración del logo
art_mind = ArtMind(logo_file="logo.png")

# Directorio temporal para almacenar los datos intermedios
TEMP_DIR = "temp_data"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def save_to_file(filename, data):
    """Guarda datos en un archivo dentro del directorio temporal."""
    with open(os.path.join(TEMP_DIR, filename), 'w') as file:
        file.write(data)

def read_from_file(filename):
    """Lee datos desde un archivo dentro del directorio temporal."""
    try:
        with open(os.path.join(TEMP_DIR, filename), 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

def clean_filename(text):
    """Limpia el texto para que sea un nombre de archivo válido."""
    # Remueve caracteres no alfanuméricos y reemplaza espacios por guiones bajos
    return re.sub(r'[^A-Za-z0-9]+', '_', text)

def upload_to_firebase(image_path, destination_blob_name):
    """Sube la imagen a Firebase Storage y retorna la URL."""
    try:
        bucket = storage.bucket()  # Obtener el bucket de Firebase
        blob = bucket.blob(destination_blob_name)  # Crear un blob en la ruta de destino

        # Subir el archivo a Firebase Storage
        blob.upload_from_filename(image_path)

        # Hacer que el archivo sea público
        blob.make_public()

        # Retornar la URL pública del archivo subido
        return blob.public_url
    except Exception as e:
        print(f"Error al subir a Firebase: {e}")
        return None

# 1. Endpoint para grabar el audio (POST)
@app.route('/record-audio', methods=['POST'])
def record_audio():
    try:
        audio_path = art_mind.record_audio()
        if not audio_path:
            raise Exception("Error al grabar el audio.")
        
        # Guardar la ruta del archivo de audio
        save_to_file("audio_path.txt", audio_path)
        
        return jsonify({"audio_path": audio_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Endpoint para transcribir el audio (GET)
@app.route('/audio-to-text', methods=['GET'])
def audio_to_text():
    try:
        audio_path = read_from_file("audio_path.txt")
        if not audio_path:
            raise Exception("No hay audio grabado disponible para transcribir.")
        
        transcription = art_mind.audio_to_text(audio_path)
        if not transcription:
            raise Exception("Error al transcribir el audio.")
        
        # Guardar la transcripción
        save_to_file("transcription.txt", transcription)
        
        return jsonify({"transcription": transcription}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Endpoint para traducir el texto (GET)
@app.route('/translate-text', methods=['GET'])
def translate_text():
    try:
        transcription = read_from_file("transcription.txt")
        if not transcription:
            raise Exception("No hay transcripción disponible para traducir.")
        
        translation = art_mind.translate_text(transcription)
        if not translation:
            raise Exception("Error al traducir el texto.")
        
        # Guardar la traducción
        save_to_file("translation.txt", translation)
        
        return jsonify({"translation": translation}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. Endpoint para generar una imagen con el logo y subirla a Firebase Storage (GET)
@app.route('/generate-image-with-logo', methods=['GET'])
def generate_image_with_logo():
    try:
        translation = read_from_file("translation.txt")
        if not translation:
            raise Exception("No hay texto traducido disponible para generar la imagen.")
        
        # 1. Generar la imagen basada en la traducción
        image_url = art_mind.generate_image(translation)
        if not image_url:
            raise Exception("Error al generar la imagen.")
        
        # 2. Añadir el logo a la imagen generada
        image_with_logo_path = art_mind.add_logo_to_image(image_url)
        if not image_with_logo_path:
            raise Exception("Error al añadir el logo a la imagen.")
        
        # 3. Usar el texto traducido para generar un nombre de archivo único
        clean_translation = clean_filename(translation)
        firebase_path = f"generated_images/{clean_translation}.png"
        
        # 4. Subir la imagen con el logo a Firebase Storage
        firebase_url = upload_to_firebase(image_with_logo_path, firebase_path)
        if not firebase_url:
            raise Exception("Error al subir la imagen con logo a Firebase.")

        return jsonify({
            "image_url": image_url,
            "image_with_logo_path": image_with_logo_path,
            "firebase_url": firebase_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
