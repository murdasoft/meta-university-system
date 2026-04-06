"""Макет портала вакансий: демо-данные и тестовая «авторизация» через сессию."""
from collections import Counter
from datetime import datetime

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .mock_data import CATEGORY_OPTIONS, MOCK_ACCOUNTS, MOCK_VACANCIES, SESSION_KEY, UNIQUE_CITIES


def _ctx(active: str, **extra):
    return {'active': active, **extra}


def _vacancy_by_slug(slug):
    for v in MOCK_VACANCIES:
        if v['slug'] == slug:
            return v
    return None


def _posted_dt(job):
    try:
        return datetime.strptime(job['posted'], '%d.%m.%Y')
    except (ValueError, TypeError, KeyError):
        return datetime.min


def _format_matches(job_format, want):
    if not want:
        return True
    f = (job_format or '').lower()
    if want == 'remote':
        return 'удал' in f
    if want == 'hybrid':
        return 'гибрид' in f
    if want == 'office':
        return 'удал' not in f and 'гибрид' not in f
    return True


def _employment_matches(employment, want):
    if not want:
        return True
    e = (employment or '').lower()
    if want == 'full':
        return 'полная' in e or e.startswith('полн')
    if want == 'part':
        return 'частич' in e or 'неполн' in e or ' / част' in e
    if want == 'shift':
        return 'смен' in e
    if want == 'project':
        return 'проект' in e
    return True


def _filter_vacancies(q='', city='', cat='', fmt='', emp=''):
    q = (q or '').strip().lower()
    city = (city or '').strip().lower()
    cat = (cat or '').strip().lower()
    fmt = (fmt or '').strip().lower()
    emp = (emp or '').strip().lower()
    out = []
    for j in MOCK_VACANCIES:
        if cat and j.get('category', '').lower() != cat:
            continue
        if city and city not in j.get('city', '').lower():
            continue
        if not _format_matches(j.get('format'), fmt):
            continue
        if not _employment_matches(j.get('employment'), emp):
            continue
        if q:
            blob = ' '.join(
                [
                    j.get('title', ''),
                    j.get('company', ''),
                    j.get('city', ''),
                    j.get('cat_label', ''),
                    j.get('description', ''),
                    ' '.join(j.get('tags', [])),
                ]
            ).lower()
            if q not in blob:
                continue
        out.append(j)
    return out


def _filter_category_rows():
    chip_counts = Counter(v['category'] for v in MOCK_VACANCIES)
    return [
        {
            'key': key,
            'label': meta['label'],
            'color': meta['color'],
            'count': chip_counts.get(key, 0),
        }
        for key, meta in CATEGORY_OPTIONS
    ]


def home(request):
    by_date = sorted(MOCK_VACANCIES, key=_posted_dt, reverse=True)
    ctx = _ctx(
        'home',
        vacancies_preview=by_date[:8],
        vacancy_total=len(MOCK_VACANCIES),
        filter_categories=_filter_category_rows(),
        unique_cities=UNIQUE_CITIES,
    )
    return render(request, 'job_portal_mock/home.dj.html', ctx)


def vacancies_list(request):
    jobs = _filter_vacancies(
        request.GET.get('q', ''),
        request.GET.get('city', ''),
        request.GET.get('cat', ''),
        request.GET.get('fmt', ''),
        request.GET.get('emp', ''),
    )
    jobs = sorted(jobs, key=_posted_dt, reverse=True)
    ctx = _ctx(
        'vacancies',
        vacancies=jobs,
        vacancy_catalog_total=len(MOCK_VACANCIES),
        unique_cities=UNIQUE_CITIES,
        filter_categories=_filter_category_rows(),
        filters={
            'q': request.GET.get('q', ''),
            'city': request.GET.get('city', ''),
            'cat': request.GET.get('cat', ''),
            'fmt': request.GET.get('fmt', ''),
            'emp': request.GET.get('emp', ''),
        },
    )
    return render(request, 'job_portal_mock/vacancies.dj.html', ctx)


def vacancy_detail(request, slug):
    job = _vacancy_by_slug(slug)
    if not job:
        raise Http404('Вакансия не найдена')
    return render(request, 'job_portal_mock/vacancy_detail.dj.html', _ctx('vacancy', job=job))


def mock_login(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip().lower()
        password = (request.POST.get('password') or '').strip()
        acc = MOCK_ACCOUNTS.get(username)
        if acc and acc['password'] == password:
            request.session[SESSION_KEY] = {
                'username': username,
                'role': acc['role'],
                'display': acc['display'],
                'email': acc['email'],
            }
            messages.success(request, f'Добро пожаловать, {acc["display"]}!')
            if acc['role'] == 'seeker':
                return redirect('job_portal_mock:seeker_dashboard')
            if acc['role'] == 'employer':
                return redirect('job_portal_mock:employer_dashboard')
            return redirect('job_portal_mock:admin_users')
        messages.error(request, 'Неверный логин или пароль. Подсказка: seeker / demo123 или employer / demo123')

    return render(request, 'job_portal_mock/login.dj.html', _ctx('login'))


def mock_register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip().lower()
        password = (request.POST.get('password') or '').strip()
        email = (request.POST.get('email') or '').strip() or f'{username}@demo.local'
        role = (request.POST.get('role') or 'seeker').strip().lower()
        if role not in ('seeker', 'employer'):
            role = 'seeker'
        if len(username) < 2:
            messages.error(request, 'Логин не короче 2 символов.')
        elif len(password) < 4:
            messages.error(request, 'Пароль не короче 4 символов.')
        elif username in MOCK_ACCOUNTS:
            messages.error(request, 'Такой логин зарезервирован для демо. Выберите другой.')
        else:
            display = email.split('@')[0].replace('.', ' ').title() if email else username
            if role == 'employer':
                display = f'Компания «{username}»'
            request.session[SESSION_KEY] = {
                'username': username,
                'role': role,
                'display': display,
                'email': email,
            }
            messages.success(request, 'Регистрация пройдена (тестовый режим, данные только в сессии).')
            if role == 'employer':
                return redirect('job_portal_mock:employer_dashboard')
            return redirect('job_portal_mock:seeker_dashboard')

    return render(request, 'job_portal_mock/register.dj.html', _ctx('register'))


def mock_logout(request):
    if request.method == 'POST':
        request.session.pop(SESSION_KEY, None)
        messages.info(request, 'Вы вышли из демо-аккаунта.')
        return redirect('job_portal_mock:home')
    return redirect('job_portal_mock:home')


# —— Соискатель ——
def seeker_dashboard(request):
    return render(request, 'job_portal_mock/seeker/dashboard.dj.html', _ctx('seeker_dash', role='seeker'))


def seeker_resumes(request):
    return render(request, 'job_portal_mock/seeker/resumes.dj.html', _ctx('seeker_resumes', role='seeker'))


def seeker_applications(request):
    return render(request, 'job_portal_mock/seeker/applications.dj.html', _ctx('seeker_apps', role='seeker'))


def seeker_saved(request):
    return render(request, 'job_portal_mock/seeker/saved.dj.html', _ctx('seeker_saved', role='seeker'))


def seeker_settings(request):
    return render(request, 'job_portal_mock/seeker/settings.dj.html', _ctx('seeker_settings', role='seeker'))


def seeker_notifications(request):
    return render(request, 'job_portal_mock/seeker/notifications.dj.html', _ctx('seeker_notif', role='seeker'))


# —— Работодатель ——
def employer_dashboard(request):
    return render(request, 'job_portal_mock/employer/dashboard.dj.html', _ctx('emp_dash', role='employer'))


def employer_vacancies(request):
    return render(request, 'job_portal_mock/employer/vacancies.dj.html', _ctx('emp_vac', role='employer'))


def employer_applications(request):
    return render(request, 'job_portal_mock/employer/applications.dj.html', _ctx('emp_apps', role='employer'))


def employer_resume_search(request):
    return render(request, 'job_portal_mock/employer/resume_search.dj.html', _ctx('emp_search', role='employer'))


def employer_company(request):
    return render(request, 'job_portal_mock/employer/company.dj.html', _ctx('emp_company', role='employer'))


def employer_notifications(request):
    return render(request, 'job_portal_mock/employer/notifications.dj.html', _ctx('emp_notif', role='employer'))


# —— Админ макет ——
def admin_users(request):
    return render(request, 'job_portal_mock/admin_mock/users.dj.html', _ctx('adm_users', role='admin'))


def admin_moderation(request):
    return render(request, 'job_portal_mock/admin_mock/moderation.dj.html', _ctx('adm_mod', role='admin'))


def admin_directories(request):
    return render(request, 'job_portal_mock/admin_mock/directories.dj.html', _ctx('adm_dir', role='admin'))


def admin_reports(request):
    return render(request, 'job_portal_mock/admin_mock/reports.dj.html', _ctx('adm_rep', role='admin'))


def admin_system(request):
    return render(request, 'job_portal_mock/admin_mock/system.dj.html', _ctx('adm_sys', role='admin'))
