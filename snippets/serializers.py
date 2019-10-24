import os
from datetime import datetime, timedelta
from redis import Redis
from rq import Queue
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rq_scheduler import Scheduler
from snippets.models import Snippet, CourseList, CoursePage, CourseUsers,\
    ReMessage, UserProfile, GradeList
from snippets.tasks import test_job, send_mail_reg, send_mail_note, send_mail_note1
from utils.token_generator import token_generator, create_email_confirm_url

queue = Queue(connection = Redis('redis', 6379))
sheduler = Scheduler(connection=Redis())


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    # highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')
    class Meta:
        model = Snippet
        # fields = ('id', 'title', 'code', 'linenos', 'language', 'style', 'owner')
        fields = ('url', 'id', 'title', 'owner')


class CreateSnippetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = (
            'url', 'id', 'title', 'code', 'linenos', 'language',
            'style', 'owner', 'perm_list'
        )


# class UserSerializer(serializers.ModelSerializer):
class UserSerializer(serializers.HyperlinkedModelSerializer):
    #snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail',
        read_only=True
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'snippets')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            is_active = True,
            email = validated_data['email']
        )
        profile = UserProfile.objects.create(
            owner = user,
            avatar='',
            birthday='1970-01-01'
        )
        print('SOMEPRINT',validated_data)
        print('SOMEPRINT')
        token = token_generator.make_token(user)
        url = create_email_confirm_url(user.id, token)
        print('SOMEPRINT', url)
        # ~ send_mail(
            # ~ 'Activation on Django', url, 'djangodev108@gmail.com',
            # ~ [validated_data['email']], fail_silently=False
        # ~ )
        user.set_password(validated_data['password'])
        user.groups.add(1)
        user.save()
        if User.objects.filter(username=self.validated_data['username']).exists():
            # ~ send_mail(
                # ~ 'Activation on Django', url, 'djangodev108@gmail.com',
                # ~ [validated_data['email']], fail_silently=False
            # ~ )
            # job = queue.enqueue(test_job, "jabba")
            job = queue.enqueue(send_mail_reg, [validated_data['email']], url)
        else:
            print('SOMEPRINT wrong')
        return user

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'first_name',
            'last_name',
        )


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'first_name',
            'last_name',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = CourseList
        fields = ('title', 'descrpt', 'owner', 'date_begin')


class CreateCoursePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePage
        fields = ('course', 'snippet', 'order', 'dtm')


class CourseListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CourseList
        fields = ('url', 'id', 'title', 'descrpt', 'owner', 'date_begin')


class CoursePageSerializer(serializers.HyperlinkedModelSerializer):
    # snippet = serializers.HyperlinkedRelatedField(many=False, view_name='snippet-detail', read_only=True)
    title = serializers.ReadOnlyField(source='snippet.title')
    class Meta:
        model = CoursePage
        fields = ('order',  'title', 'dtm','snippet')


class CourseDetailSerializer(serializers.HyperlinkedModelSerializer):
    # pages = serializers.StringRelatedField(many=True)
    # pages_listing = serializers.HyperlinkedIdentityField(view_name='coursepage-list')
    pages = CoursePageSerializer(many=True, read_only=True)
    # ~ pages = serializers.HyperlinkedRelatedField(
        # ~ many=True,
        # ~ view_name='coursepage-detail',
        # ~ read_only=True
    # ~ )

    class Meta:
        model = CourseList
        fields = ('title', 'descrpt', 'pages')


class CourseDetailPageSerializer(serializers.HyperlinkedModelSerializer):
    # pages = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)
    title = serializers.ReadOnlyField(source='snippet.title')

    class Meta:
        model = CoursePage
        fields = ('title', 'order', 'dtm', 'snippet')


class CourseUserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        queryset = CoursePage.objects.filter(course=validated_data['course'].id).values_list('dtm', flat=True)
        qset = CoursePage.objects.filter(course=validated_data['course'].id)
        qset1 = CourseList.objects.filter(id=validated_data['course'].id).values_list('owner', flat=True)

        print(qset1)
        # ~ dateb = validated_data['course'].date_begin
        # ~ sec = dateb.timestamp()-3600*24*3
        # ~ date_notice = datetime.utcfromtimestamp(sec).strftime('%Y-%m-%d %H:%M:%S')
        # ~ sheduler.enqueue_in(timedelta(seconds=15), test_job, 'TEST') 
        notice_message = 'Вы записались на курс ' + validated_data['course'].title + ' начало курса ' + str(queryset[0])
        if CourseUsers.objects.filter(course=validated_data['course'].id, owner=validated_data['owner'].id).exists():
            # ~ job = sheduler.enqueue_in(timedelta(seconds=10), send_mail_note, [validated_data['owner'].email], notice_message)
            # ~ print('job', job)
            # ~ job = queue.enqueue(send_mail_note1, [validated_data['owner'].email], notice_message, 'Notice custome 4')
            # ~ print('job', job)
            raise serializers.ValidationError('вы уже записаны')
            return 1
        else:
            courseuser = CourseUsers.objects.create(
                course=validated_data['course'],
                owner=validated_data['owner'],
                )
            for grades in qset:
                gradelist = GradeList.objects.create(
                    student=validated_data['owner'],
                    course_page=grades,
                    done=False,
                    owner_id=list(qset1)[0],
                )
            # ~ job = queue.enqueue(send_mail_note, [validated_data['owner'].email], notice_message)
            # ~ for lessn in queryset:
                # ~ ReMessage.objects.create(
                    # ~ dtm=lessn,
                    # ~ email=validated_data['owner'].email,
                    # ~ message='У вас завтра урок',
                # ~ )
                #sheduler.shedule(func=someprint(), interval=3, repeat=10)
                # ~ sec = lessn.timestamp()-3600*24
                # ~ date_notice = datetime.utcfromtimestamp(sec)
                # ~ sheduler.enqueue_at(date_notice, send_mail_note, [validated_data['owner'].email], 'У вас завтра урок')
            return courseuser

    title = serializers.ReadOnlyField(source='course.title')
    ownername = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = CourseUsers
        fields = ('id' , 'course', 'title', 'ownername' )


class CourseUsersListSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.ReadOnlyField(source='course.title')
    ownername = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = CourseUsers
        fields = ('url', 'id', 'title', 'ownername')


class CourseUserDetailSerializer(serializers.HyperlinkedModelSerializer):
    title = serializers.ReadOnlyField(source='course.title')
    ownername = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = CourseUsers
        fields = ('id' , 'course', 'title', 'ownername')


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='owner.id')
    name = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'birthday', 'avatar')


class GradeListSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    course = serializers.ReadOnlyField(source='course_page.course.title')
    snippet = serializers.ReadOnlyField(source='course_page.snippet.title')

    class Meta:
        model = GradeList
        fields = ('id', 'student', 'course', 'snippet', 'done')
