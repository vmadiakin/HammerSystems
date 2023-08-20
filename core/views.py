import random
import secrets
import string
import time
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from .models import User, InvitationCode


# View for inputting the phone number during authorization
class InputPhoneView(APIView):
    template_name = 'authorize.html'
    REQUEST_DELAY = 2  # Delay in seconds

    # Generate a random authorization code of specified length
    def generate_random_code(self, length=4):
        characters = string.digits
        time.sleep(2)  # Add a delay to simulate some processing
        return ''.join(random.choice(characters) for _ in range(length))

    # Handle POST request for inputting phone number
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            context = {
                'error_message': 'Please enter a phone number.'
            }
            return render(request, self.template_name, context)

        authorization_code = self.generate_random_code(4)
        request.session['phone_number'] = phone_number
        request.session['authorization_code'] = authorization_code

        return redirect('verify_code')

    def get(self, request):
        return render(request, self.template_name)


# View for verifying the input code during authorization
class VerifyCodeView(APIView):
    template_name = 'input_code.html'

    # Handle GET request for displaying input code verification page
    def get(self, request):
        authorization_code = request.session.get('authorization_code')
        phone_number = request.session.get('phone_number')
        context = {
            'phone_number': phone_number,
            'authorization_code': authorization_code,
        }
        return render(request, self.template_name, context)

    # Handle POST request for verifying input code
    def post(self, request):
        authorization_code = request.session.get('authorization_code')
        input_code = request.data.get('input_code')
        phone_number = request.session.get('phone_number')
        if authorization_code == input_code:
            # Generate a random 6-character invitation code
            while True:
                invitation_code = secrets.token_hex(3).upper()[:6]
                if not User.objects.filter(invitation_code=invitation_code).exists():
                    break

            # Try to get the user or create a new one with the generated invitation code
            user, created = User.objects.get_or_create(phone_number=phone_number,
                                                       defaults={'invitation_code': invitation_code})

            user.set_password(authorization_code)
            user.save()
            return redirect('profile')
        else:
            error_message = 'Incorrect authorization code.'
            context = {
                'phone_number': phone_number,
                'authorization_code': authorization_code,
                'error_message': error_message,
            }
            return render(request, self.template_name, context)


# View for displaying and managing the user profile
class ProfileView(APIView):
    # Handle GET request for displaying user profile
    def get(self, request):
        phone_number = request.session.get('phone_number')
        user = get_object_or_404(User, phone_number=phone_number)

        # Get the list of users invited by the current user
        invited_users = User.objects.filter(invited_by_id=user.id)

        context = {
            'user': user,
            'phone_number': user.phone_number,
            'invitation_code': user.invitation_code,
            'invited_by': user.invited_by,
            'invited_users': invited_users
        }
        return render(request, 'profile.html', context)

    # Handle POST request for managing user profile
    def post(self, request):
        phone_number = request.session.get('phone_number')
        user = get_object_or_404(User, phone_number=phone_number)

        invited_by = request.data.get('invited_by')
        invited_users = User.objects.filter(invited_by_id=user.id)

        if invited_by:
            invited_user = User.objects.filter(invitation_code=invited_by).first()

            if not invited_user:
                error_message = 'Invitation code does not exist.'
            elif invited_user.id == user.id:
                error_message = "This is your own invitation code."
            else:
                InvitationCode.objects.create(code=invited_by, user_id=user.id)
                user.invited_by_id = invited_user.id
                user.save()
                return redirect('profile')

            context = {
                'user': user,
                'phone_number': user.phone_number,
                'invitation_code': user.invitation_code,
                'invited_by': user.invited_by,
                'error_message': error_message,
                'invited_users': invited_users
            }
            return render(request, 'profile.html', context)
