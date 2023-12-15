import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import Profile
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(unique = True, max_length=12, blank=True)
    rol = models.ForeignKey('Role', blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    objects = Profile()
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
class View(models.Model):
    name = models.CharField(max_length=255)
class Permisos(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    view = models.ForeignKey(View, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'view'], name='unique_role_view')
        ]
    def __str__(self):
        return f'Role: {self.role.name}, View: {self.view.name}'