from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import OutcomeMedia


@receiver(post_delete, sender=OutcomeMedia)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.media.delete(save=False)
