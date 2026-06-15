from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, RegionViewSet
router = DefaultRouter()
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'', DeviceViewSet, basename='device')
urlpatterns = router.urls
