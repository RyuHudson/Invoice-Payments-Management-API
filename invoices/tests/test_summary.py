from datetime import date
import pytest
from invoices.models import Customer, Invoice
from rest_framework import status

URL = "/api/v1/invoices/summary/"


@pytest.fixture
def invoices_in_two_periods(user):
    customer = Customer.objects.create(owner=user, name="Acme")
    Invoice.objects.create(customer=customer, invoice_date=date(2026, 1, 15))
    Invoice.objects.create(customer=customer, invoice_date=date(2026, 6, 15))


@pytest.mark.django_db
def test_summary_filters_by_date_range(auth_client, invoices_in_two_periods):
    response = auth_client.get(
        URL, {"date_from": "2026-01-01", "date_to": "2026-03-31"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["invoice_count"] == 1


@pytest.mark.django_db
def test_summary_without_dates_counts_everything(auth_client, invoices_in_two_periods):
    response = auth_client.get(URL)

    assert response.data["invoice_count"] == 2


@pytest.mark.django_db
def test_summary_rejects_invalid_date(auth_client):
    response = auth_client.get(URL, {"date_from": "hello"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "date_from" in response.data
