from rest_framework import serializers
from rest_framework.reverse import reverse

from quotes.models import Quote, Author, Tag
from quotes.validators import MinWordCountValidator


class AuthorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=100, write_only=True, required=True)
    last_name = serializers.CharField(max_length=100, write_only=True, required=False)

    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "full_name", "birth_date", "death_date")
        read_only_fields = ("id",)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("id",)


class QuoteSerializer(serializers.ModelSerializer):
    text = serializers.CharField(validators=[MinWordCountValidator(3)])
    tag_listing = serializers.SerializerMethodField(read_only=True)
    author = serializers.HyperlinkedRelatedField(
        queryset=Author.objects.all(),
        view_name="author-detail",
        lookup_url_kwarg="author_id",
        lookup_field="id",
        many=False,
        required=True
    )
    tags = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all()),
        write_only=True,
        required=False
    )

    class Meta:
        model = Quote
        fields = ("id", "text", "created_at", "tags", "author", "tag_listing")
        read_only_fields = ("id", "created_at")

    def get_tag_listing(self, obj):
        return self.context['request'].build_absolute_uri(reverse('quote-tags', kwargs={'quote_id': obj.id}))

    def create(self, validated_data):
        tags = validated_data.pop("tags", None)
        instance = super().create(validated_data)
        if tags:
            instance.tags.add(*tags)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        if tags:
            instance.tags.clear()
            instance.tags.add(*tags)
        return super().update(instance, validated_data)
