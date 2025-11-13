from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
import os


User = get_user_model()


class Command(BaseCommand):
    help = 'Create default groups and assign permissions: administradores, stock, ventas. Optional demo users via env vars.'

    def handle(self, *args, **options):
        # Import models here to avoid app-loading issues at import time
        from productos.models import Producto, MovimientoStock
        from clientes.models import Cliente
        from ventas.models import Venta, ItemVenta

        # administradores: all permissions
        admins, created = Group.objects.get_or_create(name='administradores')
        if created:
            self.stdout.write('Created group administradores')
        for p in Permission.objects.all():
            admins.permissions.add(p)

        # stock group: permissions for Producto and MovimientoStock
        stock_group, created = Group.objects.get_or_create(name='stock')
        if created:
            self.stdout.write('Created group stock')
        for model in (Producto, MovimientoStock):
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            for p in perms:
                stock_group.permissions.add(p)

        # ventas group: permissions for Cliente, Venta, ItemVenta
        ventas_group, created = Group.objects.get_or_create(name='ventas')
        if created:
            self.stdout.write('Created group ventas')
        for model in (Cliente, Venta, ItemVenta):
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            for p in perms:
                ventas_group.permissions.add(p)

        # Ensure ventas group does NOT receive permissions on Producto/MovimientoStock
        prod_ct = ContentType.objects.get_for_model(Producto)
        mov_ct = ContentType.objects.get_for_model(MovimientoStock)
        prod_perms = Permission.objects.filter(content_type=prod_ct)
        mov_perms = Permission.objects.filter(content_type=mov_ct)
        for p in prod_perms:
            if p in ventas_group.permissions.all():
                ventas_group.permissions.remove(p)
        for p in mov_perms:
            if p in ventas_group.permissions.all():
                ventas_group.permissions.remove(p)

        self.stdout.write(self.style.SUCCESS('Groups and permissions configured.'))

        # Optional: create demo users if env vars provided. This avoids hardcoded passwords.
        admin_pass = os.environ.get('ADMIN_PASS')
        demo_ventas_pass = os.environ.get('DEMO_VENTAS_PASS')
        demo_stock_pass = os.environ.get('DEMO_STOCK_PASS')

        # admin (superuser) - only if ADMIN_PASS provided
        if admin_pass:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', admin_pass)
                self.stdout.write(self.style.SUCCESS('Created superuser: admin (password provided by ADMIN_PASS)'))
            else:
                self.stdout.write('Superuser admin already exists')
        else:
            self.stdout.write('ADMIN_PASS not set — skipping superuser creation')

        # demo_ventas user
        if demo_ventas_pass:
            if not User.objects.filter(username='demo_ventas').exists():
                u = User.objects.create_user('demo_ventas', 'demo_ventas@example.com', demo_ventas_pass)
                u.is_staff = False
                u.save()
                ventas_group = Group.objects.get(name='ventas')
                ventas_group.user_set.add(u)
                self.stdout.write(self.style.SUCCESS('Created demo user: demo_ventas (password from DEMO_VENTAS_PASS)'))
            else:
                self.stdout.write('demo_ventas already exists')
        else:
            self.stdout.write('DEMO_VENTAS_PASS not set — skipping demo_ventas creation')

        # demo_stock user
        if demo_stock_pass:
            if not User.objects.filter(username='demo_stock').exists():
                u = User.objects.create_user('demo_stock', 'demo_stock@example.com', demo_stock_pass)
                u.is_staff = False
                u.save()
                stock_group = Group.objects.get(name='stock')
                stock_group.user_set.add(u)
                self.stdout.write(self.style.SUCCESS('Created demo user: demo_stock (password from DEMO_STOCK_PASS)'))
            else:
                self.stdout.write('demo_stock already exists')
        else:
            self.stdout.write('DEMO_STOCK_PASS not set — skipping demo_stock creation')

        self.stdout.write(self.style.SUCCESS('Users created/verified (as configured).'))
