from model_mommy.recipe import Recipe

from cla_common.constants import DIAGNOSIS_SCOPE
from diagnosis.models import DiagnosisTraversal


diagnosis = Recipe(DiagnosisTraversal)

diagnosis_yes = Recipe(DiagnosisTraversal, state=DIAGNOSIS_SCOPE.INSCOPE)
