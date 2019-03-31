from django.contrib.auth import authenticate, login
from django.test import TestCase
from outcomes.models import Outcome, OutcomeMedia
from users.models import BaseUser 


class OutcomeTestCase(TestCase):

    def setUp(self):
        self.test_user = BaseUser.objects.create_user(username='testuser', email="testuser@csus.edu", password='12345')

    def test_can_create_outcome(self):
        outcome = Outcome.objects.create(title="title", author=self.test_user)
        self.assertIsInstance(Outcome.objects.get(pk=outcome.pk), Outcome)

    def test_can_update_outcome_title(self):
        outcome = Outcome.objects.create(title="title", author=self.test_user)
        new_title = "new title"
        outcome.title = new_title
        outcome.save()
        self.assertEqual(Outcome.objects.get(pk=outcome.pk).title, new_title)

    def test_slug_generated_from_outcome_title_is_unique(self):
        title = "slug test"
        outcome_1 = Outcome.objects.create(title=title, author=self.test_user)
        outcome_2 = Outcome.objects.create(title=title, author=self.test_user)
        outcome_1_slug = Outcome.objects.get(pk=outcome_1.pk).slug
        outcome_2_slug = Outcome.objects.get(pk=outcome_2.pk).slug
        self.assertNotEqual(outcome_1_slug, outcome_2_slug)

    def test_slug_generation_truncates_very_long_outcome(self):
        title = "veeeeeeeeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyyyyyyyyyyyyy \
                loooooooooooooooooooooooooooooooooooooooooonnnnnnnnnnngggggggggggggggggg \
                aaaaarrrttttiiiiicccclllleeeeee tiiiiiiiitttttlllllllllleeeeeeeeeee"
        outcome = Outcome.objects.create(title=title, author=self.test_user)
        outcome_slug = Outcome.objects.get(pk=outcome.pk).slug
        self.assertGreater(len(title), Outcome._meta.get_field('slug').max_length)
        self.assertLessEqual(len(outcome_slug), Outcome._meta.get_field('slug').max_length)
