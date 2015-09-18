import mock

from cla_eventlog.models import Log
from core.tests.mommy_utils import make_recipe, make_user
from legalaid.models import Case


class BaseCaseLogFormTestCaseMixin(object):
    FORM = None

    def setUp(self):
        super(BaseCaseLogFormTestCaseMixin, self).setUp()

        self.user = make_user()

    def get_default_data(self):
        return {
            'notes': 'lorem ipsum'
        }

    def test_save_successfull(self):
        self._test_save_successfull()

    def _test_save_successfull(self, case=None, data=None):
        if not case:
            case = make_recipe('legalaid.case')
        self.assertEqual(Log.objects.count(), 0)

        if data == None:
            data = self.get_default_data()
        form = self.FORM(case=case, data=data)

        self.assertTrue(form.is_valid())

        form.save(self.user)

        case = Case.objects.get(pk=case.pk)

        self.assertEqual(Log.objects.count(), 1)
        log = Log.objects.all()[0]

        self.assertEqual(log.notes, 'lorem ipsum')
        self.assertEqual(log.created_by, self.user)
        self.assertEqual(log.case, case)

    def test_invalid_form(self):
        case = make_recipe('legalaid.case')
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_default_data()
        data['notes'] = 'l'*5001
        form = self.FORM(case=case, data=data)

        self.assertFalse(form.is_valid())

        self.assertEqual(len(form.errors), 1)
        self.assertItemsEqual(
            form.errors['notes'],
            [u'Ensure this value has at most 5000 characters (it has 5001).']
        )

        # nothing has changed
        case = Case.objects.get(pk=case.pk)
        self.assertEqual(Log.objects.count(), 0)


class EventSpecificLogFormTestCaseMixin(BaseCaseLogFormTestCaseMixin):
    def get_default_data(self):
        data = super(EventSpecificLogFormTestCaseMixin, self).get_default_data()

        form = self.FORM(case=mock.MagicMock())
        event_code = form.fields['event_code'].choices[0][0]  # getting the first code
        data['event_code'] = event_code

        return data

    def test_invalid_event_code(self):
        # test with invalid code
        case = make_recipe('legalaid.case')
        self.assertEqual(Log.objects.count(), 0)

        data = self.get_default_data()
        data['event_code'] = 'invalid'
        form = self.FORM(case=case, data=data)

        self.assertFalse(form.is_valid())

        self.assertItemsEqual(
            form.errors, {
                'event_code': [u'Invalid choice']
            }
        )
