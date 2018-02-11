from accounts.models import Token, User


class PasswordlessAuthenticationBackend():

    def authenticate(self, token_uid):
        try:
            token = Token.objects.get(uid=token_uid)
            return User.objects.get(email=token.email)
        except Token.DoesNotExist:
            return None
        except User.DoesNotExist:
            return User.objects.create(email=token.email)

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None