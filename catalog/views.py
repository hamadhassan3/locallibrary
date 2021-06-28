from django.shortcuts import render
from .models import Book, BookInstance, Language, Genre, Author
from django.views import generic
from django.http import HttpResponse, HttpRequest



def index(request: HttpRequest) -> HttpResponse:
    """This function handles the request for home page
    The home page displays the count of all items in library
    """

    # Storing the count of each type of item
    
    count_of_books = Book.objects.all().count()
    count_of_authors = Author.objects.all().count()
    count_of_genres = Genre.objects.all().count()
    count_of_languages = Language.objects.all().count()
    count_of_bookinstance = BookInstance.objects.all().count()

    # Storing available books count

    count_of_available_books = BookInstance.objects.all().filter(status__exact='a').count()

    # The count of each item is stored in the context so that the page can be populated

    context = {
        'count_of_books': count_of_books,
        'count_of_authors': count_of_authors,
        'count_of_genres': count_of_genres,
        'count_of_languages': count_of_languages,
        'count_of_bookinstances': count_of_bookinstance,
        'count_of_available_books': count_of_available_books,
    }


    return render(request, 'index.html', context)




class BookListView(generic.ListView):
    """The list view for Book model"""

    model = Book
    paginate_by = 2



class BookDetailView(generic.DetailView):
    """The detail view for Book model"""

    model = Book




class AuthorListView(generic.ListView):
    """The list view for author model"""

    model = Author




class AuthorDetailView(generic.DetailView):
    """The detail view for author model"""

    model = Author
    paginate_by = 1

