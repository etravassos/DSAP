from django.conf.urls import include, url

from rest_framework_nested import routers

from src.web.api.views import DomainAPIView
from src.web.api.views import CDSRecordAPIView, PreviewCDSRecordAPIView

router = routers.SimpleRouter()
router.register(r'domains', DomainAPIView, base_name='domains')

dsrecords_router = routers.NestedSimpleRouter(router, r'domains', lookup='domain')
dsrecords_router.register(r'cds', CDSRecordAPIView, base_name='domain-cdsrecords')
dsrecords_router.register(r'cds', PreviewCDSRecordAPIView, base_name='preview-cdsrecords')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(dsrecords_router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

    
    