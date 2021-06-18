from django.contrib import admin

from .models import Book, BookInstance, Author, Language, Genre



# The models are registered here so that they can be populated by admin site
# All models that are registered here are accessible through admin site

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)