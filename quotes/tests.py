import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from quotes.models import Author, Quote, Tag


class ModelsTestCase(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name='Tag1')
        self.tag2 = Tag.objects.create(name='Tag2')

        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            birth_date='1990-01-01',
            death_date='2020-01-01'
        )

        self.quote = Quote.objects.create(
            text='This is a test quote.',
            author=self.author
        )
        self.quote.tags.add(self.tag1, self.tag2)

    def test_author_creation(self):
        author = Author.objects.create(first_name='Some', birth_date='1990-01-01')
        author.refresh_from_db()
        self.assertEqual(author.full_name, 'Some')
        self.assertEqual(author.birth_date, datetime.datetime(year=1990, month=1, day=1).date())
        self.assertIsNone(author.death_date)

    def test_quote_creation(self):
        quote = Quote.objects.get(text='This is a test quote.')
        self.assertEqual(quote.text, 'This is a test quote.')
        self.assertEqual(quote.author.full_name, 'John Doe')
        self.assertIn(self.tag1, quote.tags.all())
        self.assertIn(self.tag2, quote.tags.all())

    def test_tag_creation(self):
        tag1 = Tag.objects.get(name='Tag1')
        tag2 = Tag.objects.get(name='Tag2')
        self.assertEqual(tag1.name, 'Tag1')
        self.assertEqual(tag2.name, 'Tag2')

    def test_failure_on_create_exist_tag(self):
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='Tag1')


class AuthorTestCase(APITestCase):
    def setUp(self):
        self.authors = [
            Author(
                first_name='John',
                last_name=f'Doe-{num}',
                birth_date='1990-01-01',
                death_date='2020-01-01'
            )
            for num in range(15)
        ]
        Author.objects.bulk_create(self.authors)
        self._url = reverse("author-list")

    def test_list(self):
        response = self.client.get(self._url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data["results"]), 10)  # PAGE_SIZE which is set in settings

    def test_retrieve(self):
        test_author = self.authors[-1]
        test_author.refresh_from_db()
        author_id = str(test_author.id)

        response = self.client.get(f'{self._url}{author_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": author_id,
                "full_name": test_author.full_name,
                'birth_date': '1990-01-01',
                'death_date': '2020-01-01'
            }
        )

    def test_failure_retrieve(self):
        author_id = "non-existent"
        response = self.client.get(f'{self._url}{author_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        payload = dict(
            first_name='John',
            last_name=f'Doe-15',
            birth_date='1990-01-01'
        )
        response = self.client.post(self._url, format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('full_name', response.data)
        self.assertEqual(response.data['full_name'], 'John Doe-15')
        self.assertIn('birth_date', response.data)
        self.assertEqual(response.data['birth_date'], '1990-01-01')
        self.assertIn('death_date', response.data)
        self.assertIsNone(response.data['death_date'])

    def test_failure_on_exists(self):
        payload = dict(
            first_name='John',
            last_name=f'Doe-1',
            birth_date='1990-01-01'
        )
        response = self.client.post(self._url, format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_update(self):
        test_author = self.authors[0]
        test_author.refresh_from_db()
        author_id = str(test_author.id)

        payload = dict(
            first_name='John-updated',
            last_name=f'Doe-updated',
            birth_date='1990-01-02',
            death_date=None
        )
        response = self.client.patch(f'{self._url}{author_id}/', format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": author_id,
                "full_name": 'John-updated Doe-updated',
                'birth_date': '1990-01-02',
                'death_date': None
            }
        )


class TagTests(APITestCase):
    def setUp(self):
        self.tags = [Tag(name=f"test-{num}") for num in range(15)]
        Tag.objects.bulk_create(self.tags)
        self._url = reverse('tag-list')

    def _get_tag(self) -> Tag:
        tag = self.tags[-1]
        tag.refresh_from_db()
        return tag

    def test_list(self):
        response = self.client.get(self._url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data["results"]), 10)  # PAGE_SIZE which is set in settings

    def test_retrieve(self):
        tag = self._get_tag()
        tag_id = str(tag.id)

        response = self.client.get(f'{self._url}{tag_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,{"id": tag_id, "name": tag.name})

    def test_failure_retrieve(self):
        tag_id = "non-existent"
        response = self.client.get(f'{self._url}{tag_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        response = self.client.post(self._url, format='json', data={"name": "new-tag"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], 'new-tag')

    def test_failure_on_exists_name(self):
        response = self.client.post(self._url, format='json', data={"name": "test-1"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update(self):
        tag = self._get_tag()
        tag_id = str(tag.id)

        response = self.client.patch(f'{self._url}{tag_id}/', format='json', data=dict(name='tag-updated'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data,{"id": tag_id, "name": 'tag-updated'})


class QuoteTests(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(
            first_name='John',
            last_name='Doe',
            birth_date='1990-01-01',
        )
        self.quotes = [
            Quote(
                author=self.author,
                text=f"Some text number {num}"
            ) for num in range(10)
        ]
        Quote.objects.bulk_create(self.quotes)
        self._url = reverse('quote-list')

    def _get_quote(self):
        quote = self.quotes[-1]
        quote.refresh_from_db()
        return quote

    def test_list(self):
        response = self.client.get(self._url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data["results"]), 10)  # PAGE_SIZE which is set in settings

    def test_retrieve(self):
        quote = self._get_quote()
        quote_id = str(quote.id)

        response = self.client.get(f'{self._url}{quote_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], quote_id)
        self.assertEqual(response.data['text'], quote.text)

    def test_failure_retrieve(self):
        tag_id = "non-existent"
        response = self.client.get(f'{self._url}{tag_id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        author_url = reverse("author-detail", kwargs={"author_id": str(self.author.id)})
        payload = {"author": author_url, "text": "new quote test"}
        response = self.client.post(self._url, format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['text'], "new quote test")

    def test_failure_text_of_quote(self):
        author_url = reverse("author-detail", kwargs={"author_id": str(self.author.id)})
        payload = {"author": author_url, "text": "two words"}
        response = self.client.post(self._url, format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)

    def test_failure_author_id(self):
        payload = {"author": "non-existent"}
        response = self.client.post(self._url, format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("author", response.data)

    def test_failure_tags(self):
        author_url = reverse("author-detail", kwargs={"author_id": str(self.author.id)})
        payload = {"author": author_url, "text": "Some test quote", "tags": ["non-existent"]}
        response = self.client.post(self._url, format='json', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tags", response.data)

    def test_update(self):
        quote = self._get_quote()
        quote_id = str(quote.id)

        response = self.client.patch(f'{self._url}{quote_id}/', format='json', data=dict(name='tag-updated'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], quote_id)
        self.assertEqual(response.data['text'], quote.text)
