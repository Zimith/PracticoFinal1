from django.conf import settings
from django.shortcuts import redirect, resolve_url


class LoginRequiredMiddleware:
    """Require login for all views except a small whitelist.

    This middleware avoids importing URL names at module import time. Use
    simple path prefixes for exemptions (accounts, admin, static, media).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # simple prefixes that don't require authentication
        # ensure prefixes start with a leading slash
        def _ensure_slash(prefix, default):
            p = getattr(settings, prefix, default) if hasattr(settings, prefix) else default
            if not p.startswith('/'):
                p = '/' + p
            return p

        static_prefix = _ensure_slash('STATIC_URL', '/static/')
        media_prefix = _ensure_slash('MEDIA_URL', '/media/')

        # resolve LOGIN_URL in case it's a named URL (e.g. 'account_login')
        try:
            login_path = resolve_url(settings.LOGIN_URL)
        except Exception:
            login_path = '/accounts/login/'
        if not login_path.startswith('/'):
            login_path = '/' + login_path
        # ensure login_path ends with a slash for consistent matching
        if not login_path.endswith('/'):
            login_path = login_path + '/'
        # Build exemptions and include variants without trailing slash to be tolerant
        def _variants(p):
            p = p or '/'
            p1 = p if p.startswith('/') else '/' + p
            p2 = p1[:-1] if p1.endswith('/') else p1 + '/'
            return {p1, p2}

        exemptions = set()
        exemptions.update(_variants(login_path))
        exemptions.update(_variants('/accounts/logout/'))
        exemptions.update(_variants('/accounts/'))
        exemptions.update(_variants('/admin/'))
        exemptions.update(_variants(static_prefix))
        exemptions.update(_variants(media_prefix))

        # store as list for ordering but normalized
        self.exempt_prefixes = sorted(exemptions)

    def __call__(self, request):
        path = request.path
        # Debug info when running in development
        if getattr(settings, 'DEBUG', False):
            try:
                print("[LoginRequiredMiddleware] request.path=", path)
                print("[LoginRequiredMiddleware] exempt_prefixes=", self.exempt_prefixes)
            except Exception:
                pass
        # allow if request is for an exempt prefix
        if any(path.startswith(p) for p in self.exempt_prefixes):
            return self.get_response(request)

        if not request.user.is_authenticated:
            # Use resolve_url to support named LOGIN_URL values
            target = resolve_url(settings.LOGIN_URL)
            # Normalize target for comparison
            if not isinstance(target, str):
                target = str(target)
            if not target.startswith('/'):
                target = '/' + target
            if not target.endswith('/'):
                target = target + '/'

            # Defensive: if the request is already the login URL, allow it through
            if path == target or path == target[:-1]:
                return self.get_response(request)
            if getattr(settings, 'DEBUG', False):
                try:
                    print("[LoginRequiredMiddleware] redirecting anonymous to:", target)
                except Exception:
                    pass
            return redirect(target)

        return self.get_response(request)
