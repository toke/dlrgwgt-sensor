#!/usr/bin/python

import mosquitto
from datetime import datetime
from sensor import TemperatureSensor


#host = 'mqtt.toke.de'
host  = '127.0.0.1'
water_sensor='28-0000042a115a'
air_sensor='28-00000450fff0'


def on_connect(rc):
    if rc == 0:
        print 'Connect OK'

if __name__ == '__main__':
    sensor_water = TemperatureSensor(sensor_id = water_sensor)
    sensor_air   = TemperatureSensor(sensor_id = air_sensor)

    temp_water = long(sensor_water.get_temperature())/1000.0
    temp_air = long(sensor_air.get_temperature())/1000.0

    msg_air = '%.1f' % temp_air
    msg_water = '%.1f' % temp_water

    client = mosquitto.Mosquitto('wgtwgtwache1')
    client.on_connect = on_connect
    
    #client.will_set('/sensors/wgt/wache/status', payload='offline')
    client.connect(hostname=host, keepalive=50, clean_session=False)

    #client.publish('/sensors/wgt/wache/status', payload='online')

    client.publish('/sensors/wgt/date', payload="%s" % datetime.now(), retain=True)
    client.publish('/sensors/wgt/wache', payload=msg_air, retain=True)
    client.publish('/sensors/wgt/wasser', payload=msg_water, retain=True)


