from django.contrib.auth.models import BaseUserManager
class UserManager(BaseUserManager):
    def create_user(self, username, phone_number, email, first_name, last_name, password):
        if not username:
            raise ValueError("User must have a username")

        if not phone_number:
            raise ValueError("User must have a phone number")

        if not first_name:
            raise ValueError("User must have a first name")

        if not last_name:
            raise ValueError("User must have a last name")

        user = self.model(username=username, phone_number=phone_number, email=self.normalize_email(email),
                          first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, email, first_name, last_name, password):
        user = self.create_user(username, phone_number, email, first_name, last_name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user
