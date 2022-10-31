from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from taxiapp.models import Car
from .forms import CarForm

def show_cars(request):
	
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group):

		cars = Car.objects.all()

		context = {

				'cars': cars,

		}

		return render(request, 'carsapp/cars.html', context)

	else:
		
		return render(request, 'authapp/login.html')

	
def taxi_new_car(request):
	
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group):

		if request.method == 'POST':

			car_form = CarForm(request.POST)

			if car_form.is_valid():

				if car_form.cleaned_data['input_car_number']:
					car_number = car_form.cleaned_data['input_car_number']
				else:
					car_number = ''

				if car_form.cleaned_data['input_car_brand']:
					car_brand = car_form.cleaned_data['input_car_brand']
				else:
					car_brand = ''

				if car_form.cleaned_data['input_car_model']:
					car_model = car_form.cleaned_data['input_car_model']
				else:
					car_model = ''

				new_car = Car(

						car_number=car_number,
						car_brand=car_brand,
						car_model=car_model,

					)

				new_car.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)

		current_path = request.META['HTTP_REFERER']
		return redirect(current_path)

	else:
		
		return render(request, 'authapp/login.html')

def taxi_edit_car(request, slug):
	
	users_in_group = Group.objects.get(name="taxiadmin").user_set.all()

	if request.user.is_authenticated and (request.user in users_in_group):

		if request.method == 'POST':

			car_form = CarForm(request.POST)

			if car_form.is_valid():

				car = Car.objects.get(slug=slug)

				if car_form.cleaned_data['input_car_number']:
					car.car_number = car_form.cleaned_data['input_car_number']
				else:
					car.car_number = ''

				if car_form.cleaned_data['input_car_brand']:
					car.car_brand = car_form.cleaned_data['input_car_brand']
				else:
					car.car_brand = ''

				if car_form.cleaned_data['input_car_model']:
					car.car_model = car_form.cleaned_data['input_car_model']
				else:
					car.car_model = ''

				car.save()

				current_path = request.META['HTTP_REFERER']
				return redirect(current_path)

		current_path = request.META['HTTP_REFERER']
		return redirect(current_path)

	else:
		
		return render(request, 'authapp/login.html')		
