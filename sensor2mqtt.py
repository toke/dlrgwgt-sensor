#!/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime
from sensor import TemperatureSensor
import mosquitto
import schedule



host  = '127.0.0.1'
sensor_topic_base = '/sensors/wgt'
sensor_topic = '%s/%%s/temp'% sensor_topic_base

known_sensors = {
    '28-0000042a115a': {'name': 'Wache Weingarten Wasser', 'unit': '°C'},
    '28-00000450fff0': {'name': 'Wache Weingarten Luft', 'unit': '°C'}
}

def on_connect(rc):
    if rc == 0:
        print 'Connect OK'

def on_disconnect(mosq, obj, rc):
    print("Disconnected successfully.")

def poll_sensors():
    for sensor in get_w1_sensors():
        w1_slave = sensor.split("\n")[0]
        sensor_file = '/sys/bus/w1/devices/' + str(w1_slave) + '/w1_slave'
        with open(sensor_file) as sf:
            content = sf.read()
            stringvalue = content.split("\n")[1].split(" ")[9]
            temperature = float(stringvalue[2:]) / 1000
            yield [str(w1_slave),"%5.1f" % temperature]


def get_w1_sensors(path='/sys/devices/w1_bus_master1/w1_master_slaves'):
    with open(path) as f:
        w1_slaves = f.readlines()
    return w1_slaves


class Publish:
    def __init__(self, host='127.0.0.1'):
        self.client = mosquitto.Mosquitto('wgtsensornode01')
        #self.client.on_connect = on_connect
        #self.client.on_disconnect = on_disconnect
        self.client.connect(host, keepalive=60)
        self.client.will_set('%s/status' % sensor_topic_base, payload="offline", retain=True)
        

    def publish(self, topic, message, retain=False):
        self.client.publish(topic, payload=message, retain=retain)

    def loop(self):
        self.client.loop()
        

class SensorWorker:
    def __init__(self):
        self.mqtt = Publish()


if __name__ == '__main__':
    print "Start"
    p = Publish(host)

    def sensor_pub_job():
        for sensor in poll_sensors():
            print("Publish: %s %s" % (sensor[0], sensor[1]))
            p.publish(sensor_topic % sensor[0], sensor[1], retain = True)

    def sensor_conf_job():
        for sensor in poll_sensors():
            print("Publish: %s %s" % (sensor[0], sensor[1]))
            if (known_sensors[sensor[0]]):
                p.publish('%s/%s/name' % (sensor_topic_base, sensor[0]), known_sensors[sensor[0]]['name'], retain = True)
                p.publish('%s/%s/unit' % (sensor_topic_base, sensor[0]), known_sensors[sensor[0]]['unit'], retain = True)



    def uptime_job():
        p.publish('%s/date' % sensor_topic_base, "%s" % datetime.now(), retain=True)

    p.publish('%s/status' % sensor_topic_base, "online", retain=True)


    uptime_job()
    sensor_conf_job()
    sensor_pub_job()

    schedule.every(5).minutes.do(sensor_pub_job)
    #schedule.every(10).seconds.do(sensor_job)
    schedule.every(20).hours.do(uptime_job)


    while True:
        schedule.run_pending()
        p.loop()
        time.sleep(1)


