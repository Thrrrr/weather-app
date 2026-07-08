from flask import Flask, render_template, request, session, redirect, url_for
import requests
from datetime import datetime, timezone, timedelta
import os
from urllib.parse import quote
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Simple username/password (change these!)
VALID_USERS = {
    'admin': 'password123',
    'user': 'test123'
}

# API key and base URL
api_key = os.getenv('OPENWEATHER_API_KEY')
print(f"DEBUG: API Key loaded: {api_key[:10] if api_key else 'NOT FOUND'}...")
base_url = "https://api.openweathermap.org/data/2.5/weather?"

if not api_key:
    print("ERROR: OPENWEATHER_API_KEY environment variable not set!")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in VALID_USERS and VALID_USERS[username] == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/weather', methods=['POST'])
def get_weather():
    if 'user' not in session:
        return {'error': 'Unauthorized'}, 401
    
    if not api_key:
        return {'error': 'API key not configured'}, 500
    
    city_name = request.form.get('city')
    
    if not city_name:
        return {'error': 'Please enter a city name'}
    
    # Build the complete URL
    complete_url = base_url + "q=" + city_name + "&appid=" + api_key
    
    try:
        response = requests.get(complete_url)
        x = response.json()
        
        if x.get("cod") == "200" or response.status_code == 200:
            # Extract all the weather data
            y = x["main"]
            temp_kelvin = y["temp"]
            current_temperature = temp_kelvin - 273.15
            feels_like_kelvin = y["feels_like"]
            feels_like_temp = feels_like_kelvin - 273.15
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            
            z = x["weather"]
            weather_description = z[0]["description"]
            
            wind_speed = x["wind"]["speed"]
            wind_direction = x["wind"]["deg"]
            wind_gust = x["wind"].get("gust", "N/A")
            
            timezone_offset = x["timezone"]
            sunrise_unix = x["sys"]["sunrise"]
            sunset_unix = x["sys"]["sunset"]
            
            sunrise_time = (datetime.fromtimestamp(sunrise_unix, tz=timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%H:%M:%S")
            sunset_time = (datetime.fromtimestamp(sunset_unix, tz=timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%H:%M:%S")
            
            city_name_display = x["name"]
            country_code = x["sys"]["country"]
            
            city_time = datetime.now(timezone.utc) + timedelta(seconds=timezone_offset)
            current_time = city_time.strftime("%H:%M:%S")
            
            weather_data = {
                'city': city_name_display,
                'country': country_code,
                'time': current_time,
                'temperature': f"{current_temperature:.2f}",
                'feels_like': f"{feels_like_temp:.2f}",
                'wind_speed': f"{wind_speed:.2f}",
                'wind_direction': wind_direction,
                'wind_gust': wind_gust if isinstance(wind_gust, str) else f"{wind_gust:.2f}",
                'pressure': current_pressure,
                'humidity': current_humidity,
                'sunrise': sunrise_time,
                'sunset': sunset_time,
                'description': weather_description,
                'background_image': f"https://source.unsplash.com/1600x900/?{quote(city_name_display)}"
            }
            return weather_data
        else:
            return {'error': 'City not found'}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
