from flask import Flask, render_template, request, session, redirect, url_for
import requests
from datetime import datetime, timezone, timedelta
import os
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

CITY_IMAGES = {
    'berlin': 'https://images.unsplash.com/photo-1528728329032-2972f65dfb3f?auto=format&fit=crop&w=1600&q=80',
    'london': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=1600&q=80',
    'paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1600&q=80',
    'tokyo': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1600&q=80',
    'new york': 'https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?auto=format&fit=crop&w=1600&q=80',
    'amsterdam': 'https://images.unsplash.com/photo-1512470876302-972faa2aa9a4?auto=format&fit=crop&w=1600&q=80',
    'barcelona': 'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?auto=format&fit=crop&w=1600&q=80',
    'sydney': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=1600&q=80',
    'melbourne': 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80',
    'singapore': 'https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?auto=format&fit=crop&w=1600&q=80',
    'dubai': 'https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=1600&q=80',
    'madrid': 'https://images.unsplash.com/photo-1539037116277-4db20889f2d4?auto=format&fit=crop&w=1600&q=80',
    'rome': 'https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?auto=format&fit=crop&w=1600&q=80',
    'vienna': 'https://images.unsplash.com/photo-1516550893923-42d28e5677af?auto=format&fit=crop&w=1600&q=80',
    'prague': 'https://images.unsplash.com/photo-1541849546-216549ae216d?auto=format&fit=crop&w=1600&q=80',
    'istanbul': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?auto=format&fit=crop&w=1600&q=80',
    'cairo': 'https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1600&q=80',
    'delhi': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1600&q=80',
    'mumbai': 'https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=1600&q=80',
    'seoul': 'https://images.unsplash.com/photo-1538485399081-7191377e8241?auto=format&fit=crop&w=1600&q=80',
    'bangkok': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?auto=format&fit=crop&w=1600&q=80',
    'toronto': 'https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=1600&q=80',
    'los angeles': 'https://images.unsplash.com/photo-1449034446853-66c86144b0ad?auto=format&fit=crop&w=1600&q=80',
    'san francisco': 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=1600&q=80',
    'chicago': 'https://images.unsplash.com/photo-1514565131-fce0801e5785?auto=format&fit=crop&w=1600&q=80',
    'boston': 'https://images.unsplash.com/photo-1493540554008-8b3f0bf3a0f8?auto=format&fit=crop&w=1600&q=80',
    'austin': 'https://images.unsplash.com/photo-1518409789868-bf58c5f23e3f?auto=format&fit=crop&w=1600&q=80',
    'sao paulo': 'https://images.unsplash.com/photo-1483729558449-99ef09a8c325?auto=format&fit=crop&w=1600&q=80',
    'mexico city': 'https://images.unsplash.com/photo-1518638150340-f706e86654de?auto=format&fit=crop&w=1600&q=80',
    'cape town': 'https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=1600&q=80',
    'nairobi': 'https://images.unsplash.com/photo-1527098322221-0c1dc6f9c8f0?auto=format&fit=crop&w=1600&q=80',
    'moscow': 'https://images.unsplash.com/photo-1516496636080-14fb876e029d?auto=format&fit=crop&w=1600&q=80',
    'stockholm': 'https://images.unsplash.com/photo-1509356843151-3e7d1e3f4f1f?auto=format&fit=crop&w=1600&q=80',
    'copenhagen': 'https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&w=1600&q=80',
    'oslo': 'https://images.unsplash.com/photo-1521213181056-8a3c7f8d6f4a?auto=format&fit=crop&w=1600&q=80',
}


def get_city_background(city_name):
    if not city_name:
        return 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=1600&q=80'

    normalized = city_name.strip().lower()
    if normalized in CITY_IMAGES:
        return CITY_IMAGES[normalized]

    cleaned = normalized.replace(' ', '-')
    return f'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?auto=format&fit=crop&w=1600&q=80&city={cleaned}'

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
    
    city_name = request.form.get('city')
    
    if not city_name:
        return {'error': 'Please enter a city name'}
    
    if not api_key:
        return {
            'city': city_name.strip().title(),
            'country': 'N/A',
            'time': '--:--:--',
            'temperature': '--',
            'feels_like': '--',
            'wind_speed': '--',
            'wind_direction': '--',
            'wind_gust': '--',
            'pressure': '--',
            'humidity': '--',
            'sunrise': '--:--:--',
            'sunset': '--:--:--',
            'description': 'Weather unavailable',
            'background_image': get_city_background(city_name)
        }
    
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
                'background_image': get_city_background(city_name_display)
            }
            return weather_data
        else:
            return {'error': 'City not found'}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
