from django.contrib import admin

from .models import Book, BookInstance, Author, Language, Genre







class CatalogAdmin(admin.ModelAdmin):
    """This class extends every model admin class in the catalog
    It adds features that are common to all modeladmins
    """

    pass


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


class BookInline(admin.TabularInline):
    model = Book


@admin.register(Author)
class AuthorAdmin(CatalogAdmin):
    """Customizes how Author objects are displayed in admin portal"""

    # This inline allows inputting the books by an author directly from author form
    inlines = [BookInline]

    # Specifying which fields to display for author
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]


    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

@admin.register(Book)
class BookAdmin(CatalogAdmin):
    """Customizes how books appear in admin site"""


    # This inline allows adding book instance details while adding a book
    inlines = [BooksInstanceInline]


    # We cannot display genre directly, so we use display_genre function    
    list_display = ('title', 'author', 'display_genre')




@admin.register(BookInstance)
class BookInstanceAdmin(CatalogAdmin):
    
    # Book details are received using book_details function
    list_display = ('book_details', 'id', 'status', 'due_back')

    # We allow filtering options for admin site
    # The books are already sorted according to due_back date
    list_filter = ('status', 'due_back')



    # The details are separated into different sections
    fieldsets = (
        ('Book Details', {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )    

# The models are registered here so that they can be populated by admin site

admin.site.register(Genre)
admin.site.register(Language)
