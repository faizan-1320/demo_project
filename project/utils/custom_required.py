"""Custom required"""
def check_login_admin(user):
    """Login Required For Admin Function"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.groups.filter(name__in=['inventory manager','order manager']).exists():
        return True
    return False
