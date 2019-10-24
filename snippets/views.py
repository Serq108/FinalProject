import logging
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.views.generic import View

from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import renderers

from snippets.models import Snippet, CourseList, CoursePage, CourseUsers,\
    UserProfile, GradeList
from snippets.serializers import SnippetSerializer, UserSerializer,\
    UserCreateSerializer, CreateSnippetSerializer, CreateCourseSerializer,\
    CreateCoursePageSerializer, CourseDetailSerializer, CourseListSerializer,\
    CoursePageSerializer, CourseDetailPageSerializer, CourseUserSerializer,\
    CourseUsersListSerializer, CourseUserDetailSerializer,\
    UserProfileSerializer, UserUpdateSerializer, GradeListSerializer
from snippets.permissions import IsOwnerOrReadOnly, IfGroup2, IsUserOrReadOnly, IfOwnerSnippet
from utils.token_generator import token_generator

class SnippetList(generics.ListAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class CreateSnippet(generics.CreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = CreateSnippetSerializer
    permission_classes = (permissions.DjangoModelPermissions,)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = CreateSnippetSerializer
    permission_classes = (permissions.DjangoModelPermissions, IsOwnerOrReadOnly, IfGroup2)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.DjangoModelPermissions, IsOwnerOrReadOnly)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.DjangoModelPermissions, IsOwnerOrReadOnly)


class CreateUserView(generics.CreateAPIView):
    model = User
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserCreateSerializer


class UpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsUserOrReadOnly,)
    serializer_class = UserUpdateSerializer


class CreateCourseView(generics.ListCreateAPIView):
    queryset = CourseList.objects.all()
    serializer_class = CreateCourseSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CreatePageView(generics.ListCreateAPIView):
    queryset = CoursePage.objects.all()
    serializer_class = CreateCoursePageSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class CoursListView(generics.ListAPIView):
    queryset = CourseList.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class CourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseList.objects.all()
    serializer_class = CourseDetailSerializer
    permission_classes = (permissions.DjangoModelPermissions, IsOwnerOrReadOnly,)


class CoursPageListView(generics.ListAPIView):
    queryset = CoursePage.objects.all()
    serializer_class = CoursePageSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class CoursPageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CoursePage.objects.all()
    serializer_class = CourseDetailPageSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class CoursUserView(generics.CreateAPIView):
    queryset = CourseUsers.objects.all()
    serializer_class = CourseUserSerializer
    permission_classes = (permissions.DjangoModelPermissions,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CoursUserListView(generics.ListAPIView):
    queryset = CourseUsers.objects.all()
    serializer_class = CourseUsersListSerializer
    permission_classes = (permissions.DjangoModelPermissions,)


class CoursUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseUsers.objects.all()
    serializer_class = CourseUserDetailSerializer
    permission_classes = (permissions.DjangoModelPermissions,  IsOwnerOrReadOnly,)


class GradeListUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradeList.objects.all()
    serializer_class = GradeListSerializer
    permission_classes = (permissions.DjangoModelPermissions, IfOwnerSnippet,)



def qset_to_resp(qset):
    gradehead = ['id','student', 'order', 'lesson', 'course_title', 'done']
    resp = []
    for lessn in list(qset):
        grade_dict = dict(zip(gradehead, str(lessn).split(';')))
        resp.append(grade_dict)
    return resp

@api_view(['GET'])
def gradelist(request, format=None):
    if not request.user.id:
        return Response({'message': 'authorization required'})
    if request.user.groups.filter(name='Tutors').exists():
        qset = GradeList.objects.filter(owner_id=request.user.id)
        return Response(qset_to_resp(qset))
    else:
        qset = GradeList.objects.filter(student=request.user.id)
        return Response(qset_to_resp(qset))


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # 'users': reverse('user-list', request=request, format=format),
        # 'snippets': reverse('snippet-list', request=request, format=format),
        'courses': reverse('courselist-list', request=request, format=format),
        'registration': reverse('user-list', request=request, format=format)
    })


class ConfirmEmailView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request, user, token):
        try:
            uid = force_text(urlsafe_base64_decode(user))
            user = get_user_model().objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # ~ return Response(data={'status': 'ok'}, content_type='application/json', status=status.HTTP_202_ACCEPTED)
            return Response({'status': 'ok'})
        else:
            return Response({'status': 'error', 'message': 'Неверная ссылка активации'})
                # ~ status=status.HTTP_400_BAD_REQUEST


class AccInfoView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request):
        if request.user.id:
            birth = UserProfile.objects.filter(owner=request.user.id).values_list('birthday', flat=True)
            birthday = birth[0].strftime("%Y-%m-%d")
            group = ''
            if request.user.groups.filter(name='Tutors').exists():
                group = 'tutor'
            else:
                group = 'student'
            return Response({
                'user_id': str(request.user.id), 
                'Name': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'birthday': birthday,
                'Group': group
            })
        else:
            return Response({'user_id': str(request.user.id)})


class AccountView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'owner_id'

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsOwnerOrReadOnly,)

class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, request):
        try:
            with open(os.path.join(settings.REACT_APP_DIR, 'build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            logging.exception('Production build of app not found')
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app. Visit http://localhost:3000/ instead, or
                run `yarn run build` to test the production version.
                """,
                status=501,
            )
# ~ class AccountUploadView(APIView):
    # ~ parser_class = (FileUploadParser,)

    # ~ def post(self, request, *args, **kwargs):

      # ~ acc_serializer = AccountSerializer(data=request.data)

      # ~ if acc_serializer.is_valid():
          # ~ ac_serializer.save()
          # ~ return Response(acc_serializer.data, status=status.HTTP_201_CREATED)
      # ~ else:
          # ~ return Response(acc_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # ~ class SnippetHighlight(generics.GenericAPIView):
    # ~ queryset = Snippet.objects.all()
    # ~ renderer_classes = (renderers.StaticHTMLRenderer,)

    # ~ def get(self, request, *args, **kwargs):
        # ~ snippet = self.get_object()
        # ~ return Response(snippet.highlighted)
