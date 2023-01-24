from django.urls import path

from hint.views import SheetHintAPIView


app_name = 'hint'

urlpatterns = [
    path('sheet/<int:sheet_id>/', SheetHintAPIView.as_view(), name='sheet_hint'),
]
