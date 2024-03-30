from uuid import uuid4

from django.db import models

from quotes.validators import MinWordCountValidator


class BaseModel(models.Model):
    objects = models.Manager()

    id = models.UUIDField(default=uuid4, primary_key=True)

    class Meta:
        abstract = True


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class Author(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField()
    death_date = models.DateField(blank=True, null=True)

    @property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def __str__(self):
        return self.full_name

    class Meta:
        unique_together = ["first_name", "last_name", "birth_date"]
        ordering = ("id",)


class Quote(BaseModel):
    _text_validator = MinWordCountValidator(3)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="quotes")
    tags = models.ManyToManyField(Tag, blank=True, related_name="quotes")

    class Meta:
        indexes = (
            models.Index("id", "text", name="quote_text_idx"),
            models.Index("id", "created_at", name="quote_created_idx"),
        )
        ordering = ("-created_at",)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self._text_validator(self.text)  # for TextField validators are not called
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
