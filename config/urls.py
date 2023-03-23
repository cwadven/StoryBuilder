from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('__debug__/', include('debug_toolbar.urls')),

    path('account/', include('account.urls')),
    re_path(r'^v1/story/?$', include('story.urls')),
    re_path(r'^v1/hint/?$', include('hint.urls')),
    re_path(r'^v1/point/?$', include('point.urls')),
]
