from itertools import count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from admin_pannel.models import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from admin_pannel.models import Areas
import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from datetime import datetime
from django.utils.dateformat import DateFormat
from django.utils.timezone import localtime
from admin_pannel.models import TicketsNew, YatraRoutes, Yatras, BusNames, Registrations, Areas
from django.db.models import Count, F
from django.db.models.functions import Cast
from django.db.models import CharField


@api_view(['POST'])
def insertarea(request):
    """
    Insert a new area into the database.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        AreaName = body.get('AreaName', '').strip()
        AreaStatus = str(body.get('AreaStatus', 1))

        if not AreaName:
            response_data['message_code'] = 400
            response_data['message_text'] = 'Area name must be specified to create the area.'
            return Response(response_data, status=status.HTTP_200_OK)

        area = Areas.objects.create(AreaName=AreaName, AreaStatus=AreaStatus)

        if area.AreaId:
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Area created successfully.'
            response_data['message_data'] = {
                'AreaId': area.AreaId,
                'AreaName': area.AreaName,
                'AreaStatus': area.AreaStatus,
            }
        else:
            response_data['message_text'] = 'Unable to create area.'

    except Exception:
        response_data['message_text'] = 'An error occurred while creating area.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listarea(request):
    """
    Retrieve a list of active areas (AreaStatus = 1).
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        active_areas = Areas.objects.filter(AreaStatus='1').values(
            'AreaId', 'AreaName', 'AreaStatus'
        )

        if not active_areas:
            response_data['message_text'] = 'No Areas found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = list(active_areas)

    except Exception:
        response_data['message_text'] = 'An error occurred while fetching areas.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listareaall(request):
    """
    Retrieve a list of all areas, regardless of status.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        all_areas = Areas.objects.all().values('AreaId', 'AreaName', 'AreaStatus')

        if not all_areas:
            response_data['message_text'] = 'No Areas found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = list(all_areas)

    except Exception:
        response_data['message_text'] = 'An error occurred while fetching areas.'

    return Response(response_data, status=status.HTTP_200_OK)

   
@api_view(['POST'])
def modifyarea(request):
    """
    Modify an existing area's details.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        area_id = body.get('AreaId')
        area_name = body.get('AreaName', '').strip()
        area_status = str(body.get('AreaStatus', '1'))

        # --- Validation ---
        if not area_id:
            response_data['message_text'] = 'Area Id must be specified to modify area details.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not area_name:
            response_data['message_text'] = 'Area name must be specified to modify area.'
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            area_to_update = Areas.objects.get(AreaId=area_id)
        except Areas.DoesNotExist:
            response_data['message_text'] = 'Area does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Update fields
        area_to_update.AreaName = area_name
        area_to_update.AreaStatus = area_status
        area_to_update.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Area information modified successfully.'
        response_data['message_data'] = {
            'AreaId': area_to_update.AreaId,
            'AreaName': area_to_update.AreaName,
            'AreaStatus': area_to_update.AreaStatus,
        }

    except Exception:
        response_data['message_text'] = 'An error occurred while modifying area.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listgender(request):
    """
    Retrieve a list of all genders, ordered by GenderOrder.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        genders = Gender.objects.order_by('GenderOrder').values(
            'GenderId', 'GenderName', 'GenderOrder'
        )

        if not genders.exists():
            response_data['message_text'] = 'No Genders found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = list(genders)

    except Exception:
        response_data['message_text'] = 'An error occurred while fetching genders.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listbloodgroup(request):
    """
    Retrieve a list of all blood groups, ordered by BloodGroupOrder.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        blood_groups = BloodGroup.objects.order_by('bloodGroupOrder').values(
            'bloodGroupId', 'bloodGroupName', 'bloodGroupOrder'
        )

        if not blood_groups.exists():
            response_data['message_text'] = 'No Blood Groups found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = list(blood_groups)

    except Exception:
        response_data['message_text'] = 'An error occurred while fetching blood groups.'

    return Response(response_data, status=status.HTTP_200_OK)

    
@api_view(['POST'])
def insertuser(request):
    """
    Insert a new user into the database.

    Maps UserMobileNo to username and UserLoginPin to password.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        first_name = body.get('UserFirstname', '').strip()
        last_name = body.get('UserLastname', '').strip()
        mobile_no = body.get('UserMobileNo', '').strip()
        login_pin = body.get('UserLoginPin', '').strip()
        status_val = body.get('UserStatus', 1)

        # --- Validation ---
        if not first_name:
            response_data['message_text'] = 'User firstname must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not last_name:
            response_data['message_text'] = 'User lastname must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not mobile_no:
            response_data['message_text'] = 'User mobile no must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not login_pin:
            response_data['message_text'] = 'User login pin must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Check for existing user ---
        if User.objects.filter(username=mobile_no).exists():
            response_data['message_text'] = 'User with this mobile no. already exists.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Create User ---
        user = User(
            username=mobile_no,
            first_name=first_name,
            last_name=last_name,
            is_active=(status_val == 1)
        )
        user.set_password(login_pin)
        user.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'User created successfully.'
        response_data['message_data'] = {
            'UserId': user.id,
            'UserFirstname': user.first_name,
            'UserLastname': user.last_name,
            'UserMobileNo': user.username,
            'UserStatus': 1 if user.is_active else 0
        }

    except Exception:
        response_data['message_text'] = 'An error occurred while creating user.'

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def modifyuser(request):
    """
    Modify an existing user's details.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        user_id = body.get('UserId')
        first_name = body.get('UserFirstname', '').strip()
        last_name = body.get('UserLastname', '').strip()
        mobile_no = body.get('UserMobileNo', '').strip()
        login_pin = body.get('UserLoginPin', '').strip()
        status_val = body.get('UserStatus', 1)

        # --- Validation ---
        if not user_id:
            response_data['message_text'] = 'UserId must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not first_name:
            response_data['message_text'] = 'User firstname must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not last_name:
            response_data['message_text'] = 'User lastname must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not mobile_no:
            response_data['message_text'] = 'User mobile no must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Get User ---
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response_data['message_text'] = 'User does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Check for Mobile No. conflict ---
        if User.objects.filter(username=mobile_no).exclude(id=user_id).exists():
            response_data['message_text'] = 'Another user with this mobile no. already exists.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Update fields ---
        user.username = mobile_no
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = (status_val == 1)

        if login_pin:
            user.set_password(login_pin)

        user.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'User information modified successfully.'
        response_data['message_data'] = {
            'UserId': user.id,
            'UserFirstname': user.first_name,
            'UserLastname': user.last_name,
            'UserMobileNo': user.username,
            'UserStatus': 1 if user.is_active else 0
        }

    except Exception:
        response_data['message_text'] = 'An error occurred while modifying user.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def deleteuser(request):
    """
    Deactivate a user (soft delete) by setting is_active to False.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        user_id = body.get('UserId')

        # --- Validation ---
        if not user_id:
            response_data['message_text'] = 'UserId must be specified.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Get User ---
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            response_data['message_text'] = 'User does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Perform soft delete ---
        user.is_active = False
        user.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'User deactivated successfully.'
        response_data['message_data'] = {
            'UserId': user.id,
            'UserFirstname': user.first_name,
            'UserLastname': user.last_name,
            'UserMobileNo': user.username,
            'UserStatus': 0
        }

    except Exception:
        response_data['message_text'] = 'An error occurred while deactivating user.'

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
def listuserall(request):
    """
    Retrieve a list of all users, matching the PHP API structure, including password/PIN.
    """
    try:
        users = User.objects.all()
        
        if not users.exists():
            return Response({
                'message_code': 999,
                'message_text': 'No Users.',
                'message_data': []
            }, status=status.HTTP_200_OK)
        
        user_list = []
        for u in users:
            # Assuming User model has 'password' field as login PIN or a related field
            user_list.append({
                "UserId": str(u.id),
                "UserFirstname": u.first_name,
                "UserLastname": u.last_name,
                "UserMobileNo": u.username,
                "UserLoginPin": getattr(u, 'password', ''),  # or 'u.userloginpin' if custom field
                "UserStatus": "1" if u.is_active else "0",
                "UserRole": "1" if u.is_staff else "2"
            })
        
        return Response({
            'message_code': 1000,
            'message_text': 'Success',
            'message_data': user_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unable to fetch users: {e}',
            'message_data': []
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def agentlogin(request):
    """
    Authenticates an agent using mobile number and password/pin.
    Returns PHP-style response:
    - message_text: Success/Failure
    - message_data: array of user info
    """
    try:
        body = request.data
        mobile_no = body.get('userMobileNo', '').strip()
        password = body.get('userPassword', '').strip()

        # --- Validation ---
        if not mobile_no:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide your mobile no. for login.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        if not password:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide your password/pin for login.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # --- Fetch User ---
        try:
            user = User.objects.get(username=mobile_no)
        except User.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': 'Mobile no and Password/pin not valid.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # Check password
        if not user.check_password(password):
            return Response({
                'message_code': 999,
                'message_text': 'Mobile no and Password/pin not valid.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # Check active status
        if not user.is_active:
            return Response({
                'message_code': 999,
                'message_text': 'Your login is not active.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # --- Successful login ---
        user_data = [{
            "UserId": str(user.id),
            "UserFirstname": user.first_name,
            "UserLastname": user.last_name,
            "UserMobileNo": user.username,
            "UserLoginPin": "",
            "UserStatus": str(1 if user.is_active else 0),
            "UserRole": str(getattr(user, 'role', 1))
        }]

        return Response({
            'message_code': 1000,
            'message_text': 'Success',
            'message_data': user_data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'message_code': 999,
            'message_text': 'Failure',
            'message_data': []
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def searchregistrations(request):
    """
    Searches registrations based on a search term across multiple fields.
    Exact replica of the PHP API response and logic.
    """
    try:
        body = request.data
        search_term = body.get('search', '').strip()

        regs = Registrations.objects.select_related('areaId').all()

        # Filter if search term provided
        if search_term:
            regs = regs.filter(
                Q(firstname__icontains=search_term) |
                Q(lastname__icontains=search_term) |
                Q(mobileNo__icontains=search_term) |
                Q(alternateMobileNo__icontains=search_term) |
                Q(areaId__AreaName__icontains=search_term)
            )

        result_list = []
        for r in regs:
            # Convert date fields to Unix timestamp
            dob_ts = int(datetime.combine(r.dateOfBirth, datetime.min.time()).timestamp()) if r.dateOfBirth else ""
            dor_ts = int(datetime.combine(r.dateOfRegistration, datetime.min.time()).timestamp()) if r.dateOfRegistration else ""

            result_list.append({
                "RegistrationId": str(r.registrationId),
                "Firstname": r.firstname or "",
                "Middlename": r.middlename or "",
                "Lastname": r.lastname or "",
                "MobileNo": r.mobileNo or "",
                "AlternateMobileNo": r.alternateMobileNo or "",
                "BloodGroup": r.bloodGroup.bloodGroupName if getattr(r, 'bloodGroup', None) else "",
                "DateOfBirth": str(dob_ts),
                "Gender": str(r.gender or 0),
                "AadharNumber": r.aadharNumber or "",
                "AreaName": r.areaId.AreaName if r.areaId else "",
                "Address": r.address or "",
                "PhotoFileName": r.photoFileName or "",
                "DateOfRegistration": str(dor_ts),
                "PermanantId": str(r.permanentId or 0),
                "UserId": str(r.userId.id) if getattr(r, 'userId', None) else "",
                "IdProofFileName": r.idProofFileName or "",
                "VoterIdProof": r.voterIdProof or ""
            })

        if result_list:
            return Response({
                "message_code": 1000,
                "message_text": "Success",
                "message_data": result_list
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message_code": 999,
                "message_text": "No Registrations",
                "message_data": []
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message_code": 999,
            "message_text": f"Error: {e}",
            "message_data": []
        }, status=status.HTTP_200_OK)



@api_view(['POST'])
def pilgrimregistration(request):
    """
    Creates a new pilgrim registration or updates an existing one.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        registration_id = body.get('RegistrationId')

        # --- Validation ---
        mobile_no = body.get('userMobileNo', '').strip()
        first_name = body.get('userFirstname', '').strip()
        last_name = body.get('userLastname', '').strip()

        if len(mobile_no) != 10:
            response_data['message_text'] = 'Please provide a valid 10-digit mobile no.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not first_name or not last_name:
            response_data['message_text'] = 'Please provide first and last names to register.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Optional fields ---
        alt_mobile_no = body.get('userAlternateMobileNo') or None
        aadhar_no = body.get('userAadharNumber') or None

        data_to_save = {
            'firstname': first_name,
            'lastname': last_name,
            'mobileNo': mobile_no,
            'middlename': body.get('userMiddlename', '').strip(),
            'address': body.get('Address', ''),
            'gender': body.get('GenderId'),
            'dateOfBirth': body.get('DateofBirth'),
            'photoFileName': body.get('PhotoFileName', ''),
            'idProofFileName': body.get('IdProofFileName', ''),
            'voterIdProof': body.get('VoterId', ''),
            'zonePreference': body.get('ZonePreference', 0),
            'alternateMobileNo': alt_mobile_no,
            'aadharNumber': aadhar_no,
        }

        # --- Foreign Keys ---
        if body.get('AreaId'):
            try:
                data_to_save['areaId'] = Areas.objects.get(AreaId=body.get('AreaId'))
            except Areas.DoesNotExist:
                response_data['message_text'] = 'Area not found.'
                return Response(response_data, status=status.HTTP_200_OK)

        if body.get('BloodGroupId'):
            try:
                data_to_save['bloodGroup'] = BloodGroup.objects.get(bloodGroupId=body.get('BloodGroupId'))
            except BloodGroup.DoesNotExist:
                response_data['message_text'] = 'Blood Group not found.'
                return Response(response_data, status=status.HTTP_200_OK)

        if body.get('UserId'):
            try:
                data_to_save['userId'] = User.objects.get(id=body.get('UserId'))
            except User.DoesNotExist:
                response_data['message_text'] = 'User not found.'
                return Response(response_data, status=status.HTTP_200_OK)

        # --- Create or Update ---
        if not registration_id:
            registration = Registrations.objects.create(**data_to_save)
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Registration done successfully.'
            response_data['message_data'] = {
                'RegistrationId': registration.registrationId,
                'Tickets': []
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            try:
                registration_to_update = Registrations.objects.get(registrationId=registration_id)
            except Registrations.DoesNotExist:
                response_data['message_text'] = 'Registration to update not found.'
                return Response(response_data, status=status.HTTP_200_OK)

            for key, value in data_to_save.items():
                setattr(registration_to_update, key, value)
            registration_to_update.save()

            tickets = TicketsNew.objects.filter(registration_id=registration_id).values()

            response_data['message_code'] = 1000
            response_data['message_text'] = 'Registration Updated Successfully.'
            response_data['message_data'] = {
                'RegistrationId': registration_to_update.registrationId,
                'Tickets': list(tickets)
            }

    except Exception as e:
        response_data['message_text'] = 'An error occurred while saving registration.'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def getpilgrimcard(request):
    """
    Generates a pilgrim ID card image based on a RegistrationId.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        registration_id = body.get('RegistrationId')

        if not registration_id:
            response_data['message_text'] = 'Please provide the registration Id.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Fetch registration ---
        try:
            reg_data = Registrations.objects.select_related('areaId').get(registrationId=registration_id)
        except Registrations.DoesNotExist:
            response_data['message_text'] = 'Unable to find the registered user.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Fetch Yatra/Ticket Details ---
        yatra_details = TicketsNew.objects.filter(
            registration_id=registration_id,
            ticket_status_id=2
        ).select_related('yatra_route_id', 'yatra_bus_id', 'yatra_id').order_by('yatra_id__yatraStartDateTime')

        # --- Image generation ---
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        RED = (219, 70, 20)
        BLUE = (66, 135, 245)

        try:
            font = ImageFont.load_default()
        except IOError:
            font = ImageFont.load_default()

        image = Image.new('RGB', (252, 144), WHITE)
        draw = ImageDraw.Draw(image)

        draw.rectangle((2, 2, 250, 142), outline=BLACK)
        draw.line((78, 2, 78, 120), fill=BLACK)
        draw.line((2, 78, 78, 78), fill=BLACK)

        # --- Profile picture ---
        profile_pic_path = os.path.join(settings.BASE_DIR, 'path/to/default/profile.png')
        if reg_data.photoFileName:
            user_pic_path = os.path.join(settings.MEDIA_ROOT, str(reg_data.photoFileName))
            if os.path.exists(user_pic_path):
                profile_pic_path = user_pic_path

        try:
            profile_img = Image.open(profile_pic_path)
        except IOError:
            profile_img = Image.new('RGB', (100, 100), (200, 200, 200))

        profile_img = profile_img.resize((74, 74))
        image.paste(profile_img, (3, 3))

        # --- Draw Pilgrim Details ---
        y = 82
        draw.text((4, y), str(reg_data.firstname), fill=RED, font=font)
        y += 10
        draw.text((4, y), str(reg_data.lastname), fill=RED, font=font)
        y += 10
        draw.text((4, y), str(reg_data.mobileNo), fill=BLACK, font=font)
        if reg_data.alternateMobileNo:
            y += 10
            draw.text((4, y), str(reg_data.alternateMobileNo), fill=BLACK, font=font)
        if reg_data.address:
            y += 10
            draw.text((4, y), str(reg_data.address)[:30], fill=BLACK, font=font)
        if reg_data.areaId:
            y += 10
            draw.text((4, y), str(reg_data.areaId.AreaName), fill=BLACK, font=font)

        # --- Draw Yatra Details ---
        if yatra_details.exists():
            draw.line((160, 3, 160, 120), fill=BLUE)
            draw.line((220, 3, 220, 120), fill=BLUE)
            draw.text((83, 4), "Yatra", fill=RED, font=font)
            draw.text((162, 4), "Dep.", fill=RED, font=font)
            draw.text((222, 4), "Bus-Seat", fill=RED, font=font)
            
            y_line = 13
            draw.line((79, y_line, 250, y_line), fill=BLUE)
            draw.line((79, 120, 250, 120), fill=BLUE)
            y = y_line + 2
            
            for ticket in yatra_details:
                if y > 110: break
                draw.text((83, y), str(ticket.yatra_route_id.yatraRoutename)[:12], fill=BLACK, font=font)
                dep_datetime = ticket.yatra_id.yatraStartDateTime
                if dep_datetime:
                    dep_str = dep_datetime.strftime("%d@%H:%M")
                    draw.text((162, y), dep_str, fill=BLACK, font=font)
                bus_seat_str = f"{ticket.yatra_bus_id.busName}-{ticket.seat_no}"
                draw.text((222, y), bus_seat_str, fill=BLACK, font=font)
                
                y += 10
                draw.line((79, y, 250, y), fill=BLUE)
                y += 2

        # --- Save Image ---
        cards_dir = os.path.join(settings.MEDIA_ROOT, 'cards')
        os.makedirs(cards_dir, exist_ok=True)
        card_filename = f"{registration_id}.png"
        output_path = os.path.join(cards_dir, card_filename)
        image.save(output_path)

        card_url = f"{settings.MEDIA_URL}cards/{card_filename}"
        response_data['message_code'] = 1000
        response_data['message_text'] = 'Card Printed'
        response_data['message_data'] = card_url

    except Exception as e:
        response_data['message_text'] = 'An error occurred while generating the pilgrim card.'

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def inserttickets(request):
    """
    Book tickets for one or multiple Yatras (comma-separated IDs), following PHP logic.
    """
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        RegistrationId = body.get('RegistrationId')
        UserId = body.get('UserId')
        YatraIds = body.get('YatraIds')  # comma-separated
        AmountPaid = body.get('AmountPaid', 0)
        Discount = body.get('Discount', 0)
        DiscountReason = body.get('DiscountReason', '')
        PaymentId = body.get('PaymentId', '')
        PaymentMode = body.get('PaymentMode', 1)
        PaymentDetails = body.get('PaymentDetails', '')
        GroupCount = int(body.get('GroupCount', 1))
        CurrentTicket = int(body.get('CurrentTicket', 1))
        BalanceTicket = int(body.get('BalanceTicket', GroupCount))

        try:
            user_obj = User.objects.get(id=UserId)
        except User.DoesNotExist:
            response_data['message_text'] = f"User with id {UserId} does not exist."
            return Response(response_data, status=status.HTTP_200_OK)

        if not RegistrationId:
            response_data['message_text'] = 'Please provide Pilgrim to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not UserId:
            response_data['message_text'] = 'Please provide user who is adding ticket.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not YatraIds:
            response_data['message_text'] = 'Please provide Yatras to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        registration_obj = Registrations.objects.get(registrationId=RegistrationId)
        user_obj = User.objects.get(id=UserId)

        arrYatraIds = YatraIds.split(',')
        booked_tickets = 0

        with transaction.atomic():
            for yid in arrYatraIds:
                yatra = Yatras.objects.get(yatraId=yid)
                yatra_route = yatra.yatraRouteId

                # Step 1: Get available ticket (TicketStatusId = 0)
                available_ticket = TicketsNew.objects.filter(
                    ticket_status_id=0,
                    yatra_id=yatra,
                    yatra_route_id=yatra_route
                ).first()

                if not available_ticket:
                    continue

                # Step 2: Assign to user temporarily (TicketStatusId = 1)
                available_ticket.ticket_status_id = 1
                available_ticket.user_id = user_obj
                available_ticket.save()

                # Step 3: Confirm ticket (TicketStatusId = 2) with payment details
                available_ticket.ticket_status_id = 2
                available_ticket.seat_fees = yatra.yatraFees
                available_ticket.discount = Discount
                available_ticket.discount_reason = DiscountReason
                available_ticket.amount_paid = AmountPaid
                available_ticket.payment_mode = PaymentMode
                available_ticket.payment_details = PaymentDetails
                available_ticket.payment_id = PaymentId
                available_ticket.registration_id = registration_obj
                available_ticket.permanant_id = registration_obj.registrationId
                available_ticket.save()

                booked_tickets += 1

                # Update balance counters
                BalanceTicket -= 1
                CurrentTicket += 1

        # Reset counters if all tickets booked
        if BalanceTicket <= 0:
            CurrentTicket = 0
            GroupCount = 0

        response_data = {
            'message_code': 1000,
            'message_text': f'{booked_tickets} ticket(s) booked.',
            'message_data': {
                "GroupCount": GroupCount,
                "CurrentTicket": CurrentTicket,
                "BalanceTicket": BalanceTicket
            }
        }

    except Exception as e:
        response_data['message_text'] = f'Unable to add tickets: {e}'

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def totals(request):
    """
    Provides total counts for registrations and booked tickets for the year 2025.
    """
    try:
        # Count total registrations where the registration date is in the year 2025
        total_registrations = Registrations.objects.filter(dateOfRegistration__year=2025).count()

        # Count total tickets that are booked (status 2) for the year 2025
        total_tickets = TicketsNew.objects.filter(ticket_year=2025, ticket_status_id=2).count()

        response_data = {
            "Registrations": total_registrations,
            "Tickets": total_tickets
        }

        return Response({
            'message_code': 1000,
            'message_text': 'Registration+Tickets',
            'message_data': response_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unable to fetch totals: {e}',
            'message_data': {}
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def totalrouteyatrabus(request):
    """
    Provides a report of total bookings grouped by Yatra Route, Yatra, and Bus for 2025,
    replicating the PHP API response exactly.
    """
    try:
        # Fetch tickets for 2025 with status booked
        tickets = TicketsNew.objects.filter(
            ticket_year=2025,
            ticket_status_id=2
        ).select_related('yatra_route_id', 'yatra_id', 'yatra_bus_id')

        if not tickets.exists():
            return Response({
                'message_code': 999,
                'message_text': 'No bookings',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # Aggregate by Route, Yatra, Bus
        result_list = []
        group_dict = {}
        for t in tickets:
            key = (t.yatra_route_id.yatraRouteId, t.yatra_id.yatraId, t.yatra_bus_id.yatraBusId)
            if key not in group_dict:
                group_dict[key] = {
                    'YatraRouteId': str(t.yatra_route_id.yatraRouteId),
                    'YatraRouteName': t.yatra_route_id.yatraRoutename,
                    'YatraId': str(t.yatra_id.yatraId),
                    'YatraDateTime': t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if t.yatra_id.yatraDateTime else '',
                    'YatraStartDateTime': t.yatra_id.yatraStartDateTime.strftime('%d-%m-%Y %H-%M') if t.yatra_id.yatraStartDateTime else '',
                    'YatraFees': str(t.yatra_id.yatraFees),
                    'YatraBusId': str(t.yatra_bus_id.yatraBusId),
                    'BusName': t.yatra_bus_id.busName,
                    'Bookings': 0,
                    'YatraCount': 0,
                    'RouteCount': 0
                }
            group_dict[key]['Bookings'] += 1
            group_dict[key]['YatraCount'] += 1
            group_dict[key]['RouteCount'] += 1

        result_list = list(group_dict.values())

        return Response({
            'message_code': 1000,
            'message_text': 'Route, Yatra, Bus wise Booking counters',
            'message_data': result_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unable to fetch booking report: {e}',
            'message_data': []
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def routeyatrabustickets(request):
    """
    Lists all booked tickets for a specific Yatra Route, Yatra, and Bus for 2025,
    replicating the PHP API response exactly.
    """
    try:
        body = request.data
        YatraRouteId = body.get('YatraRouteId')
        YatraId = body.get('YatraId')
        YatraBusId = body.get('YatraBusId')

        # --- Validation ---
        if not YatraRouteId:
            return Response({'message_code': 999, 'message_text': 'Please provide yatra route for tickets.', 'message_data': []}, status=status.HTTP_200_OK)
        if not YatraId:
            return Response({'message_code': 999, 'message_text': 'Please provide Yatra for ticket.', 'message_data': []}, status=status.HTTP_200_OK)
        if not YatraBusId:
            return Response({'message_code': 999, 'message_text': 'Please provide yatra bus for tickets.', 'message_data': []}, status=status.HTTP_200_OK)

        # --- Query Tickets ---
        tickets = TicketsNew.objects.filter(
            yatra_route_id=YatraRouteId,
            yatra_id=YatraId,
            yatra_bus_id=YatraBusId,
            ticket_year=2025,
            ticket_status_id=2
        ).select_related(
            'yatra_route_id', 'yatra_id', 'yatra_bus_id', 'registration_id'
        ).order_by('seat_no')

        result_list = []
        for t in tickets:
            result_list.append({
                'YatraRouteId': str(t.yatra_route_id.yatraRouteId),
                'YatraId': str(t.yatra_id.yatraId),
                'YatraDateTime': t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if t.yatra_id.yatraDateTime else '',
                'YatraStartDateTime': t.yatra_id.yatraStartDateTime.strftime('%d-%m-%Y %H-%M') if t.yatra_id.yatraStartDateTime else '',
                'YatraFees': str(t.yatra_id.yatraFees),
                'YatraBusId': str(t.yatra_bus_id.yatraBusId),
                'BusName': t.yatra_bus_id.busName,
                'SeatNo': str(t.seat_no),
                'RegistrationId': str(t.registration_id.registrationId),
                'DiscountReason': t.discount_reason or '',
                'Firstname': t.registration_id.firstname,
                'Middlename': t.registration_id.middlename,
                'Lastname': t.registration_id.lastname or '',
                'MobileNo': t.registration_id.mobileNo,
                'AlternateMobileNo': t.registration_id.alternateMobileNo,
                'BloodGroup': t.registration_id.bloodGroup.bloodGroupName if t.registration_id.bloodGroup else '',
                'Gender': str(t.registration_id.gender),
                'PhotoFileName': t.registration_id.photoFileName or '',
                'IdProofFileName': t.registration_id.idProofFileName or '',
                'VoterIdProof': t.registration_id.voterIdProof or ''
            })

        if not result_list:
            return Response({'message_code': 999, 'message_text': 'No Tickets', 'message_data': []}, status=status.HTTP_200_OK)

        return Response({'message_code': 1000, 'message_text': 'Route, Yatra, Bus wise Tickets', 'message_data': result_list}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message_code': 999, 'message_text': f'Unable to fetch tickets: {e}', 'message_data': []}, status=status.HTTP_200_OK)


@api_view(['POST'])
def agentbookings(request):
    """
    Lists all tickets booked by a specific agent on a given date (2025),
    replicating the PHP API exactly.
    """
    try:
        from datetime import datetime

        body = request.data
        UserId = body.get('UserId')
        BookingDate = body.get('BookingDate')

        if not UserId:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide agent for tickets.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # --- Default date if missing ---
        if not BookingDate or not isinstance(BookingDate, str):
            BookingDate = datetime.today().strftime('%d/%m/%Y')

        # --- Parse BookingDate safely ---
        try:
            target_date = datetime.strptime(BookingDate, '%d/%m/%Y')
        except ValueError:
            target_date = datetime.today()

        # --- Filter tickets by day, month, year ---
        tickets = TicketsNew.objects.filter(
            ticket_year=2025,
            ticket_status_id=2,
            user_id=UserId,
            booking_date__day=target_date.day,
            booking_date__month=target_date.month,
            booking_date__year=target_date.year
        ).select_related(
            'yatra_route_id', 'yatra_id', 'yatra_bus_id', 'registration_id'
        ).order_by('yatra_route_id', 'yatra_id', 'yatra_bus_id')

        result_list = []
        for t in tickets:
            result_list.append({
                'YatraRouteId': t.yatra_route_id.yatraRouteId,
                'YatraRouteName': t.yatra_route_id.yatraRoutename,
                'YatraId': t.yatra_id.yatraId,
                'YatraDateTime': t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if t.yatra_id.yatraDateTime else '',
                'PaymentMode': t.payment_mode,
                'YatraFees': t.yatra_id.yatraFees,
                'YatraBusId': t.yatra_bus_id.yatraBusId,
                'BusName': t.yatra_bus_id.busName,
                'Firstname': t.registration_id.firstname,
                'Middlename': t.registration_id.middlename,
                'Lastname': t.registration_id.lastname,
                'MobileNo': t.registration_id.mobileNo,
                'AlternateMobileNo': t.registration_id.alternateMobileNo,
                'BloodGroup': t.registration_id.bloodGroup.bloodGroupName if t.registration_id.bloodGroup else '',
                'Gender': t.registration_id.gender,
                'PhotoFileName': t.registration_id.photoFileName
            })

        if not result_list:
            return Response({
                'message_code': 999,
                'message_text': 'No Tickets',
                'message_data': []
            }, status=status.HTTP_200_OK)

        return Response({
            'message_code': 1000,
            'message_text': 'Agent Route, Yatra, Bus wise Tickets on Date',
            'message_data': result_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unable to fetch tickets: {e}',
            'message_data': []
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def yatrabookings(request):
    """
    Retrieve agent route, yatra, bus-wise tickets for a given YatraRouteId.
    """

    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': []
    }

    try:
        body = request.data
        yatra_route_id = body.get('YatraRouteId', 0)

        if not yatra_route_id:
            response_data['message_text'] = 'Please provide agent for tickets.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch tickets matching the YatraRouteId and TicketStatusId=2 for 2025
        tickets = (
            TicketsNew.objects
            .filter(TicketYear=2025, TicketStatusId=2, YatraRouteId=yatra_route_id)
            .select_related('YatraId__YatraRouteId', 'YatraBusId', 'RegistrationId__AreaId')
            .order_by('YatraRouteId', 'YatraId', 'YatraBusId', 'SeatNo')
        )

        if not tickets.exists():
            response_data['message_text'] = 'No Tickets'
            return Response(response_data, status=status.HTTP_200_OK)

        ticket_list = []
        for t in tickets:
            yatra = t.YatraId
            bus = t.YatraBusId
            reg = t.RegistrationId
            area = reg.AreaId

            ticket_data = {
                "YatraRouteId": str(t.YatraRouteId),
                "YatraId": str(t.YatraId_id),
                "YatraDateTime": DateFormat(localtime(yatra.YatraDateTime)).format('d-m-Y') if yatra.YatraDateTime else None,
                "YatraStartDateTime": DateFormat(localtime(yatra.YatraStartDateTime)).format('d-m-Y H:i') if yatra.YatraStartDateTime else None,
                "YatraFees": str(yatra.YatraFees),
                "YatraBusId": str(bus.id) if bus else None,
                "BusName": bus.BusName if bus else None,
                "Firstname": reg.Firstname if reg else None,
                "Middlename": reg.Middlename if reg else None,
                "Lastname": reg.Lastname if reg else None,
                "MobileNo": reg.MobileNo if reg else None,
                "AlternateMobileNo": reg.AlternateMobileNo if reg else None,
                "BloodGroup": reg.BloodGroup if reg else None,
                "Gender": str(reg.Gender) if reg else None,
                "PhotoFileName": reg.PhotoFileName if reg else None,
                "Address": reg.Address if reg else None,
                "AreaName": area.AreaName if area else None
            }
            ticket_list.append(ticket_data)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Agent Route, Yatra, Bus wise Tickets on Date'
        response_data['message_data'] = ticket_list

    except Exception as e:
        response_data['message_text'] = f'An error occurred while fetching tickets: {str(e)}'

    return Response(response_data, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from datetime import datetime


@api_view(["GET"])
def route_yatra_dates(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        routes = YatraRoutes.objects.filter(yatraStatus=1, is_deleted=False)

        if not routes.exists():
            response_data['message_text'] = 'No Route Yatras.'
            return Response(response_data, status=status.HTTP_200_OK)

        route_list = []
        for route in routes:

            yatras = Yatras.objects.filter(
                yatraRouteId=route,
                yatraStatus__statusId=1,   # Active status
                is_deleted=False
            )

            yatra_list = []
            for yatra in yatras:
                yatra_list.append({
                    'YatraId': yatra.yatraId,
                    'YatraDateTime': yatra.yatraDateTime.strftime('%d-%m-%Y') if yatra.yatraDateTime else None,
                    'YatraFees': float(yatra.yatraFees) if yatra.yatraFees else 0,
                    'YatraStartDateTime': yatra.yatraStartDateTime.strftime('%d-%m-%Y %H:%M') if yatra.yatraStartDateTime else None,
                    'YatraStatus': yatra.yatraStatus.statusName if yatra.yatraStatus else None,
                })

            route_list.append({
                'YatraRouteId': route.yatraRouteId,
                'YatraRouteName': route.yatraRoutename,
                'YatraRouteDetails': route.yatraDetails,
                'YatraRouteStatus': route.yatraStatus,
                'Yatras': yatra_list
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Route Yatras Datewise'
        response_data['message_data'] = route_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching Route Yatras.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)







@api_view(["GET"])
def list_routes(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:

        routes = YatraRoutes.objects.filter(yatraStatus=1, is_deleted=False)

        if not routes.exists():
            response_data['message_text'] = 'No Routes.'
            return Response(response_data, status=status.HTTP_200_OK)

        route_list = []
        for r in routes:
            route_list.append({
                'YatraRouteId': r.yatraRouteId,
                'YatraRouteName': r.yatraRoutename,
                'YatraRouteDetails': r.yatraDetails,
                'YatraRouteStatus': r.yatraStatus
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = route_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching routes.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def list_routes_all(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        routes = YatraRoutes.objects.filter(is_deleted=False)

        if not routes.exists():
            response_data['message_text'] = 'No Routes.'
            return Response(response_data, status=status.HTTP_200_OK)

        route_list = []
        for r in routes:
            route_list.append({
                'YatraRouteId': r.yatraRouteId,
                'YatraRouteName': r.yatraRoutename,
                'YatraRouteDetails': r.yatraDetails,
                'YatraRouteStatus': r.yatraStatus
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = route_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching routes.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)






@api_view(["GET"])
def list_buses(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        buses = YatraBuses.objects.filter(busStatus=1, is_deleted=False)

        if not buses.exists():
            response_data['message_text'] = 'No Bus.'
            return Response(response_data, status=status.HTTP_200_OK)

        bus_list = []
        for b in buses:
            bus_list.append({
                'YatraBusId': b.yatraBusId,
                'BusName': b.busName,
                'BusDateTimeStart': b.busDateTimeStart.strftime('%d-%m-%Y %H:%M') if b.busDateTimeStart else None,
                'SeatFees': float(b.seatFees) if b.seatFees else 0.0,
                'YatraRouteId': b.yatraRouteId.yatraRouteId if b.yatraRouteId else None,
                'YatraId': b.yatraId.yatraId if b.yatraId else None,
                'BusStatus': b.busStatus,
                'BusCapacity': b.busCapacity
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = bus_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching buses.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(["GET"])
def list_yatras(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:

        yatras = Yatras.objects.filter(yatraStatus__statusId=1, is_deleted=False)

        if not yatras.exists():
            response_data['message_text'] = 'No Yatras.'
            return Response(response_data, status=status.HTTP_200_OK)

        yatras_list = []
        for y in yatras:
            yatras_list.append({
                'YatraId': y.yatraId,
                'YatraDateTime': y.yatraDateTime.strftime('%d-%m-%Y %H:%M') if y.yatraDateTime else None,
                'YatraRouteId': y.yatraRouteId.yatraRouteId if y.yatraRouteId else None,
                'YatraFees': float(y.yatraFees) if y.yatraFees else 0.0,
                'YatraStatus': y.yatraStatus.statusName if y.yatraStatus else None,
                'YatraRouteName': y.yatraRouteId.yatraRoutename if y.yatraRouteId else None,
                'YatraRouteDetails': y.yatraRouteId.yatraDetails if y.yatraRouteId else None
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = yatras_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching Yatras.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def list_yatras_all(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        yatras = Yatras.objects.filter(is_deleted=False)

        if not yatras.exists():
            response_data['message_text'] = 'No Yatras.'
            return Response(response_data, status=status.HTTP_200_OK)

        yatras_list = []
        for y in yatras:
            yatras_list.append({
                'YatraId': y.yatraId,
                'YatraDateTime': y.yatraDateTime.strftime('%d-%m-%Y %H:%M') if y.yatraDateTime else None,
                'YatraRouteId': y.yatraRouteId.yatraRouteId if y.yatraRouteId else None,
                'YatraFees': float(y.yatraFees) if y.yatraFees else 0.0,
                'YatraStatus': y.yatraStatus.statusName if y.yatraStatus else None,
                'YatraRouteName': y.yatraRouteId.yatraRoutename if y.yatraRouteId else None,
                'YatraRouteDetails': y.yatraRouteId.yatraDetails if y.yatraRouteId else None
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = yatras_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching Yatras.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def list_yatra_buses(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        yatras_buses = YatraBuses.objects.filter(yatraId__yatraStatus__statusName='Active', is_deleted=False)

        if not yatras_buses.exists():
            response_data['message_text'] = 'No Yatra Bus.'
            return Response(response_data, status=status.HTTP_200_OK)

        yatras_buses_list = []
        for yb in yatras_buses:
            y = yb.yatraId
            route = y.yatraRouteId if y else None
            yatras_buses_list.append({
                'YatraId': y.yatraId if y else None,
                'YatraDateTime': y.yatraDateTime.strftime('%d-%m-%Y %H:%M') if y and y.yatraDateTime else None,
                'YatraRouteId': route.yatraRouteId if route else None,
                'YatraStatus': y.yatraStatus.statusName if y and y.yatraStatus else None,
                'YatraRouteName': route.yatraRoutename if route else None,
                'YatraRouteDetails': route.yatraDetails if route else None,
                'YatraBusId': yb.yatraBusId,
                'BusName': yb.busName,
                'BusDateTimeStart': yb.busDateTimeStart.strftime('%d-%m-%Y %H:%M') if yb.busDateTimeStart else None,
                'SeatFees': float(yb.seatFees) if yb.seatFees else 0.0,
                'BusCapacity': yb.busCapacity
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = yatras_buses_list

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching Yatra buses.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_yatra_bus(request):
    """
    Creates a new Yatra Bus and optionally reserves seats for 'Swayamsevak'.
    This version is simplified and includes a robust catch-all for any error.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        bus_name = body.get('BusName', '').strip()
        start_datetime_str = body.get('BusDateTimeStart')
        seat_fees = body.get('SeatFees')
        route_id = body.get('YatraRouteId')
        yatra_id = body.get('YatraId')
        bus_capacity = body.get('BusCapacity')
        reserved_seats_str = body.get('ReservedSeats', '')
        user_id = body.get('UserId', 1)

        if not all([bus_name, start_datetime_str, seat_fees, route_id, yatra_id]):
            response_data['message_text'] = 'BusName, BusDateTimeStart, SeatFees, YatraRouteId, and YatraId are required.'
            return Response(response_data, status=status.HTTP_200_OK)

        start_datetime = datetime.strptime(start_datetime_str, '%d-%m-%Y %H:%M')
        yatra = Yatras.objects.get(yatraId=yatra_id)
        route = YatraRoutes.objects.get(yatraRouteId=route_id)
        user = User.objects.get(id=user_id)
        registration = Registrations.objects.get(userId=user)

        if YatraBuses.objects.filter(
            busName__iexact=bus_name,
            yatraId=yatra,
            busDateTimeStart__date=start_datetime.date()
        ).exists():
            response_data['message_text'] = 'Bus Name already exists for this Yatra on this date.'
            return Response(response_data, status=status.HTTP_200_OK)

        with transaction.atomic():
            new_bus = YatraBuses.objects.create(
                busName=bus_name,
                busDateTimeStart=start_datetime,
                seatFees=seat_fees,
                yatraRouteId=route,
                yatraId=yatra,
                busStatus=1,
                busCapacity=bus_capacity,
                created_by=user
            )

            if reserved_seats_str:
                seat_numbers_str = reserved_seats_str.replace(',', ' ').split()
                for seat_no_str in seat_numbers_str:
                    if seat_no_str.isdigit():
                        TicketsNew.objects.create(
                            yatra_id=yatra, yatra_route_id=route, yatra_bus_id=new_bus,
                            seat_no=int(seat_no_str), seat_fees=seat_fees, seat_ticket_type=1,
                            discount=seat_fees, discount_reason='Swayamsevak', amount_paid=0,
                            payment_mode=1, ticket_status_id=1, registration_id=registration,
                            user_id=user, booking_date=datetime.today().date(), created_by=user
                        )

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Yatra bus added successfully.'
        response_data['message_data'] = {'YatraBusId': new_bus.yatraBusId}

    except (Yatras.DoesNotExist, YatraRoutes.DoesNotExist, User.DoesNotExist, Registrations.DoesNotExist) as e:
        response_data['message_text'] = f"A required record was not found: {e}"
    except ValueError:
        response_data['message_text'] = 'Invalid date format for BusDateTimeStart. Please use DD-MM-YYYY HH:MM.'
    except BaseException as e: # This is the key change!
        response_data['message_text'] = 'An unexpected server error occurred.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['PUT'])
def modify_yatra_bus(request):
    """
    Modifies an existing Yatra Bus and re-creates its reserved seats.
    This version uses select_for_update() to be more explicit about locking.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        bus_id = body.get('YatraBusId')

        if not bus_id:
            response_data['message_text'] = 'YatraBusId must be specified to modify a bus.'
            return Response(response_data, status=status.HTTP_200_OK)

        with transaction.atomic():
            try:
                bus_to_update = YatraBuses.objects.select_for_update().get(yatraBusId=bus_id)
            except YatraBuses.DoesNotExist:
                response_data['message_text'] = 'This yatra bus does not exist.'
                return Response(response_data, status=status.HTTP_200_OK)

            bus_name = body.get('BusName', '').strip()
            start_datetime_str = body.get('BusDateTimeStart')
            seat_fees = body.get('SeatFees')
            route_id = body.get('YatraRouteId')
            yatra_id = body.get('YatraId')
            bus_capacity = body.get('BusCapacity')
            bus_status = body.get('BusStatus')
            reserved_seats_str = body.get('ReservedSeats', '')
            user_id = body.get('UserId', 1)

            if not all([bus_name, start_datetime_str, seat_fees, route_id, yatra_id]):
                response_data['message_text'] = 'BusName, BusDateTimeStart, SeatFees, YatraRouteId, and YatraId are required.'
                return Response(response_data, status=status.HTTP_200_OK)

            start_datetime = datetime.strptime(start_datetime_str, '%d-%m-%Y %H:%M')
            yatra = Yatras.objects.get(yatraId=yatra_id)
            route = YatraRoutes.objects.get(yatraRouteId=route_id)
            user = User.objects.get(id=user_id)
            registration = Registrations.objects.get(userId=user)

            if YatraBuses.objects.filter(
                busName__iexact=bus_name, yatraId=yatra
            ).exclude(yatraBusId=bus_id).exists():
                response_data['message_text'] = 'Another bus with this name already exists for this Yatra. Please choose another name.'
                return Response(response_data, status=status.HTTP_200_OK)

            bus_to_update.busName = bus_name
            bus_to_update.busDateTimeStart = start_datetime
            bus_to_update.seatFees = seat_fees
            bus_to_update.yatraRouteId = route
            bus_to_update.yatraId = yatra
            bus_to_update.busCapacity = bus_capacity
            bus_to_update.last_modified_by = user
            if bus_status is not None:
                bus_to_update.busStatus = bus_status

            TicketsNew.objects.filter(yatra_bus_id=bus_to_update, seat_ticket_type=1).delete()
            if reserved_seats_str:
                seat_numbers_str = reserved_seats_str.replace(',', ' ').split()
                for seat_no_str in seat_numbers_str:
                    if seat_no_str.isdigit():
                        TicketsNew.objects.create(
                            yatra_id=yatra, yatra_route_id=route, yatra_bus_id=bus_to_update,
                            seat_no=int(seat_no_str), seat_fees=seat_fees, seat_ticket_type=1,
                            discount=seat_fees, discount_reason='Swayamsevak', amount_paid=0,
                            payment_mode=1, ticket_status_id=1, registration_id=registration,
                            user_id=user, booking_date=datetime.today().date(), created_by=user
                        )
            bus_to_update.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Yatra bus updated successfully.'
        response_data['message_data'] = {'YatraBusId': bus_to_update.yatraBusId}

    except (Yatras.DoesNotExist, YatraRoutes.DoesNotExist, User.DoesNotExist, Registrations.DoesNotExist) as e:
        response_data['message_text'] = f"A required record was not found: {e}"
    except ValueError:
        response_data['message_text'] = 'Invalid date format for BusDateTimeStart. Please use DD-MM-YYYY HH:MM.'
    except Exception as e:
        response_data['message_text'] = 'An unexpected server error occurred.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def create_yatra(request):
    """
    Creates a new Yatra event (date) for a specific route.
    Prevents creating a duplicate Yatra if one already exists on the same date for the same route.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        datetime_str = body.get('YatraDateTime')
        route_id = body.get('YatraRouteId')
        status_id = body.get('YatraStatus', 1)
        fees = body.get('YatraFees', 0)
        start_datetime_str = body.get('YatraStartDateTime', datetime_str)

        if not datetime_str:
            response_data['message_text'] = 'Yatra date and time must be specified to add yatra.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not route_id:
            response_data['message_text'] = 'Yatra route must be specified to add yatra.'
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            yatra_datetime = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')
            yatra_start_datetime = datetime.strptime(start_datetime_str, '%d-%m-%Y %H:%M')
            
            route = YatraRoutes.objects.get(yatraRouteId=route_id)
            yatra_status_obj = YatraStatus.objects.get(statusId=status_id)
            
        except (ValueError, TypeError):
            response_data['message_text'] = 'Invalid date format. Please use DD-MM-YYYY HH:MM.'
            return Response(response_data, status=status.HTTP_200_OK)
        except (YatraRoutes.DoesNotExist, YatraStatus.DoesNotExist):
            response_data['message_text'] = 'The specified Yatra Route or Status ID does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        if Yatras.objects.filter(
            yatraRouteId=route,
            yatraDateTime__date=yatra_datetime.date(),
            yatraStatus_id=1
        ).exists():
            response_data['message_text'] = 'Yatra already exists for same route on same date.'
            return Response(response_data, status=status.HTTP_200_OK)

        new_yatra = Yatras.objects.create(
            yatraDateTime=yatra_datetime,
            yatraRouteId=route,
            yatraStatus=yatra_status_obj, # Use the fetched status object here
            yatraFees=fees,
            yatraStartDateTime=yatra_start_datetime
        )

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Yatra created successfully.'
        response_data['message_data'] = {'YatraId': new_yatra.yatraId}

    except Exception as e:
        response_data['message_text'] = 'An unexpected server error occurred while creating the Yatra.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['PUT'])
def modify_yatra(request):
    """
    Modifies an existing Yatra event.
    Prevents modification if it would create a duplicate Yatra (same route on the same date).
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        yatra_id = body.get('YatraId')

        if not yatra_id:
            response_data['message_text'] = 'YatraId must be specified to modify yatra details.'
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            yatra_to_update = Yatras.objects.get(yatraId=yatra_id)
        except Yatras.DoesNotExist:
            response_data['message_text'] = 'Yatra does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        datetime_str = body.get('YatraDateTime')
        route_id = body.get('YatraRouteId')
        status_id = body.get('YatraStatus', 1)
        fees = body.get('YatraFees', 0)
        start_datetime_str = body.get('YatraStartDateTime', datetime_str)

        if not datetime_str:
            response_data['message_text'] = 'Yatra date and time must be specified to modify yatra.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not route_id:
            response_data['message_text'] = 'Yatra route must be specified to modify yatra.'
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            yatra_datetime = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')
            yatra_start_datetime = datetime.strptime(start_datetime_str, '%d-%m-%Y %H:%M')
            route = YatraRoutes.objects.get(yatraRouteId=route_id)
            yatra_status_obj = YatraStatus.objects.get(statusId=status_id)
        except (ValueError, TypeError):
            response_data['message_text'] = 'Invalid date format. Please use DD-MM-YYYY HH:MM.'
            return Response(response_data, status=status.HTTP_200_OK)
        except (YatraRoutes.DoesNotExist, YatraStatus.DoesNotExist):
            response_data['message_text'] = 'The specified Yatra Route or Status ID does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        if Yatras.objects.filter(
            yatraRouteId=route,
            yatraDateTime__date=yatra_datetime.date(),
            yatraStatus_id=1
        ).exclude(yatraId=yatra_id).exists():
            response_data['message_text'] = 'Another Yatra already exists for same route on same date.'
            return Response(response_data, status=status.HTTP_200_OK)
        
        yatra_to_update.yatraDateTime = yatra_datetime
        yatra_to_update.yatraRouteId = route
        yatra_to_update.yatraStatus = yatra_status_obj
        yatra_to_update.yatraFees = fees
        yatra_to_update.yatraStartDateTime = yatra_start_datetime
        
        yatra_to_update.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Yatra information modified successfully.'
        response_data['message_data'] = {'YatraId': yatra_to_update.yatraId}

    except Exception as e:
        response_data['message_text'] = 'An unexpected server error occurred while modifying the Yatra.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_route(request):
    """
    Creates a new Yatra Route in the database.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        route_name = body.get('YatraRouteName', '').strip()
        route_details = body.get('YatraRouteDetails', '')
        route_status = body.get('YatraRouteStatus', 1)

        if not route_name:
            response_data['message_text'] = 'Route name must be specified to create the route.'
            return Response(response_data, status=status.HTTP_200_OK)

        new_route = YatraRoutes.objects.create(
            yatraRoutename=route_name,
            yatraDetails=route_details,
            yatraStatus=route_status
        )

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Route created successfully.'
        response_data['message_data'] = {
            'YatraRouteId': new_route.yatraRouteId,
            'YatraRouteName': new_route.yatraRoutename,
            'YatraRouteDetails': new_route.yatraDetails,
            'YatraRouteStatus': new_route.yatraStatus
        }

    except Exception as e:
        response_data['message_text'] = 'Unable to create route.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)




@api_view(['PUT'])
def modify_route(request):
    """
    Modifies an existing Yatra Route's details.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        route_id = body.get('YatraRouteId')
        route_name = body.get('YatraRouteName', '').strip()
        route_details = body.get('YatraRouteDetails', '')
        route_status = body.get('YatraRouteStatus', 1)

        if not route_id:
            response_data['message_text'] = 'Route Id must be specified to modify route details.'
            return Response(response_data, status=status.HTTP_200_OK)
        if not route_name:
            response_data['message_text'] = 'Route name must be specified to modify route details.'
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            route_to_update = YatraRoutes.objects.get(yatraRouteId=route_id)
        except YatraRoutes.DoesNotExist:
            response_data['message_text'] = 'Route does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)


        route_to_update.yatraRoutename = route_name
        route_to_update.yatraDetails = route_details
        route_to_update.yatraStatus = route_status

        route_to_update.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Route information modified successfully.'
        response_data['message_data'] = {
            'YatraRouteId': route_to_update.yatraRouteId,
            'YatraRouteName': route_to_update.yatraRoutename,
            'YatraRouteDetails': route_to_update.yatraDetails,
            'YatraRouteStatus': route_to_update.yatraStatus
        }

    except Exception as e:
        response_data['message_text'] = 'An unexpected server error occurred while modifying the route.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)


# def logout(request):
#     request.session.flush()  # clears all session data
#     messages.success(request, "You have successfully signed out")
#     return redirect('login')

# def dashboard(request):
#     return render(request, 'dashboard.html')