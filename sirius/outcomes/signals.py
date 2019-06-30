from django.core.files.storage import default_storage
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from storages.utils import safe_join

from .models import Outcome, OutcomeMedia


@receiver(post_delete, sender=OutcomeMedia)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.media.delete(save=False)


@receiver(pre_save, sender=OutcomeMedia)
def rename_if_adding_dup(sender, instance, **kwargs):
    if not instance._state.adding:
        return
    is_dup = default_storage.exists(safe_join(instance.UPLOADS_ROOT_DIR, str(instance)))
    if is_dup:
        instance.media.name = instance.rename_dup()


@receiver(pre_save, sender=Outcome)
def attach_outcome_slug(sender, instance, **kwargs):
    if instance._state.adding:
        instance.slug = instance.generate_slug()

