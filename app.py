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


def generate_image(received_prompt):
    """Genera una imagen basada en un received_prompt usando DALL·E."""
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=received_prompt,
            size="1024x1024",
            n=1
        )
        image_url = response['data'][0]['url']
        return received_prompt, image_url
        
    except Exception as e:
        print(f"Error al generar la imagen: {e}")
        return None, None


def add_logo_to_image(image_url, logo_path="logo.png"):
    """Añade un logo a la imagen generada."""
    try:
        # Descargar la imagen desde la URL
        response = requests.get(image_url)
        response.raise_for_status()  # Asegura que la solicitud fue exitosa
        image = Image.open(BytesIO(response.content))

        # Abrir el logo
        logo = Image.open(logo_path)

        # Redimensionar el logo si es necesario
        logo.thumbnail((image.width // 5, image.height // 5))

        # Superponer el logo en la esquina inferior derecha de la imagen
        image.paste(logo, (image.width - logo.width, image.height - logo.height), logo)

        # Guardar la imagen temporalmente con el logo
        image_with_logo_path = "image_with_logo.png"
        image.save(image_with_logo_path)

        # Cerrar los archivos abiertos
        image.close()
        logo.close()

        return image_with_logo_path
    except Exception as e:
        print(f"Error al añadir el logo a la imagen: {e}")
        return None


def clean_filename(text):
    """Limpia el texto para que sea un nombre de archivo válido."""
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


@app.route('/generate-image-with-logo', methods=['POST'])
def generate_image_with_logo():
    try:
        # Obtener el received_prompt desde el cuerpo de la solicitud POST
        data = request.get_json()
        received_prompt = data.get('received_prompt')

        # Verificamos que el received_prompt no esté vacío
        if not received_prompt:
            raise Exception("Se necesita un prompt para generar la imagen.")

        # 1. Generar la imagen basada en el received_prompt
        revised_prompt, image_url = generate_image(received_prompt)
        if not image_url:
            raise Exception("Error al generar la imagen.")

        # 2. Añadir el logo a la imagen generada
        image_with_logo_path = add_logo_to_image(image_url)
        if not image_with_logo_path:
            raise Exception("Error al añadir el logo a la imagen.")

        # 3. Limpiar el received_prompt para usarlo como nombre de archivo
        clean_prompt = clean_filename(revised_prompt)
        firebase_path = f"generated_images/{clean_prompt}.png"

        # 4. Subir la imagen con el logo a Firebase
        firebase_url = upload_to_firebase(image_with_logo_path, firebase_path)
        if not firebase_url:
            raise Exception("Error al subir la imagen con logo a Firebase.")

        return jsonify({
            "received_prompt": revised_prompt,
            "image_url": image_url,
            "image_with_logo_path": image_with_logo_path,
            "firebase_url": firebase_url
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
