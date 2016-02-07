# -*- coding: utf-8 -*-
# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api

# Modified by Francesco De Carlo
# decarlof@gmail.com

import plotly.plotly as py
import plotly.graph_objs as go
import csv
from datetime import datetime, date
import time

sensor_name                  = "living-room"
hist_temperature_file_path   = "sensor-values/temperature_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
hist_humidity_file_path      = "sensor-values/humidity_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
degree_sign                  = u'\N{DEGREE SIGN}'
sec_between_plot_updates     = 3600

def update_plot():
    x_temp = []
    y_temp = []
    x_humidity = []
    y_humidity = []

    with open(hist_temperature_file_path, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            x_temp.append(row[0])
            y_temp.append(row[1])

    with open(hist_humidity_file_path, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            x_humidity.append(row[0])
            y_humidity.append(row[1])
        
    trace0 = go.Scatter(
        x = x_temp,
        y = y_temp,
        mode = 'lines',
        name = 'Temperature (' +  degree_sign + 'C)'
    )
    trace1 = go.Scatter(
        x = x_humidity,
        y = y_humidity,
        mode = 'lines+markers',
        name = 'Rel. Humidity (%)'
    )

    data = [trace0, trace1]
    # Add title to layout object
    layout = go.Layout(title='Leaving Room')

    # Make a figure object
    fig = go.Figure(data=data, layout=layout)

    plot_url = py.plot(fig, filename='Temperature-Humidity', auto_open=False)

print "Started plot update"
try:
  while True:
    update_plot()
    time.sleep(sec_between_plot_updates)
except (KeyboardInterrupt, SystemExit):
    pass

