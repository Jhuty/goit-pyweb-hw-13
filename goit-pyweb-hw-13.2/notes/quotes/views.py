from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote
from django.http import HttpResponse
from noteapp.models import Note
from authors.models import Author


def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.user = request.user
            quote.save()
            return redirect('noteapp:main')
    else:
        form = QuoteForm()

    return render(request, 'quotes/add_quote.html', {'form': form})

def index(request):
    notes = Note.objects.all()
    quotes = Quote.objects.all()  # Получение всех цитат из базы данных
    return render(request, 'index.html', {'quotes': quotes})