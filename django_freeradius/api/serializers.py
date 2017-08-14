import swapper
from rest_framework import serializers
from django.utils import timezone

RadiusPostAuth = swapper.load_model("django_freeradius", "RadiusPostAuth")
RadiusAccounting = swapper.load_model("django_freeradius", "RadiusAccounting")


class RadiusPostAuthSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, allow_blank=True)
    called_station_id = serializers.CharField(required=False, allow_blank=True)
    calling_station_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # do not save correct passwords in clear text
        if data['reply'] == 'Access-Accept':
            data['password'] = ''
        return data

    class Meta:
        model = RadiusPostAuth
        fields = ['username', 'password', 'reply',
                  'called_station_id',
                  'calling_station_id']


class RadiusAccountingSerializer(serializers.ModelSerializer):

    def validate(self, data):
        if data['Acct-Status-Type'] == 'Interim-Update':
            update_time = timezone.now()
            data['update_time'] = 'update_time'
        return data
        if data['Acct-Status-Type'] == 'stop':
            stop_time = timezone.now()
            data['stop_time'] = 'stop_time'
        return data
        if data['session_time'] is None:
            session_time = timezone.now() - start_time
            data['session_time'] = 'session_time'
        return data

    class Meta:
        model = RadiusAccounting
        fields = ['session_id', 'unique_id',
                  'username', 'start_time',
                  'nas_ip_address', 'nas_port_id',
                  'nas_port_type', 'session_time',
                  'authentication', 'realm',
                  'input_octets', 'output_octets',
                  'called_station_id', 'terminate_cause',
                  'service_type', 'framed_protocol',
                  'framed_ip_address', 'groupname',
                  'calling_station_id']
