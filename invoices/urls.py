from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, InvoiceViewSet, LineItemViewSet

router = DefaultRouter()

router.register('customers', CustomerViewSet)
router.register('invoices', InvoiceViewSet)
router.register('lineitems', LineItemViewSet)

urlpatterns = router.urls