Concepts
========

.. contents:: :depth: 4
    :local:

Event Log
---------

Events are things that happen in the system, **event logs** are the record of
those things happening. To log an event it must first be registered with the
event registry. Event logs are namespaced by a *key* and there can be more
than one *code* per key.

Events can either be created by a user action explicitly (e.g a Provider accepts
a case that has been assigned to them) or implicitly by the user using the site
normally (e.g. viewing a case is logged).


How does it work?
+++++++++++++++++

It's kind of based on how admin.py works, we have an
:py:func:`cla_eventlog.autodiscover` function that walks the ``INSTALLED_APPS``
and discovers ``events.py`` files that exist inside of our apps. Each ``event.py``
is responsible for registering any events it specifies with the ``event_registry``.

.. literalinclude:: /../cla_backend/apps/cla_eventlog/__init__.py
    :pyobject: autodiscover

.. highlight:: python

A typical ``events.py`` file would look like this::

    from cla_eventlog.events import BaseEvent
    from cla_eventlog import event_registry

    class AppEvents(BaseEvent):
        key = 'foo'

    event_registry.register(AppEvents)

This obviously doesn't do anything useful but it conforms to the contract. Now
if we want to actually register an event that does something then we would do
something like:

.. code-block:: python
    :linenos:
    :emphasize-lines: 6, 10, 12, 14, 18, 20, 23, 27

    from cla_eventlog.events import BaseEvent
    from cla_eventlog import event_registry
    from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES

    class SingleCodeEvents(BaseEvent):
        key = 'bar'
        codes = {
            'BAZ': {                         # each event has one or more codes

                'type': LOG_TYPES.OUTCOME,   # define if this event generates a system or 'outcome' code

                'level': LOG_LEVELS.HIGH,    # define the importance of this event

                'selectable_by': [],         # list of user types this event code can
                                             # be created by. Can be created by anyone if left as
                                             # an empty list.

                'description': 'foo baz',    # A friendly string for your own sanity

                'stops_timer': True,         # True/False: should this stop the current
                                             # running timer when this event is processed

                'order': 10,                 # optional, what order should this code be
                                             # displayed in if a user selection of the codes
                                             # for this key are to be made. Default is 10000

                'set_requires_action_by': None # which user type needs to action this
                                               # if any.
            }
     }

    event_registry.register(AppEvents)

An example of this is ``AcceptCaseEvent`` from the ``cla_provider`` app.

.. literalinclude:: /../cla_backend/apps/cla_provider/events.py
    :pyobject: AcceptCaseEvent

I've defined some events. Now what?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Simple Usage
************

The API for an **event log** is simple. You can request an event from the
``cla_eventlog.event_registry`` by key::

    Event = event_registry.get_event('key')
    event = Event()

Once you have an event call ``.process`` on it to save::

    # event is an instance that you can 'process'
    # if key only has one code then you don't need to specify it
    event.process(
        case,
        notes='some notes',
        created_by=request.user,
    )


Here is a real life example of how we save a ``CASE_VIEWED`` event log:

.. literalinclude:: /../cla_backend/apps/legalaid/views.py
    :pyobject: FullCaseViewSet.retrieve
    :emphasize-lines: 5-8


Storing Context
***************
If you need to save some data along with an event then you can
assign a dictionary to the ``context`` kwarg. We do this for storing the
provider a case was assigned to when a case assignment is done. This is because
a provider can reject an assignment and then the case could be assigned to another
provider. We would lose all record of the initial assignment if we didn't
store that in the context.


How does it relate to Outcome Codes?
++++++++++++++++++++++++++++++++++++

Outcome codes are a subset of event logs that have some sort of
significance to the management information or something that
should be displayed to the operator.  An example of an outcome
code is ``SPOP`` as shown in the previous example. On the other
hand a ``CASE_VIEWED`` event isn't and outcome code. To define
one set the type to ``LOG_TYPES.OUTCOME`` in the event definition
in ``events.py``.

Fields that are denormalised onto ``legalaid.models.Case``?
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

During the initial design we didn't foresee needing to query
information stored in the event log to create the dashboard views,
it turns out that some fields are frequently queried and we had
to denormalise the following:

    * ``outcome_code`` The last outcome code processed on the case
    * ``outcome_code_id`` the primary key of the above to make joins
      cheaper
    * ``provider_assigned_at`` the time this case was assigned
    * ``provider_viewed`` the time the provider first viewed this
      case after getting it assigned to them
    * ``provider_accepted`` time when provider first accepted a case
    * ``provider_closed`` time when provider closed the case
    * ``search_field`` a special field for free text search, includes
      the case reference without dashes but other things can be added
      according to the operator's needs

This is starting to get unmanageable and if more fields need to be denormalised
then it would be a good idea to create a ``CaseDenorm`` model that's a OneToOne
relation of ``legalaid.Case`` and store all the denormalised fields there.

Reporting and Management Information
------------------------------------
.. automodule:: reports.forms

.. py:currentmodule:: reports.forms

The reports that exist in the system are temporary and will eventually
be replaced by the LAA's enterprise reporting solution OBIEE_. Here is a
short summary of what each one does.

    * :py:class:`MIVoiceReport`
        A report that allows contract management to download a unified report
        of all the billing CSVs that providers have uploaded to the system.
    * :py:class:`MICaseExtract`
        This is the most comprehensive report, it dumps all event logs created
        between the specified date range. The logs are joined with cases,
        personal details, diagnosis, eligibility checks and is pretty much
        a single place where you can find out almost anything that has
        happened in the system.
    * :py:class:`MIFeedbackExtract`
        This extract shows all provider feedback left on cases for the operators
    * :py:class:`MIAlternativeHelpExtract`
        This shows how many cases were referred to alternative help organisations
        and which organisations they were referred to.
    * :py:class:`MIContactsPerCaseByCategory`
        This extract shows the average number of contacts made per case in each
        legal aid category.
    * :py:class:`MISurveyExtract`
        The contact details for people who have agreed to be contracted for
        user research. Requires a password
    * :py:class:`M1CB1Extract`
        Report to show if the operator service handled contacts
        that require a callback within their SLAs or not.
    * :py:class:`MIDigitalCaseTypesExtract`
        Shows if a case was created on/by:
            * Web (full means test completed)
            * Web (callback only)
            * SMS
            * Voicemail
            * Phone

Timers
------

Timers exist to keep track of how much billable time has been spent on a case
by an **operator**.  They are not created automatically. They can't be because
we have no way of integrating with the telephony system the operators use.

A timer is created by hitting the ``/timer/`` endpoint with a HTTP POST request.

.. literalinclude:: /../cla_backend/apps/timer/views.py
    :pyobject: BaseTimerViewSet.get_or_create

You'll get a reference to the timer which you can later use to cancel it by
issuing a DELETE request to ``/timer/<reference>/``.

It's not always necessary to cancel a timer; in some situations creating an
event can stop a timer too.


Status Check
------------

There is a status check end point, this is what the checks mean.

.. _OBIEE: http://www.oracle.com/us/solutions/business-analytics/business-intelligence/enterprise-edition/overview/index.html
