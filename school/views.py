from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login, logout
from .models import SchoolClass, Teacher, Student, FeeStructure, Mark, Attendance, Timetable, UserProfile
from .serializers import (SchoolClassSerializer, TeacherSerializer, StudentSerializer,
                          FeeStructureSerializer, MarkSerializer, AttendanceSerializer,
                          TimetableSerializer, UserSerializer)
from django.shortcuts import render
from django.contrib.auth.models import User

def index(request):
    return render(request, 'school/index.html')

class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer

class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        role = request.data.get('role', 'admin')
        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, role=role, avatar=(first_name[:2] if first_name else username[:2]).upper())
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            role = 'admin'
            if user.is_superuser:
                role = 'superadmin'
            UserProfile.objects.update_or_create(user=user, defaults={'role': role, 'avatar': (user.first_name[:2] if user.first_name else user.username[:2]).upper()})
            return Response({'status': 'logged in', 'user': UserSerializer(user).data})
        return Response({'status': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'status': 'logged out'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'status': 'not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
