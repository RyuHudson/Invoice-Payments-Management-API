from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from invoices.models import Customer, Invoice, LineItem, Payment

User = get_user_model()

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo12345"


class Command(BaseCommand):
    help = "Create demo data (a demo user, customers, invoices and payments)"

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Get or create the demo user
        user, created = User.objects.get_or_create(username=DEMO_USERNAME)
        if created:
            user.set_password(DEMO_PASSWORD)  # stores a hash, not plain text
            user.save()

        # 2. Stop if demo data already exists
        if Customer.objects.filter(owner=user).exists():
            self.stdout.write("Demo data already exists. Nothing to do.")
            return

        today = date.today()

        # 3. Customers
        northwind = Customer.objects.create(
            owner=user,
            name="Northwind Traders",
            email="billing@northwind.example",
            address="12 Canal Street, Amsterdam",
        )
        bluebird = Customer.objects.create(
            owner=user,
            name="Bluebird Bakery",
            email="hello@bluebird.example",
            address="3 Market Square, Haarlem",
        )
        harbor = Customer.objects.create(
            owner=user,
            name="Harbor Consulting",
            email="accounts@harbor.example",
            address="88 Dock Road, Rotterdam",
        )

        # 4. Invoices with line items
        paid_invoice = self.create_invoice(
            northwind,
            invoice_date=today - timedelta(days=45),
            due_date=today - timedelta(days=15),
            status="sent",
            items=[
                ("Website design", "1200.00", 1),
                ("Hosting (12 months)", "240.00", 1),
            ],
        )
        partly_paid_invoice = self.create_invoice(
            northwind,
            invoice_date=today - timedelta(days=20),
            due_date=today + timedelta(days=10),
            status="sent",
            items=[("Consulting hours", "95.00", 10)],
        )
        self.create_invoice(  # overdue: due date passed and nothing paid
            bluebird,
            invoice_date=today - timedelta(days=60),
            due_date=today - timedelta(days=30),
            status="sent",
            items=[
                ("Catering, morning event", "650.00", 1),
                ("Delivery", "25.00", 2),
            ],
        )
        self.create_invoice(  # draft: no due date yet
            harbor,
            invoice_date=today,
            due_date=None,
            status="draft",
            items=[
                ("Strategy workshop", "1800.00", 1),
                ("Workshop materials", "30.00", 5),
            ],
        )

        # 5. Payments
        Payment.objects.create(  # pays the first invoice in full
            customer=northwind,
            invoice=paid_invoice,
            amount=Decimal("1440.00"),
            payment_date=today - timedelta(days=10),
        )
        Payment.objects.create(  # partial payment
            customer=northwind,
            invoice=partly_paid_invoice,
            amount=Decimal("400.00"),
            payment_date=today - timedelta(days=3),
        )
        Payment.objects.create(  # advance payment, not linked to an invoice
            customer=bluebird,
            invoice=None,
            amount=Decimal("100.00"),
            payment_date=today,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data created. Log in as '{DEMO_USERNAME}' "
                f"with password '{DEMO_PASSWORD}'."
            )
        )

    def create_invoice(self, customer, invoice_date, due_date, status, items):
        invoice = Invoice.objects.create(
            customer=customer,
            invoice_date=invoice_date,
            due_date=due_date,
            status=status,
        )
        for description, unit_price, quantity in items:
            LineItem.objects.create(
                invoice=invoice,
                description=description,
                unit_price=Decimal(unit_price),
                quantity=quantity,
            )
        return invoice
