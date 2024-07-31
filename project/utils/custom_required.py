def check_login_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.groups.filter(name__in=['inventory manager','order manager']).exists():
        return True
    return False

def role_manage(user):
    user_role = None
    if user.groups.filter(name='inventory manager').exists():
        user_role = 'inventory manager'
    elif user.groups.filter(name='order manager').exists():
        user_role = 'order manager'
    elif user.is_superuser:
        user_role = 'Admin'
    return user_role
