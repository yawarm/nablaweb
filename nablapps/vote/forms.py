from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from .models import Alternative, Voting

AlternativeFormset = inlineformset_factory(
    Voting, Alternative, fields=("text",), can_delete=False
)
