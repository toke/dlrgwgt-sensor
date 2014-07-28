import re

class Sensor(object):
	def __init__(self, sensor_id=None, device=None, bus=1):
		self.sensor_id=sensor_id
		self.device=device
		self.bus=bus

	def _get_device(self):
		if self.device:
			return self.device
		else:
			return '/sys/bus/w1/devices/w1_bus_master%i/%s/w1_slave' % (self.bus, self.sensor_id)

	def __iter__(self):
		with open(self._get_device(), 'r') as device:
			for line in device:
				yield line

	def read(self):
		return self

class TemperatureSensor(Sensor):

	def __init__(self, sensor_id=None, device=None, bus=1):
		super(TemperatureSensor, self).__init__(sensor_id=sensor_id, device=device, bus=bus) 

	def get_temperature(self):
		for line in self:
			l = re.match(r'.*t=([0-9]+)', line)
			if (l):
				return l.group(1)
	
