from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


class ProductPrice(models.Model):
    data = models.DateField()
    category = models.CharField(max_length=50)
    variety = models.CharField(max_length=100, db_index=True)
    price = models.FloatField()
    area = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default='元/公斤')
    # 新增省份字段
    province = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.variety} - {self.price}{self.unit} - {self.area}"

    class Meta:
        ordering = ['variety', '-data']
        indexes = [
            models.Index(fields=['variety', 'data']),
        ]

