from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StaffProfile, BaseUser, TEACHING_ASSISTANT, FACULTY, STUDENT

@receiver(post_save, sender=BaseUser)
def manage_staff_profile(sender, instance, **kwargs):
    if instance.user_type in [TEACHING_ASSISTANT, FACULTY]:
        try:
            instance.staffprofile.save()
        except StaffProfile.DoesNotExist:
            StaffProfile.objects.create(user=instance)
    else:
        try:
            delete_staff_profile(instance)
        except StaffProfile.DoesNotExist:
            pass


def delete_staff_profile(instance):
    if instance.staffprofile and instance.user_type == STUDENT:
        instance.staffprofile.delete()
     
