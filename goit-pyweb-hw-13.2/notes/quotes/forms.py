from django import forms
from .models import Quote
from authors.models import Author

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author']  # Поля, которые включены в форму
        widgets = {
            'author': forms.Select(),
        }
    
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()