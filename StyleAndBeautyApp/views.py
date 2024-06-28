import csv

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from StyleAndBeautyApp.forms import ClientRegistrationForm, ClientEditForm, ServiceSearchForm, RecordForm
from StyleAndBeautyApp.models import Client, Master, Record, Services, Statistics


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Проверяем, является ли пользователь клиентом
            if Client.objects.filter(user=user).exists():
                return HttpResponseRedirect(reverse('client_profile'))
            # Проверяем, является ли пользователь доктором
            elif Master.objects.filter(user=user).exists():
                return HttpResponseRedirect(reverse('master_profile'))
            # Проверяем, является ли пользователь персоналом
            elif user.is_staff:
                return HttpResponseRedirect(reverse('manager_profile'))
        else:
            messages.error(request, 'Неправильное имя пользователя или пароль.')
            return render(request, 'authentication/login.html')


class RegistrationView(View):
    def get(self, request):
        form = ClientRegistrationForm()
        return render(request, 'authentication/registration.html', {'form': form})

    def post(self, request):
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            # Проверка на уникальность имени пользователя
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                # Если имя пользователя уже существует, выводим сообщение об ошибке
                form.add_error('username', 'Имя пользователя занято.')
                return render(request, 'authentication/registration.html', {'form': form})

            # Создание пользователя и клиента
            user = User.objects.create_user(
                username=username,
                password=form.cleaned_data['password']
            )
            client = Client.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                sur_name=form.cleaned_data['sur_name'],
                contact_number=form.cleaned_data['contact_number']
            )
            return redirect('login')  # Перенаправьте пользователя на страницу после регистрации
        return render(request, 'authentication/registration.html', {'form': form})


class ClientProfileView(View):
    def get(self, request):
        # Получаем текущего пользователя
        user = request.user

        client = Client.objects.get(user=user)

        records = Record.objects.filter(client=client)

        context = {
            'client': client,
            'records': records
        }
        return render(request, 'profiles/client/client_profile.html', context)

    def post(self, request):
        client = Client.objects.get(user=request.user)

        form = ClientEditForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_profile')

        context = {
            'client': client,
            'edit_form': form
        }
        return render(request, 'profiles/client/client_profile.html', context)


class ClientServicesView(View):
    def get(self, request):
        user = request.user
        client = Client.objects.get(user=user)

        # Получение параметров запроса для сортировки
        sort_by = request.GET.get('sort_by')
        direction = request.GET.get('direction')

        # Получение всех услуг и применение сортировки, если она указана
        services = Services.objects.all()

        if sort_by and direction in ['asc', 'desc']:
            if sort_by == 'service_name':
                if direction == 'asc':
                    services = services.order_by('service_name')
                else:
                    services = services.order_by('-service_name')
            elif sort_by == 'cost':
                if direction == 'asc':
                    services = services.order_by('cost')
                else:
                    services = services.order_by('-cost')

        search_form = ServiceSearchForm(request.GET)
        query = request.GET.get('query')

        if query:
            services = services.filter(service_name__icontains=query)

        context = {
            'client': client,
            'services': services,
            'search_form': search_form,
        }
        return render(request, 'profiles/client/services.html', context)


class SignRecordView(View):
    def get(self, request, service_id=None):
        form = RecordForm()
        services = Services.objects.all()
        masters = Master.objects.all()
        context = {
            'form': form,
            'service_id': service_id,
            'services': services,
            'masters': masters
        }
        return render(request, 'profiles/client/SignRecord.html', context)

    def post(self, request, service_id=None):
        service = Services.objects.get(pk=request.POST.get('service'))
        client = Client.objects.get(user=request.user)
        master = Master.objects.get(pk=request.POST.get('master'))
        date = request.POST.get('date')
        time = request.POST.get('time')
        record = Record.objects.create(
            date=date,
            master=master,
            service=service,
            client=client,
            time=time,
            is_complete=False
        )

        return redirect('client_services')


class ClientMastersView(View):
    def get(self, request):
        masters = Master.objects.all()
        context = {'masters': masters}
        return render(request, 'profiles/client/masters.html', context)

    def post(self, request):
        master_id = request.POST.get('master_id')
        mark = request.POST.get('rating')

        master = Master.objects.get(pk=master_id)

        rating = master.rating

        mark = float(mark)
        master.rating = (rating + mark) / 2

        master.save()

        return redirect('client_masters')


class MasterProfileView(View):
    def get(self, request):
        # Получаем текущего пользователя
        user = request.user

        master = Master.objects.get(user=user)

        # Получаем записи мастера
        records = master.record_set.all()

        context = {
            'master': master,
            'records': records
        }
        return render(request, 'profiles/master/master_profile.html', context)

    def post(self, request):
        record_id = request.POST.get('record_id')
        status = request.POST.get('status')

        record = get_object_or_404(Record, pk=record_id)
        previous_status = record.is_complete  # Сохраняем предыдущее значение статуса
        record.is_complete = status == 'on'

        # Проверяем, изменился ли статус
        if previous_status != record.is_complete:
            record.save()

        return redirect('master_profile')


class ManagerProfileView(View):
    def get(self, request):
        return render(request, 'profiles/manager/manager_profile.html')


def download_statistics(request):
    # Получаем данные статистики
    statistics = Statistics.objects.all()

    # Создаем HTTP-ответ с типом содержимого CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="statistics.csv"'

    # Создаем объект для записи CSV-файла
    writer = csv.writer(response)

    # Записываем заголовки столбцов
    writer.writerow(['Date', 'Income', 'Amount Services Provided'])

    # Записываем данные статистики в CSV-файл
    for stat in statistics:
        writer.writerow([stat.date, stat.income, stat.amount_services_provided])

    return response
