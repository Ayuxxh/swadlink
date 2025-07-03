from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, username, name, role, cafe_name, password=None):
        if not username:
            raise ValueError("The Username is required")
        user = self.model(username=username, name=name, role=role, cafe_name=cafe_name)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, role=None, cafe=None, password='password'):
        user = self.create_user(username=username, name=name, role=role, cafe_name=cafe, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('employee', 'Employee'),
    )

    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)
    cafe_name = models.ForeignKey('cafes.Cafe', on_delete=models.SET_NULL, null=True, blank=False, related_name='cafes')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # ✅ Required fields for admin access
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'role']

    objects = CustomUserManager()

    def is_associated_with_cafe(self, cafe):
        return cafe in self.owned_cafes.all() or cafe in self.employed_cafes.all()

    def __str__(self):
        return f"{self.username} ({self.role})"

    # ✅ Optional: Ensure admin permissions work smoothly
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
