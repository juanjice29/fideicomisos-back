import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import Profile
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
class Profile(models.Model):
    AGENTE_CAT = 2
    AUDITORIA = 3
    AUXCUMP = 4
    AUXFIDU = 5
    AUXPRIESGO = 6
    AUXTES = 7
    COPERFIDU =8
    CORCUMP = 9
    NEGFID = 10
    OPER = 11
    AGENTE_FIDE = 12 #ROL FIDECOMISOS
    ADMIN = 1 #ROL ADMINISTRADOR
    EMPLEADO = 13 #ROL DEFAULT
    ROLE_CHOICES = (
        (ADMIN, 'ADMIN'),
        (AGENTE_CAT, 'AGENTE_CAT'),
        (AUDITORIA, 'AUDITORIA'),
        (AUXCUMP, 'AUXCUMP'),
        (AUXFIDU, 'AUXFIDU'),
        (AUXPRIESGO, 'AUXPRIESGO'),
        (AUXTES, 'AUXTES'),
        (COPERFIDU, 'COPERFIDU'),
        (CORCUMP, 'CORCUMP'),
        (NEGFID, 'NEGFID'),
        (OPER, 'OPER'),
        (AGENTE_FIDE, 'AGENTE_FIDECOMISOS'),
        (EMPLEADO, 'EMPLEADO')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(unique = True, max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    objects = Profile()
    def __str__(self):  
        return self.user.username    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
