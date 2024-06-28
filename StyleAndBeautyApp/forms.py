from django import forms
from StyleAndBeautyApp.models import *


class ClientRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'sur_name', 'contact_number']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"]
        )
        client = super().save(commit=False)
        client.user = user
        if commit:
            client.save()
        return client


class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'sur_name', 'contact_number']


class ServiceSearchForm(forms.Form):
    query = forms.CharField(label='Поиск', max_length=100)


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['date', 'time', 'service', 'master']
