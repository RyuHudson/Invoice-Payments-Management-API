from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Customer, Invoice, LineItem, Payment
from .serializers import (
    CustomerSerializer,
    InvoiceSerializer,
    LineItemSerializer,
    PaymentSerializer,
)


# Create your views here.
@extend_schema_view(
    list=extend_schema(summary="List all customers", tags=["Customers"]),
    create=extend_schema(summary="Create a new customer", tags=["Customers"]),
    retrieve=extend_schema(summary="Retrieve an customer", tags=["Customers"]),
    update=extend_schema(summary="Update a customer", tags=["Customers"]),
    partial_update=extend_schema(
        summary="Partially update a customer", tags=["Customers"]
    ),
    destroy=extend_schema(summary="Deleta a customer", tags=["Customers"]),
)
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


@extend_schema_view(
    list=extend_schema(summary="List all invoices", tags=["Invoices"]),
    create=extend_schema(summary="Create a new invoice", tags=["Invoices"]),
    retrieve=extend_schema(summary="Retrieve an invoice", tags=["Invoices"]),
    update=extend_schema(summary="Update a invoice", tags=["Invoices"]),
    partial_update=extend_schema(
        summary="Partially update a invoice", tags=["Invoices"]
    ),
    destroy=extend_schema(summary="Deleta a invoice", tags=["Invoices"]),
)
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


@extend_schema_view(
    list=extend_schema(summary="List all lineitems", tags=["Line Items"]),
    create=extend_schema(summary="Create a new lineitems", tags=["Line Items"]),
    retrieve=extend_schema(summary="Retrieve an lineitems", tags=["Line Items"]),
    update=extend_schema(summary="Update a lineitems", tags=["Line Items"]),
    partial_update=extend_schema(
        summary="Partially update a lineitems", tags=["Line Items"]
    ),
    destroy=extend_schema(summary="Deleta a lineitems", tags=["Line Items"]),
)
class LineItemViewSet(viewsets.ModelViewSet):
    queryset = LineItem.objects.all()
    serializer_class = LineItemSerializer


@extend_schema_view(
    list=extend_schema(summary="List all payment", tags=["Payments"]),
    create=extend_schema(summary="Create a new payment", tags=["Payments"]),
    retrieve=extend_schema(summary="Retrieve an payment", tags=["Payments"]),
    update=extend_schema(summary="Update a payment", tags=["Payments"]),
    partial_update=extend_schema(
        summary="Partially update a payment", tags=["Payments"]
    ),
    destroy=extend_schema(summary="Deleta a payment", tags=["Payments"]),
)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
