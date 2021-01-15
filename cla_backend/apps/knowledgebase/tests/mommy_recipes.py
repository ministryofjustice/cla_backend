from knowledgebase import models
from model_mommy.recipe import Recipe

article = Recipe(models.Article)
telephone_number = Recipe(models.TelephoneNumber)
article_category_matrix = Recipe(models.ArticleCategoryMatrix)
