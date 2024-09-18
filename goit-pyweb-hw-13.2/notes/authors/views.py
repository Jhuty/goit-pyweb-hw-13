from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Author, Quote
from .forms import AuthorForm

@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.user = request.user
            author.save()
            return redirect('authors:author_list') 
    else:
        form = AuthorForm()
    return render(request, 'authors/add_author.html', {'form': form})



def author_list(request):
    authors = Author.objects.all()  # Получаем всех авторов из базы данных
    return render(request, 'authors/author_list.html', {'authors': authors})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    quotes = Quote.objects.filter(author=author)
    return render(request, 'authors/author_detail.html', {'author': author})