from django.urls import path
from django.urls import include
from .views import taxi_show_index
from .views import show_driver, driver_add_new, driver_edit
from .views import taxi_show_cashbox, taxi_incass
from .views import taxi_show_history
from .views import gas_upload, send_debts
from .views import taxi_show_cost_items
from .views import taxi_add_cost_items
from .views import taxi_edit_cost_items
from .views import taxi_show_car_costs
from .views import car_costs_add_new
from .views import car_costs_edit
from .views import taxi_show_cost_report
from .views import taxi_admin_service_menu
from .views import service_upload_working_day
from .views import service_upload_yandex

urlpatterns = [

	path('', 						taxi_show_index, name='taxi_show_index'),
	path('cashbox/', 				taxi_show_cashbox, name='taxi_show_cashbox'),
	path('history/', 				taxi_show_history, name='taxi_show_history'),
	path('incass/', 				taxi_incass, name='taxi_incass'),
	path('driver/<str:slug>/', 		show_driver, name='show_driver'),
	path('new-driver/', 			driver_add_new, name='driver_add_new'),
	path('edit-driver/<str:slug>/', driver_edit, name='driver_edit'),
	path('gas-upload/', 			gas_upload, name='gas_upload'),
	path('profile/', 				include('authapp.urls')),
	path('working-days/', 			include('workingdayapp.urls')),
	path('cars/', 					include('carsapp.urls')),
	path('send-debts/', 			send_debts, name='send_debts'),
	path('cost-items/edit/<str:slug>/', taxi_edit_cost_items, name='taxi_edit_cost_items'),
	path('cost-items/add/', 		taxi_add_cost_items, name='taxi_add_cost_items'),
	path('cost-items/', 			taxi_show_cost_items, name='taxi_show_cost_items'),
	path('car-costs/edit/<str:car_cost_slug>/', 			car_costs_edit, name='car_costs_edit'),
	path('car-costs/add/', 			car_costs_add_new, name='car_costs_add_new'),
	path('car-costs/', 				taxi_show_car_costs, name='taxi_show_car_costs'),
	path('cost-report/', 			taxi_show_cost_report, name='taxi_show_cost_report'),
	#admin services
	path('services/upload-working-day/<str:input_date>/', 	service_upload_working_day , name='service_upload_working_day'),
	path('services/upload-yandex/<str:input_date>/', 	service_upload_yandex , name='service_upload_yandex'),
	path('services/', 				taxi_admin_service_menu, name='taxi_admin_service_menu'),

			]
