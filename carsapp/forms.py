from django import forms

class CarForm(forms.Form):

	input_car_number  			= forms.CharField(max_length = 10)
	input_car_brand  			= forms.CharField(max_length = 20, required=False)
	input_car_model  			= forms.CharField(max_length = 20, required=False)
