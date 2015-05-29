#!/bin/bash

cd  /home/pi/src/sensormqtt
source /home/pi/src/mqttenv/bin/activate
/home/pi/src/mqttenv/bin/python sensor2mqtt.py
