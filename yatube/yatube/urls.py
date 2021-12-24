"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'
urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('users.urls', namespace='users')),
    url(r'^admin/', admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
    path('auth/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
