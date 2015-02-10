Concepts
========

Event Log
---------

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
    :emphasize-lines: 6, 10

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
                                             # for this key are to be made

                'set_requires_action_by': None # which user type needs to action this
                                               # if any.
            }
     }

    event_registry.register(AppEvents)

An example of this is ``AcceptCaseEvent`` from the ``cla_provider`` app.

.. literalinclude:: /../cla_backend/apps/cla_provider/events.py
    :pyobject: AcceptCaseEvent



How does it relate to Outcome Codes?
++++++++++++++++++++++++++++++++++++

Outcome codes are a subset of event logs that have some sort of
significance to the management information or something that 
should be displayed to the operator.  An example of an outcome 
code is ``SPOP`` as shown in the previous example. On the other
hand a ``CASE_VIEWED`` event isn't and outcome code. To define 
one set the type to ``LOG_TYPES.OUTCOME`` in the event definition
in ``events.py``.

Fields that are demoralised onto case?
++++++++++++++++++++++++++++++++++++++

During the initial design we didn't foresee needing to query
information stored in the event log to create the dashboard views,
it turns out that some fields are frequently queried and we had 
to denorm the following:

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

Reporting and Management Information
++++++++++++++++++++++++++++++++++++

The reports that exist in the system are temporary and will eventually
be replaced by the LAA's enterprise reporting solution. Here is a
short summary of what each one does. 



Timers
------

timers are weird
timers can be cancelled
timers don't relate to the phone system

Reporting and Management Information
++++++++++++++++++++++++++++++++++++


Status Check
------------

There is a status check end point, this is what the checks mean.
