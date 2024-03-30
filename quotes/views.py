from django.shortcuts import render
from rest_framework import viewsets, filters, decorators, response

from quotes.filters import ListFilter
from quotes.models import Quote, Tag, Author
from quotes.serializers import QuoteSerializer, TagSerializer, AuthorSerializer


class AuthorModelViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("id", "first_name", "last_name")
    lookup_url_kwarg = "author_id"
    lookup_field = "id"


class TagModelViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("id", "name")
    lookup_url_kwarg = "tag_id"
    lookup_field = "id"


class QuoteModelViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.select_related("author").all()
    serializer_class = QuoteSerializer
    filter_backends = (filters.SearchFilter, ListFilter, filters.OrderingFilter)
    search_fields = ("id", "text", "author__first_name", "author__last_name")
    filter_by_fields = {"tags": "tags__in", "author_id": "author_id"}
    ordering_fields = ("created_at",)
    lookup_url_kwarg = "quote_id"
    lookup_field = "id"

    @decorators.action(methods=["GET"], detail=True, url_path='tags', url_name="tags")
    def get_tags(self, request, **kwargs):
        quote = self.get_object()
        tag_serializer = TagSerializer(instance=quote.tags.all(), context=self.get_serializer_context(), many=True)
        return response.Response(tag_serializer.data)


def index(request):
    return render(request, "index.html")
