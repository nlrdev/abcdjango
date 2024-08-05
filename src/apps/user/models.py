from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid


class AccountManager(BaseUserManager):
    def create_user(self, email, username=None, password=None):
        username = uuid.uuid4().hex[:6]
        if not email:
            raise ValueError("Enter a valid email address!")
        user = self.model(
            email=self.
            normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None):
        username = uuid.uuid4().hex[:6]
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=12, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    uid = models.CharField(max_length=255, unique=True)

    USERNAME_FIELD = "email"

    objects = AccountManager()

    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_perms(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class ServiceUser(Account):
    key = models.CharField(max_length=1025, unique=True)
    description = models.CharField(max_length=1023)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.uid

    def create_user(self, email, password, secret):
        user_account = ServiceUser(
            email=Account.objects.normalize_email(email),
            username=uuid.uuid4().hex[:6],
            key=secret,
            uid=uuid.uuid4(),
        )
        user_account.set_password(password)
        user_account.save()
        return user_account


    def reset_password(self):
        pass


    def last_login(self):
        return self.login_time.latest("login_time")


class LastLogin(models.Model):
    user = models.ForeignKey(
        ServiceUser, related_name="login_time", on_delete=models.CASCADE
    )
    login_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.login_time)
