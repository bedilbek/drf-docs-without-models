from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()

router.register(prefix='countries', viewset=views.CountryViewSet, basename='countries')

urlpatterns = router.urls
