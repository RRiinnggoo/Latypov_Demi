from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import EnrollmentForm, ProgramForm, ServiceReviewForm, SigninForm, SignupForm
from .models import EnrollmentRequest
 
# Главная страница
def home(request):
    return render(request, 'training/home.html')

# Регистрация пользователя
def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Регистрация успешно завершена.')
        return redirect('home')
    return render(request, 'training/signup.html', {'form': form})

# Авторизация пользователя
def signin(request):
    form = SigninForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.cleaned_data['user'])
        return redirect('home')
    return render(request, 'training/signin.html', {'form': form})

# Выход из аккаунта
@require_POST
def signout(request):
    logout(request)
    return redirect('signin')

# Личный кабинет
@login_required
def cabinet(request):
    total = request.user.enrollment_requests.count()
    return render(request, 'training/cabinet.html', {'total': total})

# Список заявок пользователя
@login_required
def request_list(request):
    requests = request.user.enrollment_requests.select_related('program')
    return render(request, 'training/request_list.html', {'requests': requests})

# Создание заявки
@login_required
def request_create(request):
    form = EnrollmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.learner = request.user
        item.save()
        messages.success(request, 'Заявка отправлена на проверку.')
        return redirect('request_list')
    return render(request, 'training/request_form.html', {'form': form})

# Добавление отзыва
@login_required
def review_create(request, request_id):
    item = get_object_or_404(EnrollmentRequest, pk=request_id, learner=request.user)
    if not item.review_allowed:
        messages.error(request, 'Отзыв доступен только после завершения обучения.')
        return redirect('request_list')
    if hasattr(item, 'service_review'):
        messages.info(request, 'По этой заявке отзыв уже оставлен.')
        return redirect('request_list')

    form = ServiceReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.request = item
        review.user = request.user
        review.save()
        messages.success(request, 'Спасибо, отзыв сохранён.')
        return redirect('request_list')
    return render(request, 'training/review_form.html', {'form': form, 'item': item})

# Панель администратора
@login_required
def staff_panel(request):
    if not request.user.is_staff:
        return redirect('home')
    status = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()
    items = EnrollmentRequest.objects.select_related('learner', 'program')
    if status in EnrollmentRequest.State.values:
        items = items.filter(state=status)
    if query:
        items = items.filter(learner__username__icontains=query)
    page_obj = Paginator(items, 6).get_page(request.GET.get('page'))
    context = {
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'status': status,
        'query': query,
        'state_choices': EnrollmentRequest.State.choices,
        'finished_state': EnrollmentRequest.State.FINISHED,
    }
    return render(request, 'training/staff_panel.html', context)

# Создание курса
@login_required
def staff_program_create(request):
    if not request.user.is_staff:
        return redirect('home')
    form = ProgramForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Курс добавлен и появится в форме заявки.')
        return redirect('staff_panel')
    return render(request, 'training/program_form.html', {'form': form})

# Обновление статуса
@login_required
@require_POST
def staff_change_state(request, request_id):
    if not request.user.is_staff:
        return redirect('home')
    item = get_object_or_404(EnrollmentRequest, pk=request_id)
    if item.state == EnrollmentRequest.State.FINISHED:
        messages.error(request, 'Статус завершённой заявки больше нельзя изменить.')
        return redirect('staff_panel')
    state = request.POST.get('state')
    if state in EnrollmentRequest.State.values:
        item.state = state
        item.save(update_fields=['state'])
        messages.success(request, 'Статус заявки обновлён.')
    return redirect('staff_panel')