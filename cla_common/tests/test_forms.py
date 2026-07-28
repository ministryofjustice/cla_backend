#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cla_common.forms
------------

Tests for `cla_common` forms module.
"""

import unittest

from cla_common import forms as f
from django import forms


class TestMultipleFormForm(unittest.TestCase):
    def test_initial(self):
        class DummyForm(forms.Form):
            pass

        class Multi(f.MultipleFormsForm):
            forms_list = (("form1", DummyForm), ("form2", DummyForm))

        form1_initial = {"foo": "bar"}
        m_instance = Multi(initial={"form1": form1_initial})

        self.assertDictEqual(m_instance.form_dict().get("form1").initial, form1_initial)
