from django.urls import path
from . import views

urlpatterns = [

    # The home page address is added here
    path('', views.index, name='index'),

    # The address to book list page
    path('books/', views.BookListView.as_view(), name='books'),

    # The address to a specific book's details
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),

    # The address to author list page
    path('authors/', views.AuthorListView.as_view(), name='authors'),

    # The address to a specific author's details
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),

    # The address to borrowed books of a user
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),


    # The address to all borrowed books
    path('allbooks/', views.AllLoanedBooks.as_view(), name='all-borrowed'),


    # The address to a form where books can be renewed
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),



]


urlpatterns += [


    #Author create, update and delete forms
    
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]


urlpatterns += [


    #Book create, update and delete forms
    
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]


