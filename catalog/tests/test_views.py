import datetime
import uuid
from django.test import TestCase
from django.urls import reverse
from catalog.models import Author
from django.utils import timezone
from django.contrib.auth.models import User  # Required to assign User as a borrower
from catalog.models import BookInstance, Book, Genre, Language
from catalog.forms import RenewBookForm
from django.contrib.auth.models import (
    Permission,
)  # Required to grant the permission needed to set a book as returned.
from django.contrib.auth.decorators import permission_required


class IndexPageTest(TestCase):
    """Tests the home page"""

    @classmethod
    def setUpTestData(cls) -> None:
        """Tests authors view"""

        # Create 13 authors for pagination tests
        number_of_authors = 13
        number_of_genres = 12
        number_of_books = 18
        number_of_languages = 5
        number_of_book_instances = 55
        number_of_available_book_instances = 26

        authors = []
        genres = []
        languages = []
        books = []
        book_instances = []

        for author_id in range(number_of_authors):
            author = Author.objects.create(
                first_name=f"Christian {author_id}",
                last_name=f"Surname {author_id}",
            )

            authors.append(author)

        for genre_id in range(number_of_genres):
            genre = Genre.objects.create(name="genre" + str(genre_id))

            genres.append(genre)

        for language_id in range(number_of_languages):
            language = Language.objects.create(language="language" + str(language_id))

            languages.append(language)

        for book_id in range(number_of_books):
            book = Book.objects.create(
                title="title" + str(book_id),
                language=languages[0],
                summary="Summary",
                isbn="123123123123" + str(book_id),
            )

            book.genre.set(genres[0:3])
            books.append(book)

        counter = 0

        for book_instance_id in range(number_of_book_instances):

            if counter < number_of_available_book_instances:

                book_instance = BookInstance.objects.create(
                    book=books[0],
                    imprint="Imprint",
                    status="a",
                    due_back=timezone.localdate()
                    + datetime.timedelta(days=book_instance_id),
                )

            else:

                book_instance = BookInstance.objects.create(
                    book=books[0],
                    imprint="Imprint",
                    status="o",
                    due_back=timezone.localdate()
                    + datetime.timedelta(days=book_instance_id),
                )

            counter += 1

    def test_book_count(self):
        response = self.client.get(reverse("index", kwargs={}))
        count_of_books = response.context.get("count_of_books")
        self.assertEqual(count_of_books, 18)

    def test_author_count(self):
        response = self.client.get(reverse("index", kwargs={}))
        count_of_authors = response.context.get("count_of_authors")
        self.assertEqual(count_of_authors, 13)

    def test_book_instances_count(self):
        response = self.client.get(reverse("index", kwargs={}))
        count_of_book_instances = response.context.get("count_of_bookinstances")
        self.assertEqual(count_of_book_instances, 55)

    def test_available_book_instances_count(self):
        response = self.client.get(reverse("index", kwargs={}))
        count_of_available_book_instances = response.context.get(
            "count_of_available_books"
        )
        self.assertEqual(count_of_available_book_instances, 26)

    def test_languages_count(self):
        response = self.client.get(reverse("index", kwargs={}))
        count_of_languages = response.context.get("count_of_languages")
        self.assertEqual(count_of_languages, 5)

    def test_genres_count(self):
        response = self.client.get(reverse("index", kwargs={}))
        count_of_genres = response.context.get("count_of_genres")
        self.assertEqual(count_of_genres, 12)

    def test_number_of_visits(self):
        response1 = self.client.get(reverse("index"))
        self.assertEqual(self.client.session["num_visits"], 1)

        response2 = self.client.get(reverse("index"))
        self.assertEqual(self.client.session["num_visits"], 2)


class AuthorListViewTest(TestCase):
    """Tests authors view"""

    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f"Christian {author_id}",
                last_name=f"Surname {author_id}",
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/authors/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_list.html")

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["author_list"]), 10)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse("authors") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["author_list"]), 3)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name="John", last_name="Smith")
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(language="English")
        test_book = Book.objects.create(
            title="Book Title",
            summary="My book summary",
            isbn="ABCDEFG",
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(
            genre_objects_for_book
        )  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = "m"
            BookInstance.objects.create(
                book=test_book,
                imprint="Unlikely Imprint, 2016",
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("my-borrowed"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/mybooks/")

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))

        # Check our user is logged in
        self.assertEqual(str(response.context["user"]), "testuser1")
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(
            response, "catalog/bookinstance_list_borrowed_user.html"
        )


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name="John", last_name="Smith")
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(language="English")
        test_book = Book.objects.create(
            title="Book Title",
            summary="My book summary",
            isbn="ABCDEFG",
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(
            genre_objects_for_book
        )  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint="Unlikely Imprint, 2016",
            due_back=return_date,
            borrower=test_user1,
            status="o",
        )

        # Create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint="Unlikely Imprint, 2016",
            due_back=return_date,
            borrower=test_user2,
            status="o",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance2.pk})
        )

        # Check that it lets us login - this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )

        # Check that it lets us login. We're a librarian, so we can view any users book
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikely UID to match our bookinstance!
        test_uid = uuid.uuid4()
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": test_uid})
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "catalog/book_renew_librarian.html")

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(
            response.context["form"].initial["renewal_date"], date_3_weeks_in_future
        )

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse(
                "renew-book-librarian",
                kwargs={
                    "pk": self.test_bookinstance1.pk,
                },
            ),
            {"renewal_date": valid_date_in_future},
        )
        self.assertRedirects(response, reverse("all-borrowed"))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk}),
            {"renewal_date": date_in_past},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", "renewal_date", "Invalid date - renewal in past"
        )

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(
            reverse("renew-book-librarian", kwargs={"pk": self.test_bookinstance1.pk}),
            {"renewal_date": invalid_date_in_future},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            "form",
            "renewal_date",
            "Invalid date - renewal more than 4 weeks ahead",
        )


class CreateAuthorViewTest(TestCase):
    """This class tests the author creation form."""

    def setUp(self):
        """This method initializes test case an author and two users with different permissions."""

        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        """This method checks if user is redirected to login page
        when the user tries to access the url and is not logged in.
        """

        response = self.client.get(reverse("author-create", kwargs={}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """This method asserts that a 403 error message should be shown for a user that is
        logged in but does'nt have the permission to access the form.
        """

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("author-create", kwargs={}))
        self.assertEqual(response.status_code, 403)

    def test_uses_correct_template(self):
        """This method checks if the correct template is displayed to a logged in user with valid permissions."""

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("author-create", kwargs={}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "catalog/author_form.html")

    def test_redirects_to_all_author_list_on_success(self):
        """This method asserts that user should be redirected to author details page
        on successfully filling out the form.
        """

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        valid_first_name = "authorfirstname"
        valid_last_name = "authorlastname"
        valid_date_of_birth = datetime.date.today() - datetime.timedelta(weeks=96)
        valid_date_of_death = datetime.date.today()
        response = self.client.post(
            reverse("author-create", kwargs={}),
            {
                "first_name": valid_first_name,
                "last_name": valid_last_name,
                "date_of_birth": valid_date_of_birth,
                "date_of_death": valid_date_of_death,
            },
        )
        self.assertRedirects(response, reverse("author-detail", kwargs={"pk": 1}))


class UpdateAuthorViewTest(TestCase):
    """This class tests the author update form."""

    def setUp(self):
        """This method initializes test case for an author and two users with different permissions."""

        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name="John", last_name="Smith")

    def test_redirect_if_not_logged_in(self):
        """This method checks if user is redirected to login page
        when the user tries to access the url and is not logged in.
        """

        response = self.client.get(reverse("author-update", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """This method asserts that a 403 error message should be shown for a user that is
        logged in but does'nt have the permission to access the form.
        """

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("author-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 403)

    def test_uses_correct_template(self):
        """This method checks if the correct template is displayed to a logged in user with valid permissions."""

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("author-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "catalog/author_form.html")

    def test_redirects_to_all_author_list_on_success(self):
        """This method asserts that user should be redirected to author details page
        on successfully filling out the form.
        """

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        valid_first_name = "authorfirstname"
        valid_last_name = "authorlastname"
        valid_date_of_birth = datetime.date.today() - datetime.timedelta(weeks=96)
        valid_date_of_death = datetime.date.today()
        response = self.client.post(
            reverse("author-update", kwargs={"pk": 1}),
            {
                "first_name": valid_first_name,
                "last_name": valid_last_name,
                "date_of_birth": valid_date_of_birth,
                "date_of_death": valid_date_of_death,
            },
        )
        self.assertRedirects(response, reverse("author-detail", kwargs={"pk": 1}))


class DeleteAuthorViewTest(TestCase):
    """This class tests the author deletion form."""

    def setUp(self):
        """This method initializes test case for an author and two users with different permissions."""

        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name="John", last_name="Smith")

    def test_redirect_if_not_logged_in(self):
        """This method checks if user is redirected to login page
        when the user tries to access the url and is not logged in.
        """

        response = self.client.get(reverse("author-delete", kwargs={"pk": 1}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """This method asserts that a 403 error message should be shown for a user that is
        logged in but does'nt have the permission to access the form.
        """

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("author-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 403)

    def test_uses_correct_template(self):
        """This method checks if the correct template is displayed to a logged in user with valid permissions."""

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("author-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, "catalog/author_confirm_delete.html")

    def test_redirects_to_confirm_deletion_screen_on_success(self):
        """This method asserts that user should be redirected to confirm deletion page
        on successfully filling out the form.
        """

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        valid_first_name = "authorfirstname"
        valid_last_name = "authorlastname"
        valid_date_of_birth = datetime.date.today() - datetime.timedelta(weeks=96)
        valid_date_of_death = datetime.date.today()
        response = self.client.post(reverse("author-delete", kwargs={"pk": 1}))
        self.assertRedirects(response, reverse("authors", kwargs={}))


class CreateBookViewTest(TestCase):
    """This class tests the book creation form."""

    def setUp(self):
        """This method initializes test case with two users with different permissions."""

        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        """This method checks if user is redirected to login page
        when the user tries to access the url and is not logged in.
        """

        response = self.client.get(reverse("book-create", kwargs={}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """This method asserts that a 403 error message should be shown for a user that is
        logged in but does'nt have the permission to access the form.
        """

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("book-create", kwargs={}))
        self.assertEqual(response.status_code, 403)

    def test_uses_correct_template(self):
        """This method checks if the correct template is displayed to a logged in user with valid permissions."""

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("book-create", kwargs={}))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "catalog/book_form.html")


class UpdateBookViewTest(TestCase):
    """This class tests the book update form."""

    def setUp(self):
        """This method initializes test case with two users with different permissions."""

        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name="John", last_name="Smith")
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(language="English")
        book = Book.objects.create(
            title="title",
            language=test_language,
            summary="Summary",
            isbn="1231231231231",
        )

        book.genre.set([test_genre])

    def test_redirect_if_not_logged_in(self):
        """This method checks if user is redirected to login page
        when the user tries to access the url and is not logged in.
        """

        response = self.client.get(reverse("book-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """This method asserts that a 403 error message should be shown for a user that is
        logged in but does'nt have the permission to access the form.
        """

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("book-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 403)

    def test_uses_correct_template(self):
        """This method checks if the correct template is displayed to a logged in user with valid permissions."""

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("book-update", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "catalog/book_form.html")


class DeleteBookViewTest(TestCase):
    """This class tests the book deletion form."""

    def setUp(self):
        """This method initializes test case with two users with different permissions."""

        # Create a user
        test_user1 = User.objects.create_user(
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        test_user2 = User.objects.create_user(
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name="Set book as returned")
        test_user2.user_permissions.add(permission)
        test_user2.save()

        test_author = Author.objects.create(first_name="John", last_name="Smith")
        test_genre = Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(language="English")
        book = Book.objects.create(
            title="title",
            language=test_language,
            summary="Summary",
            isbn="1231231231231",
        )

        book.genre.set([test_genre])

    def test_redirect_if_not_logged_in(self):
        """This method checks if user is redirected to login page
        when the user tries to access the url and is not logged in.
        """

        response = self.client.get(reverse("book-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        """This method asserts that a 403 error message should be shown for a user that is
        logged in but does'nt have the permission to access the form.
        """

        login = self.client.login(username="testuser1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("book-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 403)

    def test_uses_correct_template(self):
        """This method checks if the correct template is displayed to a logged in user with valid permissions."""

        login = self.client.login(username="testuser2", password="2HJ1vRV0Z&3iD")
        response = self.client.get(reverse("book-delete", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "catalog/book_confirm_delete.html")
