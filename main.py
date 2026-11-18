
import requests
import os
from dotenv import load_dotenv
from datetime import datetime


# ==========================================
# LOAD API KEY
# ==========================================

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

GEOCODING_URL = "https://api.openweathermap.org/geo/1.0/direct"

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"

FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


# ==========================================
# GET CITY COORDINATES
# ==========================================

def get_coordinates(city):

    params = {
        "q": city,
        "limit": 1,
        "appid": API_KEY
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError("City not found. Please enter a valid city.")

    location = data[0]

    return {
        "name": location["name"],
        "country": location.get("country", ""),
        "latitude": location["lat"],
        "longitude": location["lon"]
    }


# ==========================================
# GET CURRENT WEATHER
# ==========================================

def get_current_weather(latitude, longitude):

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(
        CURRENT_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# GET 5-DAY FORECAST
# ==========================================

def get_forecast(latitude, longitude):

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# DISPLAY CURRENT WEATHER
# ==========================================

def display_current_weather(data, location):

    print("\n========== CURRENT WEATHER ==========")

    weather = data["weather"][0]

    main = data["main"]

    wind = data["wind"]

    print(
        f"City: {location['name']}, "
        f"{location['country']}"
    )

    print("Weather:", weather["description"].title())

    print("Temperature:", main["temp"], "°C")

    print("Feels Like:", main["feels_like"], "°C")

    print("Humidity:", main["humidity"], "%")

    print("Pressure:", main["pressure"], "hPa")

    print("Wind Speed:", wind["speed"], "m/s")

    print("Cloudiness:", data["clouds"]["all"], "%")


# ==========================================
# DISPLAY FIVE-DAY FORECAST
# ==========================================

def display_forecast(data):

    print("\n========== 5-DAY WEATHER FORECAST ==========")

    daily_data = {}

    # Group forecast records by date
    for item in data["list"]:

        date = item["dt_txt"].split(" ")[0]

        if date not in daily_data:
            daily_data[date] = []

        daily_data[date].append(item)

    # Select the forecast closest to noon for each day
    today = datetime.now().astimezone().date()

    displayed_days = 0

    for date, records in daily_data.items():

        forecast_date = datetime.strptime(
            date, "%Y-%m-%d"
        ).date()

        if forecast_date <= today:
            continue

        selected = min(
            records,
            key=lambda item: abs(
                datetime.strptime(
                    item["dt_txt"], "%Y-%m-%d %H:%M:%S"
                ).hour - 12
            )
        )

        weather = selected["weather"][0]

        temperature = selected["main"]

        print("\nDate:", date)

        print("Condition:", weather["description"].title())

        print("Temperature:", temperature["temp"], "°C")

        print("Minimum:", temperature["temp_min"], "°C")

        print("Maximum:", temperature["temp_max"], "°C")

        print("Humidity:", temperature["humidity"], "%")

        displayed_days += 1

        if displayed_days == 5:
            break


# ==========================================
# SEARCH WEATHER
# ==========================================

def search_weather():

    city = input("\nEnter city name: ").strip()

    if not city:
        print("Please enter a city name.")
        return

    try:

        print("\nFetching weather information...")

        # Step 1: Get coordinates
        location = get_coordinates(city)

        # Step 2: Get current weather
        current_data = get_current_weather(
            location["latitude"],
            location["longitude"]
        )

        # Step 3: Get forecast
        forecast_data = get_forecast(
            location["latitude"],
            location["longitude"]
        )

        # Step 4: Display results
        display_current_weather(
            current_data,
            location
        )

        display_forecast(forecast_data)

    except ValueError as error:

        print("\nError:", error)

    except requests.exceptions.HTTPError as error:

        status = error.response.status_code

        if status == 401:
            print("\nInvalid or inactive API key.")

        elif status == 404:
            print("\nCity or weather data not found.")

        elif status == 429:
            print("\nAPI request limit reached.")

        else:
            print("\nHTTP Error:", error)

    except requests.exceptions.Timeout:

        print("\nRequest timed out. Please try again.")

    except requests.exceptions.ConnectionError:

        print("\nInternet connection unavailable.")

    except requests.exceptions.RequestException as error:

        print("\nAPI request failed:", error)

    except (KeyError, IndexError, TypeError):

        print("\nUnexpected API response. Please try again.")


# ==========================================
# MAIN MENU
# ==========================================

def main():

    if not API_KEY:

        print("API key missing!")
        print("Please add OPENWEATHER_API_KEY to your .env file.")

        return

    while True:

        print("\n====================================")
        print("       PYTHON WEATHER APPLICATION")
        print("====================================")

        print("1. Search Weather by City")
        print("2. Exit")

        choice = input("\nEnter your choice (1-2): ").strip()

        if choice == "1":

            search_weather()

        elif choice == "2":

            print("\nThank you for using Weather App!")
            print("Goodbye!")

            break

        else:

            print("Invalid choice! Select 1 or 2.")


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    main()
