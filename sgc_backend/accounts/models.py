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
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre
    
class Profile(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(unique = True, max_length=12, blank=True)
    rol = models.ForeignKey('Role', blank=True, null=True, on_delete=models.SET_NULL)
    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    objects = Profile()
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(usuario=instance)
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class View(models.Model):
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre
class Permisos(models.Model):
    rol = models.ForeignKey(Role, on_delete=models.CASCADE)
    vista = models.ForeignKey(View, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rol', 'vista'], name='unique_rol_vista')
        ]
    def __str__(self):
        return f'rol: {self.rol.nombre}, vista: {self.vista.nombre}'
    
