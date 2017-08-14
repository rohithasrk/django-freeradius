import swapper
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now

RadiusPostAuth = swapper.load_model("django_freeradius", "RadiusPostAuth")
RadiusAccounting = swapper.load_model("django_freeradius", "RadiusAccounting")


class TestApi(TestCase):
    def test_authorize_200(self):
        User.objects.create_user(username='molly', password='barbar')
        response = self.client.post(reverse('freeradius:authorize'),
                                    {'username': 'molly', 'password': 'barbar'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'control:Auth-Type': 'Accept'})

    def test_authorize_401(self):
        response = self.client.post(reverse('freeradius:authorize'),
                                    {'username': 'baldo', 'password': 'ugo'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, {'control:Auth-Type': 'Reject'})

    def test_postauth_accept_201(self):
        self.assertEqual(RadiusPostAuth.objects.all().count(), 0)
        params = {'username': 'molly', 'password': 'barbar', 'reply': 'Access-Accept',
                  'called_station_id': '00-11-22-33-44-55:hostname',
                  'calling_station_id': '00:26:b9:20:5f:10'}
        response = self.client.post(reverse('freeradius:postauth'), params)
        params['password'] = ''
        self.assertEqual(RadiusPostAuth.objects.filter(**params).count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, None)

    def test_postauth_reject_201(self):
        self.assertEqual(RadiusPostAuth.objects.all().count(), 0)
        params = {'username': 'molly', 'password': 'barba', 'reply': 'Access-Reject'}
        response = self.client.post(reverse('freeradius:postauth'), params)
        self.assertEqual(RadiusPostAuth.objects.filter(username='molly', password='barba').count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, None)

    def test_postauth_reject_201_empty_fields(self):
        params = {'username': 'molly', 'password': 'barba', 'reply': 'Access-Reject',
                  'called_station_id': '',
                  'calling_station_id': ''}
        response = self.client.post(reverse('freeradius:postauth'), params)
        self.assertEqual(RadiusPostAuth.objects.filter(**params).count(), 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, None)

    def test_postauth_400(self):
        response = self.client.post(reverse('freeradius:postauth'), {})
        self.assertEqual(RadiusPostAuth.objects.all().count(), 0)
        self.assertEqual(response.status_code, 400)


    def test_accounting_start(self):
        RadiusAccounting.objects.all().count()
        self.assertEqual(RadiusAccounting.objects.all().count(), 0)
        RadiusAccounting.objects.create(session_id='35000006', unique_id='75058e505ac30c5b4b9c686ee853b70f',
                                        username='admin', start_time='2017-08-08 15:16:10+0200',
                                        nas_ip_address='172.16.64.91', nas_port_id='1',
                                        nas_port_type='Async',
                                        session_time='261',
                                        authentication='authentication', realm='',
                                        input_octets='9900909',
                                        output_octets='1511075509', calling_station_id='5c:7d:c1:72:a7:3b',
                                        called_station_id='00-27-22-F3-FA-F1:hostname',
                                        terminate_cause='terminate_cause',
                                        service_type='service_type', framed_protocol='',
                                        framed_ip_address='', groupname='')
        self.assertEqual(RadiusAccounting.objects.all().count(), 1)
        response = self.client.post(reverse('freeradius:accounting'),
                                    {'username': 'admin', 'NAS-IP-Address': '172.16.64.91',
                                     'NAS-Port': "1",  'Called-Station-Id': '00-27-22-F3-FA-F1:hostname',
                                     'Calling-Station-Id': '5c:7d:c1:72:a7:3b',  'NAS-Identifier': '',
                                     'Acct-Status-Type': 'Start', 'Acct-Authentic': 'RADIUS',
                                     'Acct-Delay-Time': '0',
                                     'Acct-Unique-Session-Id': '75058e505ac30c5b4b9c686ee853b70f',
                                     'Acct-Terminate-Cause': 'User-Request',  'Acct-Input-Octets': '9900909',
                                     'Acct-Output-Octets': '1511075509',  'NAS-Port-Type': 'Async',
                                     'Acct-Session-Time': '261', 'Login-Service': 'Telnet',
                                     'Login-IP-Host': '172.16.64.25', 'Acct-Session-Id': '35000006',
                                     'Framed-Protocol': '', 'Framed-IP-Address': '',
                                     'Service-Type': 'Login-User', 'Realm': '',
                                     'Acct-Authentic': 'RADIUS'})
        self.assertEqual(RadiusAccounting.objects.filter(session_id='35000006').count(), 1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, {''})

    def test_accounting_update(self):
        RadiusAccounting.objects.all().count()
        self.assertEqual(RadiusAccounting.objects.all().count(), 0)
        RadiusAccounting.objects.create(session_id='35000006', unique_id='75058e505ac30c5b4b9c686ee853b70f',
                                        username='admin', start_time='2017-08-08 15:16:10+0200',
                                        nas_ip_address='172.16.64.91', nas_port_id='1',
                                        nas_port_type='Async',
                                        session_time='261',
                                        authentication='authentication', realm='',
                                        input_octets='9900909',
                                        output_octets='1511075509', calling_station_id='5c:7d:c1:72:a7:3b',
                                        called_station_id='00-27-22-F3-FA-F1:hostname',
                                        terminate_cause='terminate_cause',
                                        service_type='service_type', framed_protocol='',
                                        framed_ip_address='', groupname='')
        self.assertEqual(RadiusAccounting.objects.all().count(), 1)
        response = self.client.post(reverse('freeradius:accounting'),
                                    {'username': 'admin', 'NAS-IP-Address': '172.16.64.91',
                                     'NAS-Port': "1",  'Called-Station-Id': '00-27-22-F3-FA-F1:hostname',
                                     'Calling-Station-Id': '5c:7d:c1:72:a7:3b',  'NAS-Identifier': '',
                                     'Acct-Status-Type': 'Start', 'Acct-Authentic': 'RADIUS',
                                     'Acct-Delay-Time': '0',
                                     'Acct-Unique-Session-Id': '75058e505ac30c5b4b9c686ee853b70f',
                                     'Acct-Terminate-Cause': 'User-Request',  'Acct-Input-Octets': '9900909',
                                     'Acct-Output-Octets': '1511075509',  'NAS-Port-Type': 'Async',
                                     'Acct-Session-Time': '261', 'Login-Service': 'Telnet',
                                     'Login-IP-Host': '172.16.64.25', 'Acct-Session-Id': '35000006',
                                     'Framed-Protocol': '', 'Framed-IP-Address': '',
                                     'Service-Type': 'Login-User', 'Realm': '',
                                     'Acct-Authentic': 'RADIUS'})
        self.assertEqual(RadiusAccounting.objects.filter(session_id='35000006').count(), 1)
        self.assertEqual(RadiusAccounting.objects.all().count(), 1)
        response = self.client.post(reverse('freeradius:accounting'),
                                    {'username': 'admin', 'NAS-IP-Address': '172.16.64.91',
                                     'NAS-Port': "2",  'Called-Station-Id': '00-27-22-F3-FA-F1:hostname',
                                     'Calling-Station-Id': '5c:7d:c1:72:a7:3b',  'NAS-Identifier': '',
                                     'Acct-Status-Type': 'Interim-Update', 'Acct-Authentic': 'RADIUS',
                                     'Acct-Delay-Time': '0',
                                     'Acct-Unique-Session-Id': '75058e505ac30c5b4b9c686ee853b70f',
                                     'Acct-Terminate-Cause': 'User-Request',  'Acct-Input-Octets': '9810909',
                                     'Acct-Output-Octets': '1622073403',  'NAS-Port-Type': 'Async',
                                     'Acct-Session-Time': '263', 'Login-Service': 'Telnet',
                                     'Login-IP-Host': '172.16.64.25', 'Acct-Session-Id': '35000006',
                                     'Framed-Protocol': '', 'Framed-IP-Address': '',
                                     'Service-Type': 'Login-User', 'Realm': '',
                                     'Acct-Authentic': 'RADIUS'})
        self.assertEqual(RadiusAccounting.objects.filter(session_id='35000006').count(), 1)
        self.assertEqual(RadiusAccounting.objects.all().count(), 1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, {''})

    def test_accounting_stop(self):
        # Create a starting point first
        self.assertEqual(RadiusAccounting.objects.all().count(), 0)
        original = RadiusAccounting.objects.create(
            session_id='35000006', unique_id='75058e505ac30c5b4b9c686ee853b70f',
            username='admin', start_time='2017-08-08 15:16:10+0200',
            nas_ip_address='172.16.64.91', nas_port_id='1',
            nas_port_type='Async',
            session_time='261',
            authentication='authentication', realm='',
            input_octets='9900909',
            output_octets='1511075509', calling_station_id='5c:7d:c1:72:a7:3b',
            called_station_id='00-27-22-F3-FA-F1:hostname',
            terminate_cause='terminate_cause',
            service_type='service_type', framed_protocol='',
            framed_ip_address='', groupname=''
        )
        # we need to reload to cast values to correct python objects (see date)
        original.refresh_from_db()

        data = {'username': 'admin', 'nas_ip_address': '172.16.64.91',
                'nas_port': '1', 'called_station_id': '00_27_22_F3_Fa_F1',
                'calling_station_id': '5c:7d:c1:72:a7:3b', 'nas_identifier': '',
                'acct_status_type': 'Stop', 'acct_authentic': 'RADIUS',
                'acct_delay_time': '0', 
                'unique_id': '75058e505ac30c5b4b9c686ee853b70f',
                'acct_terminate_cause': 'User_Request', 'acct_input_octets': '9900909',
                'acct_output_octets': '1511075509', 'nas_port_type': 'async',
                'acct_session_time': '261', 'login_service': 'Telnet',
                'login_ip_host': '172.16.64.25', 'session_id': '35000006',
                'framed_protocol': '', 'framed_ip_address': '',
                'service_type': 'Login-User', 'Realm': ''}

        # sending an accounting packet
        response = self.client.post(reverse('freeradius:accounting'), data=data)
        self.assertEqual(response.status_code, 200)

        # this makes sure that no additional objects have been created
        self.assertEqual(RadiusAccounting.objects.filter(session_id='35000006').count(), 1)
        self.assertEqual(RadiusAccounting.objects.all().count(), 1)

        # we need to test some values provided by us
        accounting = RadiusAccounting.objects.get(session_id='35000006')
        # checking time using timetuple will remove microseconds and hopefully it makes
        # the test more stable. otherwise we need to move to freezegun
        self.assertEqual(accounting.update_time.timetuple(), now().timetuple())
        self.assertEqual(accounting.stop_time.timetuple(), now().timetuple())
        # start time is unaffected
        self.assertEqual(accounting.start_time, original.start_time)
