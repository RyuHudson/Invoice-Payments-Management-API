from django.db import models
from datetime import date
from django.core.validators import MinValueValidator
from django.conf import settings


# Create your models here.
class Customer(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customers",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField(blank=True)

    @property
    def balance(self):
        total_invoiced = sum(invoice.total for invoice in self.invoices.all())
        total_paid = sum(payment.amount for payment in self.payments.all())
        return total_invoiced - total_paid

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [("draft", "Draft"), ("sent", "Sent")]

    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="invoices"
    )
    invoice_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by("-id").first()
            if last_invoice:
                self.invoice_number = str(int(last_invoice.invoice_number) + 1)
            else:
                self.invoice_number = "1"
        super().save(*args, **kwargs)

    @property
    def total(self):
        line_items = self.line_items.all()
        items = []
        for line in line_items:
            total_item = line.unit_price * line.quantity
            items.append(total_item)
        return sum(items)

    @property
    def outstanding_amount(self):
        total_paid = sum(payment.amount for payment in self.payments.all())
        return self.total - total_paid

    @property
    def is_paid(self):
        return self.outstanding_amount <= 0

    @property
    def is_overdue(self):
        if self.due_date is None:
            return False
        return self.due_date <= date.today() and not self.is_paid

    def __str__(self):
        return self.invoice_number


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    description = models.CharField(max_length=225)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.description} ({self.invoice.invoice_number})"

    @property
    def sub_total(self):
        return self.unit_price * self.quantity


class Payment(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="payments"
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
