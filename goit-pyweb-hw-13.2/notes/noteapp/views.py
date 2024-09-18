from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TagForm, NoteForm, AuthorForm
from .models import Tag, Note, Author
from django.contrib import messages
from quotes.models import Quote


# Create your views here.
@login_required
def tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            tag.user = request.user
            tag.save()
            messages.success(request, 'Tag added successfully!')
            return redirect(to='noteapp:main')
        else:
            messages.error(request, 'Form is not valid.')
            return render(request, 'noteapp/tag.html', {'form': form})

    return render(request, 'noteapp/tag.html', {'form': TagForm()})

@login_required
def note(request):
    tags = Tag.objects.filter(user=request.user).all()

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            new_note = form.save(commit=False)
            new_note.user = request.user
            new_note.save()
            choice_tags = Tag.objects.filter(name__in=request.POST.getlist('tags'), user=request.user)
            for tag in choice_tags.iterator():
                new_note.tags.add(tag)

            return redirect(to='noteapp:main')
        else:
            return render(request, 'noteapp/note.html', {"tags": tags, 'form': form})

    return render(request, 'noteapp/note.html', {"tags": tags, 'form': NoteForm()})


@login_required
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('authors_list') 
    else:
        form = AuthorForm()
    return render(request, 'noteapp/add_author.html', {'form': form})

def author_list(request):
    authors = Author.objects.all()
    return render(request, 'noteapp/author_list.html', {'authors': authors})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'noteapp/author_detail.html', {'author': author})

@login_required
def detail(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    return render(request, 'noteapp/detail.html', {"note": note})

@login_required
def set_done(request, note_id):
    Note.objects.filter(pk=note_id, user=request.users).update(done=True)
    return redirect(to='noteapp:main')

@login_required
def delete_note(request, note_id):
    Note.objects.get(pk=note_id, user=request.user).delete()
    return redirect(to='noteapp:main')


def main(request):
    notes = Note.objects.filter(user=request.user).all() if request.user.is_authenticated else []
    quotes = Quote.objects.all()
    return render(request, 'noteapp/index.html', {"notes": notes, "quotes": quotes})
