from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('students/', include('students.urls')),
    path('academics/', include('academics.urls')),
    path('finance/', include('finance.urls')),
    path('payments/', include('payments.urls')),
    path('reports/', include('reports.urls')),
]
