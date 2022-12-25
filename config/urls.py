from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('__debug__/', include('debug_toolbar.urls')),

    path('account/', include('account.urls')),
    path('v1/story/', include('story.urls')),
]
