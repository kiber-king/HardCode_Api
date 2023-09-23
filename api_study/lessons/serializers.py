from rest_framework import serializers
from .models import Product, Lesson


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name')


class LessonSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ('id', 'name', 'video_url', 'duration', 'products')
