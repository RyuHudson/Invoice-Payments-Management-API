import pytest
from datetime import date
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from invoices.models import Customer, Invoice, LineItem, Payment
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_list_customers_returns_200(auth_client):
    response = auth_client.get("/api/v1/customers/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_invoices_returns_200(auth_client):
    response = auth_client.get("/api/v1/invoices/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_lineitems_returns_200(auth_client):
    response = auth_client.get("/api/v1/lineitems/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_payments_returns_200(auth_client):
    response = auth_client.get("/api/v1/payments/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_customer_with_valid_auth_succeeds():
    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/v1/customers/", {"name": "Acme Corp", "email": "acmecorp@gmail.com"}
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_customer_without_auth_is_rejected():
    client = APIClient()
    response = client.post(
        "/api/v1/customers/",
        {"name": "Margiella Corp", "email": "margiellacorp@gmail.com"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_invoice_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.post(
        "/api/v1/invoices/",
        {
            "invoice_number": "3",
            "customer_id": customer.id,
            "invoice_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_invoice_without_auth_is_rejected():
    client = APIClient()
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    response = client.post(
        "/api/v1/invoices/",
        {"invoice_number": "3", "customer_id": customer, "invoice_date": date.today()},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_lineitem_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    response = auth_client.post(
        "/api/v1/lineitems/",
        {
            "invoice": invoice.id,
            "description": "widget",
            "unit_price": "12.00",
            "quantity": "1",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_lineitem_without_auth_is_rejected():
    client = APIClient()
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    response = client.post(
        "/api/v1/lineitems/",
        {"invoice": invoice, "unit_price": "12.00", "quantity": "1"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_payment_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )

    response = auth_client.post(
        "/api/v1/payments/",
        {
            "customer_id": customer.id,
            "invoice": invoice.id,
            "amount": "15.00",
            "payment_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_payment_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    client = APIClient()
    response = client.post(
        "/api/v1/payments/",
        {
            "customer": customer.id,
            "invoice": invoice.id,
            "amount": "15.00",
            "payment_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_customer_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.patch(
        f"/api/v1/customers/{customer.id}/",
        {"name": "acne man", "email": "acneman@gmail.com"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_patch_customer_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    client = APIClient()
    response = client.patch(
        f"/api/v1/customers/{customer.id}/",
        {"name": "acne man", "email": "acneman@gmail.com"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_invoice_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    customer2 = Customer.objects.create(
        name="Mischelin Corp", email="mischelincorp@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )

    response = auth_client.patch(
        f"/api/v1/invoices/{invoice.id}/",
        {
            "invoice_number": "4",
            "customer_id": customer2.id,
            "invoice_date": "2026-09-29",
        },
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_patch_invoice_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    customer2 = Customer.objects.create(
        name="Mischelin Corp", email="mischelincorp@example.com"
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    client = APIClient()
    response = client.patch(
        f"/api/v1/invoices/{invoice.id}/",
        {
            "invoice_number": "4",
            "customer_id": customer2.id,
            "invoice_date": "2026-09-29",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_lineitem_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    customer2 = Customer.objects.create(
        name="Mischelin Corp", email="mischelincorp@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice2 = Invoice.objects.create(
        invoice_number="4", customer_id=customer2.id, invoice_date="2026-09-29"
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )

    response = auth_client.patch(
        f"/api/v1/lineitems/{line_item.id}/",
        {"invoice": invoice2.id, "unit_price": "20.00", "quantity": "1"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_patch_lineitem_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    customer2 = Customer.objects.create(
        name="Mischelin Corp", email="mischelincorp@example.com"
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice2 = Invoice.objects.create(
        invoice_number="4", customer_id=customer2.id, invoice_date="2026-09-29"
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )

    client = APIClient()
    response = client.patch(
        f"/api/v1/lineitems/{line_item.id}/",
        {"invoice": invoice2.id, "unit_price": "20.00", "quantity": "1"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_patch_payment_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    payment = Payment.objects.create(
        customer_id=customer.id,
        invoice_id=invoice.id,
        amount="120.00",
        payment_date=date.today(),
    )

    response = auth_client.patch(
        f"/api/v1/payments/{payment.id}/", {"amount": "120.00"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_patch_payment_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    payment = Payment.objects.create(
        customer_id=customer.id,
        invoice_id=invoice.id,
        amount="120.00",
        payment_date=date.today(),
    )
    client = APIClient()
    response = client.patch(f"/api/v1/payments/{payment.id}/", {"amount": "120.00"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_customer_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.put(
        f"/api/v1/customers/{customer.id}/",
        {"name": "Bonny Corp", "email": "bonny@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_put_customer_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    client = APIClient()
    response = client.put(
        f"/api/v1/customers/{customer.id}/",
        {"name": "Bonny", "email": "bonny@gmail.com"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_invoice_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )

    response = auth_client.put(
        f"/api/v1/invoices/{invoice.id}/",
        {
            "invoice_number": "4",
            "customer_id": customer.id,
            "invoice_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_put_invoice_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    client = APIClient()
    response = client.put(
        f"/api/v1/invoices/{invoice.id}/",
        {"customer_id": customer.id, "name": "acne man", "email": "acneman@gmail.com"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_lineitem_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    customer2 = Customer.objects.create(
        name="Mischelin Corp", email="mischelincorp@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice2 = Invoice.objects.create(
        invoice_number="4", customer_id=customer2.id, invoice_date="2026-09-29"
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )

    response = auth_client.put(
        f"/api/v1/lineitems/{line_item.id}/",
        {
            "invoice": invoice2.id,
            "description": "widget",
            "unit_price": "20.00",
            "quantity": "3",
        },
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_put_lineitem_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    customer2 = Customer.objects.create(
        name="Mischelin Corp", email="mischelincorp@example.com"
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice2 = Invoice.objects.create(
        invoice_number="4", customer_id=customer2.id, invoice_date="2026-09-29"
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )

    client = APIClient()
    response = client.put(
        f"/api/v1/lineitems/{line_item.id}/",
        {
            "invoice": invoice2.id,
            "description": "widget",
            "unit_price": "20.00",
            "quantity": "3",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_put_payment_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    payment = Payment.objects.create(
        customer_id=customer.id,
        invoice_id=invoice.id,
        amount="120.00",
        payment_date=date.today(),
    )

    response = auth_client.put(
        f"/api/v1/payments/{payment.id}/",
        {
            "invoice_id": invoice.id,
            "customer_id": customer.id,
            "amount": "110",
            "payment_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_put_payment_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    payment = Payment.objects.create(
        customer_id=customer.id,
        invoice_id=invoice.id,
        amount="120.00",
        payment_date=date.today(),
    )
    client = APIClient()
    response = client.put(
        f"/api/v1/payments/{payment.id}/",
        {
            "invoice_id": invoice.id,
            "customer_id": customer.id,
            "amount": "110",
            "payment_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_customer_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.delete(f"/api/v1/customers/{customer.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_customer_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    client = APIClient()
    response = client.delete(f"/api/v1/customers/{customer.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Customer.objects.filter(id=customer.id).exists()


@pytest.mark.django_db
def test_delete_invoice_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )

    response = auth_client.delete(f"/api/v1/invoices/{invoice.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_invoice_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    client = APIClient()
    response = client.delete(f"/api/v1/invoices/{invoice.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Invoice.objects.filter(id=invoice.id).exists()


@pytest.mark.django_db
def test_delete_lineitem_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )

    response = auth_client.delete(f"/api/v1/lineitems/{line_item.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_lineitem_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )
    client = APIClient()
    response = client.delete(f"/api/v1/lineitems/{line_item.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert LineItem.objects.filter(id=line_item.id).exists()


@pytest.mark.django_db
def test_delete_payment_with_valid_auth_succeeds(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    payment = Payment.objects.create(
        customer_id=customer.id, amount="120.00", payment_date=date.today()
    )

    response = auth_client.delete(f"/api/v1/payments/{payment.id}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_payment_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    payment = Payment.objects.create(
        customer_id=customer.id, amount="120.00", payment_date=date.today()
    )
    client = APIClient()
    response = client.delete(f"/api/v1/payments/{payment.id}/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Payment.objects.filter(id=payment.id).exists()


@pytest.mark.django_db
def test_delete_customer_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    customer_id = customer.id
    customer.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/v1/customers/{customer_id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_customer_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    customer_id = customer.id
    customer.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/v1/customers/{customer_id}/",
        {"name": "acne Corp", "email": "acne@example.com"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_put_customer_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    customer_id = customer.id
    customer.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        f"/api/v1/customers/{customer_id}/",
        {"name": "Acne Corp", "email": "acne@example.com"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_invoice_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice_id = invoice.id
    invoice.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/v1/invoices/{invoice_id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_invoice_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice_id = invoice.id
    invoice.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f"/api/v1/invoices/{invoice_id}/", {"invoice_number": "4"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_put_invoice_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    invoice_id = invoice.id
    invoice.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        f"/api/v1/invoices/{invoice_id}/",
        {
            "invoice_number": "4",
            "customer_id": customer.id,
            "invoice_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_lineitem_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )
    line_item_id = line_item.id
    line_item.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/v1/lineitems/{line_item_id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_lineitem_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )
    line_item_id = line_item.id
    line_item.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f"/api/v1/lineitems/{line_item_id}/", {"quantity": "5"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_put_lineitem_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    line_item = LineItem.objects.create(
        invoice_id=invoice.id, unit_price="15.00", quantity="2"
    )
    line_item_id = line_item.id
    line_item.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        f"/api/v1/lineitems/{line_item_id}/",
        {
            "invoice": invoice.id,
            "description": "widget",
            "unit_price": "20.00",
            "quantity": "3",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_payment_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    payment = Payment.objects.create(
        customer_id=customer.id, amount="120.00", payment_date=date.today()
    )
    payment_id = payment.id
    payment.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f"/api/v1/payments/{payment_id}/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch_payment_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    payment = Payment.objects.create(
        customer_id=customer.id, amount="120.00", payment_date=date.today()
    )
    payment_id = payment.id
    payment.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f"/api/v1/payments/{payment_id}/", {"amount": "150.00"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_put_payment_nonexistent_id_returns_404():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="3", customer_id=customer.id, invoice_date=date.today()
    )
    payment = Payment.objects.create(
        customer_id=customer.id,
        invoice_id=invoice.id,
        amount="120.00",
        payment_date=date.today(),
    )
    payment_id = payment.id
    payment.delete()

    user = User.objects.create_user(username="Gigi_Buffon", password="testpass123")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        f"/api/v1/payments/{payment_id}/",
        {
            "invoice_id": invoice.id,
            "customer_id": customer.id,
            "amount": "110",
            "payment_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_token_auth_with_valid_credentials_returns_token():
    User.objects.create_user(username="Gigi Buffon", password="testpass123")
    client = APIClient()

    response = client.post(
        "/api/token-auth/", {"username": "Gigi Buffon", "password": "testpass123"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data


@pytest.mark.django_db
def test_token_auth_without_valid_credentials_returns_no_token():
    User.objects.create_user(username="Gigi Buffon", password="testpass123")
    client = APIClient()

    response = client.post(
        "/api/token-auth/", {"username": "Gigi Buffon", "password": "testpass456"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" not in response.data


@pytest.mark.django_db
def test_list_customers_returns_created_customers(auth_client):
    Customer.objects.create(name="Acme Corp", email="acme@example.com")
    Customer.objects.create(name="Mischelin Corp", email="mischelincorp@example.com")

    response = auth_client.get("/api/v1/customers/")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_list_invoices_returns_created_invoices(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    Invoice.objects.create(
        invoice_number="1", customer_id=customer.id, invoice_date=date.today()
    )
    Invoice.objects.create(
        invoice_number="2", customer_id=customer.id, invoice_date=date.today()
    )

    response = auth_client.get("/api/v1/invoices/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    invoice_numbers = [invoice["invoice_number"] for invoice in response.data]
    assert "1" in invoice_numbers
    assert "2" in invoice_numbers


@pytest.mark.django_db
def test_list_lineitems_returns_created_lineitems(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="1", customer_id=customer.id, invoice_date=date.today()
    )
    LineItem.objects.create(
        invoice_id=invoice.id, description="widget", unit_price="10.00", quantity="1"
    )
    LineItem.objects.create(
        invoice_id=invoice.id, description="gadget", unit_price="20.00", quantity="2"
    )

    response = auth_client.get("/api/v1/lineitems/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    descriptions = [item["description"] for item in response.data]
    assert "widget" in descriptions
    assert "gadget" in descriptions


@pytest.mark.django_db
def test_list_payments_returns_created_payments(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    Payment.objects.create(
        customer_id=customer.id, amount="50.00", payment_date=date.today()
    )
    Payment.objects.create(
        customer_id=customer.id, amount="75.00", payment_date=date.today()
    )

    response = auth_client.get("/api/v1/payments/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    amounts = [payment["amount"] for payment in response.data]
    assert "50.00" in amounts
    assert "75.00" in amounts


@pytest.mark.django_db
def test_get_invoice_pdf_authorized_returns_200(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        invoice_number="1", customer_id=customer.id, invoice_date=date.today()
    )

    response = auth_client.get(
        f"http://127.0.0.1:8000/api/v1/invoices/{invoice.id}/pdf/"
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_missing_invoice_pdf_authorized_returns_404():
    user = User.objects.create(username="Gigi Buffon", password="testpass123")
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    Invoice.objects.create(
        invoice_number="1", customer_id=customer.id, invoice_date=date.today()
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("http://127.0.0.1:8000/api/v1/invoices/10/pdf/")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_invoice_pdf_unauthorized_returns_401():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        invoice_number="1", customer_id=customer.id, invoice_date=date.today()
    )
    client = APIClient()

    response = client.get(f"http://127.0.0.1:8000/api/v1/invoices/{invoice.id}/pdf/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_summary_returns_correct_totals(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )
    invoice = Invoice.objects.create(
        customer_id=customer.id, invoice_date=date.today(), status="draft"
    )
    invoice2 = Invoice.objects.create(
        customer_id=customer.id, invoice_date=date.today(), status="sent"
    )
    LineItem.objects.create(invoice=invoice, unit_price="100.00", quantity=1)
    LineItem.objects.create(invoice=invoice2, unit_price="50.00", quantity=1)
    Payment.objects.create(
        invoice=invoice,
        customer_id=customer.id,
        amount="20.00",
        payment_date=date.today(),
    )
    Payment.objects.create(
        invoice=invoice,
        customer_id=customer.id,
        amount="10.00",
        payment_date=date.today(),
    )

    response = auth_client.get("/api/v1/invoices/summary/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["invoice_count"] == 2
    assert response.data["total_invoiced"] == Decimal("150.00")
    assert response.data["total_paid"] == Decimal("30.00")
    assert response.data["total_outstanding"] == Decimal("120.00")
    assert response.data["by_status"] == {"draft": 1, "sent": 1}


@pytest.mark.django_db
def test_empty_database():
    user = User.objects.create(username="Gigi Buffon", password="testpass123")

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/v1/invoices/summary/")

    assert response.data["total_invoiced"] == Decimal("0.00")
    assert response.data["total_paid"] == Decimal("0.00")
    assert response.data["total_outstanding"] == Decimal("0.00")
    assert response.data["by_status"] == {}


@pytest.mark.django_db
def test_unauthorized_get_summary_returns_401():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(
        customer_id=customer.id, invoice_date=date.today(), status="draft"
    )
    invoice2 = Invoice.objects.create(
        customer_id=customer.id, invoice_date=date.today(), status="sent"
    )
    LineItem.objects.create(invoice=invoice, unit_price="100.00", quantity=1)
    LineItem.objects.create(invoice=invoice2, unit_price="50.00", quantity=1)
    Payment.objects.create(
        invoice=invoice,
        customer_id=customer.id,
        amount="20.00",
        payment_date=date.today(),
    )
    Payment.objects.create(
        invoice=invoice,
        customer_id=customer.id,
        amount="10.00",
        payment_date=date.today(),
    )

    client = APIClient()

    response = client.get("/api/v1/invoices/summary/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_customer_of_own_user_returns_200(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.get(f"/api/v1/customers/{customer.id}/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_customer_of_other_user_returns_404(auth_client):
    user2 = User.objects.create_user(username="testuser", password="testpass123")
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user2
    )

    response = auth_client.get(f"/api/v1/customers/{customer.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_of_customer_creates_invoice_returns_201(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.post(
        "/api/v1/invoices/",
        {
            "customer_id": customer.id,
            "invoice_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_user_of_other_customer_creates_invoice_returns_400(user, other_user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    client = APIClient()
    client.force_authenticate(user=other_user)

    response = client.post(
        "/api/v1/invoices/",
        {
            "customer_id": customer.id,
            "invoice_date": date.today(),
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_payment_without_invoice_returns_201(auth_client, user):
    customer = Customer.objects.create(
        name="Acme Corp", email="acme@example.com", owner=user
    )

    response = auth_client.post(
        "/api/v1/payments/",
        {
            "customer_id": customer.id,
            "invoice_id": None,
            "amount": "50.00",
            "payment_date": date.today(),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_payment_for_other_users_invoice_returns_400(auth_client, user, other_user):
    my_customer = Customer.objects.create(
        name="Mine", email="mine@example.com", owner=user
    )
    other_customer = Customer.objects.create(
        name="Theirs", email="theirs@example.com", owner=other_user
    )
    other_invoice = Invoice.objects.create(
        customer=other_customer, invoice_date=date.today()
    )

    response = auth_client.post(
        "/api/v1/payments/",
        {
            "customer_id": my_customer.id,
            "invoice_id": other_invoice.id,
            "amount": "50.00",
            "payment_date": date.today(),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_payment_for_other_users_customer_returns_400(auth_client, other_user):
    other_customer = Customer.objects.create(
        name="Theirs", email="theirs@example.com", owner=other_user
    )

    response = auth_client.post(
        "/api/v1/payments/",
        {
            "customer_id": other_customer.id,
            "invoice_id": None,
            "amount": "50.00",
            "payment_date": date.today(),
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_line_item_for_other_users_invoice_returns_400(auth_client, other_user):
    other_customer = Customer.objects.create(
        name="Theirs", email="theirs@example.com", owner=other_user
    )
    other_invoice = Invoice.objects.create(
        customer=other_customer, invoice_date=date.today()
    )

    response = auth_client.post(
        "/api/v1/lineitems/",
        {
            "invoice": other_invoice.id,
            "description": "Consulting",
            "quantity": 1,
            "unit_price": "100.00",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
