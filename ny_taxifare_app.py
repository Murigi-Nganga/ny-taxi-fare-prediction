# Creating a Web App with Streamlit
"""Name: Murigi Gracious Ng'ang'a"""

#Importing the necessary libraries
import streamlit as st
import joblib
import math
from datetime import date, time
import pandas as pd

# Setting the page title configurations
st.set_page_config(page_title='New York Fare Prediction App', page_icon=':shark:')

st.header("""
New York Taxi Fare Prediction App \n
`This application predicts the amount of fare you are likely to incur when moving from one \
place to another in New York`
""")
st.write('\n')

# Create 2 side-by-side columns
app_img, params = st.columns(2)

app_img.image('https://images.unsplash.com/photo-1490650404312-a2175773bbf5?ixlib\
=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto\
=format&fit=crop&w=870&q=80', width=300, caption='New York Taxis')

st.sidebar.header('Specify Input Parameters')

st.sidebar.write('---')

#New York Latitude and Longitude boundaries
min_lat, max_lat = (40.2940,45.0042)
min_lon, max_lon = (-79.4554,-71.4725)

# Input widgets with example default values
pickup_longitude = st.sidebar.number_input("Pickup longitude", 
                                                                format="%.4f",
                                                                step= 0.0001,
                                                                min_value=min_lon, 
                                                                max_value=max_lon,
                                                                value=-73.8443)

dropoff_longitude = st.sidebar.number_input("Dropoff longitude",
                                                                format="%.4f",
                                                                step= 0.0001,
                                                                min_value=min_lon, 
                                                                max_value=max_lon,
                                                                value=-73.8416)

pickup_latitude = st.sidebar.number_input("Pickup latitude",
                                                                format="%.4f",
                                                                step= 0.0001,
                                                                min_value=min_lat, 
                                                                max_value=max_lat,
                                                                value=40.7213)

dropoff_latitude = st.sidebar.number_input("Dropoff latitude",
                                                                format="%.4f",
                                                                step= 0.0001,
                                                                min_value=min_lat, 
                                                                max_value=max_lat,
                                                                value=40.7122)

passenger_count = st.sidebar.number_input("Passenger Count", 
                                                                min_value=1,
                                                                max_value=6,
                                                                value=1)

pickup_date = st.sidebar.date_input("Pickup date", value=date(2009,6,15))
pickup_time = st.sidebar.time_input("Pickup time", value=time(17,26))

def calculate_distance(lon1, lat1, lon2, lat2):
    """
    Calculates the distance between two places given the longitude and latitude
    using the Haversine Formula
    lat1: Pickup latitude
    lat2: Dropoff latitude
    lon1: Pickup longitude
    lon2: Dropoff longitude

    Returns a list of the distance, longitude difference and latitude_difference respectively
    """
    earth_radius = 6371
    
    #Convert the angles from degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    
    a = pow(math.sin(lat_diff/2), 2) + math.cos(lat1) * math.cos(lat1) * pow(math.sin(lon_diff/2), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = earth_radius * c

    #Converting the numbers back to radians -- to be used for display in the features' dict
    lon_diff, lat_diff = map(math.degrees, [lon_diff, lat_diff])
    return distance, abs(lon_diff), abs(lat_diff)

def transform_date_and_time(date_given, time_given):
    """
    Returns a list of the year, month, day, hour and minute
    """
    year = date_given.year
    month = date_given.month
    day = date_given.day
    hour = time_given.hour
    minute = time_given.minute
    return year, month, day, hour, minute

pickup_year, pickup_month, pickup_day, \
pickup_hour, pickup_minute = transform_date_and_time(pickup_date, pickup_time)

distance, lon_diff, lat_diff = calculate_distance(pickup_longitude, pickup_latitude, 
                                                                    dropoff_longitude, dropoff_latitude)

# Order of features in the dataset:  (13 columns)
# pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, 
# passenger_count, year, month, day, hour, minute, distance in kilometres,
# longitude_difference, latitude_difference 

features = [pickup_longitude, pickup_latitude, dropoff_longitude, 
                 dropoff_latitude, passenger_count, pickup_year, pickup_month,
                 pickup_day, pickup_hour, pickup_minute, distance, lon_diff, lat_diff]

features_dict = {
    "Pickup Longitude" : round(pickup_longitude, 4),
    "Dropoff Longitude": round(dropoff_longitude, 4),
    "Longitude Difference": round(lon_diff, 4),
    "Pickup Latitude": round(pickup_latitude, 4),
    "Dropoff Latitude": round(dropoff_latitude, 4),
    "Latitude Difference": round(lat_diff, 4),
    "Passenger Count": passenger_count,
    "Pickup Date": f"{pickup_date.year}-{pickup_date.month}-{pickup_date.day}",
    "Pickup Time" : f"{pickup_time.hour}{pickup_time.minute} hrs",
    "Travel Distance (km)" : round(distance, 4),
}

params.write(features_dict)

#Load the model and predict the amount of fare
model = joblib.load('ny_taxifare_predictor.joblib')
result = model.predict([features])

if(st.button("Calculate Fare")):
    if(result):
        st.write(f"Amount of fare: **${result[0]: .2f}**")  #result[0] because predicted value is an array with one value
        st.success("Fare calculated successfully")
        # st.balloons()
    else:
        st.error("Something went wrong!")

st.write('---')
st.write("Examples of predicted fare amounts from the **test.csv** samples")

# Testing the application with a sample of input values from the test.csv file
test_data = pd.read_csv('test.csv')

#A sample of 100 rows to display on the screen
samples = test_data.sample(100, random_state=42)

fare_amounts = list()

for index, row in samples.iterrows():
    dt_obj = pd.to_datetime(row['pickup_datetime'], format = '%Y-%m-%d %H:%M:%S %Z')
    year, month, day, hour, minute = dt_obj.year, dt_obj.month, dt_obj.day, dt_obj.hour, dt_obj.minute

    distance, lon_diff, lat_diff = calculate_distance(row['pickup_longitude'], row['pickup_latitude'],
                                                                        row['dropoff_longitude'], row['dropoff_latitude'])

    prediction = model.predict([[row['pickup_longitude'], row['pickup_latitude'], 
                                            row['dropoff_longitude'], row['dropoff_latitude'], 
                                            row['passenger_count'], year, month, day, hour, minute,
                                            distance, lon_diff, lat_diff]])

    fare_amounts.append(prediction[0]) 

samples['fare_amount'] = fare_amounts
st.write(samples)
