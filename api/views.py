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



@api_view(['POST'])
def insertarea(request):
    """
    Insert a new area into the database.
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while creating area.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listarea(request):
    """
    Retrieve a list of active areas (AreaStatus = 1).
    """

    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching areas.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listareaall(request):
    """
    Retrieve a list of all areas, regardless of status.
    """

    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        all_areas = Areas.objects.all().values('AreaId', 'AreaName', 'AreaStatus')

        if not all_areas:
            response_data['message_text'] = 'No Areas found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = list(all_areas)

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching areas.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)
   
    

@api_view(['PUT'])
def modifyarea(request):
    """
    Modify an existing area's details.
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while modifying area.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listgender(request):
    """
    Retrieve a list of all genders, ordered by GenderOrder.
    """

    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching genders.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listbloodgroup(request):
    """
    Retrieve a list of all blood groups, ordered by BloodGroupOrder.
    """

    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching blood groups.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)

    

@api_view(['POST'])
def insertuser(request):
    """
    Insert a new user into the database.

    Maps UserMobileNo to username and UserLoginPin to password.
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while creating user.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def modifyuser(request):
    """
    Modify an existing user's details.
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while modifying user.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def deleteuser(request):
    """
    Deactivate a user (soft delete) by setting is_active to False.
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

    except Exception as e:
        response_data['message_text'] = 'An error occurred while deactivating user.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listuserall(request):
    """
    Retrieve a list of all users.
    """

    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Failure',
        'message_data': [],
        'message_debug': debug
    }

    try:
        users = User.objects.all().values(
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff'
        )

        if not users.exists():
            response_data['message_text'] = 'No Users found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = list(users)

    except Exception as e:
        response_data['message_text'] = 'An error occurred while fetching users.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def agentlogin(request):
    """
    Authenticates an agent using their mobile number and password/pin.
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
        mobile_no = body.get('userMobileNo', '').strip()
        password = body.get('userPassword', '').strip()

        # --- Validation ---
        if not mobile_no:
            response_data['message_text'] = 'Please provide your mobile no. for login.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not password:
            response_data['message_text'] = 'Please provide your password/pin for login.'
            return Response(response_data, status=status.HTTP_200_OK)

        # --- Authentication ---
        user = authenticate(username=mobile_no, password=password)

        if user is not None:
            if not user.is_active:
                response_data['message_text'] = 'Your login is not active.'
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                # Login successful
                response_data['message_code'] = 1000
                response_data['message_text'] = 'Success'
                response_data['message_data'] = {
                    "UserId": user.id,
                    "UserFirstname": user.first_name,
                    "UserLastname": user.last_name,
                    "UserMobileNo": user.username
                }
        else:
            # Authentication failed
            response_data['message_text'] = 'Mobile no and Password/pin not valid.'

    except Exception as e:
        response_data['message_text'] = 'An error occurred while logging in.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def searchregistrations(request):
    """
    Searches registrations based on a search term across multiple fields.
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
        search_term = body.get('search', '').strip()

        # --- Fetch all registrations with related area names ---
        all_registrations = Registrations.objects.values(
            'registrationId', 'firstname', 'middlename', 'lastname', 'mobileNo',
            'alternateMobileNo', 'dateOfBirth', 'gender', 'aadharNumber',
            'address', 'photoFileName', 'idProofFileName', 'voterIdProof',
            'dateOfRegistration', 'permanentId',
            'areaId__AreaName'
        )

        # --- Filter results if search term is provided ---
        if search_term:
            search_term_lower = search_term.lower()
            filtered_results = []

            for reg in all_registrations:
                if (
                    (reg['firstname'] and search_term_lower in str(reg['firstname']).lower()) or
                    (reg['lastname'] and search_term_lower in str(reg['lastname']).lower()) or
                    (reg['mobileNo'] and search_term_lower in str(reg['mobileNo']).lower()) or
                    (reg['alternateMobileNo'] and search_term_lower in str(reg['alternateMobileNo']).lower()) or
                    (reg['areaId__AreaName'] and search_term_lower in str(reg['areaId__AreaName']).lower())
                ):
                    filtered_results.append(reg)

            results = filtered_results
        else:
            results = all_registrations

        # --- Rename 'areaId__AreaName' to 'AreaName' ---
        final_output = []
        for res in results:
            res['AreaName'] = res.pop('areaId__AreaName')
            final_output.append(res)

        if not final_output:
            response_data['message_text'] = 'No Registrations found.'
            return Response(response_data, status=status.HTTP_200_OK)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Success'
        response_data['message_data'] = final_output

    except Exception as e:
        response_data['message_text'] = 'An error occurred while searching registrations.'
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def pilgrimregistration(request):
    """
    Creates a new pilgrim registration or updates an existing one.
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
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def getpilgrimcard(request):
    """
    Generates a pilgrim ID card image based on a RegistrationId.
    """
    try:
        body = request.data
        registration_id = body.get('RegistrationId')

        if not registration_id:
            return Response({'message_code': 999, 'message_text': 'Please provide the registration Id.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Fetch Data ---
        try:
            # Fetch registration details and related area name
            reg_data = Registrations.objects.select_related('areaId').get(registrationId=registration_id)
        except Registrations.DoesNotExist:
            return Response({'message_code': 999, 'message_text': 'Unable to find the registered user.'}, status=status.HTTP_404_NOT_FOUND)

        # Fetch yatra/ticket details
        yatra_details = TicketsNew.objects.filter(
            registration_id=registration_id,
            ticket_status_id=2 # Assuming 2 means active/confirmed
        ).select_related('yatra_route_id', 'yatra_bus_id').order_by('yatra_id__yatraStartDateTime')

        # --- Prepare for Image Generation ---
        # Define colors and font
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        BLUE = (66, 135, 245)
        RED = (219, 70, 20)
        try:
            # For better text, use a real font file. Place a .ttf file in your project.
            # font = ImageFont.truetype("arial.ttf", size=10)
            # If you don't have a font file, use the basic default one
            font = ImageFont.load_default()
        except IOError:
            font = ImageFont.load_default()

        # Create blank image canvas
        image = Image.new('RGB', (252, 144), WHITE)
        draw = ImageDraw.Draw(image)

        # --- Draw Layout ---
        draw.rectangle((2, 2, 250, 142), outline=BLACK)
        draw.line((78, 2, 78, 120), fill=BLACK)
        draw.line((2, 78, 78, 78), fill=BLACK)

        # --- Paste Profile Picture ---
        profile_pic_path = os.path.join(settings.BASE_DIR, 'path/to/default/profile.png') # Define a default
        if reg_data.photoFileName:
            # In Django, photoFileName would typically be a relative path in your MEDIA_ROOT
            user_pic_path = os.path.join(settings.MEDIA_ROOT, str(reg_data.photoFileName))
            if os.path.exists(user_pic_path):
                profile_pic_path = user_pic_path

        try:
            profile_img = Image.open(profile_pic_path)
        except IOError:
            # If the user's image or the default is missing, create a blank gray box
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
            draw.text((4, y), str(reg_data.address)[:30], fill=BLACK, font=font) # Truncate address
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
                if y > 110: break # Avoid writing outside the box
                # Yatra Name
                draw.text((83, y), str(ticket.yatra_route_id.yatraRoutename)[:12], fill=BLACK, font=font)
                # Departure Date/Time
                dep_datetime = ticket.yatra_id.yatraStartDateTime
                if dep_datetime:
                    dep_str = dep_datetime.strftime("%d@%H:%M")
                    draw.text((162, y), dep_str, fill=BLACK, font=font)
                # Bus-Seat
                bus_seat_str = f"{ticket.yatra_bus_id.busName}-{ticket.seat_no}"
                draw.text((222, y), bus_seat_str, fill=BLACK, font=font)
                
                y += 10
                draw.line((79, y, 250, y), fill=BLUE)
                y += 2

        # --- Save the Image ---
        cards_dir = os.path.join(settings.MEDIA_ROOT, 'cards')
        os.makedirs(cards_dir, exist_ok=True) # Create the 'cards' directory if it doesn't exist
        
        card_filename = f"{registration_id}.png"
        output_path = os.path.join(cards_dir, card_filename)
        image.save(output_path)

        # --- Return URL to the image ---
        card_url = f"{settings.MEDIA_URL}cards/{card_filename}"

        return Response({
            'message_code': 1000, 
            'message_text': 'Card Printed', 
            'message_data': card_url
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message_code': 500, 'message_text': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    




# --- Paste this entire block at the end of your api/views.py file ---

@api_view(['POST'])
def inserttickets(request):
    """
    Creates a single new ticket record with basic details.
    """
    try:
        body = request.data
        # --- Validation ---
        if not body.get('YatraId'): return Response({'message_code': 999, 'message_text': 'Please provide Yatra.'}, status=status.HTTP_400_BAD_REQUEST)
        if not body.get('YatraRouteId'): return Response({'message_code': 999, 'message_text': 'Please provide Yatra Route.'}, status=status.HTTP_400_BAD_REQUEST)
        if not body.get('YatraBusId'): return Response({'message_code': 999, 'message_text': 'Please provide Yatra Bus.'}, status=status.HTTP_400_BAD_REQUEST)
        if not body.get('SeatNo'): return Response({'message_code': 999, 'message_text': 'Please provide Seat No.'}, status=status.HTTP_400_BAD_REQUEST)
        if not body.get('RegistrationId'): return Response({'message_code': 999, 'message_text': 'Please provide Pilgrim.'}, status=status.HTTP_400_BAD_REQUEST)
        if not body.get('UserId'): return Response({'message_code': 999, 'message_text': 'Please provide User.'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Fetch Foreign Key Objects ---
        try:
            yatra_obj = Yatras.objects.get(yatraId=body.get('YatraId'))
            yatra_route_obj = YatraRoutes.objects.get(yatraRouteId=body.get('YatraRouteId'))
            yatra_bus_obj = YatraBuses.objects.get(yatraBusId=body.get('YatraBusId'))
            registration_obj = Registrations.objects.get(registrationId=body.get('RegistrationId'))
            user_obj = User.objects.get(id=body.get('UserId'))
        except (Yatras.DoesNotExist, YatraRoutes.DoesNotExist, YatraBuses.DoesNotExist, Registrations.DoesNotExist, User.DoesNotExist) as e:
            return Response({'message_code': 404, 'message_text': f"Related object not found: {e}"}, status=status.HTTP_404_NOT_FOUND)

        # --- Create Ticket ---
        TicketsNew.objects.create(
            yatra_id=yatra_obj,
            yatra_route_id=yatra_route_obj,
            yatra_bus_id=yatra_bus_obj,
            registration_id=registration_obj,
            user_id=user_obj,
            seat_no=body.get('SeatNo'),
            seat_fees=body.get('SeatFees', 0),
            seat_ticket_type=body.get('SeatTicketType', 0),
            ticket_status_id=body.get('SeatTicketType', 0) # Status matches the type
        )
        return Response({'message_code': 1000, 'message_text': 'Ticket inserted successfully.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'message_code': 500, 'message_text': f'Unable to add the ticket: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        return Response({'message_code': 500, 'message_text': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def totalrouteyatrabus(request):
    """
    Provides a report of total bookings grouped by Yatra Route, Yatra, and Bus.
    """
    try:
        # This query uses the ORM to replicate the SQL GROUP BY and COUNT functionality
        booking_counts = TicketsNew.objects.filter(
            ticket_year=2025,
            ticket_status_id=2  # Only count booked tickets
        ).values(
            # Fields to group by, fetching names from related tables
            'yatra_route_id__yatraRouteId',
            'yatra_route_id__yatraRoutename',
            'yatra_id__yatraId',
            'yatra_id__yatraDateTime',
            'yatra_id__yatraStartDateTime',
            'yatra_id__yatraFees',
            'yatra_bus_id__yatraBusId',
            'yatra_bus_id__busName'
        ).annotate(
            # The new calculated field: a count of bookings for each group
            Bookings=Count('ticket_id')
        ).order_by(
            'yatra_route_id', 'yatra_id', 'yatra_bus_id'
        )

        if not booking_counts:
            return Response({'message_code': 999, 'message_text': 'No bookings', 'message_data': []}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message_code': 1000,
            'message_text': 'Route, Yatra, Bus wise Booking counters',
            'message_data': list(booking_counts)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message_code': 500, 'message_text': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)     


@api_view(['POST'])
def routeyatrabustickets(request):
    """
    Lists all booked tickets for a specific Yatra Route, Yatra, and Bus.
    """
    try:
        body = request.data
        route_id = body.get('YatraRouteId')
        yatra_id = body.get('YatraId')
        bus_id = body.get('YatraBusId')

        if not route_id: return Response({'message_code': 999, 'message_text': 'Please provide yatra route.'}, status=status.HTTP_400_BAD_REQUEST)
        if not yatra_id: return Response({'message_code': 999, 'message_text': 'Please provide Yatra.'}, status=status.HTTP_400_BAD_REQUEST)
        if not bus_id: return Response({'message_code': 999, 'message_text': 'Please provide yatra bus.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # CORRECTED QUERY: Every item in .values() is now a keyword argument.
        tickets = TicketsNew.objects.filter(
            yatra_route_id=route_id,
            yatra_id=yatra_id,
            yatra_bus_id=bus_id,
            ticket_year=2025,
            ticket_status_id=2
        ).values(
            YatraRouteId='yatra_route_id',
            YatraId='yatra_id',
            YatraDateTime='yatra_id__yatraDateTime',
            YatraStartDateTime='yatra_id__yatraStartDateTime',
            YatraFees='yatra_id__yatraFees',
            YatraBusId='yatra_bus_id',
            BusName='yatra_bus_id__busName',
            SeatNo='seat_no',
            RegistrationId='registration_id',
            DiscountReason='discount_reason',
            Firstname='registration_id__firstname',
            Middlename='registration_id__middlename',
            Lastname='registration_id__lastname',
            MobileNo='registration_id__mobileNo',
            AlternateMobileNo='registration_id__alternateMobileNo',
            BloodGroup='registration_id__bloodGroup__bloodGroupName',
            Gender='registration_id__gender',
            PhotoFileName='registration_id__photoFileName',
            IdProofFileName='registration_id__idProofFileName',
            VoterIdProof='registration_id__voterIdProof'
        ).order_by('seat_no')

        if not tickets.exists():
            return Response({'message_code': 999, 'message_text': 'No Tickets', 'message_data': []}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message_code': 1000, 'message_text': 'Route, Yatra, Bus wise Tickets', 'message_data': list(tickets)}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message_code': 500, 'message_text': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def agentbookings(request):
    """
    Lists all tickets booked by a specific agent on a given date.
    """
    try:
        from datetime import datetime
        body = request.data
        user_id = body.get('UserId')
        booking_date_str = body.get('BookingDate')

        if not user_id: return Response({'message_code': 999, 'message_text': 'Please provide agent.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_date = datetime.strptime(booking_date_str, '%d/%m/%Y').date()
        except (ValueError, TypeError):
            target_date = datetime.today().date()

        # CORRECTED QUERY: Every item in .values() is now a keyword argument.
        tickets = TicketsNew.objects.filter(
            user_id=user_id,
            booking_date=target_date,
            ticket_year=2025,
            ticket_status_id=2
        ).values(
            YatraRouteId='yatra_route_id',
            YatraRouteName='yatra_route_id__yatraRoutename',
            YatraId='yatra_id',
            YatraDateTime='yatra_id__yatraDateTime',
            PaymentMode='payment_mode',
            YatraFees='yatra_id__yatraFees',
            YatraBusId='yatra_bus_id',
            BusName='yatra_bus_id__busName',
            Firstname='registration_id__firstname',
            Middlename='registration_id__middlename',
            Lastname='registration_id__lastname',
            MobileNo='registration_id__mobileNo',
            AlternateMobileNo='registration_id__alternateMobileNo',
            BloodGroup='registration_id__bloodGroup__bloodGroupName',
            Gender='registration_id__gender',
            PhotoFileName='registration_id__photoFileName'
        ).order_by('yatra_route_id', 'yatra_id', 'yatra_bus_id')

        if not tickets.exists():
            return Response({'message_code': 999, 'message_text': 'No Tickets', 'message_data': []}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'message_code': 1000, 'message_text': 'Agent Route, Yatra, Bus wise Tickets on Date', 'message_data': list(tickets)}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'message_code': 500, 'message_text': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



# def logout(request):
#     request.session.flush()  # clears all session data
#     messages.success(request, "You have successfully signed out")
#     return redirect('login')

# def dashboard(request):
#     return render(request, 'dashboard.html')
