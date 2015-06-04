#!/usr/bin/env python


from datetime import datetime
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

class GpioState(object):
    def __init__(self, channel):
        self.channel = channel
        self.state = self._get_hwstate()
        self.lastchange = None
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
        return "Channel: %i, state: %s, counter: %i, lastchange: %s" % (self.channel, self.state, self.counter, self.lastchange)


class GpioEvent(object):
    def __init__(self):
        self.chan_list=[17, 18]
        self.registry = {}

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.chan_list, GPIO.IN)

    def get_cb(self, gpiostate):
        def cb(channel):
            gpiostate.trigger()
        return cb

    def _cb_gpio(self, channel):
        state = GPIO.input(channel)
        # gpio/%i/state 
        # gpio/%i/lastchange 
        # gpio/%i/counter
        print("Event detected on channel %i, now %i" % (channel, state))

    def hook_events(self):
        for channel in self.chan_list:
            self.registry[channel] = GpioState(channel)
            cb = self.get_cb(self.registry[channel])
            GPIO.add_event_detect(channel, GPIO.BOTH, callback=cb, bouncetime=300)

        
if __name__ == '__main__':
    gpio = GpioEvent()
    gpio.setup()

    gpio.hook_events()
    print "startup"
    print(gpio.registry[17])
    print(gpio.registry[18])

    while True:
        channel = 17
        if GPIO.event_detected(channel):
            print(gpio.registry[channel])
        #GPIO.wait_for_edge(17, GPIO.FALLING)
        #print("Button 2 Pressed")

    GPIO.cleanup()
