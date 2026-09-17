from django.db import models

# Create your models here.
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
    invoice = models.ForeignKey(Invoice, on_delete= models.CASCADE, related_name='line_items')
    description = models.CharField(max_length=225)
    unit_price = models.DecimalField(max_digits=10, decimal_places= 2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.description} ({self.invoice.invoice_number})"