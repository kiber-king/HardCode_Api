from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              verbose_name='Владелец')


class ProductAccess(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)


class Lesson(models.Model):
    name = models.CharField(max_length=255)
    video_url = models.URLField()
    duration = models.IntegerField()
    products = models.ManyToManyField(Product)


class Viewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    viewed_time = models.DateTimeField()
    status = models.BooleanField(default=False)
