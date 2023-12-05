from django import forms
 
class NewDriverForm(forms.Form):

	first_name  	= forms.CharField(max_length = 30)
	last_name  		= forms.CharField(max_length = 30)
	third_name  	= forms.CharField(max_length = 30, required=False)
	driver_license 	= forms.CharField(max_length = 15, required=False)
	fuel_card 		= forms.CharField(max_length = 30, required=False)
	fuel_card_2 	= forms.CharField(max_length = 30, required=False)
	email	 		= forms.CharField(max_length = 30, required=False)
	rate			= forms.CharField(max_length = 15)

	active 			= forms.BooleanField(required=False)

	monday 			= forms.BooleanField(required=False)
	tuesday 		= forms.BooleanField(required=False)
	wednesday 		= forms.BooleanField(required=False)
	thursday 		= forms.BooleanField(required=False)
	friday 			= forms.BooleanField(required=False)
	saturday 		= forms.BooleanField(required=False)
	sunday 			= forms.BooleanField(required=False)
	car_obj			= forms.CharField(max_length = 10, required=False)
	
class PeriodForm(forms.Form):

	trip_start  	= forms.CharField(max_length = 12)
	trip_end  		= forms.CharField(max_length = 12)
	cost_item		= forms.CharField(max_length = 50, required=False)
	car 			= forms.CharField(max_length = 12, required=False)


class Gas_upload(forms.Form):

	gas_file 		= forms.FileField()
	optiongas		= forms.CharField(max_length = 32)


class Car_cost_form(forms.Form):

	car 		= forms.CharField(max_length = 10, required=False)
	cost_item	= forms.CharField(max_length = 50, required=False)
	cost_date	= forms.DateField(required=False)
	cost_num	= forms.CharField(max_length = 20, required=False)
	summ		= forms.CharField(max_length = 15, required=False)
	comment		= forms.CharField(max_length = 200, required=False)
	parent_cost_item	= forms.CharField(max_length = 50, required=False)
	is_category = forms.BooleanField(required=False)

class Yandex_upload_form(forms.Form):
	date = forms.DateField()