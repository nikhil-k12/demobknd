from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(_("email address"), max_length=254, unique=True)
    fname = models.CharField(_("first name"), max_length=254)
    lname = models.CharField(_("last name"), max_length=254)
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]