from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('__debug__/', include('debug_toolbar.urls')),

    path('account/', include('account.urls')),

    path('v1/story/', include('story.urls')),
    path('cms/v1/story/', include('story.cms_urls')),

    path('v1/hint/', include('hint.urls')),
    path('v1/point/', include('point.urls')),
    path('v1/banner/', include('banner.urls')),
    path('v1/payment/', include('payment.urls')),
]
