# forms.py
from django import forms
from .models import MemberDetails

class L3ReachabilityForm(forms.Form):
    member = forms.ModelChoiceField(queryset=MemberDetails.objects.all().order_by('name')) 
    ip_address_or_hostname = forms.CharField(max_length=500)

        
        