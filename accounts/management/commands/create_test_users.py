from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test users for the Procure-to-Pay system'

    def handle(self, *args, **options):
        self.stdout.write('Creating test users...')

        test_users = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'staff1',
                'email': 'staff@example.com',
                'password': 'staff123',
                'first_name': 'John',
                'last_name': 'Staff',
                'role': 'staff',
            },
            {
                'username': 'approver1',
                'email': 'approver1@example.com',
                'password': 'approver123',
                'first_name': 'Jane',
                'last_name': 'Approver',
                'role': 'approver1',
            },
            {
                'username': 'approver2',
                'email': 'approver2@example.com',
                'password': 'approver123',
                'first_name': 'Bob',
                'last_name': 'Senior',
                'role': 'approver2',
            },
            {
                'username': 'finance1',
                'email': 'finance@example.com',
                'password': 'finance123',
                'first_name': 'Alice',
                'last_name': 'Finance',
                'role': 'finance',
            },
        ]

        with transaction.atomic():
            for user_data in test_users:
                username = user_data['username']
                if User.objects.filter(username=username).exists():
                    self.stdout.write(f'User {username} already exists, skipping...')
                    continue

                user = User.objects.create_user(**user_data)
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {username} ({user.get_role_display()})')
                )

        self.stdout.write(self.style.SUCCESS('Test users creation completed!'))

        # Display login credentials
        self.stdout.write('\n' + '='*50)
        self.stdout.write('LOGIN CREDENTIALS:')
        self.stdout.write('='*50)
        for user_data in test_users:
            self.stdout.write(f"{user_data['username']}: {user_data['password']} ({user_data['role']})")
        self.stdout.write('='*50)