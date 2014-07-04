from cla_eventlog.models import Log
from cla_eventlog.constants import LOG_TYPES

from timer.utils import get_or_create_timer


class BaseEvent(object):
    key = ''
    codes = {}

    def get_log_code(self, **kwargs):
        if len(self.codes) > 1:
            raise NotImplementedError()

        return self.codes.keys()[0]

    def save_log(self, log):
        log.save(force_insert=True)

    def process(self, case, code=None, notes="", created_by=None, **kwargs):
        if not code:
            code = self.get_log_code(**kwargs)

        code_data = self.codes[code]
        timer = get_or_create_timer(created_by)

        log = Log(
            case=case,
            code=code,
            timer=timer,
            type=code_data['type'],
            level=code_data['level'],
            notes=notes,
            created_by=created_by
        )

        self.save_log(log)

        if code_data.get('stops_timer', False):
            timer.stop()

        return log

    @classmethod
    def get_selectable_codes(cls, role):
        selectable_codes = []

        for code, code_data in cls.codes.items():
            if code_data['type'] == LOG_TYPES.OUTCOME and role in code_data['selectable_by']:
                selectable_codes.append(code)
        return selectable_codes

