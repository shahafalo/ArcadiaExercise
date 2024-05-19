
class Motor:
    direction = None

    def on(self, direction: int) -> None:
        self.direction = direction

    def off(self) -> None:
        self.direction = None

class Encoder:
    _counter = -1
    _mocked_values = [0, 0, 1, 1]

    def status(self):
        self._counter = (self._counter + 1) % 4
        return self._mocked_values[self._counter]

class MicroSwitch:
    _status = 0

    def status(self):
        return self._status
