from machine import ADC
import time

# --- Setup ---
soil_sensor = ADC(26)           # Soil sensor on GP26
DRY_VALUE = 55000               # Raw ADC value for completely dry soil
WET_VALUE = 22000               # Raw ADC value for completely wet soil

# --- Function ---
def check_soil_moisture():
    # Read the raw ADC value
    moisture = soil_sensor.read_u16()
    print(f"Raw ADC Value: {moisture}")

    # Map the raw ADC value to a percentage
    if moisture <= WET_VALUE:
        moisture_percentage = 100.0
    elif moisture >= DRY_VALUE:
        moisture_percentage = 0.0
    else:
        moisture_percentage = ((DRY_VALUE - moisture) / (DRY_VALUE - WET_VALUE)) * 100

    print(f"Soil Moisture: {moisture_percentage:.2f}%")

    return moisture_percentage  # Optional: return value for logging or tracking

# --- Main loop for testing or standalone run ---
if __name__ == "__main__":
    while True:
        check_soil_moisture()
        time.sleep(10)  # Wait between checks
