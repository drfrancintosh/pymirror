from pymirror.pmcard import PMCard

class Alert(PMCard):
	def __init__(self, pm, config):
		super().__init__(pm, config)
		self._alert = config.alert
		self.update(self._alert.header, self._alert.body, self._alert.footer)
		self.timer.set_timeout(self._alert.timeout)
		self.update("", "", "")  # Initialize with empty strings


	def exec(self) -> bool:
		is_dirty = super().exec()
		if self.timer.is_timedout(): 
			self.disabled = True
			return True
		return True	

	def onAlertEvent(self, event) -> None:
		self.disabled = False
		self.update(event.header, event.body, event.footer)
		self.timer.set_timeout(event.timeout)
