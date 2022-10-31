from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from .forms import WorkingDayForm
from taxiapp.models import Driver
from taxiapp.models import Working_day
from django.contrib.auth.models import Group
from django.contrib				import messages



def working_day_add(request, driver_slug):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:

		driver = Driver.objects.get(slug=driver_slug)

		if request.method == 'POST':

			day_form = WorkingDayForm(request.POST)


			if day_form.is_valid():

				if day_form.cleaned_data['input_date']:
					date = day_form.cleaned_data['input_date']
				else:
					date = datetime.now()

				if day_form.cleaned_data['input_rate']:
					rate = Decimal(day_form.cleaned_data['input_rate'].replace(',','.'))
				else:
					rate = 0

				if day_form.cleaned_data['input_fuel']:
					fuel = Decimal(day_form.cleaned_data['input_fuel'].replace(',','.'))
				else:
					fuel = 0

				if day_form.cleaned_data['input_penalties']:
					penalties = Decimal(day_form.cleaned_data['input_penalties'].replace(',','.'))
				else:
					penalties = 0	
							
				if day_form.cleaned_data['input_cash']:
					cash = Decimal(day_form.cleaned_data['input_cash'].replace(',','.'))
				else:
					cash = 0

				if day_form.cleaned_data['input_cash_card']:
					cash_card = Decimal(day_form.cleaned_data['input_cash_card'].replace(',','.'))
				else:
					cash_card = 0	

				if day_form.cleaned_data['input_cashless']:
					cashless = Decimal(day_form.cleaned_data['input_cashless'].replace(',','.'))
				else:
					cashless = 0	
				
				new_working_day = Working_day(
					driver=driver,
					date=date,
					rate=rate,
					fuel=fuel,
					penalties=penalties,
					cash=cash,
					cash_card=cash_card,
					cashless=cashless,
					)

				new_working_day.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)
		else:

			current_path = request.META['HTTP_REFERER']
			return redirect(current_path)	
	else:

		messages.info(request, 'У Вас не достаточно прав для доступа в данный раздел! Обратитесь к администратору!')
		return render(request, 'authapp/login.html')		


def working_day_edit(request, day_slug):

	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and request.user in users_in_group:

		working_day = Working_day.objects.get(slug=day_slug)

		if request.method == 'POST':

			day_form = WorkingDayForm(request.POST)

			if day_form.is_valid():

				if day_form.cleaned_data['input_rate']:
					working_day.rate = Decimal(day_form.cleaned_data['input_rate'].replace(',','.'))
				else:
					working_day.rate = 0

				if day_form.cleaned_data['input_fuel']:
					working_day.fuel = Decimal(day_form.cleaned_data['input_fuel'].replace(',','.'))
				else:
					working_day.fuel = 0

				if day_form.cleaned_data['input_penalties']:
					working_day.penalties = Decimal(day_form.cleaned_data['input_penalties'].replace(',','.'))
				else:
					working_day.penalties = 0	
							
				if day_form.cleaned_data['input_cash']:
					working_day.cash = Decimal(day_form.cleaned_data['input_cash'].replace(',','.'))
				else:
					working_day.cash = 0

				if day_form.cleaned_data['input_cash_card']:
					working_day.cash_card = Decimal(day_form.cleaned_data['input_cash_card'].replace(',','.'))
				else:
					working_day.cash_card = 0	

				if day_form.cleaned_data['input_cashless']:
					working_day.cashless = Decimal(day_form.cleaned_data['input_cashless'].replace(',','.'))
				else:
					working_day.cashless = 0	

				working_day.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)
		else:

			current_path = request.META['HTTP_REFERER']
			return redirect(current_path)

	else:

		messages.info(request, 'У Вас не достаточно прав для доступа в данный раздел! Обратитесь к администратору!')
		return render(request, 'authapp/login.html')			


def working_day_delete(request, day_slug):

	pass