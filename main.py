from rtc_utils import sync_ntp_time
from machine import Pin
from time import sleep, localtime, time
import socket
from temp import get_temp
from soil import check_soil_moisture
import network
from makePage import make_page

# --- Load Wi-Fi Credentials from .env File ---
def load_env(file_path="security.env"):
    """Load environment variables from a .env file."""
    env_vars = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    except Exception as e:
        print(f"Error loading .env file: {e}")
    return env_vars

# Load Wi-Fi credentials
env = load_env()
wifi_ssid = env.get("WIFI_SSID")
wifi_password = env.get("WIFI_PASSWORD")

if not wifi_ssid or not wifi_password:
    raise RuntimeError("Wi-Fi SSID or password not found in security.env file.")

# --- Wi-Fi Setup ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)

print("Connecting to Wi-Fi...")
timeout = 10
start_time = time()
while not wlan.isconnected() and (time() - start_time) < timeout:
    print("Waiting for connection...")
    sleep(1)

if wlan.isconnected():
    print("Connected to Wi-Fi:", wlan.ifconfig())
    sync_ntp_time(timezone_offset=-14400)  # EDT
else:
    raise RuntimeError("Failed to connect to Wi-Fi. Cannot continue.")

# --- Component Setup ---
led = Pin(15, Pin.OUT)
fan = Pin(14, Pin.OUT)
pump = Pin(16, Pin.OUT)
pump.off()
fan.off()
led.off()

# --- Configuration ---
LED_ON_HOUR, LED_ON_MINUTE = 7, 0
LED_OFF_HOUR, LED_OFF_MINUTE = 22, 0
FAN_RUN_TIME = 20
FAN_INTERVAL = 30 * 60
last_fan_run = 0
logs = []

# --- Functions ---
def run_pump(seconds=1):
    """Run the pump for a set number of seconds."""
    print("Pump ON")
    pump.on()
    sleep(seconds)
    pump.off()
    print("Pump OFF")

def update_led_state():
    """Update the LED state based on the current time."""
    now = localtime()
    current_sec = now[3] * 3600 + now[4] * 60 + now[5]
    on_sec = LED_ON_HOUR * 3600 + LED_ON_MINUTE * 60
    off_sec = LED_OFF_HOUR * 3600 + LED_OFF_MINUTE * 60

    if on_sec <= current_sec < off_sec:
        led.on()
        return "ON", on_sec, off_sec
    else:
        led.off()
        return "OFF", on_sec, off_sec

def log_event(event, temp, humidity, soil):
    """Log an event with timestamp and sensor data."""
    now = localtime()
    logs.insert(0, {
        "date": f"{now[1]:02}/{now[2]:02}/{now[0]}",
        "time": f"{now[3]:02}:{now[4]:02}:{now[5]:02}",
        "event": event,
        "temp": f"{temp:.1f} °F",
        "humidity": f"{humidity:.1f} %",
        "soil": f"{soil:.1f} %"
    })
    if len(logs) > 50:
        logs.pop()

# --- Web Server Setup ---
ip = wlan.ifconfig()[0]
print("Web server available at: http://" + ip)

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 80))
server.listen(1)
server.settimeout(5)

# --- Main Loop ---
while True:
    try:
        temp, humidity = get_temp()
        soil = check_soil_moisture()

        # Update LED state
        prev_led = led.value()
        status, on_time, off_time = update_led_state()
        if status == "ON" and prev_led == 0:
            log_event("Light turned ON", temp, humidity, soil)
        elif status == "OFF" and prev_led == 1:
            log_event("Light turned OFF", temp, humidity, soil)

        # Check soil moisture
        if soil < 35:
            print(" Soil dry, running pump.")
            run_pump(1)
            log_event("Pump ran (auto)", temp, humidity, soil)

        # Run fan periodically
        if time() - last_fan_run >= FAN_INTERVAL:
            print("Fan ON")
            fan.on()
            sleep(FAN_RUN_TIME)
            fan.off()
            print("Fan OFF")
            log_event("Fan ran (periodic)", temp, humidity, soil)
            last_fan_run = time()

        # Run fan if humidity exceeds 60%
        if humidity is not None and humidity > 60 and not fan.value():
            print("High humidity detected, running fan.")
            fan.on()
            sleep(10)  # Run fan for 10 seconds
            fan.off()
            print("Fan OFF (humidity)")
            log_event("Fan ran (humidity)", temp, humidity, soil)

        # Handle web requests
        try:
            client, addr = server.accept()
            print("Client connected from", addr)
            request = client.recv(1024)
            print("Request:", request.decode().split('\r\n')[0])

            if b"GET /?pump=1" in request:
                run_pump(1)
                log_event("Pump ran (manual)", temp, humidity, soil)

                # Redirect back to the home page
                client.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            else:
                # Pass the logs list to make_page()
                html = make_page(status, on_time, off_time, temp, humidity, soil, logs)
                client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                client.send(html.encode())

        except Exception as err:
            print("Client error:", err)

        finally:
            client.close()

    except Exception as e:
        print("Main loop error:", e)

    sleep(1)
