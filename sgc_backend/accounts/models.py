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
    Id = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.Nombre
class Profile(models.Model):
    Usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    Cedula = models.CharField(unique = True, max_length=12, blank=True)
    Rol = models.ForeignKey('Role', blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    objects = Profile()
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(Usuario=instance)
<<<<<<< HEAD
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(Usuario=instance)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
=======
>>>>>>> feat/bf-jobs
    instance.profile.save()
class View(models.Model):
    Nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.Nombre
class Permisos(models.Model):
    Rol = models.ForeignKey(Role, on_delete=models.CASCADE)
    Vista = models.ForeignKey(View, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Rol', 'Vista'], name='unique_rol_vista')
        ]
    def __str__(self):
        return f'Rol: {self.Rol.Nombre}, Vista: {self.Vista.Nombre}'
    
