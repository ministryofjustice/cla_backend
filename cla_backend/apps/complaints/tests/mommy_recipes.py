# -*- coding: utf-8 -*-
from legalaid.tests.mommy_recipes import eod_details
from model_mommy.recipe import Recipe, foreign_key

from ..models import Complaint, Category


category = Recipe(Category)

complaint = Recipe(
    Complaint,
    eod=foreign_key(eod_details),
    category=foreign_key(category)
)
