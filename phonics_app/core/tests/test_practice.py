"""
Tests for paper and practice functionality
"""

import pytest
from django.urls import reverse
from core.tests.factories import (
    UserFactory,
    PaperYearFactory,
    PaperPageFactory,
    WordFactory,
    PlanFactory,
)


@pytest.mark.django_db
class TestPaperYear:
    """Test paper year functionality"""

    def test_paper_year_creation(self):
        """Test paper year is created correctly"""
        paper = PaperYearFactory(year=2012)
        assert paper.year == 2012
        assert str(paper) == "2012"

    def test_unique_year_constraint(self):
        """Test year uniqueness constraint"""
        PaperYearFactory(year=2012)
        with pytest.raises(Exception):  # IntegrityError
            PaperYearFactory(year=2012)


@pytest.mark.django_db
class TestPaperPage:
    """Test paper page functionality"""

    def test_paper_page_creation(self):
        """Test paper page is created correctly"""
        page = PaperPageFactory(page_number=1, is_title=False)
        assert page.page_number == 1
        assert page.is_title is False

    def test_page_ordering(self):
        """Test pages are ordered by page number"""
        paper = PaperYearFactory()
        PaperPageFactory(paper=paper, page_number=3)
        PaperPageFactory(paper=paper, page_number=1)
        PaperPageFactory(paper=paper, page_number=2)

        pages = paper.pages.all()
        assert list(pages.values_list("page_number", flat=True)) == [1, 2, 3]

    def test_unique_page_per_paper(self):
        """Test uniqueness of page per paper"""
        paper = PaperYearFactory()
        PaperPageFactory(paper=paper, page_number=1)
        with pytest.raises(Exception):  # IntegrityError
            PaperPageFactory(paper=paper, page_number=1)


@pytest.mark.django_db
class TestWord:
    """Test word functionality"""

    def test_word_creation(self):
        """Test word is created correctly"""
        word = WordFactory(text="phonics", type="real")
        assert word.text == "phonics"
        assert word.type == "real"

    def test_word_ordering(self):
        """Test words are ordered correctly"""
        page = PaperPageFactory()
        WordFactory(page=page, text="word1", order=2)
        WordFactory(page=page, text="word2", order=1)
        WordFactory(page=page, text="word3", order=3)

        words = page.words.all()
        assert list(words.values_list("text", flat=True)) == ["word2", "word1", "word3"]


@pytest.mark.django_db
class TestPracticeViews:
    """Test practice paper views"""

    def test_year_selection_requires_authentication(self, client):
        """Test year selection requires login"""
        response = client.get(reverse("core:year_selection"))
        assert response.status_code in [302, 403]  # Redirect or forbidden

    def test_authenticated_user_can_access_year_selection(self, client):
        """Test authenticated user can access year selection"""
        user = UserFactory()
        plan = PlanFactory(access_years=[2012, 2013])
        user.plan = plan
        user.save()
        client.force_login(user)
        response = client.get(reverse("core:year_selection"))
        assert response.status_code == 200

    def test_paper_page_view_loads(self, client):
        """Test paper page view is accessible"""
        user = UserFactory()
        plan = PlanFactory(access_years=[2012])
        user.plan = plan
        user.save()

        paper = PaperYearFactory(year=2012)
        PaperPageFactory(paper=paper, page_number=1)

        client.force_login(user)
        response = client.get(reverse("core:paper_page", args=[paper.id, 1]))
        assert response.status_code == 200
