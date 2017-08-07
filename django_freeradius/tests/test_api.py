import swapper
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

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
        response = self.client.post(reverse('freeradius:accounting'),
                                    {'username': 'admin', 'NAS-IP-Address': '172.16.64.91',
                                     'NAS-Port': "2",  'Called-Station-Id': '00-27-22-F3-FA-F1:hostname',
                                     'Calling-Station-Id': '5c:7d:c1:72:a7:3b',  'NAS-Identifier': '',
                                     'Acct-Status-Type': 'Interim-Update', 'Acct-Authentic': 'RADIUS',
                                     'Acct-Delay-Time': '0',
                                     'Acct-Unique-Session-Id': '75058e505ac30c5b4b9c686ee853b70f',
                                     'Acct-Terminate-Cause': 'User-Request',  'Acct-Input-Octets': '9900909',
                                     'Acct-Output-Octets': '15110755409',  'NAS-Port-Type': 'Async',
                                     'Acct-Session-Time': '262', 'Login-Service': 'Telnet',
                                     'Login-IP-Host': '172.16.64.25', 'Acct-Session-Id': '35000006',
                                     'Framed-Protocol': '', 'Framed-IP-Address': '',
                                     'Service-Type': 'Login-User', 'Realm': '',
                                     'Acct-Authentic': 'RADIUS'})
        self.assertEqual(RadiusAccounting.objects.filter(session_id='35000006').count(), 1)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, {''})

    def test_accounting_stop(self):
        RadiusAccounting.objects.all().count()
        self.assertEqual(RadiusAccounting.objects.all().count(), 0)
        response = self.client.post(reverse('freeradius:accounting'),
                                    {'username': 'admin', 'NAS-IP-Address': '172.16.64.91',
                                     'NAS-Port': "1",  'Called-Station-Id': '00-27-22-F3-FA-F1:hostname',
                                     'Calling-Station-Id': '5c:7d:c1:72:a7:3b',  'NAS-Identifier': '',
                                     'Acct-Status-Type': 'Stop', 'Acct-Authentic': 'RADIUS',
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
