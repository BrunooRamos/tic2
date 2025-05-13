
# Este script es exclusivo para las Raspberry Pi, donde usar el paquete board tiene sentido

import board
import adafruit_dht
import random

# Inicializo el sensor en el pin 4
dht = adafruit_dht.DHT11(board.D4)

def read_sensor():
    try:
        # Leo la temperatura y la humedad
        temperatura = dht.temperature
        humedad    = dht.humidity

        # Creo el json con los datos
        data = {
            "temperature": round(temperatura, 2),
            "humidity": round(humedad, 2),
            "co2": round(random.uniform(400, 2000), 1)
        }

        print(f"Temp = {temperatura:0.3f}°C  Humidity = {humedad:0.3f}%")
        return data

    except RuntimeError as e:
        # En caso que falle al leer el sensor, se imprime el error
        print("Error al leer el sensor DHT11, probar de vuelta o chequear cableado:", e)


