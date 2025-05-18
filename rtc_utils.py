import network
import socket
import struct
import time
from utime import localtime

def connect_wifi(ssid, password, timeout=10):
    """Connect to Wi-Fi with debug messages"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("📡 Connecting to Wi-Fi...")
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("❌ Wi-Fi connection timed out.")
                raise RuntimeError("Wi-Fi connection timed out.")
            print("⏳ Waiting for connection...")
            time.sleep(0.5)

    print("✅ Connected to Wi-Fi:", wlan.ifconfig())
    return wlan.ifconfig()


from machine import RTC

def sync_ntp_time(host="pool.ntp.org", timezone_offset=-18000):  # Set default to EST (UTC-5)
    """Sync time with NTP server and apply timezone offset (in seconds)"""
    NTP_DELTA = 2208988800  # NTP time starts in 1900, Unix in 1970
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(2)
        msg = b'\x1b' + 47 * b'\0'
        s.sendto(msg, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA + timezone_offset
    print("NTP Time (UTC):", time.localtime(val - NTP_DELTA))  # Debug: Print UTC time
    print("Adjusted Time (Local):", time.localtime(t))         # Debug: Print local time

    # Set system RTC
    rtc = RTC()
    tm = time.localtime(t)
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    print("✅ RTC set to:", rtc.datetime())

def get_time_24h():
    """Returns current time in 24-hour format: HH:MM:SS"""
    now = localtime()
    return "{:02}:{:02}:{:02}".format(now[3], now[4], now[5])

def get_time_12h():
    """Returns current time in 12-hour format: HH:MM:SS AM/PM"""
    now = localtime()
    hour = now[3]
    suffix = "AM" if hour < 12 else "PM"
    hour = hour % 12
    if hour == 0:
        hour = 12
    return "{:02}:{:02}:{:02} {}".format(hour, now[4], now[5], suffix)

def get_date_us():
    """Returns current date in US format: MM/DD/YYYY"""
    now = localtime()
    return "{:02}/{:02}/{:04}".format(now[1], now[2], now[0])

def get_datetime_12h():
    """Returns full date and time in 12-hour US format"""
    return f"{get_date_us()} {get_time_12h()}"

def get_datetime_24h():
    """Returns full date and time in 24-hour format"""
    return f"{get_date_us()} {get_time_24h()}"
