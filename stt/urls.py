from django.urls import path
from stt import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
  path('stt/url', views.SttGeneral.as_view()),
  path('stt/upload/', views.upload_file),
  path('stt/result/<stt_result_key>', views.SttDetail.as_view()),
  path('schema/', SpectacularAPIView.as_view(), name='schema'),
  path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]


