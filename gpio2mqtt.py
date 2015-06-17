#!/usr/bin/env python


from datetime import datetime
import paho.mqtt.client as mqtt

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

MQTT_TOPIC_BASE = "sensors/dlrgwgt"
MQTT_LWT = "sensors/dlrgwgt/gpio/state"

class GpioState(object):
    def __init__(self, channel):
        self.channel = channel
        self.state = self._get_hwstate()
        self.lastchange = None
        self.startup = datetime.now()
        self.counter = 0
    
    def _get_hwstate(self):
        return GPIO.input(self.channel)

    def trigger(self):
        hwstate = self._get_hwstate()
        if (hwstate != self.state):
            self.counter = self.counter + 1
            self.lastchange = datetime.now()
            self.state = hwstate

    def __str__(self):
        return "Channel: %i, state: %s, counter: %i, startup: %s, lastchange: %s" % (self.channel, self.state, self.counter, self.startup, self.lastchange)


class GpioEvent(object):
    def __init__(self, handler=None):
        self.chan_list=[17, 18]
        self.handler = handler
        self.registry = {}

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.chan_list, GPIO.IN)

    def get_cb(self, gpiostate):
        def cb(channel):
            gpiostate.trigger()
            if self.handler:
                self.handler(gpiostate)
        return cb

    def hook_events(self):
        for channel in self.chan_list:
            self.registry[channel] = GpioState(channel)
            cb = self.get_cb(self.registry[channel])
            GPIO.add_event_detect(channel, GPIO.BOTH, callback=cb, bouncetime=300)

def on_disconnect(mosq, obj, rc):
    print("Disconnected")
    exit

def on_connect(client, userdata, flags, rc):
    client.publish(MQTT_LWT, "1", retain=True)
    print("Connected with result code "+str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
        
def get_sensor_handler(client):
    def handler(event):
        print (event)
        jsonstr="{\"event\": \"gpio\", \"channel\": %i, \"state\": %i, \"counter\": %i, \"lastchange\": \"%s\", \"startup\": \"%s\"}" % (event.channel, event.state, event.counter, event.lastchange, event.startup)
        client.publish("%s/gpio/%i/json" % (MQTT_TOPIC_BASE, event.channel), jsonstr, retain=True)
        client.publish("%s/gpio/%i/state" % (MQTT_TOPIC_BASE, event.channel), "%s" % event.state, retain=True)
        client.publish("%s/gpio/%i/counter" % (MQTT_TOPIC_BASE, event.channel), "%i" % event.counter, retain=True)
        client.publish("%s/gpio/%i/lastchange" % (MQTT_TOPIC_BASE, event.channel), "%s" % event.lastchange, retain=True)
        client.publish("%s/gpio/%i/startup" % (MQTT_TOPIC_BASE, event.channel), "%s" % event.startup, retain=True)
    return handler
    

if __name__ == '__main__':
    host = '127.0.0.1'
    port = '1883'
    MQTT_TIMEOUT = 60
    MQTT_RETAIN = True

    client = mqtt.Client(protocol=mqtt.MQTTv31) #'wgtsensornode01')
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(host, port, MQTT_TIMEOUT)
    client.will_set(MQTT_LWT, payload="0", retain=MQTT_RETAIN)

    mqtt_handler = get_sensor_handler(client)

    gpio = GpioEvent(handler=mqtt_handler)
    gpio.setup()

    gpio.hook_events()
    print "startup"
    for channel in gpio.registry:
        mqtt_handler(gpio.registry[channel])
        mqtt_handler(gpio.registry[channel])

    client.loop_forever()

    GPIO.cleanup()
