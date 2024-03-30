from django.contrib import admin
from django.template.defaultfilters import truncatechars

from .models import Tag, Author, Quote


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name", "id")
    readonly_fields = ("id",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "birth_date", "death_date")
    list_display_links = ("id", "full_name")
    search_fields = ("id", "first_name", "last_name")
    list_filter = ("birth_date", "death_date")
    readonly_fields = ("id",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    autocomplete_fields = ("author", "tags")
    list_display = ("id", "author", "short_text")
    search_fields = ("id", "author__full_name", "text")
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at")

    def short_text(self, obj):
        return truncatechars(obj.text, 35)

    short_text.short_description = 'Short Content'
