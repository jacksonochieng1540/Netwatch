from rest_framework.routers import DefaultRouter
from .views import AlertRuleViewSet, AlertRecordViewSet
router = DefaultRouter()
router.register(r'rules',   AlertRuleViewSet,   basename='alert-rule')
router.register(r'records', AlertRecordViewSet, basename='alert-record')
urlpatterns = router.urls
