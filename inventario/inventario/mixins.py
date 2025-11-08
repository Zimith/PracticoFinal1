from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class FriendlyPermissionRequiredMixin(PermissionRequiredMixin):
    """Permission mixin that shows a friendly message and redirects when an
    authenticated user lacks permission. Unauthenticated users are handled
    by the parent mixin (redirect to login).
    """

    def handle_no_permission(self):
        request = self.request
        if request.user.is_authenticated:
            messages.error(request, 'No tienes acceso a esta sección.')
            # try to redirect back, otherwise go to product list
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect('productos:producto_list')
        return super().handle_no_permission()
