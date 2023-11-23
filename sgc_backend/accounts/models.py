from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    AGENTE_CAT = 1
    AUDITORIA = 2
    AUXCUMP = 3
    AUXFIDU = 4
    AUXPRIESGO = 5
    AUXTES = 6
    COPERFIDU =7
    CORCUMP = 8
    NEGFID = 9
    OPER = 10
    AGENTE_FIDE = 11 #ROL FIDECOMISOS
    ADMIN = 12 #ROL ADMINISTRADOR
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
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()