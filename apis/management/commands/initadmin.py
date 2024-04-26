from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('reached here')

        User = get_user_model()

        email = "user@gmail.com"
        if not User.objects.filter(email=email).exists():
            print("let's go")
            username = 'alkatras'
            password = 'admin1'
            print('Creating account for %s (%s)' % (username, email))
            admin = User.objects.create_superuser(
                email=email, username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('User with email %s already exists' % email)
