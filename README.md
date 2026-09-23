# Invoice & Payments Management API
A REST API for managing invoices, customers, and payments. Built with Django, Django Rest Framework, and PostgreSQL, drawing on real invoicing workflows from my background in financial administration.

## Why/Motivation
During my time at my previous employer, through the daily exposure to SalesForce and SAP, processes like creating credit notes, partial payments, due dates, monthly closings, and many other aspects, have taught me how an invoice can have many different statuses, instead of just 'paid' or 'not paid'.

## Features
- Full CRUD for Customers, Invoices, Line Items
- Read access open to everyone, write access requires being authenticated.
- Token Authentication and Session Authentication
- Token-based login endpoint for obtaining an auth token

## Tech Stack
- Python
- PostgreSQL
- Django
- Django REST Framework

## Setup Instructions
1.	Clone the repository
2.	Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```
3.	Install dependencies:
```bash
pip install -r requirements.txt
```
4.	Create the Django project with virtual environment running
```bash
django-admin startproject invoiceproject .
```
5.	Create an app
```bash
python manage.py startapp invoices
```
6.	In settings.py, add the new file 'invoices' and 'rest_framework' under installed_apps
7.	Install PostgresSQL and set a password
8.	Open pgAdmin with the same password
9.	Create a database called 'invoicedb'
10.	Change ENGINE in DATABASES to 'django.db.backends.postgresql'
11.	Change NAME of database to 'invoicedb'
12.	Change USER to 'postgres'
13.	In the project root, create a file named .env
14.	Open .env in your editor
15.	Include your password in a line of code like the example -> 
```bash
DB_PASSWORD=<your_actual_password>
```
16.	Change PASSWORD in DATABASES to config('DB_PASSWORD')
17.	Change HOST to 'localhost'
18.	Change PORT to '5432'
19.	SAVE
20. Migrate in terminal
```bash
python manage.py migrate
```
21. Go to invoices/models.py
22. Create class Customer, Invoice, and LineItem:
```python
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.invoice_number

class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.description} ({self.invoice.invoice_number})"
```
23. SAVE
24. Migrate and create superuser in terminal:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
25. create a username and password for your superuser
26. register models in invoices/admin.py
```python
from django.contrib import admin
from .models import Customer, Invoice, LineItem

admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(LineItem)
```
27. SAVE
28. Create a file called serializers.py in the invoices folder
29. Open the invoices/serializers.py file and fill in the following code:
```python
from .models import Customer, Invoice, LineItem
from rest_framework import serializers

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'address']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'customer', 'invoice_date', 'due_date', 'status']

class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ['id', 'invoice', 'description', 'unit_price', 'quantity']
```
30. SAVE
31. Open invoices/views.py and include the following code:
```python
from rest_framework import viewsets
from .models import Customer, Invoice, LineItem
from .serializers import CustomerSerializer, InvoiceSerializer, LineItemSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer
```
32. SAVE
33. Open invoices/urls.py and include the following code:
```python
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, InvoiceViewSet, LineItemViewSet

router = DefaultRouter()

router.register('customers', CustomerViewSet)
router.register('invoices', InvoiceViewSet)
router.register('lineitems', LineItemViewSet)

urlpatterns = router.urls
```
34. SAVE
35. Open invoiceproject/urls.py and include the following code:
```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('invoices.urls')),
    path('api/token-auth/', obtain_auth_token)
]
```
36. SAVE
37. In invoiceproject/settings.py, find INSTALLED_APPS  and include 'rest_framework.authtoken' in the list.
38. SAVE
39. Migrate
```bash
python manage.py migrate
```
40. Add a REST_FRAMEWORK dictionary to invoiceproject/settings.py including the following:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication', 'rest_framework.authentication.TokenAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticatedOrReadOnly']
}
```
41. Restart (settings changes require a full server restart):
```bash
python manage.py runserver
```

The server should now be running at `http://127.0.0.1:8000/`. Visit `http://127.0.0.1:8000/admin/` to log in with your superuser account, or `http://127.0.0.1:8000/api/v1/customers/` to view the API directly.

## API Endpoints

All endpoints are prefixed with `/api/v1/`. Read access (GET) is open to everyone; write actions require a valid authentication token (see [Authentication](#authentication)).

| Method | Endpoint                  | Description                     |
|--------|----------------------------|----------------------------------|
| GET    | `/api/v1/customers/`       | List all customers              |
| POST   | `/api/v1/customers/`       | Create a new customer           |
| GET    | `/api/v1/customers/{id}/`  | Retrieve a specific customer    |
| PUT    | `/api/v1/customers/{id}/`  | Update a specific customer      |
| DELETE | `/api/v1/customers/{id}/`  | Delete a specific customer      |

The `invoices/` and `lineitems/` endpoints follow the same pattern (GET, POST, GET `/{id}/`, PUT `/{id}/`, DELETE `/{id}/`):

- `/api/v1/invoices/`
- `/api/v1/lineitems/`

| Method | Endpoint              | Description                          |
|--------|------------------------|---------------------------------------|
| POST   | `/api/token-auth/`     | Obtain an authentication token        |

## Authentication
Read access (GET) is open to everyone. All other actions — creating, editing, or deleting — require authentication via a token.

To obtain a token:

1. Install [Postman](https://www.postman.com/downloads/).
2. Create a new POST request to `http://127.0.0.1:8000/api/token-auth/`.
3. In the Body tab, select `x-www-form-urlencoded` and add two fields: `username` and `password`, using your superuser's credentials.
4. Make sure your Django server is running, then click Send. You'll receive a response like:
```json
   {"token": "abc123..."}
```

To use the token, include it in the `Authorization` header of any request:

```
Authorization: Token abc123...
```