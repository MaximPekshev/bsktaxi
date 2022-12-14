import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Driver, Car
from .models import Working_day
from .forms import NewDriverForm
from .forms import Car_cost_form
from django.contrib.auth.models import Group
from django.contrib				import messages
from .models import Cashbox
from .models import Cost_item
from .models import Car_cost
from django.db.models import Sum
from datetime import datetime, timedelta

from decimal import Decimal
from workingdayapp.forms import WorkingDayForm
from django.utils import timezone
from .forms import PeriodForm, Gas_upload
from django.db.models import Sum

from django.contrib.auth.models import Group

import django.core.exceptions

import requests
import json
import xlrd

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from decouple import config
import time

from .scripts import driver_mailing


def culc_debt(drivers):
	debt=0
	for driver in drivers:
		debt += driver.debt
	return debt


def taxi_show_index(request):

	taxiadmin = False

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user in users_in_group:

		taxiadmin = True

	users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group or request.user in users_in_group_collector):

		drivers_works = Driver.objects.filter(active=True).order_by('second_name')

		cars_works = []

		for dr in drivers_works:
			if dr.car in cars_works:
				pass
			else:
				if dr.car:
					cars_works.append(dr.car)

		debt_of_works = culc_debt(drivers_works)

		drivers_fired = Driver.objects.filter(active=False).order_by('second_name')

		debt_of_fired = culc_debt(drivers_fired)

		cars = Car.objects.all()

		context = {

			'drivers_works':drivers_works,
			'debt_of_works':debt_of_works,
			'drivers_fired':drivers_fired,
			'debt_of_fired':debt_of_fired,
			'cars':cars,
			'cars_works': len(cars_works),
			'taxiadmin': taxiadmin,

		}

		return render(request, 'taxiapp/base_taxi.html', context)

	else:
		
		return render(request, 'authapp/login.html')
	
def show_driver(request, slug):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group or request.user in users_in_group_collector):

		driver = Driver.objects.get(slug = slug)

		working_days = Working_day.objects.filter(driver = driver).order_by("-date")

		if driver.car:
			cars = Car.objects.exclude(slug=driver.car.slug).order_by("car_number")
		else:
			cars = Car.objects.all().order_by("car_number")



		context = {

			'working_days': working_days, 'driver': driver, 'cars':cars,

		}

		return render(request, 'taxiapp/driver.html', context)

	else:
		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')

def driver_add_new(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:
		
		if request.method == 'POST':

			dr_form = NewDriverForm(request.POST)

			if dr_form.is_valid():

				first_name 			= dr_form.cleaned_data['first_name']
				last_name 			= dr_form.cleaned_data['last_name']
				car_obj 			= dr_form.cleaned_data['car_obj']

				if car_obj:
					car = Car.objects.get(car_number=car_obj)
				else:
					car = None
						
				rate 				= float(dr_form.cleaned_data['rate'].replace(',','.'))

				if dr_form.cleaned_data['third_name']:
					third_name = dr_form.cleaned_data['third_name']
				else:
					third_name = ''


				if dr_form.cleaned_data['driver_license']:
					driver_license = dr_form.cleaned_data['driver_license']
				else:
					driver_license = ''

				if dr_form.cleaned_data['fuel_card']:
					fuel_card = dr_form.cleaned_data['fuel_card']
				else:
					fuel_card = ''


				if dr_form.cleaned_data['fuel_card_2']:
					fuel_card_2 = dr_form.cleaned_data['fuel_card_2']
				else:
					fuel_card_2 = ''

				if dr_form.cleaned_data['email']:
					email = dr_form.cleaned_data['email']
				else:
					email = ''	

				active 				= dr_form.cleaned_data['active']	

				monday 				= dr_form.cleaned_data['monday']
				tuesday 			= dr_form.cleaned_data['tuesday']
				wednesday 			= dr_form.cleaned_data['wednesday']
				thursday 			= dr_form.cleaned_data['thursday']
				friday 				= dr_form.cleaned_data['friday']
				saturday 			= dr_form.cleaned_data['saturday']
				sunday 				= dr_form.cleaned_data['sunday']

				new_driver = Driver(
					first_name=first_name, second_name=last_name, 
					third_name=third_name,
					driver_license=driver_license,
					fuel_card=fuel_card,
					fuel_card_2=fuel_card_2,
					email=email,
					rate=rate, debt=0, active=active,
					monday=monday, tuesday=tuesday, wednesday=wednesday,
					thursday=thursday, friday=friday, saturday=saturday, sunday=sunday,
					car=car,
					)
				new_driver.save()

				return redirect('taxi_show_index')
		else:

			return redirect('taxi_show_index')
	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')		

def driver_edit(request, slug):
			
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:
		
		if request.method == 'POST':

			dr_form = NewDriverForm(request.POST)

			if dr_form.is_valid():

				first_name 			= dr_form.cleaned_data['first_name']
				last_name 			= dr_form.cleaned_data['last_name']

				if dr_form.cleaned_data['third_name']:
					third_name 	= dr_form.cleaned_data['third_name']
				else:
					third_name 	= ''

				if dr_form.cleaned_data['driver_license']:
					driver_license 	= dr_form.cleaned_data['driver_license']
				else:
					driver_license 	= ''

				if dr_form.cleaned_data['fuel_card']:
					fuel_card = dr_form.cleaned_data['fuel_card']
				else:
					fuel_card = ''

				if dr_form.cleaned_data['fuel_card_2']:
					fuel_card_2 = dr_form.cleaned_data['fuel_card_2']
				else:
					fuel_card_2 = ''
					
				if dr_form.cleaned_data['email']:
					email = dr_form.cleaned_data['email']
				else:
					email = ''		


				car_obj 			= dr_form.cleaned_data['car_obj']

				if car_obj:
					try:
						car = Car.objects.get(car_number=car_obj)
					except Car.DoesNotExist:
						car = None
				else:
					car = None


				rate 				= float(dr_form.cleaned_data['rate'].replace(',','.'))

				active 				= dr_form.cleaned_data['active']

				monday 				= dr_form.cleaned_data['monday']
				tuesday 			= dr_form.cleaned_data['tuesday']
				wednesday 			= dr_form.cleaned_data['wednesday']
				thursday 			= dr_form.cleaned_data['thursday']
				friday 				= dr_form.cleaned_data['friday']
				saturday 			= dr_form.cleaned_data['saturday']
				sunday 				= dr_form.cleaned_data['sunday']

				driver = Driver.objects.get(slug=slug)

				if driver.first_name != first_name:
					driver.first_name = first_name

				if driver.second_name != last_name:
					driver.second_name = last_name	

				if driver.third_name != third_name:
					driver.third_name = third_name		

				if driver.driver_license != driver_license:
					driver.driver_license = driver_license

				if driver.fuel_card != fuel_card:
					driver.fuel_card = fuel_card	

				if driver.fuel_card_2 != fuel_card_2:
					driver.fuel_card_2 = fuel_card_2

				if driver.email != email:
					driver.email = email	

				if driver.rate != rate:
					driver.rate = rate	

				if driver.active != active:
					driver.active = active

				if driver.monday != monday:
					driver.monday = monday

				if driver.tuesday != tuesday:
					driver.tuesday = tuesday

				if driver.wednesday != wednesday:
					driver.wednesday = wednesday

				if driver.thursday != thursday:
					driver.thursday = thursday

				if driver.friday != friday:
					driver.friday = friday

				if driver.saturday != saturday:
					driver.saturday = saturday

				if driver.sunday != sunday:
					driver.sunday = sunday

				if driver.car != car:
					driver.car = car


				driver.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)

		else:

			return redirect('taxi_show_index')
	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')			


def taxi_show_cashbox(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()
	users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

	collector = False

	if request.user in users_in_group_collector:
		collector = True

	if request.user.is_authenticated and (request.user in users_in_group or request.user in users_in_group_collector):

		cashbox = Cashbox.objects.all().order_by('-date')

		ca_cash 	 = Cashbox.objects.all().aggregate(Sum('cash'))['cash__sum']
		ca_cash_card = Cashbox.objects.all().aggregate(Sum('cash_card'))['cash_card__sum']

		context = {

			'cashbox': cashbox,
            'ca_cash': ca_cash.quantize(Decimal("1.00")) if ca_cash else 0,
            'ca_cash_card': ca_cash_card.quantize(Decimal("1.00")) if ca_cash_card else 0,
			'collector': collector,

		}

		return	render(request, 'taxiapp/cashbox.html', context)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')

def taxi_incass(request):

	users_in_group = Group.objects.get(name="taxicollector").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:


		if request.method == 'POST':

			incass_form = WorkingDayForm(request.POST)

			if incass_form.is_valid():

				if incass_form.cleaned_data['input_cash']:
					cash = Decimal(incass_form.cleaned_data['input_cash'].replace(',','.'))
				else:
					cash = 0

				if incass_form.cleaned_data['input_cash_card']:
					cash_card = Decimal(incass_form.cleaned_data['input_cash_card'].replace(',','.'))
				else:
					cash_card = 0

				if cash != 0 or cash_card != 0:
			
					cashbox = Cashbox(
						date=datetime.now(),
						cash=-cash,
						cash_card=-cash_card,
						)

					cashbox.save()

					current_path = request.META['HTTP_REFERER']
					return redirect(current_path)

				else:		
					current_path = request.META['HTTP_REFERER']
					return redirect(current_path)

			else:		
				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)		

		else:		
			current_path = request.META['HTTP_REFERER']
			return redirect(current_path)			

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def taxi_show_history(request):
	
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()
	users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group or request.user in users_in_group_collector):

		if request.method == 'POST':

			period_form = PeriodForm(request.POST)

			if period_form.is_valid():

				trip_start 		= period_form.cleaned_data['trip_start'] + ' 00:00:01'
				trip_end 		= period_form.cleaned_data['trip_end'] + ' 23:59:59'

				date_lte 	= datetime.strptime(trip_start, '%Y-%m-%d %H:%M:%S')
				date_now	= datetime.strptime(trip_end, '%Y-%m-%d %H:%M:%S')

			else:

				messages.info(request, '???? ???????????? ???????????? ????????????!!')
				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)	

		else:

			date_now    =   timezone.now()

			if date_now.day > 7:

				date_lte 	= 	date_now.replace(day = int(date_now.day - 7))

			else:	

				date_lte 	= 	date_now.replace(day = int(date_now.day + 30 - 7))

				if date_now.month > 1:

					date_lte 	= 	date_lte.replace(month = int(date_lte.month - 1))

				else:

					date_lte 	= 	date_lte.replace(month = int(date_lte.month + 12 - 1))
					date_lte 	= 	date_lte.replace(year = int(date_lte.year - 1))
					

		d_history = []

		driver_history = Driver.history.filter(history_date__lte=date_now, history_date__gte=date_lte)

		for dh in driver_history:

			try:

				dr_prev = dh.get_previous_by_history_date(id=dh.id)

				driver 			= False
				if (dh.first_name != dr_prev.first_name):

					driver 		= True

				if (dh.second_name != dr_prev.second_name):

					driver 		= True

				if (dh.third_name != dr_prev.third_name):

					driver 		= True	

				driver_license 	= False if (dh.driver_license == dr_prev.driver_license) else True
				rate 			= False if (dh.rate == dr_prev.rate) else True
				fuel_card 		= False if (dh.fuel_card == dr_prev.fuel_card) else True
				car 			= False if (dh.car == dr_prev.car) else True
				fuel_card_2 	= False if (dh.fuel_card_2 == dr_prev.fuel_card_2) else True
				email 			= False if (dh.email == dr_prev.email) else True

			except dh.DoesNotExist:


				driver 			= False
				driver_license 	= False
				rate			= False
				fuel_card		= False
				car 			= False
				fuel_card_2		= False
				email			= False

			d_history.append([dh, driver, driver_license, rate, fuel_card, car, fuel_card_2, email])

		work_day_hist  = []

		wd_history     = Working_day.history.filter(history_date__lte=date_now, history_date__gte=date_lte)

		for wd in wd_history:

			try:

				wd_prev 		= wd.get_previous_by_history_date(id=wd.id)

				rate 			= False if (wd.rate == wd_prev.rate) else True
				fuel 			= False if (wd.fuel == wd_prev.fuel) else True
				penalties 		= False if (wd.penalties == wd_prev.penalties) else True
				cash 			= False if (wd.cash == wd_prev.cash) else True
				cash_card 		= False if (wd.cash_card == wd_prev.cash_card) else True
				cashless 		= False if (wd.cashless == wd_prev.cashless) else True
				debt_of_day 	= False if (wd.debt_of_day == wd_prev.debt_of_day) else True


			except wd.DoesNotExist:

				rate 			= False
				fuel 			= False
				penalties 		= False
				cash 			= False
				cash_card 		= False
				cashless		= False
				debt_of_day 	= False

			work_day_hist.append([wd, rate, fuel, penalties, cash, cash_card, cashless, debt_of_day])	


		context = {

			'd_history': d_history,
			'work_day_hist': work_day_hist,
			'date_now': date_now.strftime("%Y-%m-%d"),
			'date_lte': date_lte.strftime("%Y-%m-%d"),
		}

		return	render(request, 'taxiapp/history.html', context)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def gas_upload(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:
		
		if request.method == 'POST':

			gas_form = Gas_upload(request.POST,request.FILES)

			if gas_form.is_valid():

				gas_file = 	request.FILES['gas_file']
				option_gas = request.POST['optiongas']

				missing_drivers = []
				upload_transactions = []

				wb = xlrd.open_workbook(file_contents=gas_file.read())

				sheet = wb.sheet_by_index(0)

				if option_gas == 'option1':

					for n in range(sheet.nrows):

						if sheet.cell(n,4).value == '??????????' or sheet.cell(n,4).value == '??????????????':

							date_of_transaction = datetime.date(xlrd.xldate.xldate_as_datetime(sheet.cell(n,0).value, wb.datemode))

							fuel_card = str(int(sheet.cell(n,2).value))

							summ_of_transaction = Decimal(sheet.cell(n,10).value).quantize(Decimal("1.00"))

							taxidriver = Driver.objects.filter(fuel_card=fuel_card).first() if Driver.objects.filter(fuel_card=fuel_card).first() else Driver.objects.filter(fuel_card_2=fuel_card).first()

							if taxidriver:

								if not len(Working_day.objects.filter(driver=taxidriver)):
									missing_drivers.append([date_of_transaction, fuel_card, summ_of_transaction, True])
									continue

								working_day = Working_day.objects.filter(driver=taxidriver, date=date_of_transaction).first()

								if working_day:
									working_day.fuel = working_day.fuel + summ_of_transaction
									working_day.save()
								else:	
									working_day = Working_day.objects.filter(driver=taxidriver).last()
									working_day.fuel = working_day.fuel + summ_of_transaction
									working_day.save()

								upload_transactions.append([date_of_transaction, taxidriver.second_name, taxidriver.first_name, fuel_card, summ_of_transaction])

							else:

								missing_drivers.append([date_of_transaction, fuel_card, summ_of_transaction, False])

				elif option_gas == 'option3':

					for n in range(sheet.nrows):

						if sheet.cell(n,0).value.find('?????????? ???') != -1:

							fuel_card = str(sheet.cell(n,0).value.split(' ')[2])

						if 	sheet.cell(n,1).value == '??????????':

							date_of_transaction = xlrd.xldate.xldate_as_datetime(sheet.cell(n,2).value, wb.datemode)

							summ_of_transaction = Decimal(sheet.cell(n,8).value).quantize(Decimal("1.00"))

							taxidriver = Driver.objects.filter(fuel_card=fuel_card).first() if Driver.objects.filter(fuel_card=fuel_card).first() else Driver.objects.filter(fuel_card_2=fuel_card).first()

							if taxidriver:

								if not len(Working_day.objects.filter(driver=taxidriver)):
									missing_drivers.append([date_of_transaction, fuel_card, summ_of_transaction, True])
									continue

								working_day = Working_day.objects.filter(driver=taxidriver, date=date_of_transaction).first()

								if working_day:
									working_day.fuel = working_day.fuel + summ_of_transaction
									working_day.save()
								else:	
									working_day = Working_day.objects.filter(driver=taxidriver).last()
									working_day.fuel = working_day.fuel + summ_of_transaction
									working_day.save()

								upload_transactions.append([date_of_transaction, taxidriver.second_name, taxidriver.first_name, fuel_card, summ_of_transaction])

							else:

								missing_drivers.append([date_of_transaction, fuel_card, summ_of_transaction, False])

				elif option_gas == 'option4':

					for n in range(sheet.nrows-1)[7:]:

						fuel_card = str(sheet.cell(n,3).value)
						date_of_transaction = datetime.strptime(sheet.cell(n,0).value, '%d.%m.%Y %H:%M:%S').date()
						summ_of_transaction =  Decimal(sheet.cell(n, 9).value).quantize(Decimal("1.00"))

						taxidriver = Driver.objects.filter(fuel_card=fuel_card).first() if Driver.objects.filter(fuel_card=fuel_card).first() else Driver.objects.filter(fuel_card_2=fuel_card).first()

						if taxidriver:

							if not len(Working_day.objects.filter(driver=taxidriver)):
								missing_drivers.append([date_of_transaction, fuel_card, summ_of_transaction, True])
								continue

							working_day = Working_day.objects.filter(driver=taxidriver, date=date_of_transaction).first()

							if working_day:
								working_day.fuel = working_day.fuel + summ_of_transaction
								working_day.save()
							else:	
								working_day = Working_day.objects.filter(driver=taxidriver).last()
								working_day.fuel = working_day.fuel + summ_of_transaction
								working_day.save()

							upload_transactions.append([date_of_transaction, taxidriver.second_name, taxidriver.first_name, fuel_card, summ_of_transaction])

						else:

							missing_drivers.append([date_of_transaction, fuel_card, summ_of_transaction, False])


				context = {
							'upload_transactions': upload_transactions,
							'missing_drivers': missing_drivers,
				}

				return	render(request, 'taxiapp/upload_succes.html', context)

			else:

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)

		else:
			current_path = request.META['HTTP_REFERER']
			return redirect(current_path)
	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def send_debts(request):

	driver_mailing()

	return render(request, 'taxiapp/mailing_succes.html')

def taxi_show_cost_items(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:

		cost_items_tab = []
		for item in Cost_item.objects.filter(is_category=True).order_by('title'):
			cost_items_tab.append(item)
		for item in Cost_item.objects.filter(is_category=False, parent_item=None).order_by('title'):
			cost_items_tab.append(item)	

		context = {
				'cost_items_tab': cost_items_tab,
				'cost_items': Cost_item.objects.all().order_by('title'),
			}

		return render(request, 'taxiapp/cost_items.html', context)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')	

def taxi_add_cost_items(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:

		if request.method == 'POST':

			car_cost_form = Car_cost_form(request.POST)

			if car_cost_form.is_valid():

				cost_item = car_cost_form.cleaned_data['cost_item']
				 

				new_cost_item = Cost_item(title=cost_item)

				if car_cost_form.cleaned_data['parent_cost_item']:
					parent_item = Cost_item.objects.filter(title=car_cost_form.cleaned_data['parent_cost_item']).first()
					new_cost_item.parent_item = parent_item

				if car_cost_form.cleaned_data['is_category']:
					new_cost_item.is_category = car_cost_form.cleaned_data['is_category']

				new_cost_item.save()

		current_path = request.META['HTTP_REFERER']
		return redirect(current_path)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def taxi_edit_cost_items(request, slug):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:

		if request.method == 'POST':

			car_cost_form = Car_cost_form(request.POST)

			if car_cost_form.is_valid():

				cost_item = car_cost_form.cleaned_data['cost_item']

				editable_cost_item = Cost_item.objects.get(slug=slug)
				editable_cost_item.title = cost_item

				if car_cost_form.cleaned_data['parent_cost_item']:
					parent_item = Cost_item.objects.filter(title=car_cost_form.cleaned_data['parent_cost_item']).first()
					editable_cost_item.parent_item = parent_item

				if editable_cost_item.is_category != car_cost_form.cleaned_data['is_category']:
					editable_cost_item.is_category = car_cost_form.cleaned_data['is_category']

				editable_cost_item.save()

		current_path = request.META['HTTP_REFERER']
		return redirect(current_path)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def taxi_show_car_costs(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()
	users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group or request.user in users_in_group_collector):

		if request.method == 'POST':

			period_form = PeriodForm(request.POST)

			if period_form.is_valid():

				trip_start 		= period_form.cleaned_data['trip_start'] + ' 00:00:01'
				trip_end 		= period_form.cleaned_data['trip_end'] + ' 23:59:59'

				date_lte 	= datetime.strptime(trip_start, '%Y-%m-%d %H:%M:%S')
				date_now	= datetime.strptime(trip_end, '%Y-%m-%d %H:%M:%S')

				car = period_form.cleaned_data['car']

				if car:
					car_obj = Car.objects.filter(car_number=car).first()
				else:
					car_obj = None

				cost_item = period_form.cleaned_data['cost_item']

				if cost_item:
					cost_item_obj = Cost_item.objects.filter(title=cost_item).first()
				else:
					cost_item_obj = None

			else:

				messages.info(request, '???? ???????????? ???????????? ????????????!!')
				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)	

		else:

			car_obj = None
			cost_item_obj = None
			date_now    =   timezone.now()

			if date_now.day > 7:

				date_lte 	= 	date_now.replace(day = int(date_now.day - 7))

			else:	

				date_lte 	= 	date_now.replace(day = int(date_now.day + 30 - 7))

				if date_now.month > 1:

					date_lte 	= 	date_lte.replace(month = int(date_lte.month - 1))

				else:

					date_lte 	= 	date_lte.replace(month = int(date_lte.month + 12 - 1))
					date_lte 	= 	date_lte.replace(year = int(date_lte.year - 1))
					

		car_obj_slug = car_obj.slug if car_obj else ''
		cost_item_obj_slug = cost_item_obj.slug if cost_item_obj else ''


		car_costs = Car_cost.objects.filter(cost_date__lte=date_now, cost_date__gte=date_lte)
		if car_obj:
			car_costs = car_costs.filter(car=car_obj)
		if cost_item_obj:
			if cost_item_obj.get_childs():
				new_set = Car_cost.objects.none()
				for child in cost_item_obj.get_childs():
					new_set = new_set | car_costs.filter(cost_item=child)
				car_costs = new_set	
			else:	
				car_costs = car_costs.filter(cost_item=cost_item_obj)		

		cost_items = []
		for c_item in Cost_item.objects.exclude(slug=cost_item_obj_slug).order_by("title"):
			if c_item.is_category:
				cost_items.append(c_item)
		for c_item in Cost_item.objects.exclude(slug=cost_item_obj_slug).order_by("title"):
			if not c_item.is_category:
				cost_items.append(c_item)	


		context = {
				'car_costs': car_costs.order_by("-cost_date"),
				'total' : car_costs.aggregate(Sum('summ'))['summ__sum'],
				'date_now': date_now.strftime("%Y-%m-%d"),
				'date_lte': date_lte.strftime("%Y-%m-%d"),
				'cars': Car.objects.exclude(slug=car_obj_slug).order_by("car_number"),
				'cost_items': cost_items,
				'cost_items_with_parent': Cost_item.objects.filter(is_category=False).order_by('title'),
				'car' : car_obj,
				'cost_item' : cost_item_obj,
			}

		return render(request, 'taxiapp/car_costs.html', context)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def car_costs_add_new(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:
		
		if request.method == 'POST':

			car_cost_form = Car_cost_form(request.POST)

			if car_cost_form.is_valid():

				if car_cost_form.cleaned_data['cost_date']:
					cost_date = car_cost_form.cleaned_data['cost_date']
				else:
					cost_date = datetime.today()

				if car_cost_form.cleaned_data['cost_num']:
					cost_num = car_cost_form.cleaned_data['cost_num']
				else:
					cost_num = ''	

				car = car_cost_form.cleaned_data['car']

				if car:
					car_obj = Car.objects.filter(car_number=car).first()
				else:
					car_obj = None

				cost_item = car_cost_form.cleaned_data['cost_item']

				if cost_item:
					cost_item_obj = Cost_item.objects.filter(title=cost_item).first()
				else:
					cost_item_obj = None

				summ = float(car_cost_form.cleaned_data['summ'].replace(',','.'))

				if car_cost_form.cleaned_data['comment']:
					comment = car_cost_form.cleaned_data['comment']
				else:
					comment = ''

				new_car_cost = Car_cost(
						cost_date=cost_date,
						cost_num=cost_num,
						car=car_obj,
						cost_item=cost_item_obj,
						summ=summ,
						comment=comment,
					)
				new_car_cost.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)
		else:

			current_path = request.META['HTTP_REFERER']
			return redirect(current_path)
	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def car_costs_edit(request, car_cost_slug):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:
		
		if request.method == 'POST':

			car_cost_form = Car_cost_form(request.POST)

			if car_cost_form.is_valid():

				if car_cost_form.cleaned_data['cost_date']:
					cost_date = car_cost_form.cleaned_data['cost_date']
				else:
					cost_date = datetime.today()

				if car_cost_form.cleaned_data['cost_num']:
					cost_num = car_cost_form.cleaned_data['cost_num']
				else:
					cost_num = ''	

				car = car_cost_form.cleaned_data['car']

				if car:
					car_obj = Car.objects.filter(car_number=car).first()
				else:
					car_obj = None

				cost_item = car_cost_form.cleaned_data['cost_item']

				if cost_item:
					cost_item_obj = Cost_item.objects.filter(title=cost_item).first()
				else:
					cost_item_obj = None

				if car_cost_form.cleaned_data['summ']:
					summ = float(car_cost_form.cleaned_data['summ'].replace(',','.'))
				else:
					summ = 0

				if car_cost_form.cleaned_data['comment']:
					comment = car_cost_form.cleaned_data['comment']
				else:
					comment = ''

				editable_car_cost = Car_cost.objects.get(slug=car_cost_slug)

				if editable_car_cost.cost_date != cost_date:
					editable_car_cost.cost_date = cost_date

				if editable_car_cost.cost_num != cost_num:
					editable_car_cost.cost_num = cost_num

				if editable_car_cost.car != car_obj:
					editable_car_cost.car = car_obj

				if editable_car_cost.cost_item != cost_item_obj:
					editable_car_cost.cost_item = cost_item_obj

				if editable_car_cost.summ != summ:
					editable_car_cost.summ = summ

				if editable_car_cost.comment != comment:
					editable_car_cost.comment = comment		

				editable_car_cost.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)
		else:

			current_path = request.META['HTTP_REFERER']
			return redirect(current_path)
	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')


def taxi_show_cost_report(request):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()
	users_in_group_collector = Group.objects.get(name="taxicollector").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group or request.user in users_in_group_collector):

		if request.method == 'POST':

			period_form = PeriodForm(request.POST)

			if period_form.is_valid():

				trip_start 		= period_form.cleaned_data['trip_start'] + ' 00:00:01'
				trip_end 		= period_form.cleaned_data['trip_end'] + ' 23:59:59'

				date_lte 	= datetime.strptime(trip_start, '%Y-%m-%d %H:%M:%S')
				date_now	= datetime.strptime(trip_end, '%Y-%m-%d %H:%M:%S')

				car = period_form.cleaned_data['car']

				if car:
					car_obj = Car.objects.filter(car_number=car).first()
				else:
					car_obj = None

				cost_item = period_form.cleaned_data['cost_item']

				if cost_item:
					cost_item_obj = Cost_item.objects.filter(title=cost_item).first()
				else:
					cost_item_obj = None

			else:

				messages.info(request, '???? ???????????? ???????????? ????????????!!')
				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)	

		else:

			car_obj = None
			cost_item_obj = None
			date_now    =   timezone.now()

			if date_now.day > 7:

				date_lte 	= 	date_now.replace(day = int(date_now.day - 7))

			else:	

				date_lte 	= 	date_now.replace(day = int(date_now.day + 30 - 7))

				if date_now.month > 1:

					date_lte 	= 	date_lte.replace(month = int(date_lte.month - 1))

				else:

					date_lte 	= 	date_lte.replace(month = int(date_lte.month + 12 - 1))
					date_lte 	= 	date_lte.replace(year = int(date_lte.year - 1))
					

		car_obj_slug = car_obj.slug if car_obj else ''
		cost_item_obj_slug = cost_item_obj.slug if cost_item_obj else ''


		car_costs = Car_cost.objects.filter(cost_date__lte=date_now, cost_date__gte=date_lte)
		if car_obj:
			car_costs = car_costs.filter(car=car_obj)
		if cost_item_obj:
			if cost_item_obj.get_childs():
				new_set = Car_cost.objects.none()
				for child in cost_item_obj.get_childs():
					new_set = new_set | car_costs.filter(cost_item=child)
				car_costs = new_set
			else:
				car_costs = car_costs.filter(cost_item=cost_item_obj)

		cost_items = []
		for c_item in Cost_item.objects.exclude(slug=cost_item_obj_slug).order_by("title"):
			if c_item.is_category:
				cost_items.append(c_item)
		for c_item in Cost_item.objects.exclude(slug=cost_item_obj_slug).order_by("title"):
			if not c_item.is_category:
				cost_items.append(c_item)

		costs = []
		cars_list = []
		for item in car_costs.order_by('car__car_number'):
			if item.car not in cars_list:
				temp_list = []
				cost_item_list = []
				for i in car_costs.filter(car=item.car).order_by('car__car_number'):
					if i.cost_item.parent_item and i.cost_item.parent_item not in cost_item_list:
						temp_list.append([
							i.cost_item.parent_item,
							get_total_cost_items(car_costs.filter(car=i.car, cost_item__parent_item=i.cost_item.parent_item)),
							car_costs.filter(car=i.car, cost_item__parent_item=i.cost_item.parent_item).aggregate(Sum('summ'))['summ__sum']
							])
						cost_item_list.append(i.cost_item.parent_item)
					elif not i.cost_item.parent_item and i.cost_item not in cost_item_list:
						temp_list.append([
							'',
							list(car_costs.filter(car=i.car, cost_item=i.cost_item)),
							])
						cost_item_list.append(i.cost_item)	

				costs.append([
					item.car,
					temp_list,
					car_costs.filter(car=item.car).order_by('cost_item').aggregate(Sum('summ'))['summ__sum']
					])
				cars_list.append(item.car)

		print(costs)

		context = {
				'total' : car_costs.aggregate(Sum('summ'))['summ__sum'],
				'date_now': date_now.strftime("%Y-%m-%d"),
				'date_lte': date_lte.strftime("%Y-%m-%d"),
				'cars': Car.objects.exclude(slug=car_obj_slug).order_by("car_number"),
				'cost_items': cost_items,
				'cost_items_with_parent': Cost_item.objects.filter(is_category=False).order_by('title'),
				'car' : car_obj,
				'cost_item' : cost_item_obj,
				'total': car_costs.aggregate(Sum('summ'))['summ__sum'],
				'costs': costs,
			}

		return render(request, 'taxiapp/cost_report.html', context)

	else:

		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')



def get_total_cost_items(in_queryset):

	out_list = []

	for item in in_queryset:

		out_list.append([item.cost_item.title, in_queryset.filter(cost_item=item.cost_item).aggregate(Sum('summ'))['summ__sum']])


	return(out_list)	

#admin services
def taxi_admin_service_menu(request):
	
	if request.user.is_superuser:

		context = {

		}

		return render(request, 'taxiapp/admin_services/menu.html', context)
	else:
		messages.info(request, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????? ?? ???????????? ????????????! ???????????????????? ?? ????????????????????????????!')
		return render(request, 'authapp/login.html')

def service_upload_working_day(request, input_date):

	if request.user.is_superuser:

		drivers = Driver.objects.filter(active=True)
		current_date = datetime.strptime(input_date, "%Y-%m-%d")
		today = datetime.weekday(current_date)

		for driver in drivers:

			try:

				wd = Working_day.objects.get(driver=driver, date=current_date)

			except:

				if today == 0:
					if driver.monday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				elif today == 1:
					if driver.tuesday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				elif today == 2:
					if driver.wednesday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				elif today == 3:
					if driver.thursday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				elif today == 4:
					if driver.friday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				elif today == 5:
					if driver.saturday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				elif today == 6:
					if driver.sunday == True:
						dr_rate = driver.rate
					else:
						dr_rate = 0

				else:
					dr_rate = 0

				new_working_day = Working_day(driver=driver,date=current_date,rate=dr_rate,fuel=0,penalties=0,cash=0,cash_card=0,cashless=0,)
				new_working_day.save()

		return HttpResponse('200')		

	return HttpResponse('500')

def service_upload_yandex(request, input_date):

	if request.user.is_superuser:
		
		driver_url = 'https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list'
		dr_headers = {'Accept-Language': 'ru',
				'X-Client-ID': config('YA_X_CLIENT_ID'),
				'X-API-Key': config('YA_X_API_KEY')}

		driver_data = {
					"fields": {

						"account": [],
						"car": [],
						"park": []
					},
					"query": {
						"park": {
							"id": config('YA_ID')
						},
					},

		}

		for i in range(10):
			time.sleep(2)
			answer = requests.post(driver_url, headers=dr_headers, data=json.dumps(driver_data),)
			if answer.status_code == 200:
				break

		response = answer.json()
		profiles = response.get('driver_profiles')	
		missing_drivers = []
		current_date = datetime.strptime(input_date, "%Y-%m-%d")

		summ_of_transactions = 0
		num_of_transactions = 0

		for p in profiles:
			
			driver = (p.get('driver_profile'))
			dr_license = driver.get('driver_license')

			n = current_date
			n = n.replace(hour=0, minute=1)
			y = n + timedelta(days=1)
			y = y.replace(hour=0,minute=1)

			fromTime         =   n.isoformat() + '+00:00'
			toTime   =   y.isoformat() + '+00:00'

			url = 'https://fleet-api.taxi.yandex.net/v2/parks/driver-profiles/transactions/list'
			headers = {'Accept-Language': 'ru',
					'X-Client-ID': config('YA_X_CLIENT_ID'),
					'X-API-Key': config('YA_X_API_KEY')}

			data = {
						"query": {
								"park": {
										"driver_profile": {
										"id": driver['id']
										},
									"id": config('YA_ID'),
									"transaction": {
											"category_ids": ['partner_service_manual',],
											"event_at": {
											"from": fromTime,
											"to": toTime
											}
									}
								}
						}

			}

			for i in range(20):

				answer = requests.post(url, headers=headers, data=json.dumps(data),)
				if answer.status_code == 200:
					time.sleep(3)
					break

				time.sleep(i*3)

			response = answer.json()
			transactions = response.get('transactions')
			
			if transactions:

				for key in transactions:
					taxidriver = Driver.objects.filter(driver_license=dr_license['number']).first()
					if taxidriver:
						working_day = Working_day.objects.filter(driver=taxidriver, date=current_date).first()
						if working_day:
							working_day.cashless = working_day.cashless + Decimal(abs(float(key['amount'])))
							working_day.save()
						else:
							working_day = Working_day.objects.filter(driver=taxidriver).last()
							if working_day:
								working_day.cashless = working_day.cashless + Decimal(abs(float(key['amount'])))
								working_day.save()
							else:
								missing_drivers.append([dr_license['number'], driver.get('last_name'), driver.get('first_name'), driver.get('middle_name'), key['amount'], True,])
								continue	

						summ_of_transactions    += Decimal(abs(float(key['amount'])))
						num_of_transactions     += 1

					else:
						missing_drivers.append([dr_license['number'], driver.get('last_name'), driver.get('first_name'), driver.get('middle_name'), key['amount'], False,])

		if num_of_transactions:

			service_send_mail(missing_drivers, current_date, summ_of_transactions, num_of_transactions)


		return HttpResponse('200')
	
	return HttpResponse('500')


def service_send_mail(missing_drivers, day_before_today, summ_of_transactions, num_of_transactions):


    HOST = "mail.hosting.reg.ru"
    sender_email = config('MAIL_USER')
    receiver_email = ['info@annasoft.ru', 'cherbadgi_sn@mail.ru', 'kzamesova@mail.ru', ]
    password = config('MAIL_PASSWORD')

     
    message = MIMEMultipart("alternative")
    message["Subject"] = "?????????? ???? ???????????????? ???? ???????????? ???? {}".format(day_before_today.strftime("%Y-%m-%d"))
    message["From"] = sender_email
    message["To"] = ','.join(receiver_email)
    
    test_text = ""
    if missing_drivers:
        for item in missing_drivers:
            no_working_days = '??????'
            if item[5]:
               no_working_days = '????'
            test_text += "<p>{} {} {} {}, ?????????? : {}, ?????? ?????????????? ????????: {}</p>".format(item[0], item[1], item[2], item[3], item[4], no_working_days)

        text = """\
        {}""".format(test_text)
         
        html = """\
        <html>
          <body>
            <H3>{1} ?????????????????? {3} ???????????????????? ???? ?????????? {2}??. </H3>

            <H3>???????????? ??????????????????, ?????????????? ???? ?????????????? ?? ???????? ????????????: </H3>
               {0}
            <p>???????????? ???? ?????????????????????? ???????? ?????????????????? ???? {1} ???????????????????? ?????????????????? ??????????????!</p>
          </body>
        </html>
        """.format(test_text, day_before_today.strftime("%Y-%m-%d"), summ_of_transactions.quantize(Decimal("1.00")), num_of_transactions)

    else:

        text = """\
        """
        
        html = """\
        <html>
          <body>
            <H3>{0} ?????????????????? {2} ???????????????????? ???? ?????????? {1}??. </H3>
          </body>
        </html>
        """.format(day_before_today.strftime("%Y-%m-%d"), summ_of_transactions.quantize(Decimal("1.00")), num_of_transactions)
     
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
     
    message.attach(part1)
    message.attach(part2)
    
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(HOST, 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email , message.as_string())
        server.quit()

        log_file = open(os.path.abspath(config('LOG_FILE_PATH')), 'a+')
        log_file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ?????????????????? ???????????????????? ' + str(num_of_transactions)  + ' ???? ?????????? ' + str(summ_of_transactions.quantize(Decimal("1.00"))) + ', ???????????? ????????????????????!'   + '\n')
        log_file.close()

    except Exception as e: 
        log_file = open(os.path.abspath(config('LOG_FILE_PATH')), 'a+')
        log_file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ?????????????????? ???????????????????? ' + str(num_of_transactions)  + ' ???? ?????????? ' + str(summ_of_transactions.quantize(Decimal("1.00"))) + ' ???????????? ?????????????????? ???? ??????????????. ?????? ????????????: ' + str(e) + '\n')
        log_file.close()
