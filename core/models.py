import secrets

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        # Check if the phone number is provided
        if not phone_number:
            raise ValueError("The Phone Number field must be set")

        # Generate a unique invitation code using secrets module
        invitation_code = secrets.token_hex(3).upper()[:6]

        # Create a new user instance with provided data and generated invitation code
        user = self.model(phone_number=phone_number, invitation_code=invitation_code, **extra_fields)
        user.set_password(password)  # Hash and store the user's password securely
        user.save(using=self._db)  # Save the user object to the database
        return user


# Custom user model manager that uses the UserManager class
class User(AbstractBaseUser, PermissionsMixin):
    # Define user attributes
    phone_number = models.CharField(max_length=15, unique=True)  # Unique phone number as the username
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True,
                                   blank=True)  # User who invited this user
    invitation_code = models.CharField(max_length=6, blank=True)  # Invitation code associated with the user

    objects = UserManager()  # Use the custom UserManager for managing user instances

    USERNAME_FIELD = 'phone_number'  # The field to use as the unique identifier for authentication

    def __str__(self):
        return self.phone_number  # String representation of the user object


# Model to store invitation codes and their associated users
class InvitationCode(models.Model):
    code = models.CharField(max_length=6)  # The actual invitation code
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # User associated with the invitation code
