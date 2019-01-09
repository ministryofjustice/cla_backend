# coding=utf-8
from django.utils.unittest import TestCase

from ..tasks import BasePerformanceTask


class SingleVariableKeysTask(BasePerformanceTask):
    variables = {"a": ["c", "d", "e", "f"]}


class MultipleVariableKeysTask(BasePerformanceTask):
    variables = {"a": ["c", "d", "e", "f"], "b": ["g", "h", "i", "j"]}


class TaskKwargsTestCase(TestCase):
    def test_task_kwargs_multiple_keys(self):
        t = MultipleVariableKeysTask()

        self.assertListEqual(
            t.task_kwargs_list(),
            [
                {"a": "c", "b": "g"},
                {"a": "c", "b": "h"},
                {"a": "c", "b": "i"},
                {"a": "c", "b": "j"},
                {"a": "d", "b": "g"},
                {"a": "d", "b": "h"},
                {"a": "d", "b": "i"},
                {"a": "d", "b": "j"},
                {"a": "e", "b": "g"},
                {"a": "e", "b": "h"},
                {"a": "e", "b": "i"},
                {"a": "e", "b": "j"},
                {"a": "f", "b": "g"},
                {"a": "f", "b": "h"},
                {"a": "f", "b": "i"},
                {"a": "f", "b": "j"},
            ],
        )

    def test_task_kwargs_single_keys(self):
        t = SingleVariableKeysTask()

        self.assertListEqual(t.task_kwargs_list(), [{"a": "c"}, {"a": "d"}, {"a": "e"}, {"a": "f"}])
