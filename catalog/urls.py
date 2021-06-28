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

]
