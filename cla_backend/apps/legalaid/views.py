from rest_framework import viewsets

from .models import Category, Question
from .serializers import CategorySerializer, QuestionSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    model = Category
    serializer_class = CategorySerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    model = Question
    serializer_class = QuestionSerializer

