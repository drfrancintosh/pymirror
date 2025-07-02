from pymirror.pmcard import PMCard

class Alert(PMCard):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._alert = config.alert
		## update the card with initial values
		self.update(self._alert.header, self._alert.body, self._alert.footer)
		## set the timeout for the alert, if any
		self.timer.set_timeout(self._alert.timeout)
		## disable the alert if the timeout is 0 or less
		## this means the alert is not active
		self.disabled = self._alert.timeout < 0


	def exec(self) -> bool:
		## has there been a change in the alert text?
		is_dirty = super().exec()
		if self.timer.is_timedout(): 
			## the timer has expired
			## disable the alert (hiding it)
			## and publish an event to refresh the display
			self.disabled = True
			event = {
				"event": "PyMirrorEvent",
				"refresh": True,
			}
			self.update(None, None, None)
			self.publish_event(event)
			is_dirty = True
		return is_dirty

	def onEvent(self, event) -> None:
		## show the alert window
		self.disabled = False
		## update the alert text with the event data
		self.update(event.header, event.body, event.footer)
		## if the event has a timeout, set the timer
		self.timer.set_timeout(event.timeout)
