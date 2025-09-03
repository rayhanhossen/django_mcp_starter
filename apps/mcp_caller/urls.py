from django.urls import path
from .views import SummarizeNumbersView, SlugifyTextView, ChatToolView

urlpatterns = [
    path("summarize-numbers", SummarizeNumbersView.as_view(), name="summarize_numbers"),
    path("slugify-text", SlugifyTextView.as_view(), name="slugify_text"),
    path("chat", ChatToolView.as_view(), name="chat"),
]
