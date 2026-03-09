from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (SchoolClassViewSet, TeacherViewSet, StudentViewSet, FeeStructureViewSet,
                    MarkViewSet, AttendanceViewSet, TimetableViewSet, AuthViewSet, index)

router = DefaultRouter()
router.register(r'classes', SchoolClassViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)
router.register(r'fees', FeeStructureViewSet)
router.register(r'marks', MarkViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'timetable', TimetableViewSet)
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)),
]
