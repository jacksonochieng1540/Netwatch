from rest_framework.routers import DefaultRouter
from .views import PollResultViewSet, NetworkEventViewSet
router = DefaultRouter()
router.register(r'polls',  PollResultViewSet,  basename='poll')
router.register(r'events', NetworkEventViewSet, basename='event')
urlpatterns = router.urls
