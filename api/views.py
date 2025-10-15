from decimal import Decimal
import functools
from itertools import count
import operator
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
from django.http import JsonResponse
import json

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



# @api_view(['POST'])
# def pilgrimregistration(request):
#     """
#     Creates a new pilgrim registration.
#     """
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Failure',
#         'message_data': []
#     }

#     try:
#         body = request.data

#         # --- Validation ---
#         mobile_no = body.get('userMobileNo', '').strip()
#         first_name = body.get('userFirstname', '').strip()
#         last_name = body.get('userLastname', '').strip()

#         if len(mobile_no) != 10:
#             response_data['message_text'] = 'Please provide a valid 10-digit mobile no.'
#             return Response(response_data, status=status.HTTP_200_OK)
#         if not first_name or not last_name:
#             response_data['message_text'] = 'Please provide first and last names to register.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         # --- Prepare data for saving ---
#         data_to_save = {
#             'firstname': first_name,
#             'lastname': last_name,
#             'mobileNo': mobile_no,
#             'middlename': body.get('userMiddlename', '').strip(),
#             'address': body.get('Address', ''),
#             'dateOfBirth': body.get('DateofBirth'),
#             'photoFileName': body.get('PhotoFileName', ''),
#             'idProofFileName': body.get('IdProofFileName', ''),
#             'voterIdProof': body.get('VoterId', ''),
#             'zonePreference': body.get('ZonePreference', 0),
#             'alternateMobileNo': body.get('userAlternateMobileNo') or None,
#             'aadharNumber': body.get('userAadharNumber') or None,
#         }

#         # --- Handle Foreign Keys ---
#         if body.get('AreaId'):
#             try:
#                 data_to_save['areaId'] = Areas.objects.get(AreaId=body.get('AreaId'))
#             except Areas.DoesNotExist:
#                 response_data['message_text'] = 'Area not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         if body.get('BloodGroupId'):
#             try:
#                 data_to_save['bloodGroup'] = BloodGroup.objects.get(bloodGroupId=body.get('BloodGroupId'))
#             except BloodGroup.DoesNotExist:
#                 response_data['message_text'] = 'Blood Group not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         # ***** THE FIX IS HERE *****
#         # Add this block to correctly handle the Gender ForeignKey
#         if body.get('GenderId'):
#             try:
#                 # Replace 'Gender' with your actual Gender model name
#                 # Replace 'GenderId' with the primary key field name in your Gender model
#                 data_to_save['gender'] = Gender.objects.get(GenderId=body.get('GenderId'))
#             except Gender.DoesNotExist:
#                 response_data['message_text'] = 'Gender not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         if body.get('UserId'):
#             try:
#                 data_to_save['userId'] = User.objects.get(id=body.get('UserId'))
#             except User.DoesNotExist:
#                 response_data['message_text'] = 'User not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         # --- Create new registration ---
#         registration = Registrations.objects.create(**data_to_save)
#         response_data['message_code'] = 1000
#         response_data['message_text'] = 'Registration done successfully.'
#         response_data['message_data'] = {
#             'RegistrationId': registration.registrationId,
#             'Tickets': []
#         }
#         return Response(response_data, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         # This catch block is important for debugging!
#         response_data['message_text'] = f'An error occurred while saving registration: {e}'

#     return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def update_pilgrimregistration(request):
#     """
#     Updates an existing pilgrim registration.
#     """
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Failure',
#         'message_data': []
#     }

#     try:
#         body = request.data
#         registration_id = body.get('RegistrationId')

#         # --- RegistrationId is mandatory for an update ---
#         if not registration_id:
#             response_data['message_text'] = 'RegistrationId is required for an update.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         # --- Validation ---
#         mobile_no = body.get('userMobileNo', '').strip()
#         first_name = body.get('userFirstname', '').strip()
#         last_name = body.get('userLastname', '').strip()

#         if len(mobile_no) != 10:
#             response_data['message_text'] = 'Please provide a valid 10-digit mobile no.'
#             return Response(response_data, status=status.HTTP_200_OK)
#         if not first_name or not last_name:
#             response_data['message_text'] = 'Please provide first and last names to update.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         # --- Prepare data for saving ---
#         alt_mobile_no = body.get('userAlternateMobileNo') or None
#         aadhar_no = body.get('userAadharNumber') or None

#         data_to_update = {
#             'firstname': first_name,
#             'lastname': last_name,
#             'mobileNo': mobile_no,
#             'middlename': body.get('userMiddlename', '').strip(),
#             'address': body.get('Address', ''),
#             'gender': body.get('GenderId'),
#             'dateOfBirth': body.get('DateofBirth'),
#             'photoFileName': body.get('PhotoFileName', ''),
#             'idProofFileName': body.get('IdProofFileName', ''),
#             'voterIdProof': body.get('VoterId', ''),
#             'zonePreference': body.get('ZonePreference', 0),
#             'alternateMobileNo': alt_mobile_no,
#             'aadharNumber': aadhar_no,
#         }

#         # --- Handle Foreign Keys ---
#         if body.get('AreaId'):
#             try:
#                 data_to_update['areaId'] = Areas.objects.get(AreaId=body.get('AreaId'))
#             except Areas.DoesNotExist:
#                 response_data['message_text'] = 'Area not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         if body.get('BloodGroupId'):
#             try:
#                 data_to_update['bloodGroup'] = BloodGroup.objects.get(bloodGroupId=body.get('BloodGroupId'))
#             except BloodGroup.DoesNotExist:
#                 response_data['message_text'] = 'Blood Group not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         if body.get('UserId'):
#             try:
#                 data_to_update['userId'] = User.objects.get(id=body.get('UserId'))
#             except User.DoesNotExist:
#                 response_data['message_text'] = 'User not found.'
#                 return Response(response_data, status=status.HTTP_200_OK)

#         # --- Find and update the registration ---
#         try:
#             registration_to_update = Registrations.objects.get(registrationId=registration_id)
#         except Registrations.DoesNotExist:
#             response_data['message_text'] = 'Registration to update not found.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         for key, value in data_to_update.items():
#             setattr(registration_to_update, key, value)
#         registration_to_update.save()

#         # --- Fetch associated tickets ---
#         tickets = TicketsNew.objects.filter(registration_id=registration_id).values()

#         response_data['message_code'] = 1000
#         response_data['message_text'] = 'Registration Updated Successfully.'
#         response_data['message_data'] = {
#             'RegistrationId': registration_to_update.registrationId,
#             'Tickets': list(tickets)
#         }

#     except Exception as e:
#         response_data['message_text'] = f'An error occurred while updating registration: {e}'

#     return Response(response_data, status=status.HTTP_200_OK)    


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


# @api_view(['POST'])
# def insertblanktickets(request):
#     """
#     Creates blank tickets (seats) for a specific Yatra based on the number of buses and seats.
#     This should only be accessible by administrators.
#     """
#     try:
#         yatra_id = int(request.data.get('yatra_id'))
#         num_buses = int(request.data.get('num_buses'))
#         seats_per_bus = int(request.data.get('seats_per_bus'))
#     except (ValueError, TypeError):
#         return Response(
#             {"message_text": "Invalid input. All parameters must be integers."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     try:
#         yatra_instance = Yatras.objects.get(yatraId=yatra_id)
#         yatra_route_instance = yatra_instance.yatraRouteId
#     except Yatras.DoesNotExist:
#         return Response(
#             {"message_text": f'Yatra with ID "{yatra_id}" does not exist.'},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     bus_ids_to_fetch = list(range(1, num_buses + 1))
    
#     # ✅ FIX 1: Use the correct field name 'yatraId' for filtering.
#     bus_objects = YatraBuses.objects.filter(yatraId=yatra_instance, yatraBusId__in=bus_ids_to_fetch)

#     bus_lookup = {bus.yatraBusId: bus for bus in bus_objects}

#     if len(bus_lookup) != num_buses:
#         return Response(
#             {"message_text": f"Error: Expected {num_buses} buses for Yatra {yatra_id}, but only found {len(bus_lookup)}. Please ensure all YatraBuses records are created first."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     with transaction.atomic():
#         tickets_to_create = []
#         for bus_num in range(1, num_buses + 1):
#             bus_instance = bus_lookup.get(bus_num)
            
#             for seat_num in range(1, seats_per_bus + 1):
#                 ticket = TicketsNew(
#                     # ✅ FIX 2: Use correct camelCase keyword arguments matching your model fields.
#                     yatraId=yatra_instance,
#                     yatraRouteId=yatra_route_instance,
#                     yatraBusId=bus_instance, 
#                     seat_no=seat_num,
#                     ticket_status_id=0,
#                     seat_fees=yatra_instance.yatraFees
#                     # Add other defaults if your model requires them
#                 )
#                 tickets_to_create.append(ticket)
        
#         if tickets_to_create:
#             TicketsNew.objects.bulk_create(tickets_to_create)
#             total_created = len(tickets_to_create)
#             return Response(
#                 {
#                     "message_code": 1000,
#                     "message_text": f'Successfully created {total_created} blank tickets for Yatra {yatra_id}.'
#                 },
#                 status=status.HTTP_201_CREATED
#             )
#         else:
#             return Response({"message_text": "No tickets were created."}, status=status.HTTP_200_OK)
            

@api_view(['POST'])
def insertblanktickets(request):
    """
    Creates blank tickets for ALL buses associated with a specific Yatra.
    This version is confirmed to match the naming conventions of all models.
    """
    try:
        yatra_id = int(request.data.get('yatra_id'))
        seats_per_bus = int(request.data.get('seats_per_bus'))
    except (ValueError, TypeError):
        return Response(
            {"message_text": "Invalid input. 'yatra_id' and 'seats_per_bus' must be integers."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Query Yatras model using its 'yatraId' (camelCase) field
        yatra_instance = Yatras.objects.get(yatraId=yatra_id)
        yatra_route_instance = yatra_instance.yatraRouteId
    except Yatras.DoesNotExist:
        return Response(
            {"message_text": f'Yatra with ID "{yatra_id}" does not exist.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Query YatraBuses model using its 'yatraId' (camelCase) field
    bus_objects_for_yatra = YatraBuses.objects.filter(yatraId=yatra_instance)

    if not bus_objects_for_yatra.exists():
        return Response(
            {"message_text": f"Error: No buses have been created for Yatra {yatra_id} yet."},
            status=status.HTTP_404_NOT_FOUND
        )

    with transaction.atomic():
        tickets_to_create = []
        for bus_instance in bus_objects_for_yatra:
            for seat_num in range(1, seats_per_bus + 1):
                # This block now correctly matches your provided TicketsNew model definition.
                ticket = TicketsNew(
                    yatra_id=yatra_instance,          # Correct: snake_case for the TicketsNew model
                    yatra_route_id=yatra_route_instance,  # Correct: snake_case for the TicketsNew model
                    yatra_bus_id=bus_instance,          # Correct: snake_case for the TicketsNew model
                    seat_no=seat_num,
                    ticket_status_id=0,
                    seat_fees=yatra_instance.yatraFees
                )
                tickets_to_create.append(ticket)
        
        if tickets_to_create:
            TicketsNew.objects.bulk_create(tickets_to_create)
            total_created = len(tickets_to_create)
            num_buses_processed = len(bus_objects_for_yatra)
            return Response(
                {
                    "message_code": 1000,
                    "message_text": f'Successfully created {total_created} blank tickets for the {num_buses_processed} buses found for Yatra {yatra_id}.'
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response({"message_text": "No tickets were created."}, status=status.HTTP_200_OK)
        


@api_view(['POST'])
def inserttickets(request):
    """
    (Corrected Optimized Version)
    Books tickets using true bulk operations to prevent deadlocks and ensure high performance.
    """
    response_data = { 'message_code': 999, 'message_text': 'Failure', 'message_data': {} }

    try:
        body = request.data
        user_id = body.get('UserId')
        bookings = body.get('Bookings')

        if not all([user_id, bookings]):
            response_data['message_text'] = 'UserId and a list of Bookings are required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Step 1: Gather all IDs from the entire request ---
        yatra_ids = set()
        reg_ids = set()
        ticket_q_objects = [] # We will build a list of Q objects for a single query

        for group in bookings:
            yatra_id = group.get('YatraId')
            yatra_bus_id = group.get('BusId')
            yatra_ids.add(yatra_id)
            for reg in group.get('Registrations', []):
                reg_ids.add(reg.get('RegistrationId'))
                # Create a Q object for each specific seat we need to find
                ticket_q_objects.append(
                    Q(yatra_id=yatra_id, yatra_bus_id=yatra_bus_id, seat_no=reg.get('SeatNo'))
                )

        if not ticket_q_objects:
            raise Exception("No registration details provided in the booking request.")

        # --- Step 2: Fetch all required objects from the DB in bulk ---
        user_obj = User.objects.get(id=user_id)
        yatras_map = {y.yatraId: y for y in Yatras.objects.filter(yatraId__in=yatra_ids)}
        registrations_map = {r.registrationId: r for r in Registrations.objects.filter(registrationId__in=reg_ids)}

        # *** THE CRITICAL FIX IS HERE ***
        # Combine all Q objects with an OR operator and execute ONE single query
        combined_ticket_query = functools.reduce(operator.or_, ticket_q_objects)
        
        # Now, tickets_to_book contains all the ticket objects we need
        tickets_to_book = list(TicketsNew.objects.filter(combined_ticket_query))
        
        # --- Pre-flight checks (very fast, in-memory) ---
        if len(tickets_to_book) != len(ticket_q_objects):
             raise Exception("One or more of the requested seats could not be found or do not exist.")
        
        for ticket in tickets_to_book:
            if ticket.ticket_status_id != 0:
                raise Exception(f"Seat {ticket.seat_no} for Yatra {ticket.yatra_id_id} is not available.")

        # --- Step 3: Process the logic in memory ---
        amount_paid_total = Decimal(body.get('AmountPaid', 0))
        discount_total = Decimal(body.get('Discount', 0))
        discount_reason = body.get('DiscountReason', '')
        payment_mode = body.get('PaymentMode', 1)

        total_tickets = len(tickets_to_book)
        amount_per_ticket = amount_paid_total / total_tickets if total_tickets > 0 else 0
        discount_per_ticket = discount_total / total_tickets if total_tickets > 0 else 0
        
        # Loop through the objects we already have in memory
        for ticket_obj in tickets_to_book:
            # We need to find which registration this ticket belongs to from the original request
            # This is a bit complex, but it's all in-memory and therefore extremely fast
            found_reg = False
            for group in bookings:
                if ticket_obj.yatra_id_id == int(group.get('YatraId')) and ticket_obj.yatra_bus_id_id == int(group.get('BusId')):
                    for reg_info in group.get('Registrations', []):
                        if ticket_obj.seat_no == int(reg_info.get('SeatNo')):
                            reg_id = int(reg_info.get('RegistrationId'))
                            registration_obj = registrations_map.get(reg_id)
                            yatra_obj = yatras_map.get(ticket_obj.yatra_id_id)
                            
                            if not registration_obj or not yatra_obj:
                                raise Exception(f"Invalid YatraId or RegistrationId provided.")
                            
                            # Modify the object in memory
                            ticket_obj.ticket_status_id = 2  # Confirmed
                            ticket_obj.user_id = user_obj
                            ticket_obj.registration_id = registration_obj
                            ticket_obj.permanant_id = registration_obj.registrationId
                            ticket_obj.seat_fees = yatra_obj.yatraFees
                            ticket_obj.discount = discount_per_ticket
                            ticket_obj.discount_reason = discount_reason
                            ticket_obj.amount_paid = amount_per_ticket
                            ticket_obj.payment_mode = payment_mode
                            found_reg = True
                            break
                if found_reg:
                    break

        # --- Step 4: Perform a single bulk update ---
        with transaction.atomic():
            TicketsNew.objects.bulk_update(tickets_to_book, [
                'ticket_status_id', 'user_id', 'registration_id', 'permanant_id',
                'seat_fees', 'discount', 'discount_reason', 'amount_paid', 'payment_mode'
            ])

        response_data = {
            'message_code': 1000,
            'message_text': f'{len(tickets_to_book)} ticket(s) booked successfully.',
            'message_data': {}
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        response_data['message_text'] = f'An unexpected error occurred: {e}'
        return Response(response_data, status=status.HTTP_200_OK)
    
    
# @api_view(['POST'])
# def inserttickets(request):
#     """
#     Book tickets, correctly implementing the group/bus assignment logic from the PHP API.
#     """
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Failure',
#         'message_data': {}
#     }

#     try:
#         body = request.data
#         RegistrationId = body.get('RegistrationId')
#         UserId = body.get('UserId')
#         YatraIds = body.get('YatraIds')
#         AmountPaid = body.get('AmountPaid', 0)
#         Discount = body.get('Discount', 0)
#         DiscountReason = body.get('DiscountReason', '')
#         # ✅ FIX: Get the PaymentId from the request. It could be a number or an empty string/null.
#         payment_id_from_request = body.get('PaymentId')
#         PaymentMode = body.get('PaymentMode', 1)
#         PaymentDetails = body.get('PaymentDetails', '')
#         GroupCount = int(body.get('GroupCount', 1))
#         CurrentTicket = int(body.get('CurrentTicket', 1))
#         BalanceTicket = int(body.get('BalanceTicket', GroupCount))

#         if not all([RegistrationId, UserId, YatraIds]):
#             response_data['message_text'] = 'RegistrationId, UserId, and YatraIds are required.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         user_obj = User.objects.get(id=UserId)
#         registration_obj = Registrations.objects.get(registrationId=RegistrationId)

#         # ✅ FIX: Prepare the payment object. Default to None.
#         payment_obj = None
#         if payment_id_from_request:
#             try:
#                 # If an ID was provided, fetch the actual Payments object.
#                 payment_obj = Payments.objects.get(pk=payment_id_from_request)
#             except Payments.DoesNotExist:
#                 # Handle the case where an invalid ID is sent.
#                 response_data['message_text'] = f"Invalid PaymentId '{payment_id_from_request}' provided."
#                 raise Exception(response_data['message_text'])
        
#         arrYatraIds = YatraIds.split(',')
#         booked_tickets_count = 0
        
#         with transaction.atomic():
#             for yid in arrYatraIds:
#                 yatra = Yatras.objects.get(yatraId=yid)
#                 # ... (rest of the group logic is correct)

#                 if BalanceTicket == GroupCount:
#                     buses_with_capacity = TicketsNew.objects.filter(yatra_id=yatra, ticket_status_id=0).values('yatra_bus_id').annotate(available_seats=Count('ticket_id')).filter(available_seats__gte=GroupCount).order_by('yatra_bus_id')
#                     bus_to_use = buses_with_capacity.first()
#                     if not bus_to_use:
#                         response_data['message_text'] = f'No bus found with capacity for a group of {GroupCount} for Yatra {yid}.'
#                         raise Exception(response_data['message_text'])
#                     yatra_bus_id_for_group = bus_to_use['yatra_bus_id']
#                     seats_to_reserve = TicketsNew.objects.filter(yatra_id=yatra, yatra_bus_id=yatra_bus_id_for_group, ticket_status_id=0).order_by('ticket_id')[:GroupCount]
#                     seat_ids_to_reserve = [seat.ticket_id for seat in seats_to_reserve]
#                     TicketsNew.objects.filter(ticket_id__in=seat_ids_to_reserve).update(ticket_status_id=1, user_id=user_obj)
#                 else:
#                     existing_reservation = TicketsNew.objects.filter(yatra_id=yatra, user_id=user_obj, ticket_status_id=1).order_by('ticket_id').first()
#                     if not existing_reservation:
#                         response_data['message_text'] = 'Cannot find a reserved seat for the next person in the group.'
#                         raise Exception(response_data['message_text'])
#                     yatra_bus_id_for_group = existing_reservation.yatra_bus_id
                
#                 ticket_to_confirm = TicketsNew.objects.filter(yatra_id=yatra, yatra_bus_id=yatra_bus_id_for_group, user_id=user_obj, ticket_status_id=1).order_by('ticket_id').first()
#                 if not ticket_to_confirm:
#                     response_data['message_text'] = f'Logic error: No reserved seat found for Yatra {yid} after group assignment.'
#                     raise Exception(response_data['message_text'])

#                 ticket_to_confirm.ticket_status_id = 2
#                 ticket_to_confirm.seat_fees = yatra.yatraFees
#                 ticket_to_confirm.discount = Discount
#                 ticket_to_confirm.discount_reason = DiscountReason
#                 ticket_to_confirm.amount_paid = AmountPaid
#                 ticket_to_confirm.payment_mode = PaymentMode
#                 ticket_to_confirm.payment_details = PaymentDetails
#                 # ✅ FIX: Assign the prepared payment object (which is either a Payments instance or None).
#                 ticket_to_confirm.payment_id = payment_obj
#                 ticket_to_confirm.registration_id = registration_obj
#                 ticket_to_confirm.permanant_id = registration_obj.registrationId
#                 ticket_to_confirm.save()

#                 booked_tickets_count += 1

#             # ... (counter logic remains the same)
#             BalanceTicket -= 1
#             CurrentTicket += 1
#             if BalanceTicket <= 0:
#                 CurrentTicket = 0
#                 GroupCount = 0

#             response_data = {
#                 'message_code': 1000,
#                 'message_text': f'{booked_tickets_count} ticket(s) booked.',
#                 'message_data': {"GroupCount": GroupCount, "CurrentTicket": CurrentTicket, "BalanceTicket": BalanceTicket}
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#     except Exception as e:
#         if not response_data.get('message_text') or response_data['message_text'] == 'Failure':
#              response_data['message_text'] = f'An unexpected error occurred: {e}'
#         return Response(response_data, status=status.HTTP_200_OK)



# @api_view(['POST'])
# def inserttickets(request):
#     """
#     Book tickets for one or multiple Yatras (comma-separated IDs), following PHP logic.
#     """
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Failure',
#         'message_data': []
#     }

#     try:
#         body = request.data
#         RegistrationId = body.get('RegistrationId')
#         UserId = body.get('UserId')
#         YatraIds = body.get('YatraIds')  # comma-separated
#         AmountPaid = body.get('AmountPaid', 0)
#         Discount = body.get('Discount', 0)
#         DiscountReason = body.get('DiscountReason', '')
#         PaymentId = body.get('PaymentId', '')
#         PaymentMode = body.get('PaymentMode', 1)
#         PaymentDetails = body.get('PaymentDetails', '')
#         GroupCount = int(body.get('GroupCount', 1))
#         CurrentTicket = int(body.get('CurrentTicket', 1))
#         BalanceTicket = int(body.get('BalanceTicket', GroupCount))

#         try:
#             user_obj = User.objects.get(id=UserId)
#         except User.DoesNotExist:
#             response_data['message_text'] = f"User with id {UserId} does not exist."
#             return Response(response_data, status=status.HTTP_200_OK)

#         if not RegistrationId:
#             response_data['message_text'] = 'Please provide Pilgrim to add ticket.'
#             return Response(response_data, status=status.HTTP_200_OK)
#         if not UserId:
#             response_data['message_text'] = 'Please provide user who is adding ticket.'
#             return Response(response_data, status=status.HTTP_200_OK)
#         if not YatraIds:
#             response_data['message_text'] = 'Please provide Yatras to add ticket.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         registration_obj = Registrations.objects.get(registrationId=RegistrationId)
#         user_obj = User.objects.get(id=UserId)

#         arrYatraIds = YatraIds.split(',')
#         booked_tickets = 0

#         with transaction.atomic():
#             for yid in arrYatraIds:
#                 yatra = Yatras.objects.get(yatraId=yid)
#                 yatra_route = yatra.yatraRouteId

#                 # Step 1: Get available ticket (TicketStatusId = 0)
#                 available_ticket = TicketsNew.objects.filter(
#                     ticket_status_id=0,
#                     yatra_id=yatra,
#                     yatra_route_id=yatra_route
#                 ).first()

#                 if not available_ticket:
#                     continue

#                 # Step 2: Assign to user temporarily (TicketStatusId = 1)
#                 available_ticket.ticket_status_id = 1
#                 available_ticket.user_id = user_obj
#                 available_ticket.save()

#                 # Step 3: Confirm ticket (TicketStatusId = 2) with payment details
#                 available_ticket.ticket_status_id = 2
#                 available_ticket.seat_fees = yatra.yatraFees
#                 available_ticket.discount = Discount
#                 available_ticket.discount_reason = DiscountReason
#                 available_ticket.amount_paid = AmountPaid
#                 available_ticket.payment_mode = PaymentMode
#                 available_ticket.payment_details = PaymentDetails
#                 available_ticket.payment_id = PaymentId
#                 available_ticket.registration_id = registration_obj
#                 available_ticket.permanant_id = registration_obj.registrationId
#                 available_ticket.save()

#                 booked_tickets += 1

#                 # Update balance counters
#                 BalanceTicket -= 1
#                 CurrentTicket += 1

#         # Reset counters if all tickets booked
#         if BalanceTicket <= 0:
#             CurrentTicket = 0
#             GroupCount = 0

#         response_data = {
#             'message_code': 1000,
#             'message_text': f'{booked_tickets} ticket(s) booked.',
#             'message_data': {
#                 "GroupCount": GroupCount,
#                 "CurrentTicket": CurrentTicket,
#                 "BalanceTicket": BalanceTicket
#             }
#         }

#     except Exception as e:
#         response_data['message_text'] = f'Unable to add tickets: {e}'

#     return Response(response_data, status=status.HTTP_200_OK)


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


# @api_view(['GET'])
# def totalrouteyatrabus(request):
#     """
#     Provides a report of total bookings grouped by Yatra Route, Yatra, and Bus for 2025,
#     replicating the PHP API response exactly.
#     """
#     try:
#         # Fetch tickets for 2025 with status booked
#         tickets = TicketsNew.objects.filter(
#             ticket_year=2025,
#             ticket_status_id=2
#         ).select_related('yatra_route_id', 'yatra_id', 'yatra_bus_id')

#         if not tickets.exists():
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'No bookings',
#                 'message_data': []
#             }, status=status.HTTP_200_OK)

#         # Aggregate by Route, Yatra, Bus
#         result_list = []
#         group_dict = {}
#         for t in tickets:
#             key = (t.yatra_route_id.yatraRouteId, t.yatra_id.yatraId, t.yatra_bus_id.yatraBusId)
#             if key not in group_dict:
#                 group_dict[key] = {
#                     'YatraRouteId': str(t.yatra_route_id.yatraRouteId),
#                     'YatraRouteName': t.yatra_route_id.yatraRoutename,
#                     'YatraId': str(t.yatra_id.yatraId),
#                     'YatraDateTime': t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if t.yatra_id.yatraDateTime else '',
#                     'YatraStartDateTime': t.yatra_id.yatraStartDateTime.strftime('%d-%m-%Y %H-%M') if t.yatra_id.yatraStartDateTime else '',
#                     'YatraFees': str(t.yatra_id.yatraFees),
#                     'YatraBusId': str(t.yatra_bus_id.yatraBusId),
#                     'BusName': t.yatra_bus_id.busName,
#                     'Bookings': 0,
#                     'YatraCount': 0,
#                     'RouteCount': 0
#                 }
#             group_dict[key]['Bookings'] += 1
#             group_dict[key]['YatraCount'] += 1
#             group_dict[key]['RouteCount'] += 1

#         result_list = list(group_dict.values())

#         return Response({
#             'message_code': 1000,
#             'message_text': 'Route, Yatra, Bus wise Booking counters',
#             'message_data': result_list
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({
#             'message_code': 999,
#             'message_text': f'Unable to fetch booking report: {e}',
#             'message_data': []
#         }, status=status.HTTP_200_OK)

@api_view(['GET'])
def totalrouteyatrabus(request):
    """
    Provides a report of total bookings grouped by Yatra Route, Yatra, and Bus for 2025.
    Replicates the PHP API fi_routeyatrabus_tickets but returns aggregated counts.
    """
    try:
        # Fetch and group tickets by Route, Yatra, and Bus
        tickets = TicketsNew.objects.filter(
            ticket_year=2025,
            ticket_status_id=2
        ).select_related(
            'yatra_route_id',
            'yatra_id',
            'yatra_bus_id'
        ).values(
            'yatra_route_id__yatraRouteId',
            'yatra_route_id__yatraRoutename',
            'yatra_id__yatraId',
            'yatra_id__yatraDateTime',
            'yatra_id__yatraStartDateTime',
            'yatra_id__yatraFees',
            'yatra_bus_id__yatraBusId',
            'yatra_bus_id__busName'
        ).annotate(
            bookings=Count('ticket_id')
        ).order_by(
            'yatra_route_id__yatraRouteId',
            'yatra_id__yatraId',
            'yatra_bus_id__yatraBusId'
        )

        if not tickets.exists():
            return Response({
                'message_code': 999,
                'message_text': 'No bookings',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # Format the response data
        result_list = []
        for t in tickets:
            ticket_data = {
                'YatraRouteId': str(t['yatra_route_id__yatraRouteId']) if t['yatra_route_id__yatraRouteId'] else '',
                'YatraRouteName': t['yatra_route_id__yatraRoutename'] if t['yatra_route_id__yatraRoutename'] else '',
                'YatraId': str(t['yatra_id__yatraId']) if t['yatra_id__yatraId'] else '',
                'YatraDateTime': t['yatra_id__yatraDateTime'].strftime('%d-%m-%Y') if t['yatra_id__yatraDateTime'] else '',
                'YatraStartDateTime': t['yatra_id__yatraStartDateTime'].strftime('%d-%m-%Y %H-%M') if t['yatra_id__yatraStartDateTime'] else '',
                'YatraFees': str(t['yatra_id__yatraFees']) if t['yatra_id__yatraFees'] else '0.00',
                'YatraBusId': str(t['yatra_bus_id__yatraBusId']) if t['yatra_bus_id__yatraBusId'] else '',
                'BusName': t['yatra_bus_id__busName'] if t['yatra_bus_id__busName'] else '',
                'Bookings': str(t['bookings']),
                'YatraCount': str(t['bookings']),
                'RouteCount': str(t['bookings'])
            }
            result_list.append(ticket_data)

        return Response({
            'message_code': 1000,
            'message_text': 'Route, Yatra, Bus wise Booking counters',
            'message_data': result_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unable to fetch booking report: {str(e)}',
            'message_data': []
        }, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def routeyatrabustickets(request):
#     """
#     Lists all booked tickets for a specific Yatra Route, Yatra, and Bus for 2025,
#     replicating the PHP API response exactly.
#     """
#     try:
#         body = request.data
#         YatraRouteId = body.get('YatraRouteId')
#         YatraId = body.get('YatraId')
#         YatraBusId = body.get('YatraBusId')

#         # --- Validation ---
#         if not YatraRouteId:
#             return Response({'message_code': 999, 'message_text': 'Please provide yatra route for tickets.', 'message_data': []}, status=status.HTTP_200_OK)
#         if not YatraId:
#             return Response({'message_code': 999, 'message_text': 'Please provide Yatra for ticket.', 'message_data': []}, status=status.HTTP_200_OK)
#         if not YatraBusId:
#             return Response({'message_code': 999, 'message_text': 'Please provide yatra bus for tickets.', 'message_data': []}, status=status.HTTP_200_OK)

#         # --- Query Tickets ---
#         tickets = TicketsNew.objects.filter(
#             yatra_route_id=YatraRouteId,
#             yatra_id=YatraId,
#             yatra_bus_id=YatraBusId,
#             ticket_year=2025,
#             ticket_status_id=2
#         ).select_related(
#             'yatra_route_id', 'yatra_id', 'yatra_bus_id', 'registration_id'
#         ).order_by('seat_no')

#         result_list = []
#         for t in tickets:
#             result_list.append({
#                 'YatraRouteId': str(t.yatra_route_id.yatraRouteId),
#                 'YatraId': str(t.yatra_id.yatraId),
#                 'YatraDateTime': t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if t.yatra_id.yatraDateTime else '',
#                 'YatraStartDateTime': t.yatra_id.yatraStartDateTime.strftime('%d-%m-%Y %H-%M') if t.yatra_id.yatraStartDateTime else '',
#                 'YatraFees': str(t.yatra_id.yatraFees),
#                 'YatraBusId': str(t.yatra_bus_id.yatraBusId),
#                 'BusName': t.yatra_bus_id.busName,
#                 'SeatNo': str(t.seat_no),
#                 'RegistrationId': str(t.registration_id.registrationId),
#                 'DiscountReason': t.discount_reason or '',
#                 'Firstname': t.registration_id.firstname,
#                 'Middlename': t.registration_id.middlename,
#                 'Lastname': t.registration_id.lastname or '',
#                 'MobileNo': t.registration_id.mobileNo,
#                 'AlternateMobileNo': t.registration_id.alternateMobileNo,
#                 'BloodGroup': t.registration_id.bloodGroup.bloodGroupName if t.registration_id.bloodGroup else '',
#                 'Gender': str(t.registration_id.gender),
#                 'PhotoFileName': t.registration_id.photoFileName or '',
#                 'IdProofFileName': t.registration_id.idProofFileName or '',
#                 'VoterIdProof': t.registration_id.voterIdProof or ''
#             })

#         if not result_list:
#             return Response({'message_code': 999, 'message_text': 'No Tickets', 'message_data': []}, status=status.HTTP_200_OK)

#         return Response({'message_code': 1000, 'message_text': 'Route, Yatra, Bus wise Tickets', 'message_data': result_list}, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({'message_code': 999, 'message_text': f'Unable to fetch tickets: {e}', 'message_data': []}, status=status.HTTP_200_OK)

@api_view(['POST'])
def routeyatrabustickets(request):
    """
    Fetches ticket details for a specific Yatra Route, Yatra, and Bus combination.
    Provides complete passenger and booking information.
    """
    try:
        # Extract request parameters
        yatra_route_id = request.data.get('YatraRouteId', 0)
        yatra_id = request.data.get('YatraId', 0)
        yatra_bus_id = request.data.get('YatraBusId', 0)

        # Validate required parameters
        if not yatra_route_id or yatra_route_id == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide yatra route for tickets.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        if not yatra_id or yatra_id == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide Yatra for ticket.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        if not yatra_bus_id or yatra_bus_id == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide yatra bus for tickets.',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # Fetch tickets with all related data
        tickets = TicketsNew.objects.filter(
            ticket_year=2025,
            ticket_status_id=2,
            yatra_route_id=yatra_route_id,
            yatra_id=yatra_id,
            yatra_bus_id=yatra_bus_id
        ).select_related(
            'yatra_route_id',
            'yatra_id',
            'yatra_bus_id',
            'yatra_bus_id__busName',  # YatraBuses has a busName FK to BusNames
            'registration_id',
            'registration_id__bloodGroup'
        )

        if not tickets.exists():
            return Response({
                'message_code': 999,
                'message_text': 'No Tickets',
                'message_data': []
            }, status=status.HTTP_200_OK)

        # Build response data
        result_list = []
        for t in tickets:
            ticket_data = {
                'YatraRouteId': str(t.yatra_route_id.yatraRouteId) if t.yatra_route_id else '',
                'YatraId': str(t.yatra_id.yatraId) if t.yatra_id else '',
                'YatraDateTime': t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if t.yatra_id and t.yatra_id.yatraDateTime else '',
                'YatraStartDateTime': t.yatra_id.yatraStartDateTime.strftime('%d-%m-%Y %H-%M') if t.yatra_id and t.yatra_id.yatraStartDateTime else '',
                'YatraFees': str(t.yatra_id.yatraFees) if t.yatra_id and t.yatra_id.yatraFees else '0.00',
                'YatraBusId': str(t.yatra_bus_id.yatraBusId) if t.yatra_bus_id else '',
                'BusName': t.yatra_bus_id.busName.busName if t.yatra_bus_id and t.yatra_bus_id.busName else '',
                'SeatNo': str(t.seat_no) if t.seat_no else '',
                'RegistrationId': str(t.registration_id.registrationId) if t.registration_id else '',
                'DiscountReason': t.discount_reason if t.discount_reason else '',
                'Firstname': t.registration_id.firstname if t.registration_id and t.registration_id.firstname else '',
                'Middlename': t.registration_id.middlename if t.registration_id and t.registration_id.middlename else '',
                'Lastname': t.registration_id.lastname if t.registration_id and t.registration_id.lastname else '',
                'MobileNo': t.registration_id.mobileNo if t.registration_id and t.registration_id.mobileNo else '',
                'AlternateMobileNo': t.registration_id.alternateMobileNo if t.registration_id and t.registration_id.alternateMobileNo else '',
                'BloodGroup': t.registration_id.bloodGroup.bloodGroupName if t.registration_id and t.registration_id.bloodGroup else '',
                'Gender': str(t.registration_id.gender) if t.registration_id and t.registration_id.gender else '',
                'PhotoFileName': t.registration_id.photoFileName if t.registration_id and t.registration_id.photoFileName else '',
                'IdProofFileName': t.registration_id.idProofFileName if t.registration_id and t.registration_id.idProofFileName else '',
                'VoterIdProof': t.registration_id.voterIdProof if t.registration_id and t.registration_id.voterIdProof else '',
            }
            result_list.append(ticket_data)

        return Response({
            'message_code': 1000,
            'message_text': 'Route, Yatra, Bus wise Tickets',
            'message_data': result_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unable to fetch tickets: {str(e)}',
            'message_data': []
        }, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def agentbookings(request):
    """
    Lists all tickets booked by a specific agent on a given date (2025),
    replicating the PHP API exactly.
    """
    try:
        from datetime import datetime

        body = request.data
        
        # Extract and validate UserId
        UserId = body.get('UserId', 0)
        if UserId == "" or UserId is None:
            UserId = 0
        else:
            try:
                UserId = int(UserId)
            except (ValueError, TypeError):
                UserId = 0
        
        # Extract BookingDate with default
        BookingDate = body.get('BookingDate', '')
        if not BookingDate or BookingDate == "":
            BookingDate = datetime.today().strftime('%d/%m/%Y')

        # Validation: UserId is required
        if UserId == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Please provide agent for tickets.'
            }, status=status.HTTP_200_OK)

        # Double-check BookingDate (replicate PHP's second check)
        if BookingDate == "":
            BookingDate = datetime.today().strftime('%d/%m/%Y')

        # Parse BookingDate safely
        try:
            target_date = datetime.strptime(BookingDate, '%d/%m/%Y')
        except ValueError:
            # If parsing fails, use today's date
            BookingDate = datetime.today().strftime('%d/%m/%Y')
            target_date = datetime.today()

        # Filter tickets matching PHP query conditions
        tickets = TicketsNew.objects.filter(
            ticket_year=2025,
            ticket_status_id=2,
            user_id=UserId,
            booking_date__day=target_date.day,
            booking_date__month=target_date.month,
            booking_date__year=target_date.year
        ).select_related(
            'yatra_route_id',
            'yatra_id',
            'yatra_bus_id',
            'yatra_bus_id__busName',  # Added to get BusNames data
            'registration_id',
            'registration_id__bloodGroup'
        ).order_by('yatra_route_id', 'yatra_id', 'yatra_bus_id')

        result_list = []
        for t in tickets:
            # Handle None values safely for all fields
            yatra_route_id = t.yatra_route_id.yatraRouteId if t.yatra_route_id else None
            yatra_route_name = t.yatra_route_id.yatraRoutename if t.yatra_route_id else ''
            
            yatra_id = t.yatra_id.yatraId if t.yatra_id else None
            yatra_date_time = t.yatra_id.yatraDateTime.strftime('%d-%m-%Y') if (t.yatra_id and t.yatra_id.yatraDateTime) else ''
            yatra_fees = float(t.yatra_id.yatraFees) if (t.yatra_id and t.yatra_id.yatraFees) else 0.00
            
            # YatraBuses - busName is now FK to BusNames
            yatra_bus_id = t.yatra_bus_id.yatraBusId if t.yatra_bus_id else None
            bus_name = ''
            if t.yatra_bus_id and t.yatra_bus_id.busName:
                bus_name = t.yatra_bus_id.busName.busName
            
            # Registration details
            firstname = t.registration_id.firstname if t.registration_id else ''
            middlename = t.registration_id.middlename if t.registration_id else ''
            lastname = t.registration_id.lastname if t.registration_id else ''
            mobile_no = t.registration_id.mobileNo if t.registration_id else ''
            alternate_mobile = t.registration_id.alternateMobileNo if t.registration_id else ''
            
            # BloodGroup handling
            blood_group = ''
            if t.registration_id and t.registration_id.bloodGroup:
                # Assuming BloodGroup model has bloodGroupName field
                blood_group = getattr(t.registration_id.bloodGroup, 'bloodGroupName', '') or \
                             getattr(t.registration_id.bloodGroup, 'name', '') or ''
            
            gender = t.registration_id.gender if t.registration_id else None
            photo_filename = t.registration_id.photoFileName if t.registration_id else ''

            result_list.append({
                'YatraRouteId': yatra_route_id,
                'YatraRouteName': yatra_route_name,
                'YatraId': yatra_id,
                'YatraDateTime': yatra_date_time,
                'PaymentMode': t.payment_mode,
                'YatraFees': yatra_fees,
                'YatraBusId': yatra_bus_id,
                'BusName': bus_name,
                'Firstname': firstname,
                'Middlename': middlename,
                'Lastname': lastname,
                'MobileNo': mobile_no,
                'AlternateMobileNo': alternate_mobile,
                'BloodGroup': blood_group,
                'Gender': gender,
                'PhotoFileName': photo_filename
            })

        # Return appropriate response
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
            'message_text': f'Unable to fetch tickets: {str(e)}',
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
                'BusName': b.busName.busName if b.busName else None,  # ✅ FIXED LINE
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
def listyatrabuses(request):
    """
    Lists all Yatra buses with active Yatra status.
    Exact replica of PHP fi_list_yatra_buses API.
    """
    try:
        # PHP query filters: YatraStatus = 1 (Active)
        # Joins: Yatras → YatraRoutes → YatraBuses
        yatras_buses = YatraBuses.objects.filter(
            yatraId__yatraStatus=1,  # YatraStatus = 1 (assuming 1 = Active)
            is_deleted=False
        ).select_related(
            'yatraId',
            'yatraId__yatraRouteId',
            'yatraRouteId',
            'busName'  # FK to BusNames
        ).order_by('yatraId', 'yatraBusId')

        if not yatras_buses.exists():
            return Response({
                'message_code': 999,
                'message_text': 'No Yatra Bus.'
            }, status=status.HTTP_200_OK)

        yatras_buses_list = []
        for yb in yatras_buses:
            y = yb.yatraId  # Yatras object
            route = y.yatraRouteId if y else None  # YatraRoutes object
            
            # Handle YatraStatus - PHP returns integer 1, not status name
            yatra_status = None
            if y and y.yatraStatus:
                # If yatraStatus is FK to YatraStatus model
                if hasattr(y.yatraStatus, 'pk'):
                    yatra_status = y.yatraStatus.pk
                else:
                    yatra_status = y.yatraStatus
            
            # BusName - get actual name from BusNames FK
            bus_name = ''
            if yb.busName:
                bus_name = yb.busName.busName
            
            yatras_buses_list.append({
                'YatraId': y.yatraId if y else None,
                'YatraDateTime': y.yatraDateTime.strftime('%d-%m-%Y %H:%M') if (y and y.yatraDateTime) else None,
                'YatraRouteId': route.yatraRouteId if route else None,
                'YatraStatus': yatra_status,  # Return integer, not status name
                'YatraRouteName': route.yatraRoutename if route else None,
                'YatraRouteDetails': route.yatraDetails if route else None,
                'YatraBusId': yb.yatraBusId,
                'BusName': bus_name,  # Get from BusNames FK
                'BusDateTimeStart': yb.busDateTimeStart.strftime('%d-%m-%Y %H:%M') if yb.busDateTimeStart else None,
                'SeatFees': float(yb.seatFees) if yb.seatFees else 0.0,
                'BusCapacity': yb.busCapacity
            })

        return Response({
            'message_code': 1000,
            'message_text': 'Success',
            'message_data': yatras_buses_list
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'An error occurred while fetching Yatra buses: {str(e)}'
        }, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def createyatrabus(request):
#     """
#     Creates a new Yatra Bus and optionally reserves seats for 'Swayamsevak'.
#     Exact replica of PHP fi_create_yatra_bus API.
#     """
#     try:
#         from datetime import datetime
#         from django.db import transaction
        
#         body = request.data
        
#         # Extract parameters with proper validation (matching PHP logic)
#         BusName = body.get('BusName', '').strip() if body.get('BusName') else ''
#         BusDateTimeStart = body.get('BusDateTimeStart', '').strip() if body.get('BusDateTimeStart') else ''
#         SeatFees = body.get('SeatFees', '')
#         YatraRouteId = body.get('YatraRouteId', '')
#         YatraId = body.get('YatraId', '')
#         BusCapacity = body.get('BusCapacity', '')
#         ReservedSeats = body.get('ReservedSeats', '1,2')
#         UserId = body.get('UserId', 1)
        
#         # Convert to string for empty check (PHP treats numbers as strings in comparisons)
#         SeatFees_str = str(SeatFees).strip() if SeatFees not in [None, ''] else ''
#         YatraRouteId_str = str(YatraRouteId).strip() if YatraRouteId not in [None, ''] else ''
#         YatraId_str = str(YatraId).strip() if YatraId not in [None, ''] else ''
#         BusCapacity_str = str(BusCapacity).strip() if BusCapacity not in [None, ''] else ''
#         ReservedSeats_str = str(ReservedSeats).strip() if ReservedSeats not in [None, ''] else '1,2'
        
#         # Convert UserId to int with default 1
#         try:
#             UserId = int(UserId) if UserId else 1
#         except (ValueError, TypeError):
#             UserId = 1

#         # Validation in exact PHP order
#         if BusDateTimeStart == "":
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'Yatra date and time must be specified to add new yatra.{body.get("BusDateTimeStart", "")}'
#             }, status=status.HTTP_200_OK)
#         elif YatraRouteId_str == "":
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'Yatra route must be specified to add new yatra.'
#             }, status=status.HTTP_200_OK)
#         elif SeatFees_str == "":
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'Yatra seat fee must be specified to add new yatra.'
#             }, status=status.HTTP_200_OK)
#         elif BusName == "":
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'Yatra bus name  must be specified to add new yatra.'
#             }, status=status.HTTP_200_OK)

#         # Parse datetime: format is "DD-MM-YYYY HH:MM"
#         try:
#             arrDateTime = BusDateTimeStart.split(" ")
#             YatraDate = arrDateTime[0]  # DD-MM-YYYY
#             YatraTime = arrDateTime[1] if len(arrDateTime) > 1 else "00:00"
            
#             # Parse to datetime object
#             start_datetime = datetime.strptime(f"{YatraDate} {YatraTime}", '%d-%m-%Y %H:%M')
#         except (ValueError, IndexError) as e:
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'Invalid date format for BusDateTimeStart. Please use DD-MM-YYYY HH:MM. Error: {str(e)}'
#             }, status=status.HTTP_200_OK)

#         # Convert YatraId to int and validate
#         try:
#             YatraId_int = int(YatraId)
#         except (ValueError, TypeError):
#             YatraId_int = 0

#         if YatraId_int == 0:
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'Unable to add/locate yatra on this date.'
#             }, status=status.HTTP_200_OK)

#         # Convert YatraRouteId to int
#         try:
#             YatraRouteId_int = int(YatraRouteId)
#         except (ValueError, TypeError):
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'Invalid YatraRouteId.'
#             }, status=status.HTTP_200_OK)

#         # Check if bus with same name exists on same date for same route and yatra
#         existing_bus = YatraBuses.objects.filter(
#             busName__busName__iexact=BusName,  # Case-insensitive comparison via BusNames FK
#             busDateTimeStart__date=start_datetime.date(),
#             yatraRouteId=YatraRouteId_int,
#             yatraId=YatraId_int
#         ).exists()

#         if existing_bus:
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'Bus Name already exists. Please choose another name.'
#             }, status=status.HTTP_200_OK)

#         # Get related objects
#         try:
#             yatra = Yatras.objects.get(yatraId=YatraId_int)
#         except Yatras.DoesNotExist:
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'Yatra with ID {YatraId_int} not found.'
#             }, status=status.HTTP_200_OK)
        
#         try:
#             route = YatraRoutes.objects.get(yatraRouteId=YatraRouteId_int)
#         except YatraRoutes.DoesNotExist:
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'YatraRoute with ID {YatraRouteId_int} not found.'
#             }, status=status.HTTP_200_OK)
        
#         try:
#             user = User.objects.get(id=UserId)
#         except User.DoesNotExist:
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'User with ID {UserId} not found.'
#             }, status=status.HTTP_200_OK)
        
#         # Get or create BusNames object
#         try:
#             bus_name_obj, created = BusNames.objects.get_or_create(
#                 busName__iexact=BusName,
#                 defaults={'busName': BusName, 'created_by': user}
#             )
#         except Exception as e:
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'Error creating/finding bus name: {str(e)}'
#             }, status=status.HTTP_200_OK)

#         # Create YatraBus with transaction
#         try:
#             with transaction.atomic():
#                 # Convert BusCapacity to int or None
#                 bus_capacity_value = None
#                 if BusCapacity_str != "":
#                     try:
#                         bus_capacity_value = int(BusCapacity)
#                     except (ValueError, TypeError):
#                         bus_capacity_value = None
                
#                 new_bus = YatraBuses.objects.create(
#                     busName=bus_name_obj,  # FK to BusNames
#                     busDateTimeStart=start_datetime,
#                     seatFees=SeatFees,
#                     yatraRouteId=route,
#                     yatraId=yatra,
#                     busStatus=1,
#                     busCapacity=bus_capacity_value,
#                     created_by=user
#                 )

#                 # Reserve seats if specified
#                 if ReservedSeats_str != "":
#                     seat_list = ReservedSeats_str.split(",")
                    
#                     for seat_no_str in seat_list:
#                         seat_no_str = seat_no_str.strip()
#                         if seat_no_str.isdigit():
#                             try:
#                                 TicketsNew.objects.create(
#                                     ticket_year=start_datetime.year,
#                                     yatra_id=yatra,
#                                     yatra_route_id=route,
#                                     yatra_bus_id=new_bus,
#                                     seat_no=int(seat_no_str),
#                                     seat_fees=SeatFees,
#                                     seat_ticket_type=1,
#                                     discount=SeatFees,
#                                     discount_reason='Swayamsevak',
#                                     amount_paid=SeatFees,
#                                     payment_mode=1,
#                                     payment_id=None,
#                                     ticket_status_id=1,
#                                     registration_id=None,
#                                     permanant_id=0,
#                                     user_id=user,
#                                     booking_date=start_datetime.date(),
#                                     created_by=user
#                                 )
#                             except Exception as ticket_error:
#                                 # Log but don't fail the entire transaction
#                                 print(f"Error creating ticket for seat {seat_no_str}: {str(ticket_error)}")

#             return Response({
#                 'message_code': 1000,
#                 'message_text': 'Yatra bus added successfully.'
#             }, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response({
#                 'message_code': 999,
#                 'message_text': f'Unable to add yatra bus. Error: {str(e)}'
#             }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({
#             'message_code': 999,
#             'message_text': f'Unexpected error: {str(e)}'
#         }, status=status.HTTP_200_OK)


@api_view(['POST'])
def createyatrabus(request):
    """
    Creates a new Yatra Bus and creates all seats up to BusCapacity.
    Reserved seats (specified in ReservedSeats) are created with status 2,
    remaining seats are created with status 0.
    """
    try:
        from datetime import datetime
        from django.db import transaction
        
        body = request.data
        
        # Extract parameters with proper validation (matching PHP logic)
        BusName = body.get('BusName', '').strip() if body.get('BusName') else ''
        BusDateTimeStart = body.get('BusDateTimeStart', '').strip() if body.get('BusDateTimeStart') else ''
        SeatFees = body.get('SeatFees', '')
        YatraRouteId = body.get('YatraRouteId', '')
        YatraId = body.get('YatraId', '')
        BusCapacity = body.get('BusCapacity', '')
        ReservedSeats = body.get('ReservedSeats', '1,2')
        UserId = body.get('UserId', 1)
        
        # Convert to string for empty check (PHP treats numbers as strings in comparisons)
        SeatFees_str = str(SeatFees).strip() if SeatFees not in [None, ''] else ''
        YatraRouteId_str = str(YatraRouteId).strip() if YatraRouteId not in [None, ''] else ''
        YatraId_str = str(YatraId).strip() if YatraId not in [None, ''] else ''
        BusCapacity_str = str(BusCapacity).strip() if BusCapacity not in [None, ''] else ''
        ReservedSeats_str = str(ReservedSeats).strip() if ReservedSeats not in [None, ''] else '1,2'
        
        # Convert UserId to int with default 1
        try:
            UserId = int(UserId) if UserId else 1
        except (ValueError, TypeError):
            UserId = 1

        # Validation in exact PHP order
        if BusDateTimeStart == "":
            return Response({
                'message_code': 999,
                'message_text': f'Yatra date and time must be specified to add new yatra.{body.get("BusDateTimeStart", "")}'
            }, status=status.HTTP_200_OK)
        elif YatraRouteId_str == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra route must be specified to add new yatra.'
            }, status=status.HTTP_200_OK)
        elif SeatFees_str == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra seat fee must be specified to add new yatra.'
            }, status=status.HTTP_200_OK)
        elif BusName == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra bus name  must be specified to add new yatra.'
            }, status=status.HTTP_200_OK)

        # Parse datetime: format is "DD-MM-YYYY HH:MM"
        try:
            arrDateTime = BusDateTimeStart.split(" ")
            YatraDate = arrDateTime[0]  # DD-MM-YYYY
            YatraTime = arrDateTime[1] if len(arrDateTime) > 1 else "00:00"
            
            # Parse to datetime object
            start_datetime = datetime.strptime(f"{YatraDate} {YatraTime}", '%d-%m-%Y %H:%M')
        except (ValueError, IndexError) as e:
            return Response({
                'message_code': 999,
                'message_text': f'Invalid date format for BusDateTimeStart. Please use DD-MM-YYYY HH:MM. Error: {str(e)}'
            }, status=status.HTTP_200_OK)

        # Convert YatraId to int and validate
        try:
            YatraId_int = int(YatraId)
        except (ValueError, TypeError):
            YatraId_int = 0

        if YatraId_int == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Unable to add/locate yatra on this date.'
            }, status=status.HTTP_200_OK)

        # Convert YatraRouteId to int
        try:
            YatraRouteId_int = int(YatraRouteId)
        except (ValueError, TypeError):
            return Response({
                'message_code': 999,
                'message_text': 'Invalid YatraRouteId.'
            }, status=status.HTTP_200_OK)

        # Check if bus with same name exists on same date for same route and yatra
        existing_bus = YatraBuses.objects.filter(
            busName__busName__iexact=BusName,  # Case-insensitive comparison via BusNames FK
            busDateTimeStart__date=start_datetime.date(),
            yatraRouteId=YatraRouteId_int,
            yatraId=YatraId_int
        ).exists()

        if existing_bus:
            return Response({
                'message_code': 999,
                'message_text': 'Bus Name already exists. Please choose another name.'
            }, status=status.HTTP_200_OK)

        # Get related objects
        try:
            yatra = Yatras.objects.get(yatraId=YatraId_int)
        except Yatras.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': f'Yatra with ID {YatraId_int} not found.'
            }, status=status.HTTP_200_OK)
        
        try:
            route = YatraRoutes.objects.get(yatraRouteId=YatraRouteId_int)
        except YatraRoutes.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': f'YatraRoute with ID {YatraRouteId_int} not found.'
            }, status=status.HTTP_200_OK)
        
        try:
            user = User.objects.get(id=UserId)
        except User.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': f'User with ID {UserId} not found.'
            }, status=status.HTTP_200_OK)
        
        # Get or create BusNames object
        try:
            bus_name_obj, created = BusNames.objects.get_or_create(
                busName__iexact=BusName,
                defaults={'busName': BusName, 'created_by': user}
            )
        except Exception as e:
            return Response({
                'message_code': 999,
                'message_text': f'Error creating/finding bus name: {str(e)}'
            }, status=status.HTTP_200_OK)

        # Create YatraBus with transaction
        try:
            with transaction.atomic():
                # Convert BusCapacity to int or None
                bus_capacity_value = None
                if BusCapacity_str != "":
                    try:
                        bus_capacity_value = int(BusCapacity)
                    except (ValueError, TypeError):
                        bus_capacity_value = None
                
                new_bus = YatraBuses.objects.create(
                    busName=bus_name_obj,  # FK to BusNames
                    busDateTimeStart=start_datetime,
                    seatFees=SeatFees,
                    yatraRouteId=route,
                    yatraId=yatra,
                    busStatus=1,
                    busCapacity=bus_capacity_value,
                    created_by=user
                )

                # Parse reserved seats into a set for quick lookup
                reserved_seat_numbers = set()
                if ReservedSeats_str != "":
                    seat_list = ReservedSeats_str.split(",")
                    for seat_no_str in seat_list:
                        seat_no_str = seat_no_str.strip()
                        if seat_no_str.isdigit():
                            reserved_seat_numbers.add(int(seat_no_str))

                # Create all seats up to BusCapacity
                if bus_capacity_value is not None and bus_capacity_value > 0:
                    for seat_number in range(1, bus_capacity_value + 1):
                        try:
                            # Check if this seat is reserved
                            is_reserved = seat_number in reserved_seat_numbers
                            
                            TicketsNew.objects.create(
                                ticket_year=start_datetime.year,
                                yatra_id=yatra,
                                yatra_route_id=route,
                                yatra_bus_id=new_bus,
                                seat_no=seat_number,
                                seat_fees=SeatFees,
                                seat_ticket_type=1,
                                discount=SeatFees if is_reserved else 0,
                                discount_reason='Swayamsevak' if is_reserved else '',
                                amount_paid=SeatFees if is_reserved else 0,
                                payment_mode=1 if is_reserved else 0,
                                payment_id=None,
                                ticket_status_id=2 if is_reserved else 0,  # 2=Reserved, 0=Available
                                registration_id=None,
                                permanant_id=0,
                                user_id=user if is_reserved else None,
                                booking_date=start_datetime.date(),
                                created_by=user
                            )
                        except Exception as ticket_error:
                            # Log the error with more details
                            import traceback
                            print(f"Error creating ticket for seat {seat_number}: {str(ticket_error)}")
                            print(traceback.format_exc())
                            raise  # Re-raise to see the actual error

            return Response({
                'message_code': 1000,
                'message_text': 'Yatra bus added successfully.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message_code': 999,
                'message_text': f'Unable to add yatra bus. Error: {str(e)}'
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def modifyyatrabus(request):
    """
    Modifies an existing Yatra Bus and updates seats.
    Reserved seats are marked within the bus capacity with status 2.
    """
    try:
        from datetime import datetime
        from django.db import transaction
        
        body = request.data
        
        # Extract parameters with proper validation (matching PHP logic)
        YatraBusId = body.get('YatraBusId', '')
        BusName = body.get('BusName', '').strip() if body.get('BusName') else ''
        BusDateTimeStart = body.get('BusDateTimeStart', '').strip() if body.get('BusDateTimeStart') else ''
        SeatFees = body.get('SeatFees', '')
        YatraRouteId = body.get('YatraRouteId', '')
        YatraId = body.get('YatraId', '')
        BusStatus = body.get('BusStatus', '')
        BusCapacity = body.get('BusCapacity', '')
        ReservedSeats = body.get('ReservedSeats', '1,2')
        UserId = body.get('UserId', 1)
        
        # Convert to string for empty check (PHP treats numbers as strings in comparisons)
        YatraBusId_str = str(YatraBusId).strip() if YatraBusId not in [None, ''] else ''
        SeatFees_str = str(SeatFees).strip() if SeatFees not in [None, ''] else ''
        YatraRouteId_str = str(YatraRouteId).strip() if YatraRouteId not in [None, ''] else ''
        YatraId_str = str(YatraId).strip() if YatraId not in [None, ''] else ''
        BusCapacity_str = str(BusCapacity).strip() if BusCapacity not in [None, ''] else ''
        ReservedSeats_str = str(ReservedSeats).strip() if ReservedSeats not in [None, ''] else '1,2'
        
        # Convert UserId to int with default 1
        try:
            UserId = int(UserId) if UserId else 1
        except (ValueError, TypeError):
            UserId = 1

        # Convert YatraBusId to int
        try:
            YatraBusId_int = int(YatraBusId) if YatraBusId_str != '' else 0
        except (ValueError, TypeError):
            YatraBusId_int = 0

        # Validation in exact PHP order
        if YatraBusId_int == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Yatra Id  must be specified to modify yatra.'
            }, status=status.HTTP_200_OK)
        elif BusDateTimeStart == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra date and time must be specified to modify yatra.'
            }, status=status.HTTP_200_OK)
        elif YatraRouteId_str == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra route must be specified to modify yatra.'
            }, status=status.HTTP_200_OK)
        elif SeatFees_str == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra seat fee must be specified to modify yatra.'
            }, status=status.HTTP_200_OK)
        elif BusName == "":
            return Response({
                'message_code': 999,
                'message_text': 'Yatra bus name  must be specified to modify yatra.'
            }, status=status.HTTP_200_OK)

        # Parse datetime: format is "DD-MM-YYYY HH:MM"
        try:
            arrDateTime = BusDateTimeStart.split(" ")
            YatraDate = arrDateTime[0]  # DD-MM-YYYY
            YatraTime = arrDateTime[1] if len(arrDateTime) > 1 else "00:00"
            
            # Parse to datetime object
            start_datetime = datetime.strptime(f"{YatraDate} {YatraTime}", '%d-%m-%Y %H:%M')
        except (ValueError, IndexError) as e:
            return Response({
                'message_code': 999,
                'message_text': f'Invalid date format for BusDateTimeStart. Please use DD-MM-YYYY HH:MM. Error: {str(e)}'
            }, status=status.HTTP_200_OK)

        # Check if YatraBus exists
        if not YatraBuses.objects.filter(yatraBusId=YatraBusId_int).exists():
            return Response({
                'message_code': 999,
                'message_text': 'This yatra bus does not exist.'
            }, status=status.HTTP_200_OK)

        # Convert YatraId to int and validate
        try:
            YatraId_int = int(YatraId)
        except (ValueError, TypeError):
            YatraId_int = 0

        if YatraId_int == 0:
            return Response({
                'message_code': 999,
                'message_text': 'Unable to add/locate yatra on this date.'
            }, status=status.HTTP_200_OK)

        # Convert YatraRouteId to int
        try:
            YatraRouteId_int = int(YatraRouteId)
        except (ValueError, TypeError):
            return Response({
                'message_code': 999,
                'message_text': 'Invalid YatraRouteId.'
            }, status=status.HTTP_200_OK)

        # Check if bus with same name exists on same date (excluding current bus)
        existing_bus = YatraBuses.objects.filter(
            busName__busName__iexact=BusName,  # Case-insensitive comparison via BusNames FK
            busDateTimeStart__date=start_datetime.date(),
            yatraId=YatraId_int
        ).exclude(yatraBusId=YatraBusId_int).exists()

        if existing_bus:
            return Response({
                'message_code': 999,
                'message_text': 'Bus Name already exists. Please choose another name.'
            }, status=status.HTTP_200_OK)

        # Get related objects
        try:
            yatra = Yatras.objects.get(yatraId=YatraId_int)
        except Yatras.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': f'Yatra with ID {YatraId_int} not found.'
            }, status=status.HTTP_200_OK)
        
        try:
            route = YatraRoutes.objects.get(yatraRouteId=YatraRouteId_int)
        except YatraRoutes.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': f'YatraRoute with ID {YatraRouteId_int} not found.'
            }, status=status.HTTP_200_OK)
        
        try:
            user = User.objects.get(id=UserId)
        except User.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': f'User with ID {UserId} not found.'
            }, status=status.HTTP_200_OK)
        
        # Get or create BusNames object
        try:
            bus_name_obj, created = BusNames.objects.get_or_create(
                busName__iexact=BusName,
                defaults={'busName': BusName, 'created_by': user}
            )
        except Exception as e:
            return Response({
                'message_code': 999,
                'message_text': f'Error creating/finding bus name: {str(e)}'
            }, status=status.HTTP_200_OK)

        # Update YatraBus with transaction
        try:
            with transaction.atomic():
                # Get the existing bus
                existing_yatra_bus = YatraBuses.objects.get(yatraBusId=YatraBusId_int)
                
                # Store old capacity for comparison
                old_capacity = existing_yatra_bus.busCapacity
                
                # Convert BusCapacity to int or None
                bus_capacity_value = None
                if BusCapacity_str != "":
                    try:
                        bus_capacity_value = int(BusCapacity)
                    except (ValueError, TypeError):
                        bus_capacity_value = None
                
                # Update the bus
                existing_yatra_bus.busName = bus_name_obj
                existing_yatra_bus.busDateTimeStart = start_datetime
                existing_yatra_bus.seatFees = SeatFees
                existing_yatra_bus.yatraRouteId = route
                existing_yatra_bus.yatraId = yatra
                existing_yatra_bus.busCapacity = bus_capacity_value
                existing_yatra_bus.last_modified_by = user
                existing_yatra_bus.save()

                # Parse reserved seats into a set for quick lookup
                reserved_seat_numbers = set()
                if ReservedSeats_str != "":
                    seat_list = ReservedSeats_str.split(",")
                    for seat_no_str in seat_list:
                        seat_no_str = seat_no_str.strip()
                        if seat_no_str.isdigit():
                            reserved_seat_numbers.add(int(seat_no_str))

                # Get all existing tickets for this bus
                existing_tickets = TicketsNew.objects.filter(
                    yatra_id=yatra,
                    yatra_route_id=route,
                    yatra_bus_id=existing_yatra_bus
                )

                # If capacity changed, handle seat addition/removal
                if bus_capacity_value != old_capacity:
                    if bus_capacity_value is not None:
                        # Get existing seat numbers
                        existing_seat_numbers = set(existing_tickets.values_list('seat_no', flat=True))
                        
                        # If capacity increased, add new seats
                        if old_capacity is None or bus_capacity_value > old_capacity:
                            start_seat = (old_capacity + 1) if old_capacity else 1
                            for seat_number in range(start_seat, bus_capacity_value + 1):
                                if seat_number not in existing_seat_numbers:
                                    is_reserved = seat_number in reserved_seat_numbers
                                    
                                    TicketsNew.objects.create(
                                        ticket_year=start_datetime.year,
                                        yatra_id=yatra,
                                        yatra_route_id=route,
                                        yatra_bus_id=existing_yatra_bus,
                                        seat_no=seat_number,
                                        seat_fees=SeatFees,
                                        seat_ticket_type=1,
                                        discount=SeatFees if is_reserved else 0,
                                        discount_reason='Swayamsevak' if is_reserved else '',
                                        amount_paid=SeatFees if is_reserved else 0,
                                        payment_mode=1 if is_reserved else 0,
                                        payment_id=None,
                                        ticket_status_id=2 if is_reserved else 0,
                                        registration_id=None,
                                        permanant_id=0,
                                        user_id=user if is_reserved else None,
                                        booking_date=start_datetime.date(),
                                        created_by=user
                                    )
                        
                        # If capacity decreased, remove seats beyond new capacity (only if unbooked)
                        elif bus_capacity_value < old_capacity:
                            TicketsNew.objects.filter(
                                yatra_id=yatra,
                                yatra_route_id=route,
                                yatra_bus_id=existing_yatra_bus,
                                seat_no__gt=bus_capacity_value,
                                ticket_status_id=0  # Only delete available seats
                            ).delete()

                # Update existing seats' reserved status
                for ticket in existing_tickets:
                    is_reserved = ticket.seat_no in reserved_seat_numbers
                    
                    # Only update if the seat is available (status 0) or already reserved (status 2)
                    if ticket.ticket_status_id in [0, 2]:
                        ticket.ticket_status_id = 2 if is_reserved else 0
                        ticket.discount = SeatFees if is_reserved else 0
                        ticket.discount_reason = 'Swayamsevak' if is_reserved else ''
                        ticket.amount_paid = SeatFees if is_reserved else 0
                        ticket.payment_mode = 1 if is_reserved else 0
                        ticket.user_id = user if is_reserved else None
                        ticket.seat_fees = SeatFees
                        ticket.save()

            return Response({
                'message_code': 1000,
                'message_text': 'Yatra bus updated successfully.'
            }, status=status.HTTP_200_OK)
            
        except YatraBuses.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': 'This yatra bus does not exist.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({
                'message_code': 999,
                'message_text': f'Unable to update yatra bus. Error: {str(e)}'
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'message_code': 999,
            'message_text': f'Unexpected error: {str(e)}'
        }, status=status.HTTP_200_OK)
    

@api_view(['POST'])
def deleteyatrabus(request):
    """
    Permanently deletes a Yatra Bus and all its associated tickets.
    Expects:
    {
        "YatraBusId": 123,
        "UserId": 1   # Optional, who is performing the deletion
    }
    """
    try:
        from django.db import transaction
        
        body = request.data
        yatra_bus_id = body.get('YatraBusId')
        user_id = body.get('UserId', 1)

        if not yatra_bus_id:
            return Response({
                'message_code': 999,
                'message_text': 'YatraBusId must be specified to delete a bus.'
            }, status=status.HTTP_200_OK)

        # Convert to int
        try:
            yatra_bus_id_int = int(yatra_bus_id)
        except (ValueError, TypeError):
            return Response({
                'message_code': 999,
                'message_text': 'Invalid YatraBusId.'
            }, status=status.HTTP_200_OK)

        # Check if bus exists (without is_deleted filter for permanent delete)
        try:
            bus_to_delete = YatraBuses.objects.get(yatraBusId=yatra_bus_id_int)
        except YatraBuses.DoesNotExist:
            return Response({
                'message_code': 999,
                'message_text': 'This Yatra bus does not exist.'
            }, status=status.HTTP_200_OK)

        # Permanently delete inside a transaction
        with transaction.atomic():
            # Delete all tickets associated with this bus
            deleted_tickets_count = TicketsNew.objects.filter(
                yatra_bus_id=bus_to_delete
            ).delete()[0]  # Returns tuple (count, {model: count})
            
            # Store bus name for response
            bus_name = bus_to_delete.busName.busName if bus_to_delete.busName else 'Unknown'
            
            # Permanently delete the bus
            bus_to_delete.delete()

        return Response({
            'message_code': 1000,
            'message_text': 'Yatra bus and all its tickets deleted successfully.',
            'message_data': {
                'YatraBusId': yatra_bus_id_int,
                'BusName': bus_name,
                'DeletedTickets': deleted_tickets_count
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({
            'message_code': 999,
            'message_text': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_200_OK)

# @api_view(['POST'])
# def deleteyatrabus(request):
#     """
#     Soft delete a Yatra Bus by setting `is_deleted` to True.
#     Expects:
#     {
#         "YatraBusId": 123,
#         "UserId": 1   # Optional, who is performing the deletion
#     }
#     """
#     try:
#         body = request.data
#         yatra_bus_id = body.get('YatraBusId')
#         user_id = body.get('UserId', 1)

#         if not yatra_bus_id:
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'YatraBusId must be specified to delete a bus.'
#             }, status=status.HTTP_200_OK)

#         try:
#             bus_to_delete = YatraBuses.objects.get(yatraBusId=yatra_bus_id, is_deleted=False)
#         except YatraBuses.DoesNotExist:
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'This Yatra bus does not exist or is already deleted.'
#             }, status=status.HTTP_200_OK)

#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({
#                 'message_code': 999,
#                 'message_text': 'User performing deletion does not exist.'
#             }, status=status.HTTP_200_OK)

#         # Soft delete inside a transaction
#         with transaction.atomic():
#             bus_to_delete.is_deleted = True
#             bus_to_delete.deleted_by = user
#             bus_to_delete.save()

#         return Response({
#             'message_code': 1000,
#             'message_text': 'Yatra bus deleted successfully (soft delete).',
#             'message_data': {'YatraBusId': bus_to_delete.yatraBusId}
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({
#             'message_code': 999,
#             'message_text': f'An unexpected error occurred: {str(e)}'
#         }, status=status.HTTP_200_OK)


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



@api_view(['POST'])
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




@api_view(['POST'])
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


@api_view(['POST'])
def fetch_bus_seats(request):
    """
    An independent API to fetch detailed seat availability for a specific bus,
    including Bus Name, Capacity, and categorized seat numbers.
    """
    # 1. Enforce POST request method
    if request.method != 'POST':
        return JsonResponse({
            "message_code": 999,
            "message_text": "Invalid request method. Only POST is supported."
        }, status=405)

    # 2. Parse JSON body
    try:
        params = json.loads(request.body)
        yatra_id = params.get('yatra_id')
        bus_id = params.get('bus_id')
        route_id = params.get('route_id') # Included for API consistency
    except json.JSONDecodeError:
        return JsonResponse({
            "message_code": 998,
            "message_text": "Invalid JSON format in request body."
        }, status=400)

    # 3. Validate required parameters
    if not all([yatra_id, bus_id, route_id]):
        return JsonResponse({
            "message_code": 997,
            "message_text": "Missing required parameters. 'route_id', 'yatra_id', and 'bus_id' are required."
        }, status=400)

    try:
        # 4. Fetch Bus details from the database
        try:
            # Use select_related to efficiently fetch the bus name from the related table
            bus = YatraBuses.objects.select_related('busName').get(pk=bus_id)
            bus_name = bus.busName.busName
            bus_capacity = bus.busCapacity
        except YatraBuses.DoesNotExist:
            return JsonResponse({
                "message_code": 996,
                "message_text": f"Error: Bus with ID {bus_id} not found."
            }, status=404)

        # 5. Fetch all seat statuses for the given bus in one query
        all_tickets_for_bus = TicketsNew.objects.filter(
            yatra_bus_id=bus_id
        ).values('seat_no', 'ticket_status_id')

        # 6. Initialize lists to categorize seats
        reserved_for_swayamsevak = []
        available_seats = []
        booked_seats = []

        # 7. Categorize each seat based on its status_id
        # Based on createyatrabus logic: 0 = Available, 2 = Reserved (Swayamsevak)
        # Any other status is considered a regular booking by a pilgrim.
        for ticket in all_tickets_for_bus:
            seat_number = ticket.get('seat_no')
            status_id = ticket.get('ticket_status_id')
            
            if seat_number is None:
                continue

            if status_id == 2:
                reserved_for_swayamsevak.append(seat_number)
            elif status_id == 0:
                available_seats.append(seat_number)
            else: # Any other status (e.g., 1 for Confirmed) is a booked seat
                booked_seats.append(seat_number)

        # 8. Structure the successful response payload
        response_data = {
            "BusName": bus_name,
            "Capacity": bus_capacity,
            "reserved_for_swayamsevak": sorted(reserved_for_swayamsevak),
            "available_seats": sorted(available_seats),
            "booked_seats": sorted(booked_seats)
        }

        return JsonResponse({
            "message_code": 1000,
            "message_text": "Seat information retrieved successfully.",
            "message_data": response_data
        })

    except Exception as e:
        # 9. Catch-all for any other unexpected errors
        return JsonResponse({
            "message_code": 990,
            "message_text": f"An unexpected server error occurred: {str(e)}"
        }, status=500)
    

@api_view(['POST'])
def insert_ticket(request):
    """
    Inserts a new ticket record for a Yatra bus booking.
    Validates all required fields before creating the ticket.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data

        # Extract and validate input parameters
        yatra_id = body.get('YatraId', 0)
        yatra_route_id = body.get('YatraRouteId', 0)
        yatra_bus_id = body.get('YatraBusId', 0)
        seat_no = body.get('SeatNo', 0)
        seat_fees = body.get('SeatFees', 0)
        seat_ticket_type = body.get('SeatTicketType', 0)
        registration_id = body.get('RegistrationId', 0)
        user_id = body.get('UserId', 0)

        # Validation checks
        if not yatra_id or yatra_id == 0:
            response_data['message_text'] = 'Please provide Yatra to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not yatra_route_id or yatra_route_id == 0:
            response_data['message_text'] = 'Please provide Yatra Route to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not yatra_bus_id or yatra_bus_id == 0:
            response_data['message_text'] = 'Please provide Yatra Bus to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not seat_no or seat_no == 0:
            response_data['message_text'] = 'Please provide Seat No to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not registration_id or registration_id == 0:
            response_data['message_text'] = 'Please provide Pilgrim to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not user_id or user_id == 0:
            response_data['message_text'] = 'Please provide user who is adding ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch foreign key objects
        try:
            yatra_obj = Yatras.objects.get(pk=yatra_id)
            yatra_route_obj = YatraRoutes.objects.get(pk=yatra_route_id)
            yatra_bus_obj = YatraBuses.objects.get(pk=yatra_bus_id)
            registration_obj = Registrations.objects.get(pk=registration_id)
            user_obj = User.objects.get(pk=user_id)
        except (Yatras.DoesNotExist, YatraRoutes.DoesNotExist, YatraBuses.DoesNotExist,
                Registrations.DoesNotExist, User.DoesNotExist) as e:
            response_data['message_text'] = f'One or more referenced records do not exist: {str(e)}'
            return Response(response_data, status=status.HTTP_200_OK)

        # Create new ticket
        new_ticket = TicketsNew.objects.create(
            yatra_id=yatra_obj,
            yatra_route_id=yatra_route_obj,
            yatra_bus_id=yatra_bus_obj,
            seat_no=seat_no,
            seat_fees=seat_fees,
            seat_ticket_type=seat_ticket_type,
            discount=0,
            discount_reason='0',
            amount_paid=0,
            payment_id=None,
            ticket_status_id=seat_ticket_type,
            registration_id=registration_obj,
            permanant_id=0,
            user_id=user_obj,
            created_by=user_obj,
            last_modified_by=user_obj
        )

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Ticket inserted successfully.'
        response_data['message_data'] = {'TicketId': new_ticket.ticket_id}

    except Exception as e:
        response_data['message_text'] = 'Unable to add the ticket.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def cancel_ticket(request):
    """
    Cancels an existing ticket by updating its status to cancelled (4).
    Records the cancellation reason and updates audit fields.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data

        # Extract and validate input parameters
        ticket_id = body.get('TicketId', 0)
        user_id = body.get('UserId', 0)
        cancel_reason = body.get('CancelReason', '')

        # Validation checks
        if not ticket_id or ticket_id == 0:
            response_data['message_text'] = 'Please provide Ticket to cancel ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not user_id or user_id == 0:
            response_data['message_text'] = 'Please provide user who is adding ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the ticket and user objects
        try:
            ticket = TicketsNew.objects.get(ticket_id=ticket_id)
            user_obj = User.objects.get(pk=user_id)
        except TicketsNew.DoesNotExist:
            response_data['message_text'] = 'The specified ticket does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data['message_text'] = 'The specified user does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Update the ticket with cancellation details
        ticket.cancel_reason = cancel_reason
        ticket.ticket_status_id = 4  # Status 4 = Cancelled
        ticket.last_modified_by = user_obj  # Properly track who cancelled it
        ticket.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Ticket cancelled successfully.'
        response_data['message_data'] = {'TicketId': ticket.ticket_id}

    except Exception as e:
        response_data['message_text'] = 'Unable to cancel the ticket.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)    


@api_view(['POST'])
def remove_ticket(request):
    """
    Removes a ticket by resetting its type and status to 0.
    This typically makes the seat available again or marks the ticket as inactive.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data

        # Extract and validate input parameters
        ticket_id = body.get('TicketId', 0)
        user_id = body.get('UserId', 0)

        # Validation checks
        if not ticket_id or ticket_id == 0:
            response_data['message_text'] = 'Please provide Ticket to remove ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not user_id or user_id == 0:
            response_data['message_text'] = 'Please provide user who is removing ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the ticket and user objects
        try:
            ticket = TicketsNew.objects.get(ticket_id=ticket_id)
            user_obj = User.objects.get(pk=user_id)
        except TicketsNew.DoesNotExist:
            response_data['message_text'] = 'The specified ticket does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data['message_text'] = 'The specified user does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Update the ticket - reset type and status to 0
        ticket.seat_ticket_type = 0
        ticket.ticket_status_id = 0
        ticket.last_modified_by = user_obj  # Properly track who removed it
        ticket.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Ticket removed successfully.'
        response_data['message_data'] = {'TicketId': ticket.ticket_id}

    except Exception as e:
        response_data['message_text'] = 'Unable to remove the ticket.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_ticket(request):
    """
    Changes/transfers a ticket by:
    1. Marking the old ticket as 'Changed' with status 2
    2. Creating a new ticket with updated details
    Both operations are done in a transaction to ensure data consistency.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data

        # Extract and validate input parameters
        ticket_id = body.get('TicketId', 0)
        yatra_id = body.get('YatraId', 0)
        yatra_route_id = body.get('YatraRouteId', 0)
        yatra_bus_id = body.get('YatraBusId', 0)
        seat_no = body.get('SeatNo', 0)
        seat_fees = body.get('SeatFees', 0)
        seat_ticket_type = body.get('SeatTicketType', 0)
        amount_paid = body.get('AmountPaid', 0)
        discount = body.get('Discount', 0)
        discount_reason = body.get('DiscountReason', '')
        payment_id = body.get('PaymentId', 0)
        registration_id = body.get('RegistrationId', 0)
        permanant_id = body.get('PermanantId', 0)
        user_id = body.get('UserId', 0)

        # Validation checks
        if not ticket_id or ticket_id == 0:
            response_data['message_text'] = 'Please provide Ticket ID to change ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not yatra_id or yatra_id == 0:
            response_data['message_text'] = 'Please provide Yatra to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not yatra_route_id or yatra_route_id == 0:
            response_data['message_text'] = 'Please provide Yatra Route to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not yatra_bus_id or yatra_bus_id == 0:
            response_data['message_text'] = 'Please provide Yatra Bus to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not seat_no or seat_no == 0:
            response_data['message_text'] = 'Please provide Seat No to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not registration_id or registration_id == 0:
            response_data['message_text'] = 'Please provide Pilgrim to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not user_id or user_id == 0:
            response_data['message_text'] = 'Please provide user who is adding ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch foreign key objects
        try:
            old_ticket = TicketsNew.objects.get(ticket_id=ticket_id)
            yatra_obj = Yatras.objects.get(pk=yatra_id)
            yatra_route_obj = YatraRoutes.objects.get(pk=yatra_route_id)
            yatra_bus_obj = YatraBuses.objects.get(pk=yatra_bus_id)
            registration_obj = Registrations.objects.get(pk=registration_id)
            user_obj = User.objects.get(pk=user_id)
            
            payment_obj = None
            if payment_id and payment_id != 0:
                payment_obj = Payments.objects.get(pk=payment_id)
                
        except TicketsNew.DoesNotExist:
            response_data['message_text'] = 'The specified ticket does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)
        except (Yatras.DoesNotExist, YatraRoutes.DoesNotExist, YatraBuses.DoesNotExist,
                Registrations.DoesNotExist, User.DoesNotExist, Payments.DoesNotExist) as e:
            response_data['message_text'] = f'One or more referenced records do not exist: {str(e)}'
            return Response(response_data, status=status.HTTP_200_OK)

        # Use transaction to ensure both operations succeed or fail together
        with transaction.atomic():
            # Step 1: Update old ticket - mark as changed
            old_ticket.cancel_reason = 'Changed'
            old_ticket.ticket_status_id = 2  # Status 2 = Changed/Transferred
            old_ticket.last_modified_by = user_obj
            old_ticket.save()

            # Step 2: Create new ticket with updated details
            new_ticket = TicketsNew.objects.create(
                yatra_id=yatra_obj,
                yatra_route_id=yatra_route_obj,
                yatra_bus_id=yatra_bus_obj,
                seat_no=seat_no,
                seat_fees=seat_fees,
                seat_ticket_type=seat_ticket_type,
                discount=discount,
                discount_reason=discount_reason,
                amount_paid=amount_paid,
                payment_id=payment_obj,
                ticket_status_id=1,  # Status 1 = Active/Confirmed
                registration_id=registration_obj,
                permanant_id=permanant_id,
                user_id=user_obj,
                created_by=user_obj,
                last_modified_by=user_obj
            )

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Ticket changed successfully.'
        response_data['message_data'] = {
            'OldTicketId': old_ticket.ticket_id,
            'NewTicketId': new_ticket.ticket_id
        }

    except Exception as e:
        response_data['message_text'] = 'Unable to change the ticket.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_ticket_payment(request):
    """
    Updates payment details for all tickets with status 2 (Reserved/Changed) 
    for a specific pilgrim and marks them as status 3 (Paid/Confirmed).
    This is a bulk update operation for all reserved tickets of a pilgrim.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data

        # Extract and validate input parameters
        amount_paid = body.get('AmountPaid', 0)
        discount = body.get('Discount', 0)
        discount_reason = body.get('DiscountReason', '')
        payment_details = body.get('PaymentDetails', '')
        payment_proof = body.get('PaymentProof', '')
        registration_id = body.get('RegistrationId', 0)
        user_id = body.get('UserId', 0)

        # Validation checks
        if not registration_id or registration_id == 0:
            response_data['message_text'] = 'Please provide Pilgrim to add ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not user_id or user_id == 0:
            response_data['message_text'] = 'Please provide user who is adding ticket.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch foreign key objects
        try:
            registration_obj = Registrations.objects.get(pk=registration_id)
            user_obj = User.objects.get(pk=user_id)
        except Registrations.DoesNotExist:
            response_data['message_text'] = 'The specified registration/pilgrim does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data['message_text'] = 'The specified user does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Find all tickets with status 2 for this registration
        tickets_to_update = TicketsNew.objects.filter(
            registration_id=registration_obj,
            ticket_status_id=2
        )

        if not tickets_to_update.exists():
            response_data['message_text'] = 'No tickets found with status 2 (Reserved) for this pilgrim.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Update all matching tickets with payment information
        with transaction.atomic():
            updated_count = tickets_to_update.update(
                discount=discount,
                discount_reason=discount_reason,
                payment_details=payment_details,
                payment_proof=payment_proof,
                amount_paid=amount_paid,  # Fixed: Now actually using AmountPaid
                ticket_status_id=3,  # Status 3 = Paid/Confirmed
                last_modified_by=user_obj
            )

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Tickets updated successfully.'
        response_data['message_data'] = {
            'RegistrationId': registration_id,
            'TicketsUpdated': updated_count
        }

    except Exception as e:
        response_data['message_text'] = 'Unable to update ticket payment.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def list_pilgrim_tickets(request):
    """
    Fetch all valid tickets for a given pilgrim (RegistrationId).
    Equivalent to fi_list_pilgrim_tickets in PHP.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        registration_id = body.get('RegistrationId', 0)

        # Validation
        if not registration_id or registration_id == 0:
            response_data['message_text'] = 'Please provide Pilgrim (RegistrationId).'
            return Response(response_data, status=status.HTTP_200_OK)

        try:
            registration_obj = Registrations.objects.get(pk=registration_id)
        except Registrations.DoesNotExist:
            response_data['message_text'] = 'The specified registration/pilgrim does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Query tickets with joins
        tickets = (
            TicketsNew.objects.filter(
                registration_id=registration_obj,
                ticket_status_id__in=[1, 2, 3, 4],
                yatra_bus_id__busStatus=1
            )
            .select_related('yatra_bus_id', 'yatra_route_id')
        )

        if not tickets.exists():
            response_data['message_text'] = 'No Tickets.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Build result
        tickets_data = []
        for t in tickets:
            bus_obj = t.yatra_bus_id
            route_obj = t.yatra_route_id
            tickets_data.append({
                "TicketId": t.ticket_id,
                "YatraId": t.yatra_id.pk if t.yatra_id else None,
                "YatraRouteId": route_obj.pk if route_obj else None,
                "YatraRouteName": getattr(route_obj, 'yatraRoutename', None),
                "YatraBusId": bus_obj.pk if bus_obj else None,
                "BusName": getattr(bus_obj.busName, 'name', None) if bus_obj and bus_obj.busName else None,
                "SeatNo": t.seat_no,
                "BusDateTimeStart": bus_obj.busDateTimeStart.strftime("%d-%m-%Y %H-%M") if bus_obj and bus_obj.busDateTimeStart else None,
                "SeatFees": str(t.seat_fees) if t.seat_fees else "0.00",
                "SeatTicketType": t.seat_ticket_type,
                "Discount": str(t.discount) if t.discount else "0.00",
                "DiscountReason": t.discount_reason,
                "AmountPaid": str(t.amount_paid) if t.amount_paid else "0.00",
                "PaymentId": t.payment_id.pk if t.payment_id else None,
                "UserId": t.user_id.pk if t.user_id else None,
                "TicketStatusId": t.ticket_status_id,
                "CancelReason": t.cancel_reason,
            })

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = tickets_data

    except Exception as e:
        response_data['message_text'] = 'Unable to fetch tickets.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def list_available_tickets(request):
    """
    List all seats for a given Yatra and Bus, marking reserved/booked seats.
    Equivalent to fi_list_available_tickets in PHP.
    """
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        body = request.data
        yatra_id = body.get('YatraId', "")
        yatra_bus_id = body.get('YatraBusId', 0)

        # Validation checks
        if not yatra_id:
            response_data['message_text'] = 'Yatra must be specified to list bus seats.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not yatra_bus_id or int(yatra_bus_id) == 0:
            response_data['message_text'] = 'Yatra Bus must be specified to list seats.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch bus info
        try:
            bus_obj = YatraBuses.objects.get(pk=yatra_bus_id, yatraId__pk=yatra_id)
        except YatraBuses.DoesNotExist:
            response_data['message_text'] = 'The specified Yatra Bus does not exist.'
            return Response(response_data, status=status.HTTP_200_OK)

        bus_capacity = bus_obj.busCapacity or 0
        seat_fees = bus_obj.seatFees or 0

        # Step 1: Load all seats from BusSeats (limited by bus capacity)
        seats = BusSeats.objects.all().order_by('id')[:bus_capacity]

        if not seats.exists():
            response_data['message_text'] = 'No Seats.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Build seat map (default status from BusSeats table)
        seat_map = []
        for seat in seats:
            seat_map.append({
                "SeatName": seat.seatName,
                "SeatStatus": seat.seatStatus,   # initial from tblBusSeats
                "SeatFees": str(seat_fees)
            })

        # Step 2: Fetch already booked seats for this bus
        booked_seats = TicketsNew.objects.filter(
            yatra_id=yatra_id,
            yatra_bus_id=yatra_bus_id
        ).values('seat_no', 'seat_ticket_type')

        # Update seat status
        for booking in booked_seats:
            seat_no = booking['seat_no']
            seat_type = booking['seat_ticket_type']
            if seat_no and seat_no <= len(seat_map):
                seat_map[seat_no - 1]['SeatStatus'] = seat_type

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = seat_map

    except Exception as e:
        response_data['message_text'] = 'Unable to fetch available tickets.'
        debug.append(f"Error Type: {type(e).__name__}, Details: {str(e)}")

    return Response(response_data, status=status.HTTP_200_OK)