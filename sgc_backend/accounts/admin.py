from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
TokenAdmin.raw_id_fields = ['user']
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path
from .models import Role, View, Permisos
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import Profile
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib import admin

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            user_part, domain_part = email.rsplit('@', 1)
            if not domain_part in ['fgs.co', 'fundaciongruposocial.co']:
                raise ValidationError("Invalid domain. Accepted domains are: '@fgs.co', '@fundaciongruposocial.co'")
        return email

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'usuario'

class CustomUserAdmin(AuthUserAdmin):
    form = UserAdminForm
    inlines = (ProfileInline, )
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Unregister the original User admin
admin.site.unregister(User)

# Register your custom User admin
admin.site.register(User, CustomUserAdmin)
@admin.register(Role)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre']
@admin.register(Permisos)
class PermisosAdmin(admin.ModelAdmin):
    list_display = ['rol', 'vista','accion']
    
@admin.register(View)
class ViewAdmin(admin.ModelAdmin):
    list_display = ['nombre']