import openai
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import requests

class ArtMind:
    def __init__(self, audio_file="audio.wav", image_output="image_with_logo.png", logo_file="logo.png"):
        # Cargar las variables de entorno desde el archivo .env
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        
        # Parámetros de grabación
        self.fs = 44100  # Frecuencia de muestreo
        self.seconds = 5  # Duración de la grabación
        self.audio_file = audio_file
        self.image_output = image_output
        self.logo_file = logo_file

    def record_audio(self):
        """Graba audio y guarda en un archivo WAV."""
        try:
            print("Grabando...")
            audio_data = sd.rec(int(self.seconds * self.fs), samplerate=self.fs, channels=1, dtype=np.int16)
            sd.wait()  # Esperar a que la grabación termine
            write(self.audio_file, self.fs, audio_data)
            print(f"Grabación completada. Archivo guardado en {self.audio_file}")
            return self.audio_file
        except Exception as e:
            print(f"Error al grabar audio: {e}")
            return None

    def audio_to_text(self, audio_path):
        """Convierte el audio en texto usando OpenAI."""
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file)
            return transcription['text']
        except Exception as e:
            print(f"Error en la transcripción del audio: {e}")
            return None

    def translate_text(self, text, language="en"):
        """Traduce el texto al inglés usando OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un traductor experto en varios idiomas y puedes traducir cualquier texto al inglés."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error al traducir el texto: {e}")
            return None

    def generate_image(self, prompt):
        """Genera una imagen basada en el prompt usando DALL-E."""
        try:
            response = openai.Image.create(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                n=1
            )
            return response['data'][0]['url']
        except Exception as e:
            print(f"Error al generar la imagen: {e}")
            return None

    def add_logo_to_image(self, image_url):
        """Descarga la imagen generada y le añade un logo."""
        try:
            # Descargar la imagen desde la URL
            image = Image.open(BytesIO(requests.get(image_url).content))
            
            # Abrir el logo
            logo = Image.open(self.logo_file)
            
            # Superponer el logo en la esquina inferior derecha
            image.paste(logo, (image.width - logo.width, image.height - logo.height), logo)
            
            # Guardar la imagen con el logo
            image.save(self.image_output)
            print(f"Logo añadido y imagen guardada en {self.image_output}")
            return self.image_output
        except Exception as e:
            print(f"Error al añadir el logo a la imagen: {e}")
            return None