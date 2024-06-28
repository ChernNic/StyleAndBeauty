from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Master(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    sur_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=11)
    salary = models.FloatField()
    rating = models.FloatField()
    specialization = models.ForeignKey('Specialization', on_delete=models.CASCADE)
    shedule = models.ForeignKey('Shedule', on_delete=models.CASCADE)

    def get_full_name(self):
        if self.sur_name:
            return f"{self.first_name} {self.last_name} {self.sur_name}"
        else:
            return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    sur_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=11)

    def get_full_name(self):
        if self.sur_name:
            return f"{self.first_name} {self.last_name} {self.sur_name}"
        else:
            return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()


class Record(models.Model):
    date = models.DateField()
    time = models.TimeField()
    is_complete = models.BooleanField()
    service = models.ForeignKey('Services', on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    def get_formatted_date(self):
        return self.date.strftime("%Y:%m-%d")

    def get_formatted_time(self):
        return self.time.strftime("%H:%M:%S")

    def __str__(self):
        return f"Запись {self.get_formatted_date()} {self.get_formatted_time()} {self.client.get_full_name()} ({self.service.service_name})"


class Specialization(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Shedule(models.Model):
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()

    def get_formatted_date(self):
        return self.date.strftime("%Y:%m:%d")

    def get_formatted_time_start(self):
        return self.time_start.strftime("%H:%M:%S")

    def get_formatted_time_end(self):
        return self.time_end.strftime("%H:%M:%S")

    def __str__(self):
        return f"Расписание на {self.date}"


class Services(models.Model):
    service_name = models.CharField(max_length=50)
    service_description = models.TextField(null=True)
    cost = models.FloatField()

    def __str__(self):
        return self.service_name


class Statistics(models.Model):
    date = models.DateField()
    income = models.FloatField()
    amount_services_provided = models.IntegerField()

    def __str__(self):
        return f"Статистика за {self.date}"


@receiver(post_save, sender=Record)
def update_statistics(sender, instance, created, **kwargs):
    if instance.is_complete:
        # Получаем сегодняшнюю дату
        today = timezone.now().date()

        try:
            statistics_entry = Statistics.objects.get(date=today)
            # Обновляем существующую запись
            statistics_entry.income += instance.service.cost
            statistics_entry.amount_services_provided += 1
            statistics_entry.save()
        except Statistics.DoesNotExist:
            # Если запись не существует, создаем новую запись
            Statistics.objects.create(date=today, income=instance.service.cost, amount_services_provided=1)
    elif not instance.is_complete:
        # Получаем сегодняшнюю дату
        today = timezone.now().date()

        try:
            statistics_entry = Statistics.objects.get(date=today)
            # Обновляем существующую запись
            statistics_entry.income -= instance.service.cost
            statistics_entry.amount_services_provided -= 1
            statistics_entry.save()
        except Statistics.DoesNotExist:
            pass