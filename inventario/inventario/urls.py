"""
URL configuration for inventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import viewss
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import os
import re
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve
from django.http import HttpResponse
from django.views.generic.base import RedirectView

urlpatterns = [
    # Simple health endpoint to diagnose redirect loops (no auth)
    path('health/', lambda request: HttpResponse('ok'), name='health'),
    # Redirigir la raíz '/' a la lista de productos para que la app sea accesible
    path('', RedirectView.as_view(pattern_name='productos:producto_list', permanent=False)),
    path('admin/', admin.site.urls),
    path("productos/", include("productos.urls")),
    path("clientes/", include("clientes.urls")),
    path("ventas/", include("ventas.urls")),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif os.environ.get('SERVE_MEDIA', '0') == '1':
    # Serve MEDIA files in demo/CI environments even when DEBUG is False.
    prefix = settings.MEDIA_URL or '/media/'
    # build a regex like ^media/(?P<path>.*)$ (strip leading slash)
    escaped = re.escape(prefix.lstrip('/'))
    urlpatterns += [
        re_path(rf'^{escaped}(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]