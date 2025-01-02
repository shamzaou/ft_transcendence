from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from decouple import config
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import jwt
import datetime
import requests

import qrcode
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.core.mail import send_mail
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django_otp.oath import totp
from django.contrib.auth import authenticate
import time
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import random
from django.core.cache import cache  # cache framework for temporary storage of otp

def login_view(request):
    return render(request, 'authentication/login.html')

import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        try:
            # Generate a random 6-digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Store the OTP in the cache with a 5-minute expiration
            cache_key = f"otp_{user.id}"
            cache.set(cache_key, otp, timeout=300)
            

            # Log the generated OTP for debugging (remove in production)
            logger.debug(f"Generated OTP for user {user.username}: {otp}")

            # Send the OTP to email
            send_mail(
                subject="Your OTP Code",
                message=f"Your OTP code is {otp}. It expires in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return Response({"message": "Login successful. Please verify OTP."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


def register_view(request):
    return render(request, 'authentication/register.html')

def homepage_view(request):
    return render(request, 'authentication/homepage.html')

@api_view(['POST'])
def register_user(request):
    try:
        # Extract user details from the request
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        # profile_picture = request.FILES.get('profile_picture')

        # Validate input fields
        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Handle the profile picture
        # Uncomment this section if profile picture functionality is implemented
        # if profile_picture:
        #     file_path = default_storage.save(f"profile_pictures/{username}_{profile_picture.name}", ContentFile(profile_picture.read()))
        #     user.profile.profile_picture = file_path
        # else:
        #     # Set a default profile picture if not provided
        #     user.profile.profile_picture = 'default_profile_picture.png'
        # user.profile.save()

        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        # Handle invalid JSON data in the request
        return Response({"error": "Invalid JSON data."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Handle other exceptions and return an error message
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def redirect_uri(request):
    if request.method == 'POST':
        try:
            intra_link = config('INTRA_LINK')
            if not intra_link:
                return JsonResponse({"error": "INTRA_LINK not set in environment"}, status=500)
            # Log the link to check if it's correctly set
            print("INTRA_LINK:", intra_link)
            return JsonResponse({"oauth_link": intra_link})
        except Exception as e:
            return JsonResponse({"error": f"Exception: {str(e)}"}, status=500)
    return JsonResponse({'error': "Method not allowed"}, status=405)

@csrf_exempt
def oauth_callback(request):
    if request.method == 'GET':  # Change to GET for handling redirect
        code = request.GET.get('code')

        if not code:
            return JsonResponse({'message': 'Authorization code not provided'}, status=400)

        # Exchange the authorization code for an access token
        token_url = 'https://api.intra.42.fr/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.REDIRECT_URI,
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET
        }
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            return JsonResponse({'message': 'Failed to retrieve access token'}, status=400)

        token_info = token_response.json()
        access_token = token_info.get('access_token')

        # Retrieve user information using the access token
        user_info_url = 'https://api.intra.42.fr/v2/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        if user_info_response.status_code != 200:
            return JsonResponse({'message': 'Failed to retrieve user info'}, status=400)

        user_info = user_info_response.json()
        username = user_info.get('login')
        email = user_info.get('email')

        if not username:
            return JsonResponse({'message': 'Failed to retrieve username'}, status=400)

        # Get or create user in Django
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.email = email
            user.set_unusable_password()  # Password is managed externally
            user.save()

        # Generate JWT token
        token = jwt.encode({
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_SETTINGS['JWT_EXP_DELTA_SECONDS'])
        }, settings.JWT_SETTINGS['JWT_SECRET_KEY'], algorithm=settings.JWT_SETTINGS['JWT_ALGORITHM'])

        return JsonResponse({'message': 'Login successful', 'token': token, 'username': username}, status=200)

    return JsonResponse({'message': 'Only GET requests are allowed'}, status=405)

def verify_jwt(request):
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        return None
    token = auth_header.split()[1]
    try:
        payload = jwt.decode(token, settings.JWT_SETTINGS['JWT_SECRET_KEY'], algorithms=[settings.JWT_SETTINGS['JWT_ALGORITHM']])
        return User.objects.get(username=payload['username'])
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
        return None

@csrf_exempt
def get_user_info(request):
    username = verify_jwt(request)
    if not username:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        match_count = len(profile.match_history)
        return JsonResponse({'username': user.username, 'match_count': match_count}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'message': 'User does not exist'}, status=404)
    except Profile.DoesNotExist:
        return JsonResponse({'message': 'Profile does not exist'}, status=404)


# @api_view(['POST'])
# def send_otp_view(request):
#     try:
#         username = request.POST.get('username')
#         user = User.objects.get(username=username)

#         # Retrieve the TOTP device
#         device = TOTPDevice.objects.get(user=user, name="email")

#         # Generate an OTP
#         otp = device.token

#         # Send OTP via email
#         send_mail(
#             subject="Your OTP Code",
#             message=f"Your OTP code is {otp}. It expires in 5 minutes.",
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#         )

#         return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
#     except User.DoesNotExist:
#         return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def verify_otp_view(request):
    username = request.data.get('username')
    otp = request.data.get('otp')

    # Debugging: Log incoming data
    logger.debug(f"Received username: {username}")
    logger.debug(f"Received OTP: {otp}")

    if not username or not otp:
        return Response({"error": "Username and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        cache_key = f"otp_{user.id}"
        cached_otp = cache.get(cache_key)

        # Debugging: Log cached OTP
        logger.debug(f"Cached OTP for user {user.username}: {cached_otp}")

        if cached_otp == otp:
            token = jwt.encode(
                {"username": user.username, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)},
                settings.SECRET_KEY,
                algorithm="HS256"
            )
            return Response({"message": "OTP verified successfully.", "token": token}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
