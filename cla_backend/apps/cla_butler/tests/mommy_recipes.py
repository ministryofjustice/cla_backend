# coding=utf-8
from model_bakery.recipe import Recipe

from ..models import DiversityDataCheck

diversitydatacheck = Recipe(DiversityDataCheck, status="ok", action="check")
