#!/bin/bash

# Script de configuración completa para Raspberry Pi
# Este script instala y configura todo el sistema de monitoreo ambiental

echo "=== Configuración del Sistema de Monitoreo Ambiental en Raspberry Pi ==="

# Verificar que se ejecuta como usuario pi
if [ "$USER" != "pi" ]; then
    echo "Advertencia: Se recomienda ejecutar este script como usuario 'pi'"
fi

# Variables
PROJECT_NAME="monitoreo"
PROJECT_DIR="/home/pi/$PROJECT_NAME"

echo "1. Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

echo "2. Instalando dependencias del sistema..."
sudo apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib

echo "3. Configurando PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configurar base de datos
sudo -u postgres psql -c "CREATE DATABASE roomdb;"
sudo -u postgres psql -c "CREATE USER room WITH PASSWORD 'room13';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE roomdb TO room;"

echo "4. Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

echo "5. Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "6. Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp env_template.txt .env
    echo "Archivo .env creado. Por favor, edítalo con tus configuraciones específicas."
    echo "Especialmente cambia RASPBERRY_ID para cada dispositivo."
fi

echo "7. Configurando la base de datos..."
if [ -f "database/script/script.sql" ]; then
    sudo -u postgres psql -d roomdb -f database/script/script.sql
fi

echo "8. Configurando permisos para GPIO y cámara..."
sudo usermod -a -G gpio,i2c,spi,video pi

echo "9. Habilitando interfaces necesarias..."
# Habilitar I2C, SPI y cámara
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_camera 0

echo ""
echo "=== Configuración básica completada ==="
echo ""
echo "Pasos siguientes:"
echo "1. Edita el archivo .env con tus configuraciones específicas:"
echo "   nano .env"
echo ""
echo "2. Para instalar como servicio (demonio), ejecuta:"
echo "   sudo ./install_service.sh"
echo ""
echo "3. Para probar manualmente:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "4. Reinicia el sistema para aplicar todos los cambios:"
echo "   sudo reboot" 