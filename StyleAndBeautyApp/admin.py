from django.contrib import admin
from .models import Master, Client, Record, Specialization, Shedule, Services, Statistics

admin.site.register(Master)
admin.site.register(Client)
admin.site.register(Record)
admin.site.register(Specialization)
admin.site.register(Shedule)
admin.site.register(Services)
admin.site.register(Statistics)
