from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User

@receiver(pre_save, sender=User)
def handle_doctor_approval(sender, instance, **kwargs):
    if instance.pk:  # Only for existing users
        try:
            old_user = User.objects.get(pk=instance.pk)
            if (old_user.verification_status != 'approved' and 
                instance.verification_status == 'approved' and
                instance.original_user_type == 'Doctor'):
                instance.user_type = 'Doctor'
        except User.DoesNotExist:
            pass