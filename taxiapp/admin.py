from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import Driver
from .models import Working_day
from .models import Cashbox
from .models import Car
from .models import Cost_item, Car_cost


class Working_dayInline(admin.TabularInline):
    model = Working_day
    exclude = ('slug', 'debt_of_day')
    extra = 0

class DriverAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
	
	list_display = (
					'first_name',
					'second_name',
					'third_name',
					'car',
					)

	inlines		= [Working_dayInline]

	exclude = ('slug',)




admin.site.register(Driver, DriverAdmin)


class Working_dayAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
	list_display = (
					'date',
					'rate',
					'fuel',
					'penalties',
					'cash',
					'cashless',
					)	

	exclude = ('slug', 'debt_of_day',)


admin.site.register(Working_day, Working_dayAdmin)


class CashboxAdmin(SimpleHistoryAdmin, admin.ModelAdmin):

	list_display = (
					'date', 
					'cash',
					'cash_card',
					)

	exclude = ('slug',)

admin.site.register(Cashbox, CashboxAdmin)


class CarAdmin(admin.ModelAdmin):

	list_display = (
					'car_number', 
					'car_brand',
					'car_model',
					)

	exclude = ('slug',)

admin.site.register(Car, CarAdmin)

class Cost_itemAdmin(admin.ModelAdmin):

	list_display = (
					'title', 
					'parent_item',
					)

	exclude = ('slug', 'date',)

admin.site.register(Cost_item, Cost_itemAdmin)

class Car_costAdmin(admin.ModelAdmin):

	list_display = (
					'cost_date',
					'cost_item',
					'car',
					'summ',
					)

	exclude = ('slug',)

admin.site.register(Car_cost, Car_costAdmin)