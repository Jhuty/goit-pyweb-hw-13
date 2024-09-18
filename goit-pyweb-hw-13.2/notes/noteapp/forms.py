from django.forms import ModelForm, CharField, TextInput
from .models import Tag, Note, Author  
from django import forms


class TagForm(ModelForm):

    name = CharField(min_length=3, max_length=25, required=True, widget=TextInput())
    
    class Meta:
        model = Tag
        fields = ['name']

class NoteForm(ModelForm):

    name = CharField(min_length=5, max_length=50, required=True, widget=TextInput())
    description = CharField(min_length=10, max_length=150, required=True, widget=TextInput())

    class Meta:
        model = Note
        fields = ['name', 'description']
        exclude = ['tags']
        # widgets = {'tags': format.CheckboxSelectMultiple}

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']