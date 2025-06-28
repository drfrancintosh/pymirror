from pymirror import PMCard

class Alert(PMCard):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._alert = config.alert
		self.header = self._alert.header
		self.body = self._alert.body
		self.footer = self._alert.footer
		self.timer.set_timeout(self._alert.timeout)

		self.last_header = None
		self.last_body = None
		self.last_footer = None

	def exec(self) -> bool:
		if self.timer.is_timedout(): 
			self.update(None, None, None)
			return True
		return self.has_changed()	

	def onAlertEvent(self, event) -> None:
		self.update(event.header, event.body, event.footer)
		self.timer.set_timeout(event.timeout)
