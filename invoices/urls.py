from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, InvoiceViewSet, LineItemViewSet, PaymentViewSet

router = DefaultRouter()

router.register("customers", CustomerViewSet)
router.register("invoices", InvoiceViewSet)
router.register("lineitems", LineItemViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = router.urls
