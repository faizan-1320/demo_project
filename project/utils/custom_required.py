
def check_login_admin(user):
    if not user.is_authenticated:
        return False
    elif user.is_superuser:
        return True
    else:
        return False