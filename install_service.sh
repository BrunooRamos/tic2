#!/bin/bash

# Script de instalación del servicio de monitoreo ambiental
# Este script configura el sistema para ejecutarse como demonio

echo "=== Instalando Sistema de Monitoreo Ambiental como Servicio ==="

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Variables
SERVICE_NAME="monitoreo"
PROJECT_DIR="/home/pi/monitoreo"
LOG_DIR="/var/log/monitoreo"
USER="grupo13"

echo "1. Creando directorio de logs..."
mkdir -p $LOG_DIR
chown $USER:$USER $LOG_DIR
chmod 755 $LOG_DIR

echo "2. Copiando archivo de servicio..."
cp $PROJECT_DIR/$SERVICE_NAME.service /etc/systemd/system/

echo "3. Configurando permisos..."
chmod 644 /etc/systemd/system/$SERVICE_NAME.service

echo "4. Recargando systemd..."
systemctl daemon-reload

echo "5. Habilitando el servicio para inicio automático..."
systemctl enable $SERVICE_NAME

echo "6. Iniciando el servicio..."
systemctl start $SERVICE_NAME

echo "7. Verificando estado del servicio..."
systemctl status $SERVICE_NAME

echo ""
echo "=== Instalación completada ==="
echo ""
echo "Comandos útiles:"
echo "  Ver estado:     sudo systemctl status $SERVICE_NAME"
echo "  Iniciar:        sudo systemctl start $SERVICE_NAME"
echo "  Detener:        sudo systemctl stop $SERVICE_NAME"
echo "  Reiniciar:      sudo systemctl restart $SERVICE_NAME"
echo "  Ver logs:       sudo journalctl -u $SERVICE_NAME -f"
echo "  Deshabilitar:   sudo systemctl disable $SERVICE_NAME"
echo ""
echo "El servicio se iniciará automáticamente al reiniciar el sistema." 