import board
import adafruit_dht
import random

def read_sensor():    
    try:
        dht = adafruit_dht.DHT11(board.D4)

        # Leo la temperatura y la humedad
        temperatura = dht.temperature
        humedad    = dht.humidity

        # Creo el json con los datos
        data = {
            "temperature": round(temperatura, 2),
            "humidity": round(humedad, 2),
            "co2": round(random.uniform(400, 2000), 1)
        }

        return data
    except RuntimeError as e:
        return None 


