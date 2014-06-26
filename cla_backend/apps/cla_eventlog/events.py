from cla_eventlog.models import Log


class BaseEvent(object):
    key = ''
    codes = {}

    def get_log_code(self, **kwargs):
        if len(self.codes) > 1:
            raise NotImplementedError()

        return self.codes.keys()[0]

    def process(self, case, code=None, notes="", created_by=None, **kwargs):
        if not code:
            code = self.get_log_code(**kwargs)

        code_data = self.codes[code]

        return Log.objects.create(
            case=case,
            code=code,
            type=code_data['type'],
            level=code_data['level'],
            notes=notes,
            created_by=created_by
        )
