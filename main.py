"""""
International Space Station is Overhead Notifier
================================================
This program uses info from the ISS and Sunset and Sunrise APIs to 
ompare your location to that of the ISS. If it is night, if will send an email to notify you to look up!

"""

import requests
from datetime import datetime
import json
import smtplib
import pytz
import time

# Define constants 
MY_LAT = -33.798531
MY_LONG = 151.286163


def is_night():
    parameters = {
        'lat': MY_LAT,
        'lng': MY_LONG,
        'formatted': 0,
        'date': '2023-06-12'
    }

    response = requests.get(url='https://api.sunrise-sunset.org/json', params=parameters)
    response.raise_for_status()

    data = response.json()

    sunrise_utc = data['results']['sunrise']
    sunset_utc = data['results']['sunset']

    local_tz = pytz.timezone('Australia/Sydney') 
    sunrise = datetime.fromisoformat(sunrise_utc).astimezone(local_tz).hour
    sunset = datetime.fromisoformat(sunset_utc).astimezone(local_tz).hour

    time_now = datetime.now().hour
    return sunrise > time_now or time_now > sunset

def ISS_in_position():

    response = requests.get(url='http://api.open-notify.org/iss-now.json')

    response.raise_for_status()

    data = response.json()

    longitutde = float(data['iss_position']['longitude'])
    latitude = float(data['iss_position']['latitude'])

    return (MY_LAT-5) < latitude < (MY_LAT+5) and (MY_LONG-5) < longitutde < (MY_LONG+5)

def send_email():
    with open('Day 33 API/config.json', 'r') as config_file:
        config = json.load(config_file)

        my_email = config['Email']['my_email']
        password = config['Email']['password']
        smtp_server = config['SMTP']['server']
        smtp_port = config['SMTP']['port']
        recipient_email = config['Email']['recipient_email']

        #Establish connnection to gmail 
        with smtplib.SMTP(smtp_server, smtp_port) as connection:

            #Add transport layer security
            connection.starttls()

            #Login to connection
            connection.login(user=my_email,password=password)

            #Send email 
            connection.sendmail(from_addr=my_email, 
                                to_addrs=recipient_email, 
                                msg=f'subject:ISS Notification\n\nLook Up! the ISS is overhead.')


def send_notification():
    if  is_night() and  ISS_in_position():
        send_email()

while True:
    time.sleep(60)
    send_notification()