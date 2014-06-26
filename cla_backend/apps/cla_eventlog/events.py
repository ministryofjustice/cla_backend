
class BaseEvent(object):
    key = ''
    codes = {}

    def get_log_code(self, **kwargs):
        if len(self.codes) > 1:
            raise NotImplementedError()

        return self.codes.keys()[0]

    def process(self, code=None, notes="", **kwargs):
        if not code:
            code = self.get_log_code(**kwargs)

        return (code, self.codes[code]['type'], notes)
