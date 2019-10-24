from django.db import models

# Create your models here.
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.core.validators import validate_comma_separated_integer_list
from django.contrib.auth.models import User, Group

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    perm_list = models.CharField(validators=[validate_comma_separated_integer_list], max_length=20, default='1,2')
    owner = models.ForeignKey('auth.User', related_name = 'snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()

    class Meta:
        ordering = ('created',)


    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)


class CourseList(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    descrpt = models.TextField()
    owner = models.ForeignKey('auth.User', related_name='courses', on_delete=models.CASCADE)
    date_begin = models.DateTimeField(default='1970-01-01')

    class Meta:
        ordering = ('created',)


class CoursePage(models.Model):
    course = models.ForeignKey('CourseList',related_name = 'pages',  on_delete=models.CASCADE)
    snippet = models.ForeignKey('Snippet', related_name = 'snippet', on_delete=models.CASCADE)
    order = models.IntegerField()
    dtm = models.DateTimeField()

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return '%d;%s;%s' % (self.order, self.snippet.title, self.course.title)


class CourseUsers(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey('CourseList',related_name = 'getcourse',  on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', related_name = 'student', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return '%d %s' % (self.id, self.course.title)


class ReMessage(models.Model):
    message = models.CharField(max_length=100, blank=True, default='')
    dtm = models.DateTimeField()
    email = models.CharField(max_length=64, blank=True, default='')

    def __str__(self):
        return ' %s %s %s ' % (self.message, self.dtm, self.email)


class UserProfile(models.Model):
    owner = models.ForeignKey('auth.User', related_name = 'profile', on_delete=models.CASCADE)
    avatar = models.FileField(upload_to='media/')
    birthday = models.DateTimeField(default='1970-01-01')

    def __str__(self):
        return '%d %s' % (self.owner.id, self.birthday)


class GradeList(models.Model):
     student = models.ForeignKey('auth.User', related_name = 'cadet', on_delete=models.CASCADE)
     course_page = models.ForeignKey('CoursePage', related_name = 'coursepage', on_delete=models.CASCADE)
     done = models.BooleanField(default=False)
     owner_id = models.IntegerField(default=0)

     
     def __str__(self):
         return '%d;%s;%s;%d' % (self.id, self.student, self.course_page, self.done)
