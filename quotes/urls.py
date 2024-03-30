from django.urls import path, include
from rest_framework.routers import SimpleRouter

from quotes.views import QuoteModelViewSet, AuthorModelViewSet, TagModelViewSet

router = SimpleRouter()
router.register('quotes', QuoteModelViewSet, basename="quote")
router.register('tags', TagModelViewSet, basename="tag")
router.register('authors', AuthorModelViewSet, basename="author")

urlpatterns = [
    path('', include(router.urls)),
]
