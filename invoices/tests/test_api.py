import pytest
from datetime import date
from rest_framework.test import APIClient
from rest_framework import status
from invoices.models import Customer, Invoice, LineItem, Payment
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_list_customers_returns_200():
    client = APIClient()
    response = client.get('/api/v1/customers/')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_list_invoices_returns_200():
    client = APIClient()
    response = client.get('/api/v1/invoices/')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_list_lineitems_returns_200():
    client = APIClient()
    response = client.get('/api/v1/lineitems/')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_list_payments_returns_200():
    client = APIClient()
    response = client.get('/api/v1/payments/')
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_create_customer_with_valid_auth_succeeds():
    user = User.objects.create_user(username='Gigi_Buffon', password='testpass123')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/v1/customers/', {'name': 'Acme Corp', 'email': 'acmecorp@gmail.com'})

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_customer_without_auth_is_rejected():
    client = APIClient()
    response = client.post('/api/v1/customers/', {'name': 'Margiella Corp', 'email': 'margiellacorp@gmail.com'})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_invoice_with_valid_auth_succeeds():
    user = User.objects.create_user(username='Gigi_Buffon', password='testpass123')
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/v1/invoices/', {'invoice_number': '3', 'customer_id': customer.id, 'invoice_date': date.today()})

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_invoice_without_auth_is_rejected():
    client = APIClient()
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    response = client.post('/api/v1/invoices/', {'invoice_number': '3', 'customer_id': customer, 'invoice_date': date.today()})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_lineitem_with_valid_auth_succeeds():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(invoice_number='3', customer_id= customer.id, invoice_date= date.today())
    user = User.objects.create_user(username='Gigi_Buffon', password='testpass123')

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/v1/lineitems/', {'invoice': invoice.id, 'description': 'widget','unit_price': '12.00', 'quantity': '1'})

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_lineitem_without_auth_is_rejected():
    client = APIClient()
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(invoice_number='3', customer_id= customer.id, invoice_date= date.today())
    response = client.post('/api/v1/lineitems/', {'invoice': invoice, 'unit_price': '12.00', 'quantity': '1'})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_create_payment_with_valid_auth_succeeds():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(invoice_number='3', customer_id= customer.id, invoice_date= date.today())
    user = User.objects.create_user(username='Gigi_Buffon', password='testpass123')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/v1/payments/', {'customer_id': customer.id, 'invoice': invoice.id, 'amount': '15.00', 'payment_date': date.today()})

    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_payment_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    invoice = Invoice.objects.create(invoice_number='3', customer_id= customer.id, invoice_date= date.today())
    client = APIClient()
    response = client.post('/api/v1/payments/', {'customer': customer.id, 'invoice': invoice.id, 'amount': '15.00', 'payment_date': date.today()})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_patch_customer_with_valid_auth_succeeds():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    user = User.objects.create_user(username='Gigi_Buffon', password='testpass123')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(f'/api/v1/customers/{customer.id}/', {'name': 'acne man', 'email': 'acneman@gmail.com'})

    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_patch_customer_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    client = APIClient()
    response = client.patch(f'/api/v1/customers/{customer.id}/', {'name': 'acne man', 'email': 'acneman@gmail.com'})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_delete_customer_with_valid_auth_succeeds():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")   
    user = User.objects.create_user(username='Gigi_Buffon', password='testpass123')
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(f'/api/v1/customers/{customer.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_delete_customer_without_auth_is_rejected():
    customer = Customer.objects.create(name="Acme Corp", email="acme@example.com")
    client = APIClient()
    response = client.delete(f'/api/v1/customers/{customer.id}/')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED 
    assert Customer.objects.filter(id=customer.id).exists()