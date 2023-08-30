# Import necessary libraries
import requests
from datetime import datetime, timedelta

# A dictionary that maps AQI values to their corresponding air quality category
air_quality_index = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}

def get_location(location_input):
    # Initialize an empty list to store location data
    data = []
    # Initialize an empty list to store search results
    search_results = []
    # Make a request to the OpenWeatherMap API to get location data
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={location_input}&limit=5&appid=44d1756e7fd91b4801d50fa88ac13b8c")
    # Parse the response as JSON
    results = response.json()

    # Iterate over each location result
    for result in results:
        # Extract the location name, state, and country
        location = {"name": result.get('name', ''), "state": result.get('state', ''), "country": result.get('country', '')}
        # Check if the location is already in the data list, and add it if not
        if location not in data:
            data.append(location)

    # Iterate over each location in the data list
    for i, location in enumerate(data):
        # Create a list with the index, location name, state, and country
        data = [i, location['name'], location['state'], location['country']]
        # Add the list to the search results list
        search_results.append(data)
    # Return the search results list
    return search_results

def get_location_data(selected_item):
    # Split the selected item into a list containing the location name, state, and country
    location_details = selected_item.split(',')
    # Make a request to the OpenWeatherMap API to get the location data
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={location_details[0]},{location_details[1]},{location_details[2]}&limit={1}&appid=44d1756e7fd91b4801d50fa88ac13b8c")
    # Parse the response as JSON
    results = response.json()
    # Return the location data
    return results

def get_weather_data(latitude, longitude, selected_item, api_url):
    # Make a request to the OpenWeatherMap API to get the weather data
    response = requests.get(api_url.format(latitude=latitude, longitude=longitude, name=selected_item[1], country=selected_item[2]))
    # Parse the response as JSON
    return response.json()

def print_date(forecast):
    # Convert the forecast timestamp to a formatted date string and print it
    dt = forecast['dt']
    print(datetime.datetime.fromtimestamp(dt).strftime("%d/%m/%Y %I:%M:%S %p")) 

def print_time(timestamps):
    # Initialize an empty list to store the formatted time strings
    time_list = []
    # Sort the timestamp list and iterate over the first four timestamps
    for timestamp in sorted(timestamps)[:4]:
        # Convert the timestamp to a formatted time string and append it to the time list
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime('%H:%M %p')
        time_list.append(time_str)
    # Return the time list
    return time_list


def print_date():
    # Initialize a list with the first two day names
    day_list = ['Today', 'Tomorrow']
    today = datetime.now()
    for i in range(3):
        today += timedelta(days=1)
        # append the formatted date to the list
        day_list.append(today.strftime('%B %d'))
    return day_list

# function to get air quality indexes for pollutants
def current_pollution_indexes(pollutants):
    aqi_indexes = {}
    # AQI ranges for different pollutants
    ranges = {
        'so2': [(0, 20), (20, 80), (80, 250), (250, 350), (350, float('inf'))],
        'no': [(0, 20), (20, 40), (40, 100), (100, 150), (150, float('inf'))],
        'no2': [(0, 40), (40, 70), (70, 150), (150, 200), (200, float('inf'))],
        'nh3': [(0, 20), (20, 50), (50, 100), (100, 200), (200, float('inf'))],
        'pm10': [(0, 20), (20, 50), (50, 100), (100, 200), (200, float('inf'))],
        'pm2_5': [(0, 10), (10, 25), (25, 50), (50, 75), (75, float('inf'))],
        'o3': [(0, 60), (60, 100), (100, 140), (140, 180), (180, float('inf'))],
        'co': [(0, 4400), (4400, 9400), (9400, 12400), (12400, 15400), (15400, float('inf'))],
    }

    # loop through the pollutants and check their AQI index
    for item in pollutants:
        name = item['name']
        data = item['data']

        if name in ranges:
            for i, (low, high) in enumerate(ranges[name]):
                if low <= data < high:
                    aqi_indexes[name] = i + 1
                    break

    return aqi_indexes

# function to get current weather information
def current_weather(latitude, longitude, selected_item):
    api_url = "https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid=44d1756e7fd91b4801d50fa88ac13b8c&units=metric"
    response = get_weather_data(latitude, longitude, selected_item, api_url)
    # extract name and country from the response
    name, country =  response['name'], response['sys']['country']
    return name, country

# function to get 5 day weather forecast information
def five_day_forecast(latitude, longitude, selected_item): 
    timestamps = []
    temps = []
    day_info = []

    api_url = "https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid=44d1756e7fd91b4801d50fa88ac13b8c&units=metric"
    response = get_weather_data(latitude, longitude, selected_item, api_url)
    for i, forecast in enumerate(response['list']):
        # get data in 3 hour sets, 4 times
        if i <= 4:
            current = int(forecast['main']['temp'])
            temps.append(current)
            timestamps.append(forecast['dt'])
        # get data every 8th position, i.e. once per day
        if i == 0 or i % 8 == 0:
            day_info.append([int(forecast['main']['temp']), forecast['weather'][0]['main'], 
            forecast['weather'][0]['description'], 
            
            int(forecast['visibility']), 
            forecast['main']['humidity'], int(forecast['wind']['speed']), forecast['main']['sea_level'], forecast['main']['grnd_level'], forecast['clouds']['all']])
    # get the time of each forecasted day
    hours = print_time(timestamps)
    # get the list of 5 days starting from tomorrow
    day_list = print_date()
    return response, day_list, day_info, hours, temps

# function to get future pollution forecast information
def forecast_pollution(latitude, longitude, selected_item):
    pollution_indexes = []
    pollutants = []
    api_url = "http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={latitude}&lon={longitude}&appid=44d1756e7fd91b4801d50fa88ac13b8c"
    response = get_weather_data(latitude, longitude, selected_item, api_url)
    # extract air quality data for each forecast
    for i, current in enumerate(response['list']):
        if i == 0:
            # extract pollutant data for the first forecast
            for key, value in current['components'].items():
                pollutant = {'name': key, 'data': value}
                pollutants.append(pollutant)
        # get data every 25th position, i.e. once per day
        if i == 0 or i % 25 == 0:
            pollution_indexes.append({"aqi": current['main']['aqi'], "name": air_quality_index[current['main']['aqi']]})
    return pollution_indexes, pollutants

# NON FUNCTIONAL PROOF OF CONCEPT STARTS HERE
def get_weather_alerts():
    response = get_weather_data("https://api.weatherbit.io/v2.0/alerts?lat={latitude}&lon={longitude}&key=b3e792d10fd54853b69b2c2954b0c8c0&city={name}&country={country}")
    for alert in response['alerts']:
        print(f"\n\nTitle: {alert['title']}\n\nDescription: {alert['description']}\n\nSeverity: {alert['severity']}\n\n(UTC) time that alert was issued: {alert['effective_utc']}\n\n(UTC) time that alert expires: {alert['expires_utc']}")
    return response
# NON FUNCTIONAL PROOF OF CONCEPT END HERE


