from django.urls import path
from .views import working_day_add, working_day_edit, working_day_delete

urlpatterns = [
	path('working-day-add/<str:driver_slug>/', 		working_day_add, name='working_day_add'),
	path('working-day-edit/<str:day_slug>/', 		working_day_edit, name='working_day_edit'),
	path('working-day-delete/<str:day_slug>/', 		working_day_delete, name='working_day_delete'),
]
