from django.conf.urls.defaults import patterns, url
from tendenci.core.site_settings.utils import get_setting

urlpath = get_setting('module', 'users', 'url')
if not urlpath:
    urlpath = "profiles"

urlpatterns = patterns('tendenci.apps.profiles.views',
    url(r'^%s/$' % urlpath, 'index', name="profile.index"),
    url(r'^%s/admins/$' % urlpath, 'admin_list', name="profile.admins"),
    url(r'^%s/search/$' % urlpath, 'search', name="profile.search"),
    url(r'^%s/export/$' % urlpath, 'export', name="profile.export"),
    url(r'^%s/export/(?P<task_id>[-\w]+)/$' % urlpath, 'export', name="profile.export"),
    url(r'^%s/export/(?P<task_id>[-\w]+)/status/$' % urlpath, 'export_status', name="profile.export_status"),
    url(r'^%s/export/(?P<task_id>[-\w]+)/check/$' % urlpath, 'export_check', name="profile.export_check"),
    url(r'^%s/export/(?P<task_id>[-\w]+)/download/$' % urlpath, 'export_download', name="profile.export_download"),
    url(r'^%s/add/$' % urlpath, 'add', name="profile.add"),
    url(r'^%s/edit/(?P<id>\d+)/$' % urlpath, 'edit', name="profile.edit"),
    url(r'^%s/similar/$' % urlpath, 'similar_profiles', name="profile.similar"),
    url(r'^%s/merge/(?P<sid>\d+)/$' % urlpath, 'merge_profiles', name="profile.merge_view"),
    url(r'^%s/merge/process/(?P<sid>\d+)/$' % urlpath, 'merge_process', name="profile.merge_process"),
    url(r'^%s/edit_perms/(?P<id>\d+)/$' % urlpath, 'edit_user_perms', name="profile.edit_perms"),
    url(r'^%s/avatar/(?P<id>\d+)/$' % urlpath, 'change_avatar', name="profile.change_avatar"),
    url(r'^%s/delete/(?P<id>\d+)/$' % urlpath, 'delete', name="profile.delete"),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/$' % urlpath, 'index', name='profile'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/groups/edit/$' % urlpath, 'user_groups_edit', name='profile.edit_groups'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/groups/(?P<membership_id>\d+)/edit/$' % urlpath, 'user_role_edit', name='profile.edit_role'),
    url(r'^%s/(?P<username>[+-.\w\d@\s]+)/memberships/add/$' % urlpath, 'user_membership_add', name='profile.add_membership'),
)

urlpatterns += patterns('',
    # Special redirect for user.get_absolute_url
    url(r'^users/(?P<username>[+-.\w\d@\s]+)/$', 'django.views.generic.simple.redirect_to', {
        'url': '/%s/%s/' % (urlpath, '%(username)s')}),
)
