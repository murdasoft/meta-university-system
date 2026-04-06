from .mock_data import SESSION_KEY


def mock_portal(request):
    """Контекст только для URL макета вакансий."""
    path = request.path
    if not path.startswith('/api/vacancies-mock'):
        return {}

    section = 'home'
    if '/seeker/' in path:
        section = 'seeker'
    elif '/employer/' in path:
        section = 'employer'
    elif '/admin-panel/' in path:
        section = 'admin'
    elif '/vacancies/' in path:
        section = 'vacancies'
    elif '/login/' in path or '/register/' in path:
        section = 'auth'

    return {
        'mock_user': request.session.get(SESSION_KEY),
        'mock_nav_section': section,
    }
