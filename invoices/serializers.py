from .models import Customer, Invoice, LineItem, Payment
from rest_framework import serializers

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'address']

class InvoiceSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only= True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source='customer', write_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'customer', 'customer_id', 'invoice_date', 'due_date', 'status', 'total']

    def get_total(self, obj):
        return obj.total

class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ['id', 'invoice', 'description', 'unit_price', 'quantity']

class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source='customer', write_only=True)
    invoice = InvoiceSerializer(read_only=True)
    invoice_id = serializers.PrimaryKeyRelatedField(queryset=Invoice.objects.all(), source='invoice', write_only=True, required=False, allow_null=True)
    class Meta:
        model = Payment
        fields = ['customer', 'customer_id' 'invoice', 'invoice_id', 'amount', 'payment_date']

