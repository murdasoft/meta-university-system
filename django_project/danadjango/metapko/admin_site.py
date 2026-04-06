from django.contrib.admin import AdminSite


class MetaPkoAdminSite(AdminSite):
    site_header = 'Meta-PKO — интеграции'
    site_title = 'Meta-PKO'
    index_title = 'Управление API и клиентами'


meta_pko_admin = MetaPkoAdminSite(name='meta_pko_admin')
