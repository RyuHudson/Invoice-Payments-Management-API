from .models import Customer, Invoice, LineItem, Payment
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    balance = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = ["id", "name", "email", "address", "balance"]


class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ["id", "invoice", "description", "unit_price", "quantity"]
        extra_kwargs = {"invoice": {"required": False}}


class InvoiceSerializer(serializers.ModelSerializer):
    invoice_number = serializers.ReadOnlyField()
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source="customer", write_only=True
    )
    total = serializers.SerializerMethodField()
    outstanding_amount = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    line_items = LineItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "outstanding_amount",
            "is_paid",
            "is_overdue",
            "customer",
            "customer_id",
            "invoice_date",
            "due_date",
            "status",
            "total",
            "line_items",
        ]

    def get_total(self, obj):
        return obj.total

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])
        invoice = Invoice.objects.create(**validated_data)

        for item_data in line_items_data:
            item_data.pop("invoice", None)
            LineItem.objects.create(invoice=invoice, **item_data)

        return invoice


class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source="customer", write_only=True
    )
    invoice = InvoiceSerializer(read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(
        queryset=Invoice.objects.all(),
        source="invoice",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Payment
        fields = [
            "customer",
            "customer_id",
            "invoice",
            "invoice_id",
            "amount",
            "payment_date",
        ]

    def validate(self, data):
        invoice = data.get("invoice")
        customer = data.get("customer", getattr(self.instance, "customer", None))
        if invoice and customer and invoice.customer_id != customer.id:
            raise serializers.ValidationError(
                "Invoice must belong to the same customer as the payment."
            )
        return data
