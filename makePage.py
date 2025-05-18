from time import localtime  # Import localtime for use in the function

def make_page(status, on_time, off_time, temp=None, humidity=None, soil=None, logs=None):
    """Generate the HTML page for the web server."""
    def fmt(sec): return f"{sec//3600:02}:{(sec%3600)//60:02}:{sec%60:02}"
    now = localtime()
    current_time = f"{now[3]:02}:{now[4]:02}:{now[5]:02}"
    current_date = f"{now[1]:02}/{now[2]:02}/{now[0]}"
    on_str = fmt(on_time) if on_time else "--"
    off_str = fmt(off_time) if off_time else "--"

    temp_str = f"{temp} °F" if temp else "--"
    hum_str = f"{humidity} %" if humidity else "--"
    soil_str = f"{soil:.2f} %" if soil else "--"

    # Use provided logs or initialize an empty list if logs is None
    if logs is None:
        logs = []

    rows = "\n".join(
        f"<tr><td>{e['date']}</td><td>{e['time']}</td><td>{e['event']}</td><td>{e['temp']}</td><td>{e['humidity']}</td><td>{e['soil']}</td></tr>"
        for e in logs
    )

    return f"""
    <html>
    <head>
        <title>Grow Box Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }}
            h1 {{
                color: #333;
            }}
            table {{
                margin: 20px auto;
                border-collapse: collapse;
                width: 80%;
                background-color: #fff;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #ddd;
            }}
            button {{
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px 0;
                cursor: pointer;
                border-radius: 5px;
            }}
            button:hover {{
                background-color: #45a049;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Grow Box Dashboard</h1>
            <p><b>Current Time:</b> {current_date} {current_time}</p>
            <p><b>Light Status:</b> {status}</p>
            <p><b>Light On At:</b> {on_str} | <b>Off At:</b> {off_str}</p>
            <form action="/" method="get">
                <button type="submit" name="pump" value="1">Run Pump</button>
            </form>
            <p><b>Temp:</b> {temp_str} | <b>Humidity:</b> {hum_str} | <b>Soil Moisture:</b> {soil_str}</p>
            <h2>Recent Events</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Event</th>
                    <th>Temp</th>
                    <th>Humidity</th>
                    <th>Soil</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """