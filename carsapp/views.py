from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from taxiapp.models import Car
from .forms import CarForm

def show_cars(request):
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if not (request.user.is_authenticated and request.user in users_in_group):
		return render(request, 'authapp/login.html')

	cars = Car.objects.all().order_by('car_number')

	cars_paginator = Paginator(cars, 100)
	cars_page = cars_paginator.get_page(request.GET.get('page'))

	context = {
		'cars': cars_page,
		'cars_page_range': list(cars_paginator.get_elided_page_range(cars_page.number, on_each_side=2, on_ends=1)),
	}

	return render(request, 'carsapp/cars.html', context)

def taxi_new_car(request):
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if not (request.user.is_authenticated and request.user in users_in_group):
		return render(request, 'authapp/login.html')

	if request.method == 'POST':
		car_form = CarForm(request.POST)

		if car_form.is_valid():
			new_car = Car(
				car_number=car_form.cleaned_data['input_car_number'] or '',
				car_brand=car_form.cleaned_data['input_car_brand'] or '',
				car_model=car_form.cleaned_data['input_car_model'] or '',
			)
			new_car.save()

	current_path = request.META['HTTP_REFERER']
	return redirect(current_path)

def taxi_edit_car(request, slug):
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if not (request.user.is_authenticated and request.user in users_in_group):
		return render(request, 'authapp/login.html')

	if request.method == 'POST':
		car_form = CarForm(request.POST)

		if car_form.is_valid():
			car = Car.objects.get(slug=slug)
			car.car_number = car_form.cleaned_data['input_car_number'] or ''
			car.car_brand = car_form.cleaned_data['input_car_brand'] or ''
			car.car_model = car_form.cleaned_data['input_car_model'] or ''
			car.save()

	current_path = request.META['HTTP_REFERER']
	return redirect(current_path)
