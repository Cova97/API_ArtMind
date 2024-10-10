# ArtMind

ArtMind es una API que permite transformar grabaciones de audio en imágenes generadas automáticamente, utilizando las herramientas de OpenAI y el almacenamiento de Firebase. El flujo del proceso es el siguiente:

1. **Grabación de audio**: Se graba el audio que contiene la descripción.
2. **Transcripción del audio**: El audio se transforma en texto utilizando la tecnología de **Whisper** de OpenAI.
3. **Traducción del texto**: El texto transcrito se traduce al inglés mediante **ChatGPT 3.5 Turbo**.
4. **Generación de imagen**: El texto en inglés se utiliza como input para **DALL·E 3** de OpenAI, que genera una imagen a partir de la descripción.
5. **Almacenamiento de la imagen**: La imagen generada se sube a **Firebase Storage** y se guarda con el nombre o el texto traducido.

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

## Uso

### Endpoints

- **POST /audio**: Sube un archivo de audio, lo convierte a texto, traduce el texto al inglés y genera una imagen a partir de él.
  - Parámetros:
    - `file`: Archivo de audio (formato .wav o .mp3).
  - Respuesta:
    - URL de la imagen generada almacenada en Firebase.

### Ejemplo con cURL

```bash
curl -X POST http://localhost:5000/audio -F "file=@path-to-audio-file.wav"
