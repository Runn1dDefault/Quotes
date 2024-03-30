from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.utils import send_notification
from quotes.models import Quote


@receiver(post_save, sender=Quote)
def notification_on_new_quote(sender, instance, created, **kwargs):
    if created:
        send_notification("Created new quote", quote_id=str(instance.id))
