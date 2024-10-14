import os
from openai import OpenAI
import gradio as gr
import webbrowser
from io import BytesIO
from PIL import Image
import requests
import qrcode

client = OpenAI()


def speech_to_text(audio):
    try:
        audio_file = open(audio, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
        return transcript
    except Exception as e:
        print(f"Error en la transcripción del audio: {e}")
        return ""


def translate(text, language="en"):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un traductor experto en varios idiomas y puedes traducir cualquier texto al ingles."},
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error en la traducción: {e}")
        return ""


def image_generator(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        revised_prompt = response.data[0].revised_prompt
        image_url = response.data[0].url
        return revised_prompt, image_url
    except Exception as e:
        print(f"Error en la generación de la imagen: {e}")
        return "", ""


def qrcode_generator(text):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img_byte = BytesIO()
        qr_img.save(qr_img_byte, format='PNG')
        qr_img_byte.seek(0)
        return Image.open(qr_img_byte)
    except Exception as e:
        print(f"Error en la generación del código QR: {e}")
        return None


def multi_model(audio):
    # Transcripción de voz a texto
    text = speech_to_text(audio)
    print(f'\nSPEECH TO TEXT: {text}')

    # Traducción del texto
    translated_text = translate(text)
    print(f'\nTRANSLATED TEXT: {translated_text}')

    # Generación de imagen
    revised_prompt, image_url = image_generator(translated_text)
    print(f'\nMAGIC PROMPT: {revised_prompt}')
    print(f'\nIMAGE URL: {image_url}')
    image = Image.open(BytesIO(requests.get(image_url).content))
    print(f'\nIMAGE: {image}')

    # Cargar imagen (logo_frojo_tblanco.png) y superponerla a la imagen generada en la esquina inferior derecha
    logo = Image.open("logo.png")
    image.paste(logo, (image.width - logo.width, image.height - logo.height), logo)

    # Generación de código QR
    qr_code = qrcode_generator(image_url)

    return text, image, qr_code


output_text = gr.Textbox(label="Texto transcrito")
output_image = gr.Image(type='pil', label="Imagen generada")
output_qr_code = gr.Image(type='pil', label="Código QR")
description = """
ArtMind - Generador de imagenes cool por voz 
"""

ui = gr.Interface(
    fn=multi_model,
    inputs=gr.Audio(sources=["microphone"], type="filepath",
                    label="Ejemplo: Un perro en patineta"),
    outputs=[
        output_text,
        output_image,
        output_qr_code
    ],
    title="ArtMind",
    description=description,
)

if __name__ == "__main__":
    ui.launch(share=True)
    # ui.launch()
