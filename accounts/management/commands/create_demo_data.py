from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from requests.models import PurchaseRequest, Approval, RequestItem
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for the Procure-to-Pay system'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        # Get existing users
        try:
            staff_user = User.objects.get(username='staff1')
            approver1 = User.objects.get(username='approver1')
            approver2 = User.objects.get(username='approver2')
            finance_user = User.objects.get(username='finance1')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test users not found. Run create_test_users first.'))
            return

        # Sample vendors and items
        vendors = [
            'TechCorp Solutions', 'Office Supplies Inc', 'Global Electronics',
            'Business Services Ltd', 'Digital Solutions', 'Professional Services'
        ]

        categories = ['office_supplies', 'software', 'hardware', 'services', 'equipment']
        urgencies = ['low', 'normal', 'high', 'critical']

        items_data = [
            {'name': 'Laptop Computer', 'price': Decimal('1200.00')},
            {'name': 'Office Chair', 'price': Decimal('250.00')},
            {'name': 'Printer Paper (500 sheets)', 'price': Decimal('45.00')},
            {'name': 'Software License', 'price': Decimal('299.99')},
            {'name': 'Projector', 'price': Decimal('800.00')},
            {'name': 'Conference Table', 'price': Decimal('1500.00')},
            {'name': 'Whiteboard', 'price': Decimal('120.00')},
            {'name': 'Coffee Machine', 'price': Decimal('350.00')},
            {'name': 'External Hard Drive', 'price': Decimal('89.99')},
            {'name': 'Wireless Router', 'price': Decimal('75.00')},
        ]

        # Create demo purchase requests with different statuses
        demo_requests = [
            {
                'title': 'Office Equipment Purchase',
                'description': 'New laptops and office chairs for the development team',
                'amount': Decimal('2900.00'),
                'quantity': 2,
                'department': 'IT',
                'vendor_name': vendors[0],
                'category': 'hardware',
                'urgency': 'high',
                'status': 'approved',
                'items': [items_data[0], items_data[1]],  # Laptop + Chair
            },
            {
                'title': 'Software Licenses',
                'description': 'Annual software licenses for design tools',
                'amount': Decimal('899.97'),
                'quantity': 3,
                'department': 'Design',
                'vendor_name': vendors[4],
                'category': 'software',
                'urgency': 'normal',
                'status': 'approved',
                'items': [items_data[3], items_data[3], items_data[3]],  # 3 Software licenses
            },
            {
                'title': 'Conference Room Setup',
                'description': 'Equipment for the new conference room',
                'amount': Decimal('2420.00'),
                'quantity': 3,
                'department': 'Facilities',
                'vendor_name': vendors[1],
                'category': 'equipment',
                'urgency': 'high',
                'status': 'pending_l1',
                'items': [items_data[4], items_data[5], items_data[6]],  # Projector + Table + Whiteboard
            },
            {
                'title': 'IT Infrastructure',
                'description': 'Network equipment and storage devices',
                'amount': Decimal('164.99'),
                'quantity': 2,
                'department': 'IT',
                'vendor_name': vendors[2],
                'category': 'hardware',
                'urgency': 'normal',
                'status': 'approved',
                'items': [items_data[8], items_data[9]],  # Hard drive + Router
            },
            {
                'title': 'Office Supplies',
                'description': 'Monthly office supplies and coffee machine',
                'amount': Decimal('395.00'),
                'quantity': 2,
                'department': 'Admin',
                'vendor_name': vendors[1],
                'category': 'office_supplies',
                'urgency': 'low',
                'status': 'rejected_l1',
                'items': [items_data[2], items_data[7]],  # Paper + Coffee machine
            },
            {
                'title': 'Consulting Services',
                'description': 'External consulting for system optimization',
                'amount': Decimal('2500.00'),
                'quantity': 5,
                'department': 'IT',
                'vendor_name': vendors[5],
                'category': 'services',
                'urgency': 'high',
                'status': 'pending_l1',
                'items': [{'name': 'Consulting Services (per day)', 'price': Decimal('500.00'), 'quantity': 5}],
            }
        ]

        created_requests = []

        for req_data in demo_requests:
            # Create purchase request
            request = PurchaseRequest.objects.create(
                title=req_data['title'],
                description=req_data['description'],
                amount=req_data['amount'],
                quantity=req_data['quantity'],
                department=req_data['department'],
                vendor_name=req_data['vendor_name'],
                category=req_data['category'],
                urgency=req_data['urgency'],
                status=req_data['status'],
                created_by=staff_user,
                created_at=timezone.now() - timezone.timedelta(days=random.randint(1, 30))
            )

            # Create request items
            for item_data in req_data['items']:
                quantity = item_data.get('quantity', 1)
                RequestItem.objects.create(
                    purchase_request=request,
                    item_name=item_data['name'],
                    price=item_data['price'],
                    quantity=quantity
                )

            # Create approvals based on status
            if req_data['status'] in ['approved', 'rejected']:
                # Level 1 approval
                Approval.objects.create(
                    purchase_request=request,
                    approver=approver1,
                    level=1,
                    status='approved' if req_data['status'] != 'rejected' else 'rejected',
                    comment='Approved for procurement' if req_data['status'] != 'rejected' else 'Budget constraints',
                    date=request.created_at + timezone.timedelta(hours=2)
                )

                if req_data['status'] == 'approved':
                    # Level 2 approval
                    Approval.objects.create(
                        purchase_request=request,
                        approver=approver2,
                        level=2,
                        status='approved',
                        comment='Final approval granted',
                        date=request.created_at + timezone.timedelta(hours=4)
                    )

                    # Note: approved_by field was removed from the model

            created_requests.append(request)
            self.stdout.write(f'Created request: {request.title} ({request.status})')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(created_requests)} demo purchase requests with items and approvals!'))

        # Summary
        total_requests = PurchaseRequest.objects.count()
        approved_requests = PurchaseRequest.objects.filter(status='approved').count()
        pending_requests = PurchaseRequest.objects.filter(status='pending').count()
        rejected_requests = PurchaseRequest.objects.filter(status='rejected').count()

        self.stdout.write('\n' + '='*50)
        self.stdout.write('DEMO DATA SUMMARY:')
        self.stdout.write('='*50)
        self.stdout.write(f'Total Requests: {total_requests}')
        self.stdout.write(f'Approved: {approved_requests}')
        self.stdout.write(f'Pending: {pending_requests}')
        self.stdout.write(f'Rejected: {rejected_requests}')
        self.stdout.write('='*50)