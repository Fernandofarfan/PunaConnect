# PunaConnect

Este es un MVP de un bot de Telegram diseñado para resolver el problema de matchmaking en una Hackathon. Permite a los usuarios registrarse, seleccionar su rol y modalidad, y ejecutar un algoritmo para agrupar automáticamente a los participantes sin equipo en grupos de hasta 4 personas balanceando los perfiles.

## Archivos incluidos
* `bot.py`: Contiene la lógica del bot de Telegram, manejadores de comandos y flujos de conversación.
* `database.py`: Define el esquema de la base de datos usando SQLAlchemy y funciones para registrar y agrupar usuarios.
* `requirements.txt`: Dependencias del proyecto.
* `Dockerfile`: Archivo para contenerizar la aplicación.

## Requisitos previos
1. Obtén un Token de Telegram hablando con [BotFather](https://t.me/BotFather).
2. Tener Docker instalado (para ejecución contenerizada) o Python 3.11+.

## Ejecución Local

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el bot pasándole el token como variable de entorno:
   ```bash
   # En Windows (PowerShell)
   $env:TELEGRAM_TOKEN="tu_token_aqui"
   python bot.py
   
   # En Linux/Mac
   export TELEGRAM_TOKEN="tu_token_aqui"
   python bot.py
   ```

## Ejecución con Docker (Listo para Cloud Run / Kubernetes)

1. Construye la imagen:
   ```bash
   docker build -t punaconnect .
   ```
2. Corre el contenedor:
   ```bash
   docker run -e TELEGRAM_TOKEN="tu_token_aqui" punaconnect
   ```

Para desplegar en Google Cloud Run u otro servicio similar, solo necesitas subir la imagen Docker a un Container Registry y desplegarla inyectando la variable de entorno `TELEGRAM_TOKEN` (no te olvides de asegurar que el contenedor tenga permisos para escribir en el archivo SQLite, o alternativamente conectarlo a una base de datos externa tipo PostgreSQL para producción).
