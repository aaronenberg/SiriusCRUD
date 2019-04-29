from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Development, DevelopmentMedia


@receiver(post_delete, sender=DevelopmentMedia)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.media.delete(save=False)


@receiver(pre_save, sender=Development)
def attach_outcome_slug(sender, instance, **kwargs):
    if instance._state.adding:
        instance.slug = instance.generate_slug()
