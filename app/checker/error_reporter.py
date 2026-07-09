class ErrorReporter:
    def __init__(self):
        self._errors = []

    def reset(self):
        self._errors = []

    def report(self, message):
        self._errors.append(message)

    @property
    def errors(self):
        return list(self._errors)
