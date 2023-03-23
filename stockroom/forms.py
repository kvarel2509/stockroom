from django import forms


class GenerateDataForm(forms.Form):
	product_count = forms.IntegerField()
	stockroom_count = forms.IntegerField()
	client_count = forms.IntegerField()
