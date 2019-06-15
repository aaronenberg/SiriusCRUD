"""sirius URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView
from outcomes.views import IndexView


urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('favicon.ico',
        RedirectView.as_view(url=staticfiles_storage.url('images/favicon.ico'), permanent=False),
        name="favicon"),
    path('', include('users.urls', namespace='users')),
    path('', include('outcomes.urls', namespace='outcomes')),
    path('', include('developments.urls', namespace='developments')),
    path('', include('courses.urls', namespace='courses')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        path('_s3_mock/', include('s3file.urls')),
    ] + urlpatterns
