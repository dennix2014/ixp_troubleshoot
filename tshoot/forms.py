# forms.py
from django import forms
from .models import MemberDetails, Switch

class L3ReachabilityForm(forms.Form):
    member = forms.ModelChoiceField(queryset=MemberDetails.objects.all().order_by('name')) 
    ip_address_or_hostname = forms.CharField(max_length=500)

        
class SwitchForm(forms.ModelForm):
    class Meta:
        model = Switch
        fields = '__all__'


class MemberDetailsForm(forms.ModelForm):
    class Meta:
        model = MemberDetails
        fields = '__all__'


