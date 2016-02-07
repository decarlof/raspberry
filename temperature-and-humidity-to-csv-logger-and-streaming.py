# -*- coding: utf-8 -*-
# Written by David Neuy
# Version 0.1.0 @ 03.12.2014
# This script was first published at: http://www.home-automation-community.com/
# You may republish it as is or publish a modified version only when you 
# provide a link to 'http://www.home-automation-community.com/'. 

# Modified by Francesco De Carlo
# decarlof@gmail.com

#install dependency with 'sudo easy_install apscheduler' NOT with 'sudo pip install apscheduler'
import os, sys, Adafruit_DHT, time
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler

import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls
import numpy as np

sensor                       = Adafruit_DHT.AM2302 #DHT11/DHT22/AM2302
pin                          = 4
sensor_name                  = "living-room"
hist_temperature_file_path   = "sensor-values/temperature_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
latest_temperature_file_path = "sensor-values/temperature_" + sensor_name + "_latest_value.csv"
hist_humidity_file_path      = "sensor-values/humidity_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
latest_humidity_file_path    = "sensor-values/humidity_" + sensor_name + "_latest_value.csv"
csv_header_temperature       = "timestamp,temperature_in_celsius\n"
csv_header_humidity          = "timestamp,relative_humidity\n"
csv_entry_format             = "{:%Y-%m-%d %H:%M:%S},{:0.1f}\n"
sec_between_log_entries      = 60
sec_between_stream_entries   = 10
latest_humidity              = 0.0
latest_temperature           = 0.0
latest_value_datetime        = None
degree_sign                  = u'\N{DEGREE SIGN}'

def write_header(file_handle, csv_header):
  file_handle.write(csv_header)

def write_value(file_handle, datetime, value):
  line = csv_entry_format.format(datetime, value)
  file_handle.write(line)
  file_handle.flush()

def open_file_ensure_header(file_path, mode, csv_header):
  f = open(file_path, mode, os.O_NONBLOCK)
  if os.path.getsize(file_path) <= 0:
    write_header(f, csv_header)
  return f

def write_hist_value_callback():
  write_value(f_hist_temp, latest_value_datetime, latest_temperature)
  write_value(f_hist_hum, latest_value_datetime, latest_humidity)

def write_latest_value():
  with open_file_ensure_header(latest_temperature_file_path, 'w', csv_header_temperature) as f_latest_value:  #open and truncate
    write_value(f_latest_value, latest_value_datetime, latest_temperature)
  with open_file_ensure_header(latest_humidity_file_path, 'w', csv_header_humidity) as f_latest_value:  #open and truncate
    write_value(f_latest_value, latest_value_datetime, latest_humidity)

f_hist_temp = open_file_ensure_header(hist_temperature_file_path, 'a', csv_header_temperature)
f_hist_hum  = open_file_ensure_header(hist_humidity_file_path, 'a', csv_header_humidity)

print "Ignoring first 2 sensor values to improve quality..."
for x in range(2):
  Adafruit_DHT.read_retry(sensor, pin)

print "Creating interval timer. This step takes almost 2 minutes on the Raspberry Pi..."
#create timer that is called every n seconds, without accumulating delays as when using sleep
scheduler = BackgroundScheduler()
scheduler.add_job(write_hist_value_callback, 'interval', seconds=sec_between_log_entries)
scheduler.start()
print "Started interval timer which will be called the first time in {0} seconds.".format(sec_between_log_entries);

# setting the plot streaming
stream_ids = tls.get_credentials_file()['stream_ids']
# Get stream id from stream id list 
stream_id_0 = stream_ids[0]
stream_id_1 = stream_ids[0]

# Make instance of stream id object 
stream_0 = go.Stream(
    token=stream_id_0,  # (!) link stream id to 'token' key
    maxpoints= 24 * 3600 / sec_between_stream_entries     # (!) keep a max of pts on screen
)

# Initialize trace of streaming plot by embedding the unique stream_id
trace_0 = go.Scatter(
    x=[],
    y=[],
    mode='lines+markers',
    stream=stream_0         # (!) embed stream id, 1 per trace
)

data = go.Data([trace_0])

# Add title to layout object
layout = go.Layout(title='Leaving Room Temperature (' +  degree_sign + 'C)')

# Make a figure object
fig = go.Figure(data=data, layout=layout)

# (@) Send fig to Plotly, initialize streaming plot, open new tab
unique_url = py.plot(fig, filename='s7_first-stream', auto_open=False)

# (@) Make instance of the Stream link object, 
#     with same stream id as Stream id object
s = py.Stream(stream_id_0)

# (@) Open the stream
s.open()

print "Started Temperature Streaming"
try:
  while True:
    hum, temp = Adafruit_DHT.read_retry(sensor, pin)
    if hum is not None and temp is not None:
      latest_humidity, latest_temperature = hum, temp
      latest_value_datetime = datetime.today()
      write_latest_value()

      # (@) write to Plotly stream!
      s.write(dict(x=latest_value_datetime, y=latest_temperature))

    time.sleep(sec_between_stream_entries)
except (KeyboardInterrupt, SystemExit):
  scheduler.shutdown()

