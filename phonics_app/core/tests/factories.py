"""
Factory fixtures for creating test data
"""

import factory
from factory.django import DjangoModelFactory
from core.models import User, Plan, PaperYear, PaperPage, Word, UserProgress


class PlanFactory(DjangoModelFactory):
    class Meta:
        model = Plan

    name = factory.Sequence(lambda n: f"Plan {n}")
    price = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    access_years = [2012, 2013, 2014]
    audio_enabled = False
    is_free = False
    demo = False


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Faker("email")
    password = "testpass123"
    plan = factory.SubFactory(PlanFactory, is_free=True)

    @classmethod
    def create(cls, **kwargs):
        user = super().create(**kwargs)
        user.set_password(kwargs.get("password", "testpass123"))
        user.save()
        return user


class PaperYearFactory(DjangoModelFactory):
    class Meta:
        model = PaperYear

    year = factory.Sequence(lambda n: 2012 + n)
    title_pdf = factory.django.FileField()


class PaperPageFactory(DjangoModelFactory):
    class Meta:
        model = PaperPage

    paper = factory.SubFactory(PaperYearFactory)
    page_number = factory.Sequence(lambda n: n + 1)
    image = factory.django.ImageField()
    is_title = False


class WordFactory(DjangoModelFactory):
    class Meta:
        model = Word

    page = factory.SubFactory(PaperPageFactory)
    text = factory.Faker("word")
    type = "real"
    audio_file = factory.django.FileField()
    order = factory.Sequence(lambda n: n + 1)


class UserProgressFactory(DjangoModelFactory):
    class Meta:
        model = UserProgress

    user = factory.SubFactory(UserFactory)
    paper_year = factory.SubFactory(PaperYearFactory)
    pages_completed = 0
    words_attempted = 0
    audio_used = False
    completed = False
