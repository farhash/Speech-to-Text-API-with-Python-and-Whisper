from django.urls import path, re_path
from stt import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.shortcuts import redirect


urlpatterns = [
  path('url/', views.SttGeneral.as_view()),
  path('upload/', views.upload_file),
  path('result/<stt_result_key>/', views.SttDetail.as_view()),
  path('schema/', SpectacularAPIView.as_view(), name='schema'),
  path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
  re_path(r'^swagger$', lambda request: redirect('/stt/swagger/', permanent=True)),
]


