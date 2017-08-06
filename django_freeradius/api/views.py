import swapper
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone

from .serializers import RadiusPostAuthSerializer

RadiusPostAuth = swapper.load_model("django_freeradius", "RadiusPostAuth")
RadiusAccounting = swapper.load_model("django_freeradius", "RadiusAccounting")
User = get_user_model()


@api_view(['POST'])
def authorize(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    if user and user.check_password(password):
        return Response({'control:Auth-Type': 'Accept'}, status=200)
    return Response({'control:Auth-Type': 'Reject'}, status=401)


class PostAuthView(generics.CreateAPIView):
    serializer_class = RadiusPostAuthSerializer

    def post(self, request, *args, **kwargs):
        """
        Sets the response data to None in order to instruct
        FreeRADIUS to avoid processing the response body
        """
        response = self.create(request, *args, **kwargs)
        response.data = None
        return response


postauth = PostAuthView.as_view()


@api_view(['POST'])
def accounting(request):
    session_id = request.data.get('Acct-Session-Id')
    if RadiusAccounting.objects.filter(session_id=session_id).exists():
        radacct = RadiusAccounting.objects.get(session_id=session_id)
        radacct.username = request.data.get("username", '')
        radacct.session_id = request.data.get('Acct-Session-Id', '')
        radacct.groupname = request.data.get('groupname', '')
        radacct.unique_id = request.data.get('Acct-Unique-Session-Id', '')
        radacct.realm = request.data.get('Realm', '')
        radacct.nas_ip_address = request.data.get('NAS-IP-Address', '')
        radacct.nas_port_id = request.data.get('NAS-Port-ID', '')
        radacct.nas_port_type = request.data.get('NAS-Port-Type', '')
        radacct.session_time = request.data.get('Acct-Session-Time', '')
        radacct.authentication = request.data.get('Acct-Authentic', '')
        radacct.input_octets = request.data.get('Acct-Input-Octets', '')
        radacct.output_octets = request.data.get('Acct-Output-Octets', '')
        radacct.calling_station_id = request.data.get('Calling_Station_Id', '')
        radacct.called_station_id = request.data.get('Called_Station_Id', '')
        radacct.terminate_cause = request.data.get('Acct-Terminate-Cause', '')
        radacct.service_type = request.data.get('Service-Type', '')
        radacct.framed_protocol = request.data.get('Framed-Protocol', '')
        radacct.framed_ip_address = request.data.get('Framed-IP-Address', '')
        status_type = request.data.get('Acct-Status-Type')
        if status_type == 'Interim-Update':
            update_time = timezone.now()
            radacct.update_time = update_time
        if status_type == 'stop':
            stop_time = timezone.now()
            radacct.stop_time = stop_time
        radacct.save()
        return Response({''}, status=204)
    else:
        session_id = request.data.get('Acct-Session-Id')
        unique_id = request.data.get('Acct-Unique-Session-Id')
        username = request.data.get('username')
        groupname = request.data.get('groupname')
        realm = request.data.get('Realm')
        session_time = request.data.get('Acct-Session-Time')
        nas_ip_address = request.data.get('NAS-IP-Address')
        nas_port_id = request.data.get('NAS-Port-ID')
        nas_port_type = request.data.get('NAS-Port-Type')
        authentication = request.data.get('Acct-Authentic')
        input_octets = request.data.get('Acct-Input-Octets')
        output_octets = request.data.get('Acct-Output-Octets')
        calling_station_id = request.data.get('Calling_Station_Id')
        called_station_id = request.data.get('Called_Station_Id')
        terminate_cause = request.data.get('Acct-Terminate-Cause')
        service_type = request.data.get('Service-Type')
        framed_protocol = request.data.get('Framed-Protocol')
        framed_ip_address = request.data.get('Framed-IP-Address')
        status_type = request.data.get('Acct-Status-Type')
        if status_type == 'start':
            start_time = timezone.now()
        if session_time is None:
            session_time = timezone.now() - start_time
        RadiusAccounting.objects.create(session_id=session_id, unique_id=unique_id,
                                        username=username, start_time=start_time,
                                        nas_ip_address=nas_ip_address, nas_port_id=nas_port_id,
                                        nas_port_type=nas_port_type,
                                        session_time=session_time,
                                        authentication=authentication, realm=realm,
                                        input_octets=input_octets,
                                        output_octets=output_octets, calling_station_id=calling_station_id,
                                        called_station_id=called_station_id, terminate_cause=terminate_cause,
                                        service_type=service_type, framed_protocol=framed_protocol,
                                        framed_ip_address=framed_ip_address, groupname=groupname)
    return Response({''}, status=204)
