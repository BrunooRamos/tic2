import random
from datetime import datetime

def get_random_measure():    
    data = {
        "co2": round(random.uniform(400, 2000), 1),
        "temperature": round(random.uniform(15, 30), 1),
        "humidity": round(random.uniform(30, 70), 1)
    }
    
    return data
