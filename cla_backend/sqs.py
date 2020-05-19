import collections

from boto.sqs.queue import Queue
from boto.sqs.message import Message

from kombu.transport.SQS import Channel
from kombu.transport import virtual
from kombu.utils import cached_property


class CLASQSChannel(Channel):
    @cached_property
    def predefined_queues(self):
        # We are using a strict sqs setup which we are given only list of predefined queues and
        url = self.transport_options.get("predefined_queue_url", None)
        q = Queue(connection=self.sqs, url=url, message_class=Message)
        return [q]

    def __init__(self, *args, **kwargs):
        # CLA Change - On cloud platforms we don't have permissions to perform actions such as ListQueues
        # So instead lets use a list of predefined queue names
        # Remove call to direct parent as that will perform the ListQueues action
        # super(CLASQSChannel, self).__init__(*args, **kwargs)
        virtual.Channel.__init__(self, *args, **kwargs)

        queues = self.predefined_queues  # self.sqs.get_all_queues(prefix=self.queue_name_prefix)

        for queue in queues:
            self._queue_cache[queue.name] = queue
        self._fanout_queues = set()

        # The drain_events() method stores extra messages in a local
        # Deque object. This allows multiple messages to be requested from
        # SQS at once for performance, but maintains the same external API
        # to the caller of the drain_events() method.
        self._queue_message_cache = collections.deque()

    def _new_queue(self, queue, **kwargs):
        # Translate to SQS name for consistency with initial
        # _queue_cache population.
        queue = self.entity_name(self.queue_name_prefix + queue)
        # We don't want to create a queue if it does not exist, instead return None
        return self._queue_cache.get(queue)

    def _delete(self, queue, *args):
        # We don't want to delete our only queues as this done as part of terraform setup by cloud platforms
        pass
