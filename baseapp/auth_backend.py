from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            d = {'%s__iexact'%UserModel.USERNAME_FIELD: username}
            user = UserModel.objects.get(**d)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)

        return None
