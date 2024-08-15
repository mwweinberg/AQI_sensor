# AQI_sensor
A project to read &amp; display local air quality

Full original project writeup [https://michaelweinberg.org/blog/2023/07/29/AQI_sensor/](https://michaelweinberg.org/blog/2023/07/29/AQI_sensor/)

In August of 2024 I updated the project to use a new API endpoint for the AQI.  If you use code after that, there are two changes you will need to make:  

1. Add a new entry to your secrets.py. The key should be `'aqicn_key'` and the value should be the API key you get from aqicn.org: https://aqicn.org/data-platform/token/

2. You won't have to dig into the code to find the number of your local AQI sensor. The new code just uses your IP address location to find your local sensor and pulls from there.  

