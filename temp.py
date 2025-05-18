from machine import Pin, I2C
import time

# AHT21 I2C address
AHT21_ADDRESS = 0x38

# Initialize I2C (moved inside a function to avoid conflicts during import)
i2c = None

def aht21_init():
    """Initialize the AHT21 sensor."""
    global i2c
    if i2c is None:
        # Setup I2C (I2C0 bus on GP0 and GP1)
        i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
    try:
        # Soft reset
        i2c.writeto(AHT21_ADDRESS, bytearray([0xBE]))
        time.sleep(0.02)
    except OSError as e:
        print("Error during initialization:", e)
        raise

def aht21_read():
    """Read temperature and humidity from the AHT21 sensor."""
    global i2c
    if i2c is None:
        raise RuntimeError("I2C not initialized. Call aht21_init() first.")
    
    try:
        # Trigger measurement
        i2c.writeto(AHT21_ADDRESS, bytearray([0xAC, 0x33, 0x00]))
        time.sleep(0.08)
        
        # Read 6 bytes of data
        data = i2c.readfrom(AHT21_ADDRESS, 6)
    except OSError as e:
        print("Error reading from sensor:", e)
        return None, None

    # Check if the sensor is busy
    status = data[0]
    if (status & 0x80):
        print("Sensor is busy.")
        return None, None  # Sensor busy
    
    # Calculate humidity
    humidity = (((data[1] << 8) | data[2]) >> 4) / (1 << 12) * 100.0
    
    # Calculate temperature
    temperature = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]) / (1 << 20) * 200.0 - 50.0
    
    return temperature, humidity

def get_temp():
    """Read and return temperature and humidity once."""
    try:
        # Initialize the sensor
        aht21_init()
    except RuntimeError as e:
        print("Failed to initialize the sensor:", e)
        return None, None

    # Read temperature and humidity
    temp_c, hum = aht21_read()
    if temp_c is not None and hum is not None:
        temp_f = (temp_c * 9/5) + 32
        print('Temperature: {:.2f} °F'.format(temp_f))
        print('Humidity: {:.2f} %'.format(hum))
        return temp_f, hum
    else:
        print('Sensor not ready.')
        return None, None

# Ensure this block only runs when the script is executed directly
if __name__ == "__main__":
    get_temp()