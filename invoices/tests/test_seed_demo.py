import pytest
from datetime import date
from decimal import Decimal
from invoices.models import Customer, Invoice, LineItem, Payment
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()


@pytest.mark.django_db
def test_seed_demo_creates_data_only_once():
    call_command("seed_demo")
    call_command("seed_demo")

    assert User.objects.filter(username="demo").count() == 1
    assert Customer.objects.count() == 3
    assert Customer.objects.filter(owner__username="demo").count() == 3
    assert Invoice.objects.count() == 4
    assert LineItem.objects.count() == 7
    assert Payment.objects.count() == 3


@pytest.mark.django_db
def test_seed_demo_covers_the_main_invoice_cases():
    call_command("seed_demo")

    invoices = list(Invoice.objects.all())
    assert sum(1 for invoice in invoices if invoice.is_paid) == 1
    assert sum(1 for invoice in invoices if invoice.is_overdue) == 1

    partly_paid = Invoice.objects.get(
        customer__name="Northwind Traders", due_date__gt=date.today()
    )
    assert partly_paid.outstanding_amount == Decimal("550.00")

    draft = Invoice.objects.get(status="draft")
    assert draft.due_date is None
