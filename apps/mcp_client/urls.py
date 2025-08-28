from django.urls import path
from .views import summarize_numbers_views, slugify_text_views

urlpatterns = [
    path("summarize-numbers", summarize_numbers_views, name="summarize_numbers"),
    path("slugify-text", slugify_text_views, name="slugify_text"),
]