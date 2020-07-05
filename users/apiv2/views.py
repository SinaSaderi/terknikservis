import base64
import uuid
from gpay.settings import KAVE_NEGAR_TOKEN
from organization.models import Organization, Membership
from .serializers import *
from ..models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import secrets
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
from django.core.files.base import ContentFile
from rest_framework_tracking.mixins import LoggingMixin


@permission_classes((AllowAny,))
class NewPasswd(LoggingMixin, APIView):
    def post(self, request):
        mobile = request.data['mobile']
        if len(mobile) < 10:
            return Response({"status": False, "message": "incorrect mobile phone"}, 400)
        mobile = "0" + mobile[-10:]
        import kavenegar
        import json
        api = kavenegar.KavenegarAPI(KAVE_NEGAR_TOKEN)
        
        secretsGenerator = secrets.SystemRandom()
        new_pass = secretsGenerator.randint(11111, 99999)

        params = {
            'receptor': mobile,
            'message': "گردش پی" + "\n" + "رمز عبور: " + str(new_pass),
        }
        api.sms_send(params)
        organization_token = request.META.get('HTTP_ORGANIZATION', None)
        if User.objects.filter(mobile=mobile):
            u = User.objects.get(mobile=mobile)
            u.set_password(new_pass)
            u.expire_pass = True
            u.save()
            if organization_token != None:
                organization = Organization.objects.get(token__exact=organization_token)
                if not Membership.objects.filter(organization=organization, user=u).exists():
                    Membership.objects.create(organization=organization, user=u)
        else:
            user = User.objects.create_user(mobile, new_pass)
            if organization_token != None:
                organization = Organization.objects.get(token__exact=organization_token)
                if not Membership.objects.filter(organization=organization, user=user).exists():
                    Membership.objects.create(organization=organization, user=user)
        content = {"status": True}
        return Response(content)


@permission_classes((AllowAny,))
class WhichPasswd(LoggingMixin, APIView):
    def post(self, request):
        mobile = request.data['mobile']
        if len(mobile) < 10:
            return Response({"status": False, "message": "incorrect mobile phone"}, 400)
        mobile = "0" + mobile[-10:]
        if User.objects.filter(mobile=mobile).exists():
            u = User.objects.get(mobile=mobile)
            return Response({"status": True, "otp": u.expire_pass})
        else:
            return Response({"status": True, "otp": True})


class SetPasswd(LoggingMixin, APIView):
    def post(self, request):
        if request.data['password'] == request.data['password_confirm']:
            request.user.set_password(request.data['password'])
            request.user.expire_pass = False
            request.user.save()
            return Response({'success': True, 'message': "password change correctly"})
        else:
            return Response({'success': False,
                             'message': 'Password and password_confirm not match',
                             'data': request.data},
                            status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(LoggingMixin, ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        if len(request.data['mobile']) < 10:
            return Response({"status": False, "message": "incorrect mobile phone"}, 400)
        mobile = request.data['mobile']
        request.data['mobile'] = "0" + mobile[-10:]
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        res = response.data
        token = res.get('token')
        if token:
            user = jwt_decode_handler(token)
        else:
            req = request.data
            mobile = req.get('mobile')
            password = req.get('password')

            if mobile is None or password is None:
                return Response({'success': False,
                                 'message': 'Missing or incorrect credentials',
                                 'data': req},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(mobile=mobile)
                if not user.check_password(password):
                    return Response({'success': False,
                                     'message': 'Incorrect password',
                                     'data': req},
                                    status=status.HTTP_403_FORBIDDEN)
                if user.expire_pass == True:
                    user.set_password(User.objects.make_random_password())
                    user.save()
            except:
                return Response({'success': False,
                                 'message': 'User not found',
                                 'data': req},
                                status=status.HTTP_404_NOT_FOUND)

        user_model = User.objects.get(pk=user['user_id'])
        user_serlize = UserSerializer(user_model)
        user_serlize_data = user_serlize.data
        user_serlize_data['token'] = token
        user_serlize_data['max_amount'] = user_model.groups.values_list('max_amount', flat=True) or 10000000
        return Response({'success': True, "user": user_serlize_data}, status=status.HTTP_200_OK)


class userInfo(LoggingMixin, APIView):
    def get(self, request):
        user = request.user
        user_serlize = UserSerializer(user)
        user_serlize_data = user_serlize.data
        user_serlize_data['max_amount'] = user.groups.values_list('max_amount', flat=True) or 10000000
        return Response(user_serlize_data)


class ContactsCheck(LoggingMixin, APIView):
    def post(self, request):
        input_contacts = set(request.data['contacts'])
        match_contacts = set()
        result = User.objects.filter(mobile__in=input_contacts).values("mobile").all()
        for item in result:
            match_contacts.add(item['mobile'])
        diff_contact = input_contacts.difference(match_contacts)
        return Response({
            "match": match_contacts,
            'not_match': diff_contact
        })


class UserDetail(LoggingMixin, APIView):
    def put(self, request, pk=0, format=None):
        user = request.user
        if request.data.get('file', False):
            base64_file = request.data.pop('file')
            format, imgstr = base64_file.split(';base64,')
            ext = format.split('/')[-1]
            if user.file is not None:
                user.file.delete()
                data = ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + "." + ext)
            else:
                data = ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + "." + ext)
            request.data['file'] = data
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
