from rest_framework import viewsets
from collections import Counter
from django.utils.dateparse import parse_date
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.decorators import action
from drf_spectacular.types import OpenApiTypes
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .renderers import PDFRenderer
from .models import Customer, Invoice, LineItem, Payment
from .serializers import (
    CustomerSerializer,
    InvoiceSerializer,
    LineItemSerializer,
    PaymentSerializer,
)
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from decimal import Decimal


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

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Customer.objects.all()
        return Customer.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


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

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoice.objects.all()
        return Invoice.objects.filter(customer__owner=user)

    @extend_schema(
        tags=["Invoices"],
        summary="Download invoice as PDF",
        responses={(200, "application/pdf"): OpenApiTypes.BINARY},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="pdf",
        permission_classes=[IsAuthenticated],
        renderer_classes=[JSONRenderer, PDFRenderer],
    )
    def invoice_pdf(self, request, pk=None):
        invoice = self.get_object()
        html_string = render_to_string(
            "invoices/invoice_pdf.html", {"invoice": invoice}
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice_{invoice.id}.pdf"'
        )

        pisa.CreatePDF(html_string, dest=response)

        return response

    @extend_schema(
        tags=["Invoices"],
        summary="Invoice summary report",
        parameters=[
            OpenApiParameter(
                name="date_from",
                type=OpenApiTypes.DATE,
                required=False,
                description="Invoices dated on or after this date (YYYY-MM-DD)",
            ),
            OpenApiParameter(
                name="date_to",
                type=OpenApiTypes.DATE,
                required=False,
                description="Invoices dated on or before this date (YYYY-MM-DD)",
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="summary",
        permission_classes=[IsAuthenticated],
    )
    def summary(self, request):
        raw_from = request.query_params.get("date_from")
        date_from = None

        if raw_from:
            try:
                date_from = parse_date(raw_from)
            except ValueError:
                date_from = None
            if date_from is None:
                return Response(
                    {"date_from": "Invalid date. Use YYYY-MM-DD."}, status=400
                )

        raw_to = request.query_params.get("date_to")
        date_to = None
        if raw_to:
            try:
                date_to = parse_date(raw_to)
            except ValueError:
                date_to = None
            if date_to is None:
                return Response(
                    {"date_to": "Invalid date. Use YYYY-MM-DD."}, status=400
                )

        invoices = self.get_queryset()

        if date_from:
            invoices = invoices.filter(invoice_date__gte=date_from)
        if date_to:
            invoices = invoices.filter(invoice_date__lte=date_to)

        invoices = invoices.prefetch_related("line_items", "payments")
        zero = Decimal("0.00")

        total_invoiced = sum((invoice.total for invoice in invoices), zero)
        total_paid = sum(
            (p.amount for inv in invoices for p in inv.payments.all()), zero
        )
        total_outstanding = sum((inv.outstanding_amount for inv in invoices), zero)

        data = {
            "invoice_count": len(invoices),
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_outstanding": total_outstanding,
            "overdue_count": sum(1 for inv in invoices if inv.is_overdue),
            "by_status": dict(Counter(inv.status for inv in invoices)),
        }
        return Response(data)


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

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return LineItem.objects.all()
        return LineItem.objects.filter(invoice__customer__owner=user)


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

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(customer__owner=user)
