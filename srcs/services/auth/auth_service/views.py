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
from django.contrib.auth.decorators import login_required

def login_view(request):
    return render(request, 'authentication/login.html')

def register_view(request):
    return render(request, 'authentication/register.html')

def homepage_view(request):
    return render(request, 'authentication/homepage.html')

@api_view(['POST'])
def register_user(request):
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        # profile_picture = request.FILES.get('profile_picture')

        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Handle the profile picture
        # if profile_picture:
        #     file_path = default_storage.save(f"profile_pictures/{username}_{profile_picture.name}", ContentFile(profile_picture.read()))
        #     user.profile.profile_picture = file_path
        # else:
        #     # Set a default profile picture if not provided
        #     user.profile.profile_picture = 'default_profile_picture.png'

        # user.profile.save()

        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON data."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
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
