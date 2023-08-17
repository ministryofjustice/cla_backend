from kombu.transport.SQS import Channel


class CLASQSChannel(Channel):
    def _update_queue_cache(self, queue_name_prefix):
        url = self.transport_options.get("predefined_queue_url", None)
        queue_name = url.split("/")[-1]
        self._queue_cache[queue_name] = url

    def _new_queue(self, queue, **kwargs):
        # Translate to SQS name for consistency with initial
        # _queue_cache population.
        queue = self.entity_name(self.queue_name_prefix + queue)
        # We don't want to create a queue if it does not exist, instead return None
        return self._queue_cache.get(queue)

    def _delete(self, queue, *args):
        # We don't want to delete our only queues as this done as part of terraform setup by cloud platforms
        pass
