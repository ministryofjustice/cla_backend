# coding=utf-8
from legalaid.tests.mommy_recipes import eod_details
from model_mommy.recipe import Recipe, foreign_key

from ..models import DiversityDataCheck


diversitydatacheck = Recipe(DiversityDataCheck, status='ok', action='check')
