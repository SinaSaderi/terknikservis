import base64
import uuid
from gpay.settings import KAVE_NEGAR_TOKEN
from organization.models import Organization, Membership
from ..models import User
from . import serializers
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import secrets
from django.core import serializers as serr
from django.dispatch import receiver
from ..lib import SmsNotify

from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import obtain_jwt_token, ObtainJSONWebToken
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
from django.core.files.base import ContentFile

from rest_framework.authtoken.models import Token
import jwt,json

from rest_framework_tracking.mixins import LoggingMixin


class UserListView(LoggingMixin, generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

@permission_classes((AllowAny, ))
class NewPasswd(LoggingMixin, APIView):
    def post(self, request):
        mobile = request.POST['mobile']
        if len(mobile) <10:
            return Response({"status":False,"message":"incorrect mobile phone"},400)
        mobile ="0"+mobile[-10:]
        if mobile == "09999999999":
            new_pass = 99999
            if User.objects.filter(mobile=mobile):
                u = User.objects.get(mobile=mobile)
                u.set_password(new_pass)
                u.expire_pass = False
                u.save()
            else:
                user = User.objects.create_user(mobile, new_pass)
                user.expire_pass = False
                re = user.save();
            content = {"status": True}

            # content = {'new pass': new_pass}
            return Response(content)

        import kavenegar
        import json
        api = kavenegar.KavenegarAPI(KAVE_NEGAR_TOKEN)

        secretsGenerator = secrets.SystemRandom()
        new_pass = secretsGenerator.randint(11111, 99999)


        params = {
                'receptor': mobile,
                'message': "گردش پی" + "\n" + "رمز عبور: " + str(new_pass),
            }

        response = api.sms_send(params)

        organization_token = request.META.get('HTTP_ORGANIZATION', None)
        if User.objects.filter(mobile=mobile):
            u = User.objects.get(mobile=mobile)
            u.set_password(new_pass)
            u.expire_pass = True
            u.save()
            if organization_token != None:
                organization = Organization.objects.get(token__exact=organization_token)
                if not Membership.objects.filter(organization=organization,user=u).exists():
                    Membership.objects.create(organization=organization,user=u)
        else:
            user = User.objects.create_user(mobile, new_pass)
            if organization_token != None:
                organization = Organization.objects.get(token__exact=organization_token)
                if not Membership.objects.filter(organization=organization, user=user).exists():
                    Membership.objects.create(organization=organization, user=user)
        content = {"status": True}

        # content = {'new pass': new_pass}
        return Response(content)


@permission_classes((AllowAny, ))
class WhichPasswd(LoggingMixin, APIView):
    def post(self, request):
        mobile = request.POST['mobile']
        if len(mobile) < 10:
            return Response({"status": False, "message": "incorrect mobile phone"}, 400)
        mobile = "0" + mobile[-10:]
        if User.objects.filter(mobile=mobile).exists():
            u = User.objects.get(mobile=mobile)
            return Response({"status":True,"otp":u.expire_pass})
        else:
          return Response({"status": True,"otp":True})




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






class UserCreateAPIView(LoggingMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (AllowAny,)


class CustomAuthToken(LoggingMixin, ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        _mutable = request.data._mutable
        request.data._mutable = True

        if len(request.data['mobile']) < 10:
            return Response({"status": False, "message": "incorrect mobile phone"}, 400)
        mobile = request.data['mobile']
        request.data['mobile']= "0" + mobile[-10:]
        request.data._mutable = _mutable

        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        res = response.data
        token = res.get('token')
        if token:
            user = jwt_decode_handler(token)  # aleady json - don't serialize
        else:
            req = request.data  # try and find email in request
            mobile = req.get('mobile')
            password = req.get('password')

            if mobile is None or password is None:
                return Response({'success': False,
                                'message': 'Missing or incorrect credentials',
                                'data': req},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(mobile=mobile)
            except:
                return Response({'success': False,
                                'message': 'User not found',
                                'data': req},
                                status=status.HTTP_404_NOT_FOUND)

            if not user.check_password(password):
                return Response({'success': False,
                                'message': 'Incorrect password',
                                'data': req},
                                status=status.HTTP_403_FORBIDDEN)

            # make token from user found by email
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user = UserSerializer(user).data

        u = User.objects.get(pk=user['user_id'])
        if u.expire_pass:
            u.set_password(User.objects.make_random_password())
            u.save()

        file ="/media/"+str(u.file) if str(u.file) != "" else None
        return Response({'success': True,
                        "token": token,
                        'expire_pass': u.expire_pass,
                        'user_id': u.pk,
                        'mobile': u.mobile,
                        "first_name": u.first_name,
                        "last_name": u.last_name,
                        "full_name": u.first_name+' '+u.last_name,
                        "national_code": u.national_code,
                        "birth_date": u.birth_date,
                        "max_amount": u.groups.values_list('max_amount',flat = True) or 10000000,
                        "user": user,
                        "file":file
                        },
                        status=status.HTTP_200_OK)




        # serializer = self.serializer_class(data=request.data,
        #                                    context={'request': request})
        # serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data['user']
        # token, created = Token.objects.get_or_create(user=user)
        # return Response({
        #     'token': token.key,
        #     'user_id': user.pk,
        #     'mobile': user.mobile,
        #     "first_name": user.first_name,
        #     "last_name": user.last_name,
        #     "full_name": user.first_name+' '+user.last_name,
        #     "national_code": user.national_code,
        #     "birth_date": user.birth_date,
        #     "max_amount": user.groups.values_list('max_amount',flat = True) or 10000000
        # })

class userInfo(LoggingMixin, APIView):
    def get(self, request):
        user = request.user
        content = {
                "mobile": user.mobile,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.first_name + ' ' + user.last_name,
                "national_code": user.national_code,
                "birth_date": user.birth_date,
                "image":str(user.file),
                "max_amount": user.groups.values_list('max_amount',flat = True) or 10000000
            }
        return Response(content)


class ContactsCheck(LoggingMixin, APIView):
    def post(self, request):
        input_contacts = set(request.data['contacts'])
        match_contacts = set()
        result = User.objects.filter(mobile__in=input_contacts).values("mobile").all()
        for item in result:
            match_contacts.add(item['mobile'])
        diff_contact = input_contacts.difference(match_contacts)
        return Response({
            "match":match_contacts,
            'not_match':diff_contact
        })


class UserDetail(LoggingMixin, APIView):
    """
    Retrieve, update or delete a user instance.
    """
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk = 0, format=None):
        # user = self.get_object(pk)
        user = request.user
        if request.data.get('file',False):
            base64_file = request.data.pop('file')
            format, imgstr = base64_file.split(';base64,')
            ext = format.split('/')[-1]
            if user.file is not None:
                user.file.delete()
                data = ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + "." + ext)
            else:
                data = ContentFile(base64.b64decode(imgstr), name=str(uuid.uuid4()) + "." + ext)
            request.data['file'] = data
        serializer = serializers.UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class UserUpdateAPIView(generics.CreateAPIView):

#     def put(self, request, *args, **kwargs):
#         data = request.data
#         user = request.user
#         try:
#             user.first_name = request.data['first_name']
#         except NameError:
#             print("first_name needed")

#         try:
#             user.last_name = request.data['last_name']
#         except NameError:
#             print("last_name needed")

#         try:
#             user.national_code = request.data['national_code']
#         except NameError:
#             print("national_code needed")

#         try:
#             user.birth_date = request.data['birth_date']
#         except NameError:
#             print("birth_date needed")
#         user.save()

#         content = {'User data updated': "ok"}
#         return Response(content)

