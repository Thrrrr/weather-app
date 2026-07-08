import requests 
from datetime import datetime, timezone, timedelta 
  
# Enter your API key here 
api_key = "24d18b231df4ea0585fbfadb7cc77b2c"
  
# base_url variable to store url
base_url = "https://api.openweathermap.org/data/2.5/weather?"
  
# Give city name 
city_name = input("Enter city name : ") 

# Build the complete URL by combining the base URL + city name + API key
# This is what we'll send to OpenWeatherMap to ask for data
complete_url = base_url + "q=" + city_name + "&appid=" + api_key 
print(f"Request URL: {complete_url}")

# Send the request to OpenWeatherMap's servers
response = requests.get(complete_url) 
print(f"Status Code: {response.status_code}")

# Convert the response from the API into a Python dictionary so we can use it
x = response.json() 
print(f"Full Response: {x}")

# Check if the API gave us good data (status code 200 means "success")
if x.get("cod") == "200" or response.status_code == 200: 
  
    # Extract the "main" section which has temperature, pressure, humidity
    y = x["main"] 
    # Get the temperature from the data (in Kelvin)
    temp_kelvin = y["temp"]
    # Convert temperature from Kelvin to Celsius
    current_temperature = temp_kelvin - 273.15
    # Get the "feels like" temperature in Celsius
    feels_like_kelvin = y["feels_like"]
    feels_like_temp = feels_like_kelvin - 273.15
    # Get the atmospheric pressure from the data
    current_pressure = y["pressure"] 
    # Get the humidity percentage from the data
    current_humidiy = y["humidity"]
    # Extract the "weather" section which has the description of weather
    z = x["weather"] 
    # Get the description (like "cloudy" or "sunny") - [0] means first item
    weather_description = z[0]["description"]
    # Extract wind speed data
    wind_speed = x["wind"]["speed"]
    # Extract wind direction (in degrees)
    wind_direction = x["wind"]["deg"]
    # Extract wind gust speed
    wind_gust = x["wind"].get("gust", "N/A")
    # Get the timezone offset (in seconds) for the city
    timezone_offset = x["timezone"]
    # Extract sunrise and sunset times (Unix timestamps)
    sunrise_unix = x["sys"]["sunrise"]
    sunset_unix = x["sys"]["sunset"]
    # Convert sunrise/sunset from Unix time to readable format in the city's timezone
    sunrise_time = (datetime.fromtimestamp(sunrise_unix, tz=timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%H:%M:%S")
    sunset_time = (datetime.fromtimestamp(sunset_unix, tz=timezone.utc) + timedelta(seconds=timezone_offset)).strftime("%H:%M:%S")
    # Calculate the current time in the city using UTC time + timezone offset
    city_time = datetime.now(timezone.utc) + timedelta(seconds=timezone_offset)
    # Format the time nicely (just the time, not the date)
    current_time = city_time.strftime("%H:%M:%S")
    # Extract city name and country code
    city_name_display = x["name"]
    country_code = x["sys"]["country"]
    # Print all the weather info nicely formatted with proper units in an ASCII box
    print("\n" + "="*50)
    print(f"   {city_name_display.upper()}, {country_code}")
    print("="*50)
    print(f"  Current Time ............ {current_time}")
    print(f"  Temperature ............ {current_temperature:.2f}°C")
    print(f"  Feels Like ............. {feels_like_temp:.2f}°C")
    print(f"  Wind Speed ............. {wind_speed} m/s")
    print(f"  Wind Direction ......... {wind_direction}°")
    print(f"  Wind Gust .............. {wind_gust} m/s")
    print(f"  Atmospheric Pressure ... {current_pressure} hPa")
    print(f"  Humidity ............... {current_humidiy}%")
    print(f"  Sunrise ................ {sunrise_time}")
    print(f"  Sunset ................. {sunset_time}")
    print(f"  Description ............ {weather_description}")
    print("="*50 + "\n") 
  
else: 
    print(" City Not Found or API Error")
    print(f"Response: {x}") 