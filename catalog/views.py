from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Book, BookInstance, Language, Genre, Author
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

def index(request):
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
