from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Lesson, Product, ProductAccess, Viewed, User
from .serializers import LessonSerializer, ProductSerializer


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Lesson.objects.all()

    @action(detail=False, methods=['get'])
    def all_lessons(self, request):
        user = request.user
        product_ids = list(
            ProductAccess.objects.filter(user=user).values_list('product_id',
                                                                flat=True))
        lessons = Lesson.objects.filter(
            products__id__in=product_ids)
        response_data = []
        for lesson in lessons:
            time_viewed = timedelta(seconds=0)
            user_event = Viewed.objects.filter(user=user,
                                               lesson=lesson).first()
            if user_event:
                time_viewed = user_event.viewed_time.time() - user_event.lesson.duration
            response_data.append({
                'id': lesson.id,
                'name': lesson.name,
                'video_url': lesson.video_url,
                'duration': lesson.duration,
                'status': user_event.status if user_event else False,
                'time_viewed': str(time_viewed)
            })
        return Response(response_data)

    @action(detail=True, methods=['get'])
    def product_lessons(self, request, pk=None):
        user = request.user
        product_access = get_object_or_404(ProductAccess, user=user,
                                           product=pk)
        lessons = product_access.product.lesson_set.all()
        response_data = []
        for lesson in lessons:
            time_viewed = timedelta(seconds=0)
            last_viewed = ''
            user_event = Viewed.objects.filter(user=user,
                                               lesson=lesson).first()
            all_events = Viewed.objects.filter(lesson=lesson,
                                               status=True).order_by(
                '-viewed_time')
            if all_events:
                last_viewed = all_events.first().viewed_time.strftime(
                    "%Y-%m-%d %H:%M:%S")
            if user_event:
                time_viewed = user_event.viewed_time.time() - user_event.lesson.duration
            response_data.append({
                'id': lesson.id,
                'name': lesson.name,
                'video_url': lesson.video_url,
                'duration': lesson.duration,
                'status': user_event.status if user_event else False,
                'time_viewed': str(time_viewed),
                'last_viewed': last_viewed
            })
        return Response(response_data)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()

    @action(detail=False, methods=['get'])
    def products_stats(self, request):
        products = Product.objects.all()
        response_data = []
        for product in products:
            all_events = Viewed.objects.filter(lesson__products=product,
                                               status=True)
            students_count = ProductAccess.objects.filter(
                product=product).count()
            stats = {
                'product': product.name,
                'viewed_lessons': all_events.values_list(
                    'lesson_id').distinct().count(),
                'total_time_spent': str(
                    all_events.aggregate(total_time=Sum('lesson__duration'))[
                        'total_time']),
                'students_count': students_count,
                'purchase_percentage': students_count / User.objects.count()
            }
            response_data.append(stats)
        return Response(response_data)
