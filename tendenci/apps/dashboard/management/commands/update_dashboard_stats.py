from datetime import datetime, timedelta
from decimal import Decimal
import simplejson as json

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count, Q


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        from tendenci.apps.dashboard.models import DashboardStat

        print "Creating dashboard statistics for upcoming events"
        events = DashboardStat(key="events_upcoming")
        events.value = json.dumps(self.get_events(4), use_decimal=True)
        events.save()

        print "Creating dashboard statistics for form submissions"
        forms = DashboardStat(key="forms_30_submissions")
        forms.value = json.dumps(self.get_forms(3, 30))
        forms.save()

        print "Creating dashboard statistics for pages traffic"
        pages_traffic = DashboardStat(key="pages_30_traffic")
        pages_traffic.value = json.dumps(self.get_pages_traffic(3, 30))
        pages_traffic.save()

        print "Creating dashboard statistics for events traffic"
        events_traffic = DashboardStat(key="events_30_traffic")
        events_traffic.value = json.dumps(self.get_events_traffic(3, 30))
        events_traffic.save()

        print "Creating dashboard statistics for memberships"
        members = DashboardStat(key="memberships_30_count")
        members.value = json.dumps(self.get_membership_count(30))
        members.save()
        
        print "Creating dashboard statistics for new corporate memberships"
        corp_new = DashboardStat(key="corp_memberships_30_new")
        corp_new.value = json.dumps(self.get_new_corp_memberships(5, 30))
        corp_new.save()

        print "Creating dashboard statistics for renewed corporate memberships"
        corp_renew = DashboardStat(key="corp_memberships_30_renew")
        corp_renew.value = json.dumps(self.get_renew_corp_memberships(5, 30))
        corp_renew.save()

        print "Creating dashboard statistics for expired corporate memberships"
        corp_expired = DashboardStat(key="corp_memberships_30_expired")
        corp_expired.value = json.dumps(self.get_expired_corp_memberships(5, 30))
        corp_expired.save()

        print "Creating dashboard statistics for expiring corporate memberships"
        corp_expiring = DashboardStat(key="corp_memberships_30_expiring")
        corp_expiring.value = json.dumps(self.get_expiring_corp_memberships(5, 30))
        corp_expiring.save()

        print "Creating dashboard statistics for top corporate members"
        corp_members = DashboardStat(key="corp_members_top")
        corp_members.value = json.dumps(self.get_top_corp_members(5))
        corp_members.save()


    def get_events(self, items):
        from tendenci.addons.events.models import Event
        from tendenci.core.site_settings.utils import get_setting

        now = datetime.now().replace(second=0, microsecond=0)
        events = Event.objects.filter(start_dt__gt=now).order_by('start_dt')
        events = events.select_related()[:items]
        events_list = []
        for event in events:
            registration = "disabled"
            invoice_totals = ''
            invoice_percentage = ''
            if event.registration_configuration.enabled:
                count = event.registrants().count()
                limit = event.registration_configuration.limit
                if limit == 0:
                    registration = "%s" % count
                else:
                    registration = "%s/%s" % (count, limit)
                registrations = event.registration_set.all()
                total = registrations.aggregate(Sum('invoice__total'))
                total = total['invoice__total__sum']
                invoice_totals = get_setting('site', 'global', 'currencysymbol') + str(total)
                reg_count = Decimal(registrations.count())
                reg_paid_count = Decimal(registrations.filter(invoice__balance=0).count())
                if reg_count != 0:
                    invoice_percentage = (reg_paid_count / reg_count)
                    invoice_percentage = '{0:.2%}'.format(invoice_percentage)
                
            events_list.append([event.start_dt.strftime('%a, %b %d, %Y'),
                                event.title,
                                event.get_absolute_url(),
                                registration,
                                invoice_totals,
                                invoice_percentage])
        return events_list
                                    

    def get_forms(self, items, days):
        from tendenci.apps.forms_builder.forms.models import Form

        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        forms = Form.objects.extra(select={
            'submissions': "SELECT COUNT(*) " + \
                           "FROM forms_formentry " + \
                           "WHERE forms_formentry.form_id = " + \
                               "forms_form.id AND " + \
                               "forms_formentry.create_dt >= TIMESTAMP '%s'" % dt})
        forms = forms.order_by("-submissions")[:items]
        forms_list = []
        for form in forms:
            forms_list.append([form.title,
                               form.get_absolute_url(),
                               form.submissions,
                               reverse('form_entries', args=[form.pk])])
        return forms_list


    def get_pages_traffic(self, items, days):
        from tendenci.apps.pages.models import Page
        from tendenci.core.event_logs.models import EventLog

        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        cid = ContentType.objects.get_for_model(Page)
        total_count = EventLog.objects.filter(content_type=cid, create_dt__gte=dt).count()
        pages = Page.objects.extra(select={
            'logs': "SELECT COUNT(*) " + \
                    "FROM event_logs_eventlog " + \
                         "WHERE event_logs_eventlog.object_id = " + \
                               "pages_page.id AND " + \
                               "event_logs_eventlog.content_type_id = " + \
                               "%s AND " % cid.pk + \
                               "event_logs_eventlog.create_dt >= TIMESTAMP '%s'" % dt})
        pages = pages.order_by("-logs")[:items]
        pages_list = [['','',total_count]]
        for page in pages:
            pages_list.append([page.title,
                               page.get_absolute_url(),
                               page.logs])
        return pages_list


    def get_events_traffic(self, items, days):
        from tendenci.addons.events.models import Event
        from tendenci.core.event_logs.models import EventLog

        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        cid = ContentType.objects.get_for_model(Event)
        total_count = EventLog.objects.filter(content_type=cid, create_dt__gte=dt).count()
        events = Event.objects.extra(select={
            'logs': "SELECT COUNT(*) " + \
                    "FROM event_logs_eventlog " + \
                         "WHERE event_logs_eventlog.object_id = " + \
                               "events_event.id AND " + \
                               "event_logs_eventlog.content_type_id = " + \
                               "%s AND " % cid.pk + \
                               "event_logs_eventlog.create_dt >= TIMESTAMP '%s'" % dt})
        events = events.order_by("-logs")[:items]
        events_list = [['','',total_count]]
        for event in events:
            events_list.append([event.title,
                                event.get_absolute_url(),
                                event.logs])
        return events_list


    def get_new_corp_memberships(self, items, days):
        from tendenci.addons.corporate_memberships.models import CorpMembership

        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        corp_memberships = CorpMembership.objects.filter(join_dt__gte=dt,
                                                         status_detail="active")
        corp_memberships = corp_memberships.order_by("-join_dt")[:items]
        corp_mem_list = []
        for corp_mem in corp_memberships:
            corp_mem_list.append([corp_mem.corp_profile.name,
                                  corp_mem.get_absolute_url()])
        return corp_mem_list


    def get_renew_corp_memberships(self, items, days):
        from tendenci.addons.corporate_memberships.models import CorpMembership

        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        corp_memberships = CorpMembership.objects.filter(renew_dt__gte=dt,
                                                         status_detail="active")
        corp_memberships = corp_memberships.order_by("-renew_dt")[:items]
        corp_mem_list = []
        for corp_mem in corp_memberships:
            corp_mem_list.append([corp_mem.corp_profile.name,
                                  corp_mem.get_absolute_url()])
        return corp_mem_list


    def get_expired_corp_memberships(self, items, days):
        from tendenci.addons.corporate_memberships.models import CorpMembership

        now = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        active_qs = Q(status_detail__iexact='active')
        expired_qs = Q(status_detail__iexact='expired')

        corp_memberships = CorpMembership.objects.filter(active_qs|expired_qs)
        corp_memberships = corp_memberships.filter(expiration_dt__gte=dt,
                                                   expiration_dt__lte=now)
        corp_memberships = corp_memberships.order_by("-expiration_dt")[:items]
        corp_mem_list = []
        for corp_mem in corp_memberships:
            corp_mem_list.append([corp_mem.corp_profile.name,
                                  corp_mem.get_absolute_url()])
        return corp_mem_list


    def get_expiring_corp_memberships(self, items, days):
        from tendenci.addons.corporate_memberships.models import CorpMembership

        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dt = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999) + timedelta(days=days)
        corp_memberships = CorpMembership.objects.filter(expiration_dt__gte=now,
                                                         expiration_dt__lte=dt,
                                                         status_detail="active")
        corp_memberships = corp_memberships.order_by("expiration_dt")[:items]
        corp_mem_list = []
        for corp_mem in corp_memberships:
            corp_mem_list.append([corp_mem.corp_profile.name,
                                  corp_mem.get_absolute_url()])
        return corp_mem_list


    def get_top_corp_members(self, items):
        from tendenci.addons.corporate_memberships.models import CorpMembership
        from tendenci.addons.memberships.models import MembershipDefault

        total = MembershipDefault.QS_ACTIVE().exclude(corp_profile_id=0).count()
        corp_memberships = CorpMembership.objects.filter(status_detail='active').extra(select={
            'members': "SELECT COUNT(*) " + \
                           "FROM memberships_membershipdefault " + \
                           "WHERE memberships_membershipdefault.corp_profile_id = " + \
                               "corporate_memberships_corpmembership.corp_profile_id AND " +\
                               "memberships_membershipdefault.status_detail = 'active'"})
        corp_memberships = corp_memberships.order_by("-members")[:items]
        corp_mem_list = [['','',total]]
        for corp_mem in corp_memberships:
            corp_mem_list.append([corp_mem.corp_profile.name,
                                  corp_mem.get_absolute_url(),
                                  corp_mem.members])
        return corp_mem_list


    def get_membership_count(self, days):
        from tendenci.addons.memberships.models import MembershipDefault

        now = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)

        active_qs = Q(status_detail__iexact='active')
        expired_qs = Q(status_detail__iexact='expired')
        active_memberships = MembershipDefault.QS_ACTIVE()
        pending_memberships = MembershipDefault.QS_PENDING()
        memberships = MembershipDefault.objects.filter(active_qs | expired_qs)

        # Total active memberships count
        active = active_memberships.count()
        # Latest active memberships
        new = active_memberships.filter(create_dt__gte=dt).count()
        # Latest pending memberships
        pending = pending_memberships.filter(create_dt__gte=dt).count()
        # Latest expired memberships
        expired = memberships.filter(expire_dt__gte=dt,
                                     expire_dt__lte=now).count()
        # Memberships that are expiring soon
        dt = now + timedelta(days=days)
        now = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expiring = memberships.filter(expire_dt__gte=now,
                                      expire_dt__lte=dt).count()

        return [[active, expiring, new, pending, expired]]
