"""Minimal drop-in replacement for django-extended-choices.

This project only relies on:
- constant attributes (e.g. ``MY_CHOICES.FOO``)
- ``CHOICES`` as a Django-compatible ``(value, label)`` iterable
- ``CHOICES_DICT`` for value-to-label lookups

The external package currently depends on ``pkg_resources``; this local module
avoids that runtime dependency while preserving existing call sites.
"""


class Choices:
    def __init__(self, *definitions):
        self.CHOICES = []
        self.CHOICES_DICT = {}

        for definition in definitions:
            if len(definition) == 3:
                constant, value, label = definition
            elif len(definition) == 2:
                constant, value = definition
                label = value
            else:
                raise ValueError("Choices entries must be (constant, value[, label]) tuples")

            setattr(self, constant, value)
            self.CHOICES.append((value, label))
            self.CHOICES_DICT[value] = label

        self.CHOICES = tuple(self.CHOICES)

    def __iter__(self):
        return iter(self.CHOICES)

    def __len__(self):
        return len(self.CHOICES)

    def __getitem__(self, index):
        return self.CHOICES[index]

    def __contains__(self, value):
        return value in self.CHOICES_DICT
