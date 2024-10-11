from flask import Flask, jsonify, request
import json
import openai
import os
import requests
from io import BytesIO
from PIL import Image
import re
import firebase_admin
from firebase_admin import credentials, storage
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurar Firebase Admin SDK para desplegarla en Render
firebase_cred_json = os.getenv("FIREBASE_ADMIN_SDK")
firebase_cred = json.loads(firebase_cred_json)
cred = credentials.Certificate(firebase_cred)  # Credenciales JSON
firebase_admin.initialize_app(cred, {
    'storageBucket': 'artmind-9f80a.appspot.com'  # Tu bucket de Firebase
})

# Configurar OpenAI key para desplegar en Render
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_image(prompt):
    """Genera una imagen basada en un prompt usando DALL·E."""
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )
        image_url = response['data'][0]['url']
        return prompt, image_url
    except Exception as e:
        print(f"Error al generar la imagen: {e}")
        return None, None


def clean_filename(text):
    """Limpia el texto para que sea un nombre de archivo válido."""
    return re.sub(r'[^A-Za-z0-9]+', '_', text)


def upload_to_firebase(image_url, destination_blob_name):
    """Descarga la imagen desde la URL y la sube a Firebase Storage."""
    try:
        # Descargar la imagen desde la URL
        response = requests.get(image_url)
        response.raise_for_status()  # Asegura que la solicitud fue exitosa

        # Guardar la imagen temporalmente en el servidor
        image_data = BytesIO(response.content)

        # Subir la imagen a Firebase
        bucket = storage.bucket()
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(image_data, content_type='image/png')

        # Hacer que el archivo sea público
        blob.make_public()

        # Retornar la URL pública del archivo subido
        return blob.public_url
    except Exception as e:
        print(f"Error al subir a Firebase: {e}")
        return None


@app.route('/generate-image-with-logo', methods=['POST'])
def generate_image_with_logo():
    try:
        # Obtener el prompt desde el cuerpo de la solicitud POST
        data = request.get_json()
        prompt = data.get('prompt')

        # Verificamos que el prompt no esté vacío
        if not prompt:
            raise Exception("Se necesita un prompt para generar la imagen.")

        # 1. Generar la imagen basada en el prompt
        revised_prompt, image_url = generate_image(prompt)
        if not image_url:
            raise Exception("Error al generar la imagen.")

        # 2. Limpiar el prompt para usarlo como nombre de archivo
        clean_prompt = clean_filename(revised_prompt)
        firebase_path = f"generated_images/{clean_prompt}.png"

        # 3. Subir la imagen generada a Firebase
        firebase_url = upload_to_firebase(image_url, firebase_path)
        if not firebase_url:
            raise Exception("Error al subir la imagen a Firebase.")

        return jsonify({
            "prompt": revised_prompt,
            "image_url": image_url,
            "firebase_url": firebase_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
