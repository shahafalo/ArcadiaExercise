
class Motor:
    direction = None

    def on(self, direction: int) -> None:
        self.direction = direction

    def off(self) -> None:
        self.direction = None

class Encoder:
    _status = 0

    def status(self):
        return self._status

class MicroSwitch:
    _status = 0

    def status(self):
        return self._status
