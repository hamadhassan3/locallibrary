import datetime
import uuid
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Book, BookInstance, Language, Genre, Author
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.models import Author
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


    # The number of visits on this page are stored in session and incremented on each visit

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    cookie_support_exists = 'No cookie support.'    # String that tells if cookie support exists

    # Testing if sessions are supported by the browser.
    # The result of the test is received the second time that the user opens the page

    if request.session.test_cookie_worked():

        cookie_support_exists = 'Cookie support exists!'

        # The cookie is deleted after testing
        request.session.delete_test_cookie()

    request.session.set_test_cookie()



    # The count of each item is stored in the context so that the page can be populated

    context = {
        'count_of_books': count_of_books,
        'count_of_authors': count_of_authors,
        'count_of_genres': count_of_genres,
        'count_of_languages': count_of_languages,
        'count_of_bookinstances': count_of_bookinstance,
        'count_of_available_books': count_of_available_books,
        'num_visits': num_visits,
        'cookie_support': cookie_support_exists,
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
    paginate_by = 10




class AuthorDetailView(generic.DetailView):
    """The detail view for author model"""

    model = Author
    paginate_by = 1


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet:
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllLoanedBooks(PermissionRequiredMixin, generic.ListView):
    """Displays all books to users with permission"""
    model = BookInstance
    template_name ='catalog/bookinstance_list_all_borrowed_librarian.html'
    paginate_by = 10

    # The user must have these permissions to access this functionality
    permission_required = 'catalog.can_mark_returned'


    def get_queryset(self) -> QuerySet:
        """There is no filter on user id so all books are fetched"""

        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'
    

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'
