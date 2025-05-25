# Sistema de Monitoreo Ambiental

Sistema de monitoreo ambiental que recolecta datos de sensores (temperatura, humedad, CO2) y conteo de personas, procesa la información y la envía a un servidor central.

## Características

- Recolección de datos en tiempo real de:
  - Temperatura
  - Humedad
  - Niveles de CO2
  - Conteo de personas (usando YOLOv8)
- Procesamiento de datos cada 2 minutos
- Envío seguro de datos a servidor central
- Sistema de reintentos automático
- Logging detallado de operaciones
- Manejo robusto de errores

## Requisitos

- Python 3.8+
- PostgreSQL
- Raspberry Pi (recomendado)
- Sensores:
  - DHT22 (temperatura y humedad)
  - Cámara para conteo de personas

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear un archivo `.env` en la raíz del proyecto con:
```env
# Raspberry Pi Configuration
RASPBERRY_ID=1

# Processing Intervals (in seconds)
PROCESSING_INTERVAL=120

# Database Configuration
DATABASE_URL=database_url

# API Configuration
API_ENDPOINT=your_api_endpoint
```

5. Configurar la base de datos:
```bash
psql -U your_user -d your_database -f database/script/script.sql
```

## Estructura del Proyecto

```
.
├── camara/              # Módulo de detección de personas
├── database/           # Módulo de base de datos
│   ├── models/        # Modelos de datos
│   ├── queries.py     # Consultas a la base de datos
│   └── db_handler.py  # Manejo de conexión
├── iot/               # Módulo de IoT (no utilizado actualmente)
├── process_to_ec2/    # Módulo de procesamiento y envío
├── seguridad/         # Módulo de seguridad y criptografía
├── sensor/           # Módulo de lectura de sensores
├── main.py           # Punto de entrada principal
├── requirements.txt  # Dependencias del proyecto
└── .env             # Configuración (no incluido en el repositorio)
```

## Uso

1. Asegurarse de que los sensores estén conectados correctamente
2. Activar el entorno virtual si no está activo
3. Ejecutar el programa principal:
```bash
python main.py
```

## Flujo de Datos

1. **Recolección**:
   - Los datos se recolectan en tiempo real
   - Se guardan en la base de datos con `processed=False`

2. **Procesamiento** (cada 2 minutos):
   - Se obtienen datos no procesados
   - Se calculan promedios
   - Se crea un registro procesado
   - Se intenta enviar a la API
   - Se borran los datos originales

3. **Manejo de Errores**:
   - Reintentos automáticos en caso de fallo
   - Logging detallado de errores
   - Mantenimiento de datos procesados

## Logging

Los logs se guardan en `app.log` e incluyen:
- Lecturas de sensores
- Procesamiento de datos
- Envíos a la API
- Errores y reintentos
