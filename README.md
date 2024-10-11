# ArtMind

ArtMind es una API que permite transformar grabaciones de audio en imágenes generadas automáticamente, utilizando las herramientas de OpenAI y el almacenamiento de Firebase.

## Características

- **Transcripción automática**: Convierte grabaciones de audio a texto con gran precisión.
- **Traducción automática**: Traduce el texto transcrito al inglés, facilitando la generación de imágenes en un idioma universal.
- **Generación de imágenes**: Utiliza el potente modelo de **DALL·E 3** para crear imágenes realistas y creativas a partir de las descripciones traducidas.
- **Almacenamiento en la nube**: Guarda las imágenes generadas en **Firebase**, permitiendo un acceso rápido y seguro.

## Tecnologías

- **OpenAI Whisper**: Transcripción de audio a texto.
- **OpenAI ChatGPT 3.5 Turbo**: Traducción de texto a inglés.
- **OpenAI DALL·E 3**: Generación de imágenes a partir de texto.
- **Firebase Storage**: Almacenamiento de las imágenes generadas.

## Requisitos

- **Python 3.12** o superior.
- Una cuenta en OpenAI para acceder a las APIs de **Whisper**, **ChatGPT** y **DALL·E**.
- Una cuenta de Firebase con un proyecto configurado para almacenar imágenes.
- Paquetes requeridos (instalables vía `pip`):
  - `openai`
  - `firebase-admin`
  - `flask`
  - `flask-cors`
  - `requests`
  - Otros (ver `requirements.txt` para detalles completos).

## Instalación

1. Clona este repositorio:

    ```bash
    git clone https://github.com/tu-usuario/artmind.git
    cd artmind
    ```

2. Crea un entorno virtual (opcional pero recomendado):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Configura las credenciales de OpenAI y Firebase en un archivo `.env`:

    ```bash
    OPENAI_API_KEY=tu-api-key-de-openai
    FIREBASE_CREDENTIALS_PATH=ruta/a/tus/credenciales-de-firebase.json
    ```

5. Ejecuta la API:

    ```bash
    flask run
    ```

## Uso con Postman

Aquí tienes los pasos detallados y los comandos para probar cada uno de los endpoints usando Postman:

### 1. Grabar audio (POST)

Este endpoint permite grabar un audio y guardarlo en un archivo WAV.

- **Método**: POST
- **URL**: `http://127.0.0.1:5000/record-audio`

#### Instrucciones en Postman:
1. Abre Postman y crea una nueva solicitud.
2. Selecciona **POST** como método.
3. Ingresa la URL `http://127.0.0.1:5000/record-audio`.
4. En la pestaña **Body**, asegúrate de que esté vacío o selecciona **none**.
5. Haz clic en **Send**.

#### Respuesta esperada:
```json
{
  "audio_path": "ruta_del_audio.wav"
}

