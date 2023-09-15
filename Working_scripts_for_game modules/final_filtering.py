
from collections import deque

class LowPassFilter:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self.state = 0.0

    def set_alpha(self, alpha: float):
        self.alpha = alpha

    def filter(self, value: float) -> float:
        self.state = self.alpha * value + (1 - self.alpha) * self.state
        return self.state

class HighPassFilter:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self.prev_raw = None
        self.prev_high_passed = 0.0
        self.low_pass_filter = LowPassFilter(alpha)

    def set_alpha(self, alpha: float):
        self.alpha = alpha
        self.low_pass_filter.set_alpha(alpha)

    def filter(self, value: float) -> float:
        if self.prev_raw is None:
            self.prev_raw = value
        high_passed = self.prev_high_passed + self.alpha * (value - self.prev_raw + self.low_pass_filter.filter(value))
        self.prev_raw = value
        self.prev_high_passed = high_passed
        return high_passed

class CombFilter:
    def __init__(self, delay: int, gain: float):
        self.delay = delay
        self.gain = gain
        self.buffer = deque(maxlen=delay)

    def set_parameters(self, delay: int, gain: float):
        self.delay = delay
        self.gain = gain
        self.buffer = deque(maxlen=delay)

    def filter(self, signal: float) -> float:
        self.buffer.append(signal)
        if len(self.buffer) < self.delay:
            return signal
        return signal - self.gain * self.buffer[0]

