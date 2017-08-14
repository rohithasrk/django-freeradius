import swapper
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.generics import UpdateAPIView

from .serializers import RadiusPostAuthSerializer
from .serializers import RadiusAccountingSerializer

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


class AccountingView(generics.ListCreateAPIView, generics.UpdateAPIView):
    serializer_class = RadiusAccountingSerializer

    def get_object(self):
        try:
            queryset = RadiusAccounting.objects.all()
            session_id = self.request.query_params.get('session_id')
            if queryset.filter(session_id=session_id).exists():
              return queryset
        except:
            return None


    def accounting(self, queryset, request, *args, **kwargs):
        if get_object is None:
           response = self.create(request, *args, **kwargs)
           return response
        else:
            response = self.update(request, *args, **kwargs)
            return response


accounting = AccountingView.as_view()
