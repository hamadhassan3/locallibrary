import datetime
from django.test import TestCase
from catalog.models import Author, Genre, Book, BookInstance, Language
from django.contrib.auth.models import User
from django.utils import timezone


class AuthorModelTest(TestCase):
    """Tests the author model"""

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name="Big", last_name="Bob")

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("first_name").verbose_name
        self.assertEqual(field_label, "first name")

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("date_of_death").verbose_name
        self.assertEqual(field_label, "died")

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f"{author.last_name}, {author.first_name}"
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), "/catalog/author/1")


class GenreModelTest(TestCase):
    """Tests the genre model"""

    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name="Fiction")

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_genre_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)

    def test_genre_str(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEqual(str(genre), expected_object_name)


class LanguageModelTest(TestCase):
    """Tests the language model"""

    @classmethod
    def setUpTestData(cls):
        Language.objects.create(language="English")

    def test_name_label(self):
        language = Language.objects.get(id=1)
        field_label = language._meta.get_field("language").verbose_name
        self.assertEqual(field_label, "language")

    def test_language_max_length(self):
        language = Language.objects.get(id=1)
        max_length = language._meta.get_field("language").max_length
        self.assertEqual(max_length, 100)

    def test_genre_str(self):
        language = Language.objects.get(id=1)
        expected_object_name = language.language
        self.assertEqual(str(language), expected_object_name)


class BookModelTest(TestCase):
    """Tests the Book model"""

    @classmethod
    def setUpTestData(cls):
        test_author = Author.objects.create(first_name="Big", last_name="Bog")
        test_genre1 = Genre.objects.create(name="Fiction")
        test_genre2 = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(language="English")

        test_book = Book.objects.create(
            title="title",
            author=test_author,
            language=test_language,
            summary="Book Summary",
            isbn="1234567891231",
        )

        test_book.genre.set([test_genre1, test_genre2])
        test_book.save()

    def test_book_title(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.title, "title")

    def test_book_author(self):
        book = Book.objects.get(id=1)
        author = Author.objects.get(id=1)
        self.assertEqual(book.author, author)

    def test_book_isbn(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.isbn, "1234567891231")

    def test_book_summary(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.summary, "Book Summary")

    def test_book_language(self):
        book = Book.objects.get(id=1)
        language = Language.objects.get(id=1)
        self.assertEqual(book.language, language)

    def test_book_genre(self):
        book = Book.objects.get(id=1)

        # Since there is only one genre in database, fetching the first genre is enough
        genre = Genre.objects.all().first()

        self.assertEqual(book.genre.first(), genre)

    def test_book_str(self):
        book = Book.objects.get(id=1)
        self.assertEqual(str(book), book.title)

    def test_display_genre(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.display_genre(), "Fiction, Fantasy")

    def test_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_absolute_url(), "/catalog/book/1")


class BookInstanceModelTest(TestCase):
    """Tests Book Instance Model"""

    @classmethod
    def setUpTestData(cls) -> None:

        # This user object will be used as a borrower for book
        test_user = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user.save()

        test_author = Author.objects.create(first_name="Big", last_name="Bog")
        test_genre1 = Genre.objects.create(name="Fiction")
        test_genre2 = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(language="English")

        test_book = Book.objects.create(
            title="title",
            author=test_author,
            language=test_language,
            summary="Book Summary",
            isbn="1234567891231",
        )

        test_book.genre.set([test_genre1, test_genre2])
        test_book.save()

        # Creating a book instance which is not overdue
        BookInstance.objects.create(
            id=1,
            book=test_book,
            imprint="Imprint",
            due_back=timezone.localtime() + datetime.timedelta(days=1),
            borrower=test_user,
        )

        # Creating a book instance which is overdue
        BookInstance.objects.create(
            id=2,
            book=test_book,
            imprint="Imprint",
            due_back=timezone.localtime() - datetime.timedelta(days=1),
            borrower=test_user,
        )

    def test_is_overdue_when_overdue(self):
        """Tests that an overdue book returns True when asked for overdue propery"""

        book_instance = BookInstance.objects.get(id=2)
        self.assertTrue(book_instance.is_overdue)

    def test_is_not_overdue_when_not_overdue(self):
        """Tests that a book that is not overdue returns False when asked for overdue propery"""

        book_instance = BookInstance.objects.get(id=1)
        self.assertFalse(book_instance.is_overdue)

    def test_book_instance_str(self):
        book_instance = BookInstance.objects.get(id=1)
        self.assertEqual(
            str(book_instance),
            "{} ({})".format(book_instance.id, book_instance.book.title),
        )

    def test_book_details(self):
        book_instance = BookInstance.objects.get(id=1)
        self.assertEqual(book_instance.book_details(), "title")
