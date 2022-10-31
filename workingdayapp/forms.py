from django import forms

class WorkingDayForm(forms.Form):

	input_date  			= forms.DateField(required=False)
	input_rate  			= forms.CharField(max_length = 50, required=False)
	input_fuel  			= forms.CharField(max_length = 50, required=False)
	input_penalties 		= forms.CharField(max_length = 50, required=False)
	input_cash				= forms.CharField(max_length = 50, required=False)
	input_cash_card			= forms.CharField(max_length = 50, required=False)
	input_cashless			= forms.CharField(max_length = 50, required=False)
