from django.urls import path
from .views import show_cars, taxi_new_car, taxi_edit_car

urlpatterns = [
	path('', 							show_cars, name='show_cars'),
	path('new-car/', 					taxi_new_car, name= 'taxi_new_car'),
	path('edit-car/<str:slug>/', 		taxi_edit_car, name= 'taxi_edit_car')
]

