from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

SchemaView = get_schema_view(
    openapi.Info(
        title='Image Repository API',
        default_version='api',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API
    path('api/auth/', include(('account.urls', 'account'), namespace='account_api')),
    path('api/images/', include(('images.urls', 'images'), namespace='images_api')),
    # API Swagger Docs
    path('api/docs/swagger/', SchemaView.with_ui('swagger'), name='schema_swagger'),
    path('api/docs/redoc/', SchemaView.with_ui('redoc'), name='schema_redoc'),
]