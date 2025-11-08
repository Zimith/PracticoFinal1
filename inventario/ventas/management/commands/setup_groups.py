from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Create default groups and assign permissions: administradores, stock, ventas'

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
        # (sales should only manage clients and ventas)
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

        # --- create basic users for convenience (if they don't exist) ---
        # admin (superuser)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'AdminPass123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / AdminPass123'))
        else:
            self.stdout.write('Superuser admin already exists')

        # demo_ventas user
        if not User.objects.filter(username='demo_ventas').exists():
            u = User.objects.create_user('demo_ventas', 'demo_ventas@example.com', 'DemoPass123!')
            u.is_staff = False
            u.save()
            ventas_group = Group.objects.get(name='ventas')
            ventas_group.user_set.add(u)
            self.stdout.write(self.style.SUCCESS('Created demo user: demo_ventas / DemoPass123!'))
        else:
            self.stdout.write('demo_ventas already exists')

        # demo_stock user
        if not User.objects.filter(username='demo_stock').exists():
            u = User.objects.create_user('demo_stock', 'demo_stock@example.com', 'DemoPass123!')
            u.is_staff = False
            u.save()
            stock_group = Group.objects.get(name='stock')
            stock_group.user_set.add(u)
            self.stdout.write(self.style.SUCCESS('Created demo user: demo_stock / DemoPass123!'))
        else:
            self.stdout.write('demo_stock already exists')

        self.stdout.write(self.style.SUCCESS('Users created/verified.'))
