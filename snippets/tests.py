from django.test import TestCase
import pytest


# Create your tests here.
from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from snippets.models import Snippet, CoursePage, CourseList
from django.utils import timezone



class SnippetModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username = 'test', password = '123')
        #"""Set up non-modified objects used by all test methods."""
        Snippet.objects.create(
            title = 'ABCDF',
            code = 'abcd',
            linenos = False,
            language = 'python',
            style = 'friendly',
            perm_list = '1,2',
            owner = user,
            highlighted = 'oprst'
        )

    def test_title(self):
        snippet = Snippet.objects.get(id=1)
        print('SOME', snippet)
        field_label = snippet._meta.get_field('title').verbose_name
        #self.assertEquals(field_label, 'title')
        assert field_label == 'title'


class CoursePageModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username = 'test', password = '123')
        snippet = Snippet.objects.create(
            title = 'ABCDF',
            code = 'abcd',
            linenos = False,
            language = 'python',
            style = 'friendly',
            perm_list = '1,2',
            owner = user,
            highlighted = 'oprst'
        )
        course = CourseList.objects.create(
                created = timezone.now(),
                title = 'abcd',
                descrpt = 'afajhaja',
                owner = user,
                date_begin = datetime(2017, 3, 5),
        )
        #"""Set up non-modified objects used by all test methods."""
        CoursePage.objects.create(
                course = course,
                snippet = snippet,
                order = 1,
                dtm = datetime(2017, 3, 5),
        )

    def test_object_name(self):
        coursepage = CoursePage.objects.get(id=1)
        expected_object_name = '%d %s ID = %d %s ' % (
            coursepage.order, 
            coursepage.snippet.title, 
            coursepage.snippet.id, 
            coursepage.dtm,
    )
        assert expected_object_name == str(coursepage)

@pytest.fixture
def input_data():
    print('Solver data generated!')
    return ['abc@abx.ab'], 'def'

@pytest.fixture
def input_data_with_result(input_data):
    return input_data, ('abc', 'def')

def test_send_mail_note(input_data):
    from snippets.management.commands.run_check import send_mail_note
    try:
        send_mail_note(*input_data)
    except TypeError:
        pytest.fail('Function must take 2 args')


