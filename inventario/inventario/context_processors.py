from django.conf import settings


def account_settings(request):
    """Expose a small set of account-related settings to templates."""
    return {
        'ACCOUNT_ALLOW_REGISTRATION': getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', False),
    }
