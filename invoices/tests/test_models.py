import pytest
from datetime import date, timedelta
from invoices.models import Customer, Invoice, LineItem, Payment


@pytest.mark.django_db
def test_invoice_total_sums_line_items():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        customer=customer, invoice_date="2026-09-01", due_date="2026-09-30"
    )
    LineItem.objects.create(
        invoice=invoice, description="Widget", unit_price="10.00", quantity=2
    )
    LineItem.objects.create(
        invoice=invoice, description="GAdget", unit_price="5.00", quantity=3
    )

    assert invoice.total == 35.00


@pytest.mark.django_db
def test_unmatched_payment():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    payment = Payment.objects.create(
        customer=customer, amount="100.00", payment_date="2026-09-01"
    )

    assert payment.invoice is None


@pytest.mark.django_db
def test_invoice_outstanding_amount():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        customer=customer, invoice_date="2026-09-01", due_date="2026-09-30"
    )
    LineItem.objects.create(
        invoice=invoice, description="Widget", unit_price="10.00", quantity=2
    )
    LineItem.objects.create(
        invoice=invoice, description="GAdget", unit_price="5.00", quantity=3
    )
    Payment.objects.create(
        customer=customer, invoice=invoice, amount="20.00", payment_date="2026-09-01"
    )

    assert invoice.outstanding_amount == 15

    Payment.objects.create(
        customer=customer, invoice=invoice, amount="15.00", payment_date="2026-09-01"
    )

    assert invoice.is_paid is True


@pytest.mark.django_db
def test_customer_balance():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(customer=customer, invoice_date="2026-09-01")
    LineItem.objects.create(
        invoice=invoice, description="Widget", unit_price="10.00", quantity=2
    )
    LineItem.objects.create(
        invoice=invoice, description="GAdget", unit_price="5.00", quantity=3
    )
    Payment.objects.create(
        customer=customer, invoice=invoice, amount="20.00", payment_date="2026-10-01"
    )

    assert customer.balance == 15.00

    Payment.objects.create(customer=customer, amount="20.00", payment_date="2026-10-01")

    assert customer.balance == -5.00


@pytest.mark.django_db
def test_invoice_is_paid():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(customer=customer, invoice_date="2026-09-01")
    LineItem.objects.create(
        invoice=invoice, description="Widget", unit_price="10.00", quantity=2
    )
    LineItem.objects.create(
        invoice=invoice, description="GAdget", unit_price="5.00", quantity=3
    )
    Payment.objects.create(
        customer=customer, invoice=invoice, amount="20.00", payment_date="2026-10-01"
    )

    assert invoice.is_paid is False


@pytest.mark.django_db
def test_invoice_is_overdue():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(customer=customer, invoice_date="2026-08-01")
    LineItem.objects.create(
        invoice=invoice, description="Widget", unit_price="10.00", quantity=2
    )
    LineItem.objects.create(
        invoice=invoice, description="GAdget", unit_price="5.00", quantity=3
    )

    assert invoice.is_overdue is False

    invoice2 = Invoice.objects.create(
        customer=customer,
        invoice_date="2026-08-01",
        due_date=date.today() - timedelta(days=5),
    )
    LineItem.objects.create(
        invoice=invoice2, description="Widget", unit_price="10.00", quantity=2
    )
    LineItem.objects.create(
        invoice=invoice2, description="GAdget", unit_price="5.00", quantity=3
    )

    assert invoice2.is_overdue is True
