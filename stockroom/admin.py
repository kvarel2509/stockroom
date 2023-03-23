from django.contrib import admin
from stockroom import models


admin.site.register(models.Client)
admin.site.register(models.Product)
admin.site.register(models.StockRoom)
admin.site.register(models.StockRoomBasket)
admin.site.register(models.Road)
