import datetime
from django.db import IntegrityError, connection
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from admin_pannel.models import TblUsers, Registrations, Areas, ElectionManagement,TicketsNew, DiwaliKirana,BJPOffice

from django.db.models import Count, Max
from django.db.models.functions import TruncDate

from django.utils import timezone 
import os, uuid
from django.conf import settings


# ==========================================
# 1. AGENT LOGIN API
# ==========================================
@api_view(['POST'])
def agent_login_api(request):
    debug = []
    response_data = {
        "message_code": 999,
        "message_text": "An error occurred.",
        "message_data": {},
        "message_debug": debug
    }

    try:
        data = request.data
        mobile = data.get("mobile")
        pin = data.get("pin")

        # ===== 1️⃣ Required Fields Validation =====
        if not mobile or not pin:
            response_data["message_text"] = "Mobile number and PIN are required."
            return Response(response_data, status=status.HTTP_200_OK)

        # ===== 2️⃣ Fetch User =====
        # Check for matching Mobile, PIN and Active Status (1)
        user = TblUsers.objects.filter(
            UserMobileNo=mobile,
            UserLoginPin=pin,
            UserStatus=1
        ).first()

        if not user:
            response_data["message_text"] = "Invalid credentials or account inactive."
            return Response(response_data, status=status.HTTP_200_OK)

        # ===== 3️⃣ Success Response =====
        response_data["message_code"] = 1000
        response_data["message_text"] = "Login successful."
        response_data["message_data"] = {
            "UserId": user.UserId,
            "UserFirstname": user.UserFirstname,
            "UserLastname": user.UserLastname,
            "UserMobileNo": user.UserMobileNo,
            "UserRole": user.UserRole
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        debug.append(str(e))
        response_data["message_text"] = "Login failed due to server error."
        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_area_list(request):
    try:
        areas = Areas.objects.filter(AreaStatus=1).values_list('AreaName', flat=True).order_by('AreaName')
        return Response({"message_code": 1000, "data": list(areas)}, status=status.HTTP_200_OK)
    except:
        return Response({"message_code": 999, "data": []}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_registration_list(request):
    try:
        data = request.data
        
        # Filters
        selected_area = data.get('area')
        assembly_no = data.get('assembly')
        yadi_no = data.get('yadi')
        function_type = data.get('function_type')
        search_term = data.get('search')
        
        # Pagination
        try:
            limit = int(data.get('limit', 500))
            offset = int(data.get('offset', 0))
        except:
            limit = 500
            offset = 0

        # 1. Base Query
        queryset = Registrations.objects.select_related('areaId').prefetch_related('Election_RegistrationId').all().order_by('registrationId')

        # 2. Function Type Filter
        if function_type == 'darshan':
            darshan_ids = TicketsNew.objects.values_list('registration_id', flat=True)
            queryset = queryset.filter(registrationId__in=darshan_ids)
        elif function_type == 'diwali':
            diwali_ids = DiwaliKirana.objects.values_list('RegistrationId', flat=True)
            queryset = queryset.filter(registrationId__in=diwali_ids)

        # 3. Area Filter
        if selected_area and selected_area != "-- All Areas --" and selected_area != "":
            queryset = queryset.filter(areaId__AreaName=selected_area)

        # 4. Election Filters
        if assembly_no:
            queryset = queryset.filter(Election_RegistrationId__AssemblyNo=assembly_no)
        if yadi_no:
            queryset = queryset.filter(Election_RegistrationId__YadiNo=yadi_no)

        # 5. Search Filter (Optional - matches your screenshot search bar)
        if search_term:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(firstname__icontains=search_term) | 
                Q(mobileNo__icontains=search_term)
            )

        # 6. Count & Slice
        total_count = queryset.count() # This IS the filtered count (Area wise)
        records = queryset[offset : offset + limit]
        
        voter_list = []
        for r in records:
            area_name = r.areaId.AreaName if r.areaId else "-"

            # Get Election Data
            election_record = r.Election_RegistrationId.first()
            
            # --- VOTING CARD LOGIC FIX ---
            voting_card_no = "-"
            
            # 1. Try to get Number from Election Table
            if election_record and election_record.VotingCardNo:
                voting_card_no = election_record.VotingCardNo
            
            # 2. Identify Image URL
            voting_card_img = None
            raw_proof = str(r.voterIdProof) if r.voterIdProof else ""
            
            # If the proof looks like a URL/Path, save it as image, don't show as text
            if "http" in raw_proof or "/media/" in raw_proof or "/static/" in raw_proof or ".jpg" in raw_proof or ".png" in raw_proof:
                voting_card_img = raw_proof
            elif voting_card_no == "-" and raw_proof != "" and raw_proof != "None":
                # If it's NOT a URL, maybe it's the number stored in the wrong column?
                voting_card_no = raw_proof

            # Other Fields
            if election_record:
                assembly = election_record.AssemblyNo or "-"
                yadi = election_record.YadiNo or "-"
                booth = election_record.BoothAddress or "-"
            else:
                assembly = "-"
                yadi = "-"
                booth = "-"

            voter_list.append({
                "RegistrationId": r.registrationId,
                "Firstname": r.firstname,
                "Middlename": r.middlename,
                "Lastname": r.lastname,
                "MobileNo": r.mobileNo,
                "AlternateMobileNo": r.alternateMobileNo,
                "Address": r.address,
                "AreaName": area_name,
                "VotingCardNo": voting_card_no,   # The clean Number
                "VotingCardImg": voting_card_img, # The URL
                "AssemblyNo": assembly,
                "YadiNo": yadi,
                "BoothAddress": booth
            })

        return Response({
            "message_code": 1000, 
            "message_text": "Success",
            "message_data": voter_list,
            "total_count": total_count 
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message_code": 999, 
            "message_text": str(e), 
            "message_data": []
        }, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
def get_grid_data(request):
    try:
        # Params
        area_name = request.GET.get('area', '')
        search_term = request.GET.get('search', '')
        function_type = request.GET.get('function_type', '')
        
        try:
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
        except:
            limit = 50
            offset = 0

        # Base Query
        queryset = Registrations.objects.select_related('areaId').prefetch_related('Election_RegistrationId').all().order_by('registrationId')

        # Filters
        if function_type == 'darshan':
            darshan_ids = TicketsNew.objects.values_list('registration_id', flat=True)
            queryset = queryset.filter(registrationId__in=darshan_ids)
        elif function_type == 'diwali':
            diwali_ids = DiwaliKirana.objects.values_list('RegistrationId', flat=True)
            queryset = queryset.filter(registrationId__in=diwali_ids)

        if area_name and area_name != "-- All Areas --":
            queryset = queryset.filter(areaId__AreaName=area_name)

        if search_term:
            queryset = queryset.filter(
                Q(firstname__icontains=search_term) | 
                Q(middlename__icontains=search_term) | 
                Q(lastname__icontains=search_term) | 
                Q(mobileNo__icontains=search_term)
            )

        total_count = queryset.count()
        records = queryset[offset : offset + limit]

        data_list = []
        for r in records:
            election_record = r.Election_RegistrationId.first()
            
            # --- FIXED VOTING CARD LOGIC ---
            voting_card = ""

            # 1. Priority: Check Election Management Table
            if election_record and election_record.VotingCardNo:
                voting_card = election_record.VotingCardNo
            
            # 2. Fallback: Check Registrations Table (BUT Filter out Image URLs)
            elif r.voterIdProof:
                raw_proof = str(r.voterIdProof)
                # If it looks like an image or URL, DO NOT show it as the number
                is_url = any(x in raw_proof for x in ['http', 'https', '/media/', '/static/', '.jpg', '.png', '.jpeg', '.pdf'])
                
                if not is_url:
                    voting_card = raw_proof
            # -------------------------------

            # Other Fields
            if election_record:
                assembly = election_record.AssemblyNo or ""
                yadi = election_record.YadiNo or ""
                booth = election_record.BoothAddress or ""
                sr_no = election_record.SrNo or ""
            else:
                assembly = ""
                yadi = ""
                booth = ""
                sr_no = ""

            data_list.append({
                "RegistrationId": r.registrationId,
                "Firstname": r.firstname,
                "Middlename": r.middlename,
                "Lastname": r.lastname,
                "MobileNo": r.mobileNo,
                "VotingCardNo": voting_card, # Now sends Clean Number or Empty String
                "AssemblyNo": assembly,
                "YadiNo": yadi,
                "SrNo": sr_no,
                "BoothAddress": booth
            })

        return Response({
            "success": True,
            "data": data_list,
            "total_count": total_count
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_200_OK)


# --- 4. UPDATE GRID CELL API ---
@api_view(['POST'])
def update_grid_cell(request):
    try:
        data = request.data
        reg_id = data.get('id')
        field = data.get('field')
        value = data.get('value')

        if not reg_id or not field:
            return Response({"success": False, "error": "Missing ID or Field"}, status=status.HTTP_200_OK)

        # 1. Registration Fields
        reg_fields = ['Firstname', 'Middlename', 'Lastname', 'MobileNo']
        
        if field in reg_fields:
            field_map = {
                'Firstname': 'firstname',
                'Middlename': 'middlename',
                'Lastname': 'lastname',
                'MobileNo': 'mobileNo'
            }
            db_field = field_map.get(field)
            
            Registrations.objects.filter(registrationId=reg_id).update(**{db_field: value})
            return Response({"success": True}, status=status.HTTP_200_OK)

        # 2. Election Fields
        elec_fields = ['VotingCardNo', 'AssemblyNo', 'YadiNo', 'SrNo', 'BoothAddress']
        
        if field in elec_fields:
            # Check if record exists
            election_obj = ElectionManagement.objects.filter(RegistrationId=reg_id).first()
            
            if election_obj:
                # Update existing
                setattr(election_obj, field, value)
                election_obj.save()
            else:
                # Create new record linked to Registration
                reg_obj = Registrations.objects.get(registrationId=reg_id)
                new_record = ElectionManagement(RegistrationId=reg_obj)
                setattr(new_record, field, value)
                
                try:
                    new_record.save()
                except IntegrityError:
                    # --- AUTO FIX: Reset Sequence ---
                    # If ID 1 already exists, this command forces the DB to jump to the highest ID
                    with connection.cursor() as cursor:
                        # This SQL resets the sequence to MAX(ID)
                        sql = """
                            SELECT setval(
                                pg_get_serial_sequence('"tblElectionManagement"', 'ElectionId'), 
                                COALESCE((SELECT MAX("ElectionId") FROM "tblElectionManagement"), 1), 
                                true
                            );
                        """
                        cursor.execute(sql)
                    
                    # Retry Save after fix
                    new_record.save()
                
            return Response({"success": True}, status=status.HTTP_200_OK)

        return Response({"success": False, "error": "Invalid Field"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_200_OK)





# --- 5. GET EXCEL DATA API (Bulk Load) ---
@api_view(['GET'])
def get_excel_data(request):
    try:
        # 1. Pagination Params
        try:
            limit = int(request.GET.get('limit', 100)) 
            offset = int(request.GET.get('offset', 0))
        except:
            limit = 100
            offset = 0
        
        # 2. Filter Params
        search_term = request.GET.get('search', '')
        function_type = request.GET.get('function_type', '')
        voting_card_status = request.GET.get('voting_card_status', '') # 'with' or 'without'

        # 3. Base Query
        queryset = Registrations.objects.select_related('areaId').prefetch_related('Election_RegistrationId').all().order_by('registrationId')

        # 4. Apply Filters
        
        # Function Type
        if function_type == 'darshan':
            darshan_ids = TicketsNew.objects.values_list('registration_id', flat=True)
            queryset = queryset.filter(registrationId__in=darshan_ids)
        elif function_type == 'diwali':
            diwali_ids = DiwaliKirana.objects.values_list('RegistrationId', flat=True)
            queryset = queryset.filter(registrationId__in=diwali_ids)

        # Search
        if search_term:
            queryset = queryset.filter(
                Q(firstname__icontains=search_term) | 
                Q(middlename__icontains=search_term) | 
                Q(lastname__icontains=search_term) | 
                Q(mobileNo__icontains=search_term)
            )

        # Voting Card Filter (New)
        if voting_card_status == 'with':
            # Has entry in Election table AND it's not empty
            queryset = queryset.filter(Election_RegistrationId__VotingCardNo__isnull=False).exclude(Election_RegistrationId__VotingCardNo='')
        elif voting_card_status == 'without':
            # No entry OR entry is empty
            queryset = queryset.filter(Q(Election_RegistrationId__isnull=True) | Q(Election_RegistrationId__VotingCardNo=''))

        # 5. Count & Slice
        total_count = queryset.count()
        records = queryset[offset : offset + limit]
        
        data_list = []
        for r in records:
            election = r.Election_RegistrationId.first()
            
            # Voting Card Display Logic (Hide URLs)
            voting_card = ""
            if election and election.VotingCardNo:
                voting_card = election.VotingCardNo
            elif r.voterIdProof:
                raw_proof = str(r.voterIdProof)
                is_url = any(x in raw_proof for x in ['http', '/media/', '/static/', '.jpg', '.png'])
                if not is_url:
                    voting_card = raw_proof

            data_list.append({
                "RegistrationId": r.registrationId,
                "Firstname": r.firstname,
                "Middlename": r.middlename,
                "Lastname": r.lastname,
                "MobileNo": r.mobileNo,
                "AlternateMobileNo": r.alternateMobileNo,
                "BloodGroup": r.bloodGroup.bloodGroupName if r.bloodGroup else None,
                "DateOfBirth": r.dateOfBirth,
                "Age": r.age,
                "Gender": "Male" if r.gender == 2 else "Female" if r.gender == 1 else "Other",
                "AadharNumber": r.aadharNumber,
                "AreaName": r.areaId.AreaName if r.areaId else "",
                "Address": r.address,
                "PhotoFileName": r.photoFileName,
                "IdProofFileName": r.idProofFileName,
                "VoterIdProof": r.voterIdProof,
                "DateOfRegistration": r.dateOfRegistration,
                "PermanantId": r.permanentId,
                "RationCardPhoto": r.ration_card_photo,
                "ParentId": r.parent_id,
                
                # Editable Fields
                "VotingCardNo": voting_card,
                "BoothAddress": election.BoothAddress if election else "",
                "AssemblyNo": election.AssemblyNo if election else "",
                "YadiNo": election.YadiNo if election else "",
                "SrNo": election.SrNo if election else ""
            })

        return Response({
            "message_code": 1000, 
            "data": data_list,
            "total_count": total_count
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)}, status=status.HTTP_200_OK)


# --- 6. SAVE EXCEL DATA API (Bulk Save) ---
@api_view(['POST'])
def save_excel_data(request):
    try:
        data_list = request.data
        updated_count = 0
        inserted_count = 0

        # Helper to convert "" to None for Integers
        def clean_int(val):
            if val is None or str(val).strip() == "":
                return None
            try:
                return int(val)
            except ValueError:
                return None # Or handle error

        for row in data_list:
            reg_id = row.get('RegistrationId')
            
            # --- Prepare Registration Data ---
            reg_fields = {
                'firstname': row.get('Firstname'),
                'middlename': row.get('Middlename'),
                'lastname': row.get('Lastname'),
                'mobileNo': row.get('MobileNo'),
                'alternateMobileNo': row.get('AlternateMobileNo'),
                'address': row.get('Address'),
                'age': clean_int(row.get('Age')) # Clean Age
            }

            area_name = row.get('AreaName')
            if area_name:
                area_obj = Areas.objects.filter(AreaName=area_name).first()
                if area_obj:
                    reg_fields['areaId'] = area_obj
            # -----------------------------------

            reg_fields = {k: v for k, v in reg_fields.items() if v is not None}

            # --- Prepare Election Data (Clean Integers Here) ---
            election_fields = {
                'VotingCardNo': row.get('VotingCardNo'),
                'AssemblyNo': row.get('AssemblyNo'), # Usually string, but if model expects int, clean it
                'YadiNo': row.get('YadiNo'),         # Usually string, but if model expects int, clean it
                'SrNo': clean_int(row.get('SrNo')),  # <--- FIX: Clean SrNo
                'BoothAddress': row.get('BoothAddress')
            }
            # Remove keys with None values so we don't overwrite existing data with NULL unintentionally
            # (Unless you want to allow clearing fields, then keep None)
            election_fields = {k: v for k, v in election_fields.items() if v is not None}

            # --- UPDATE ---
            if reg_id:
                # 1. Update Registration
                if reg_fields:
                    Registrations.objects.filter(registrationId=reg_id).update(**reg_fields)
                
                # 2. Update Election
                if election_fields:
                    try:
                        ElectionManagement.objects.update_or_create(
                            RegistrationId_id=reg_id,
                            defaults=election_fields
                        )
                    except IntegrityError:
                        # Auto-Fix Sequence
                        with connection.cursor() as cursor:
                            sql = "SELECT setval(pg_get_serial_sequence('\"tblElectionManagement\"', 'ElectionId'), COALESCE((SELECT MAX(\"ElectionId\") FROM \"tblElectionManagement\"), 1), true);"
                            cursor.execute(sql)
                        # Retry
                        ElectionManagement.objects.update_or_create(
                            RegistrationId_id=reg_id,
                            defaults=election_fields
                        )
                
                updated_count += 1

            # --- INSERT ---
            else:
                if not reg_fields.get('firstname'): continue
                
                new_reg = Registrations.objects.create(**reg_fields)
                
                new_election = ElectionManagement(
                    RegistrationId=new_reg,
                    VotingCardNo=row.get('VotingCardNo'),
                    AssemblyNo=row.get('AssemblyNo'),
                    YadiNo=row.get('YadiNo'),
                    SrNo=clean_int(row.get('SrNo')), # <--- FIX HERE TOO
                    BoothAddress=row.get('BoothAddress')
                )
                
                try:
                    new_election.save()
                except IntegrityError:
                    with connection.cursor() as cursor:
                        sql = "SELECT setval(pg_get_serial_sequence('\"tblElectionManagement\"', 'ElectionId'), COALESCE((SELECT MAX(\"ElectionId\") FROM \"tblElectionManagement\"), 1), true);"
                        cursor.execute(sql)
                    new_election.save()
                
                inserted_count += 1

        return Response({
            "message_code": 1000, 
            "message_text": f"Saved! Updated: {updated_count}, Added: {inserted_count}"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)}, status=status.HTTP_200_OK)




# --- 7. GET TELECALLING DATA API ---
@api_view(['POST'])
def get_telecalling_data(request):
    try:
        data = request.data
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        
        area = data.get('area')
        function_type = data.get('function_type')
        search = data.get('search')

        # Base Query: Must have Mobile Number
        queryset = Registrations.objects.select_related('areaId').prefetch_related('Election_RegistrationId').filter(mobileNo__isnull=False).exclude(mobileNo='')

        # Filters
        if function_type == 'darshan':
            darshan_ids = TicketsNew.objects.values_list('registration_id', flat=True)
            queryset = queryset.filter(registrationId__in=darshan_ids)
        elif function_type == 'diwali':
            diwali_ids = DiwaliKirana.objects.values_list('RegistrationId', flat=True)
            queryset = queryset.filter(registrationId__in=diwali_ids)

        if area and area != "-- All Areas --":
            queryset = queryset.filter(areaId__AreaName=area)

        if search:
            queryset = queryset.filter(
                Q(firstname__icontains=search) | 
                Q(mobileNo__icontains=search)
            )

        total_count = queryset.count()
        records = queryset[offset : offset + limit]

        data_list = []
        for r in records:
            election = r.Election_RegistrationId.first()
            
            # Defaults
            call_status = 0
            caller_name = None
            voting_card = "-"

            if election:
                call_status = election.CallStatus
                caller_name = election.CallerName
                voting_card = election.VotingCardNo or "-"
            
            # Fallback for Voting Card if missing in Election table
            if voting_card == "-" and r.voterIdProof:
                 if not any(x in str(r.voterIdProof) for x in ['http', '.jpg', '.png']):
                     voting_card = r.voterIdProof

            data_list.append({
                "RegistrationId": r.registrationId,
                "Firstname": r.firstname,
                "Middlename": r.middlename,
                "Lastname": r.lastname,
                "MobileNo": r.mobileNo,
                "AlternateMobileNo": r.alternateMobileNo,
                "AreaName": r.areaId.AreaName if r.areaId else "",
                "VotingCardNo": voting_card,
                "CallStatus": call_status,
                "CallerName": caller_name
            })

        return Response({
            "message_code": 1000, 
            "data": data_list,
            "total_count": total_count
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)}, status=status.HTTP_200_OK)


# --- 8. UPDATE CALL STATUS API ---
from django.utils import timezone  # <--- Make sure to import this at top

@api_view(['POST'])
def update_call_status(request):
    debug_msg = ""
    try:
        data = request.data
        
        # 1. Clean Inputs
        reg_id = data.get('id')
        if reg_id: 
            reg_id = int(reg_id)
        else:
            return Response({"message_code": 999, "message_text": "Missing Registration ID"}, status=status.HTTP_200_OK)

        status_val = int(data.get('status')) # 1 or 0
        
        # 2. Handle Caller ID Safely
        caller_id = data.get('caller_id')
        if caller_id and str(caller_id).lower() != 'none':
            try:
                caller_id = int(caller_id)
            except:
                caller_id = None
        else:
            caller_id = None
            
        caller_name = data.get('caller_name')

        # 3. Robust Database Logic
        # Instead of update_or_create (which crashes on duplicates), we use filter + first
        election_obj = ElectionManagement.objects.filter(RegistrationId_id=reg_id).first()

        if election_obj:
            # --- UPDATE EXISTING RECORD ---
            election_obj.CallStatus = status_val
            
            if status_val == 1:
                election_obj.CallerId_id = caller_id
                election_obj.CallerName = caller_name
                election_obj.CallTimestamp = timezone.now()
            else:
                # If unchecking, clear the caller info
                election_obj.CallerId_id = None
                election_obj.CallerName = None
                election_obj.CallTimestamp = None
            
            election_obj.save()
            debug_msg = "Updated existing record"

        else:
            # --- CREATE NEW RECORD ---
            new_record = ElectionManagement(
                RegistrationId_id=reg_id,
                CallStatus=status_val,
                CallerId_id=caller_id if status_val == 1 else None,
                CallerName=caller_name if status_val == 1 else None,
                CallTimestamp=timezone.now() if status_val == 1 else None
            )
            new_record.save()
            debug_msg = "Created new record"

        return Response({
            "message_code": 1000, 
            "message_text": "Success",
            "debug": debug_msg
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("Update Call Error:", str(e)) # Print error to your terminal for debugging
        return Response({
            "message_code": 999, 
            "message_text": f"Error: {str(e)}"
        }, status=status.HTTP_200_OK) 




@api_view(['GET'])
def get_telecalling_report(request):
    try:
        # --- PART 1: TELECALLING STATS ---
        
        # 1. User Summary
        user_qs = ElectionManagement.objects.filter(CallStatus=1, CallerName__isnull=False) \
            .values('CallerName') \
            .annotate(TotalCalls=Count('ElectionId'), LastCallTime=Max('CallTimestamp')) \
            .order_by('-TotalCalls')
            
        # Convert QuerySet to List to modify data
        user_summary = list(user_qs)
        
        # FIX 1: Format 'LastCallTime' for User Summary
        for item in user_summary:
            if item['LastCallTime']:
                # Example: 04 Feb, 10:30 AM
                item['LastCallTime'] = item['LastCallTime'].strftime('%d %b, %I:%M %p')
            else:
                item['LastCallTime'] = "-"

        # 2. Date-wise + Caller-wise Summary
        date_qs = ElectionManagement.objects.filter(
            CallStatus=1,
            CallTimestamp__isnull=False,
            CallerName__isnull=False
        ).annotate(
            CallDate=TruncDate('CallTimestamp')
        ).values(
            'CallDate', 'CallerName'
        ).annotate(
            DailyCount=Count('ElectionId')
        ).order_by('-CallDate', '-DailyCount')

        date_summary = list(date_qs)

        # Format CallDate (string)
        for item in date_summary:
            item['CallDate'] = item['CallDate'].strftime('%d %b %Y') if item['CallDate'] else "-"



        # --- PART 2: VOTING STATS ---
        
        # 3. Area-wise Voting Summary
        voting_summary = list(Registrations.objects.values('areaId__AreaName') \
            .annotate(
                TotalVoters=Count('registrationId'),
                VotedCount=Count('Election_RegistrationId', filter=Q(Election_RegistrationId__VotingStatus=1))
            ) \
            .order_by('areaId__AreaName'))

        return Response({
            "message_code": 1000, 
            "data": {
                "user_summary": user_summary,
                "date_summary": date_summary,
                "voting_summary": voting_summary
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)}, status=status.HTTP_200_OK)
    




# --- 10. GET VOTER CALLING DATA (Election Day) ---
@api_view(['POST'])
def get_voter_calling_data(request):
    try:
        data = request.data
        limit = int(data.get('limit', 50))
        offset = int(data.get('offset', 0))
        search = data.get('search', '').strip()

        # Base Query
        queryset = Registrations.objects.select_related('areaId').prefetch_related('Election_RegistrationId').all().order_by('registrationId')

        # Filter Logic (Jump vs Search)
        if search:
            if search.isdigit() and len(search) < 8:
                # "Jump" Logic: Start from this ID
                queryset = queryset.filter(registrationId__gte=search)
            else:
                # Standard Search
                queryset = queryset.filter(
                    Q(firstname__icontains=search) | 
                    Q(middlename__icontains=search) | 
                    Q(lastname__icontains=search) | 
                    Q(mobileNo__icontains=search)
                )

        # Calculate Stats (Before Slicing)
        # Note: We need to filter ElectionManagement related to these Registrations
        # This is a bit complex with reverse relation, so we do a simplified count
        # Or fetch all IDs and query Election table
        
        # Simple Stats (Global or Filtered)
        total_count = queryset.count()
        
        # Fetch Data
        records = queryset[offset : offset + limit]
        
        voter_list = []
        for r in records:
            election = r.Election_RegistrationId.first()
            
            # Defaults
            call_status = 0
            voting_status = 0
            voting_card = "-"
            assm = "-"
            yadi = "-"
            booth = "-"

            if election:
                call_status = election.CallStatus
                voting_status = election.VotingStatus
                voting_card = election.VotingCardNo or "-"
                assm = election.AssemblyNo or "-"
                yadi = election.YadiNo or "-"
                booth = election.BoothAddress or "-"
            
            if voting_card == "-" and r.voterIdProof and not any(x in str(r.voterIdProof) for x in ['http', '.jpg']):
                voting_card = r.voterIdProof

            voter_list.append({
                "RegistrationId": r.registrationId,
                "Firstname": r.firstname,
                "Middlename": r.middlename,
                "Lastname": r.lastname,
                "MobileNo": r.mobileNo,
                "AreaName": r.areaId.AreaName if r.areaId else "",
                "VotingCardNo": voting_card,
                "AssemblyNo": assm,
                "YadiNo": yadi,
                "BoothAddress": booth,
                "CallStatus": call_status,
                "VotingStatus": voting_status
            })

        return Response({
            "message_code": 1000, 
            "data": voter_list,
            "total_count": total_count,
            # You might want separate API for stats if performance is slow
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)}, status=status.HTTP_200_OK)


# --- 11. UPDATE VOTING STATUS ---
@api_view(['POST'])
def update_voting_status(request):
    try:
        data = request.data
        reg_id = data.get('id')
        status_val = int(data.get('status')) # 1=Voted, 0=Not
        
        # Update or Create
        obj, created = ElectionManagement.objects.update_or_create(
            RegistrationId_id=reg_id,
            defaults={'VotingStatus': status_val}
        )
        return Response({"message_code": 1000, "message_text": "Updated"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)}, status=status.HTTP_200_OK)    
    






    ############  BJP Office Managment ##########


@api_view(["POST"])
def office_search_voter(request):
    # Get inputs (Frontend sends the same value in both fields)
    mobile = (request.data.get("mobile") or "").strip()
    name = (request.data.get("name") or "").strip()

    qs = Registrations.objects.all()

    # LOGIC FIX: Use Q objects to perform an 'OR' search.
    # This checks if the query matches the Mobile OR the Name.
    if mobile or name:
        query = Q()
        
        if mobile:
            query |= Q(mobileNo__icontains=mobile)
            query |= Q(alternateMobileNo__icontains=mobile)
        
        if name:
            query |= Q(firstname__icontains=name)
            query |= Q(middlename__icontains=name)
            query |= Q(lastname__icontains=name)
            
        qs = qs.filter(query)

    data = []
    # Fetch results (limit to 25 to prevent overload)
    for r in qs.order_by("-registrationId")[:25]:
        data.append({
            "RegistrationId": r.registrationId,
            "Firstname": r.firstname,
            "Middlename": r.middlename,
            "Lastname": r.lastname,
            "MobileNo": r.mobileNo,
            "AlternateMobileNo": r.alternateMobileNo,
            "Address": r.address,
            # Use getattr to safely get the Foreign Key ID without an extra DB call
            "AreaId": getattr(r, "areaId_id", None), 
            "AadharNumber": r.aadharNumber,
            "DateOfBirth": str(r.dateOfBirth) if r.dateOfBirth else None,
            "VoterID_No": r.voterIdProof if hasattr(r, 'voterIdProof') else "",
        })

    return Response({
        "message_code": 1000,
        "message_text": "Success",
        "message_data": data
    })



@api_view(["POST"])
def office_create_record(request):
    try:
        data = request.data
        user_id = data.get("caller_id")
        
        reg_id = data.get("RegistrationId") # If ID exists, we update. If NULL, we create NEW.
        
        v_name = data.get("voter_name", "").strip()
        v_mobile = data.get("voter_mobile", "").strip()
        v_area = data.get("area_text", "").strip()
        v_address = data.get("address_text", "").strip()
        v_aadhar = data.get("aadhar", "").strip()
        v_voter_id = data.get("voter_id", "").strip()
        v_docs = data.get("documents", "").strip() 

        # Find Area Object
        area_obj = None
        if v_area:
            area_obj = Areas.objects.filter(AreaName=v_area).first()

        reg_obj = None

        if reg_id:
            # --- SCENARIO A: UPDATE EXISTING FAMILY MEMBER ---
            reg_obj = Registrations.objects.filter(registrationId=reg_id).first()
            if reg_obj:
                is_changed = False
                if v_address and reg_obj.address != v_address:
                    reg_obj.address = v_address; is_changed = True
                if v_aadhar and reg_obj.aadharNumber != v_aadhar:
                    reg_obj.aadharNumber = v_aadhar; is_changed = True
                if v_voter_id and getattr(reg_obj, 'voterIdProof', '') != v_voter_id:
                    reg_obj.voterIdProof = v_voter_id; is_changed = True
                if area_obj and not reg_obj.areaId:
                    reg_obj.areaId = area_obj; is_changed = True
                
                if is_changed: reg_obj.save()

        else:
            # --- SCENARIO B: CREATE NEW FAMILY MEMBER ---
            # We do NOT check for duplicate mobile here. 
            # We allow multiple people with same mobile.
            reg_obj = Registrations.objects.create(
                firstname=v_name,
                mobileNo=v_mobile,
                address=v_address,
                aadharNumber=v_aadhar,
                voterIdProof=v_voter_id,
                areaId=area_obj,
                created_by_id=user_id
            )

        # --- CREATE OFFICE RECORD ---
        notes = data.get("description", "")
        if v_docs: notes = f"{notes} (Docs: {v_docs})"

        obj = BJPOffice.objects.create(
            registration=reg_obj,
            voter_name=v_name,
            voter_mobile=v_mobile,
            record_type=data.get("record_type", "ComplaintRegistration"),
            complaint_category=data.get("complaint_category", "Other"),
            complaint_type=data.get("complaint_type", ""),
            description=notes,
            priority=data.get("priority", "Normal"),
            status="Open",
            handled_by_id=user_id,
            handled_by_name=data.get("caller_name"),
            area_text=v_area,
            address_text=v_address,
            followup_date=data.get("followup_date") or None,
            missing_info_notes=v_docs
        )

        return Response({
            "message_code": 1000,
            "message_text": "Saved Successfully",
            "message_data": {"bjp_office_id": obj.bjp_office_id, "RegistrationId": reg_obj.registrationId}
        })

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)})

def abs_url(request, url):
    if not url:
        return None
    u = str(url).strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    return request.build_absolute_uri(u)  # handles /static/... or /media/...



@api_view(["POST"])
def office_record_list(request):
    # Fix: Ensure we catch mobile numbers properly
    status_val = request.data.get("status", "")
    category = request.data.get("complaint_category", "")
    mobile = request.data.get("mobile", "")

    qs = BJPOffice.objects.all().order_by("-created_on")

    if status_val:
        qs = qs.filter(status=status_val)
    if category:
        qs = qs.filter(complaint_category__icontains=category)
    if mobile:
        # Filter by the mobile number stored in the office record OR the linked registration
        qs = qs.filter(Q(voter_mobile__icontains=mobile) | Q(registration__mobileNo__icontains=mobile))

    data = []
    for x in qs[:100]: # Limit 100 for speed
        data.append({
            "bjp_office_id": x.bjp_office_id,
            "voter_name": x.voter_name,
            "voter_mobile": x.voter_mobile,
            "complaint_category": x.complaint_category,
            "complaint_type": x.complaint_type,
            "description": x.description,
            "priority": x.priority,
            "status": x.status,
            "created_on": x.created_on,
            "personal_aadhar_url": abs_url(request, getattr(x, "personal_aadhar_url", None)),
            "personal_voting_url": abs_url(request, getattr(x, "personal_voting_url", None)),
            "personal_ration_url": abs_url(request, getattr(x, "personal_ration_url", None)),

            # ✅ COMPLAINT PHOTOS (ADD THESE)
            "complaint_photo1_url": abs_url(request, getattr(x, "complaint_photo1_url", None)),
            "complaint_photo2_url": abs_url(request, getattr(x, "complaint_photo2_url", None)),
            "complaint_photo3_url": abs_url(request, getattr(x, "complaint_photo3_url", None)),
        })

    return Response({"message_code": 1000, "message_text": "Success", "message_data": data})



@api_view(['GET'])
def get_area_list(request):
    try:
        # Fetch active areas, order by name
        areas = Areas.objects.filter(AreaStatus=1).values('AreaId', 'AreaName').order_by('AreaName')
        return Response({"message_code": 1000, "data": list(areas)})
    except Exception as e:
        return Response({"message_code": 999, "data": []})
    



@api_view(["POST"])
def office_update_record(request):
    try:
        data = request.data
        record_id = data.get("bjp_office_id")
        new_status = data.get("status")
        followup_note = data.get("followup_note")
        
        obj = BJPOffice.objects.filter(bjp_office_id=record_id).first()
        if not obj:
            return Response({"message_code": 999, "message_text": "Record not found"})
        
        # Update Status
        if new_status:
            obj.status = new_status
            if new_status == 'Resolved':
                obj.resolved_date = timezone.now().date()
        
        # Append Note
        if followup_note:
            current_desc = obj.description or ""
            timestamp = timezone.now().strftime("%d-%m-%Y")
            # Append new note clearly
            obj.description = f"{current_desc}\n\n[Update {timestamp}]: {followup_note}"

        obj.save()

        return Response({"message_code": 1000, "message_text": "Updated Successfully"})
    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e)})    
    






def _save_to_static_and_get_url(file_obj, subdir):
    """
    Saves uploaded file into: BASE_DIR/static/uploads/<subdir>/
    Returns the STATIC_URL link saved in DB.
    """
    if not file_obj:
        return None

    ext = os.path.splitext(file_obj.name)[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    # Physical folder inside your project
    base_static_dir = os.path.join(settings.BASE_DIR, "staticfiles")
    upload_dir = os.path.join(base_static_dir, "uploads", "office_docs", subdir)
    os.makedirs(upload_dir, exist_ok=True)

    full_path = os.path.join(upload_dir, filename)

    with open(full_path, "wb+") as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    # URL to store in DB (served by frontend/static)
    url = f"{settings.STATIC_URL}uploads/office_docs/{subdir}/{filename}"
    return url


@api_view(["POST"])
def office_upload_docs(request):
    """
    multipart/form-data upload
    - Personal docs: aadhar_img, voting_img, ration_img
    - Complaint photos: complaint_img_1, complaint_img_2, complaint_img_3
    Must send at least one identifier:
      - bjp_office_id (recommended for complaint photos)
      - or RegistrationId (for personal docs)
    """
    try:
        bjp_office_id = request.data.get("bjp_office_id")
        reg_id = request.data.get("RegistrationId")

        obj = None

        if bjp_office_id:
            obj = BJPOffice.objects.filter(bjp_office_id=bjp_office_id).first()

        if not obj and reg_id:
            # If office record id not given, attach to latest record of that registration
            obj = BJPOffice.objects.filter(registration__registrationId=reg_id).order_by("-created_on").first()

        if not obj:
            return Response({"message_code": 999, "message_text": "Record not found for upload", "message_data": []})

        # ---- Personal Docs ----
        aadhar_file = request.FILES.get("aadhar_img")
        voting_file = request.FILES.get("voting_img")
        ration_file = request.FILES.get("ration_img")

        if aadhar_file:
            obj.personal_aadhar_url = _save_to_static_and_get_url(aadhar_file, "personal/aadhar")
        if voting_file:
            obj.personal_voting_url = _save_to_static_and_get_url(voting_file, "personal/voting")
        if ration_file:
            obj.personal_ration_url = _save_to_static_and_get_url(ration_file, "personal/ration")

        # ---- Complaint Photos ----
        c1 = request.FILES.get("complaint_img_1")
        c2 = request.FILES.get("complaint_img_2")
        c3 = request.FILES.get("complaint_img_3")

        if c1:
            obj.complaint_photo1_url = _save_to_static_and_get_url(c1, "complaints/1")
        if c2:
            obj.complaint_photo2_url = _save_to_static_and_get_url(c2, "complaints/2")
        if c3:
            obj.complaint_photo3_url = _save_to_static_and_get_url(c3, "complaints/3")

        obj.save()

        return Response({
            "message_code": 1000,
            "message_text": "Docs Uploaded Successfully",
            "message_data": {
                "bjp_office_id": obj.bjp_office_id,
                "personal_aadhar_url": obj.personal_aadhar_url,
                "personal_voting_url": obj.personal_voting_url,
                "personal_ration_url": obj.personal_ration_url,
                "complaint_photo1_url": obj.complaint_photo1_url,
                "complaint_photo2_url": obj.complaint_photo2_url,
                "complaint_photo3_url": obj.complaint_photo3_url,
            }
        })

    except Exception as e:
        return Response({"message_code": 999, "message_text": str(e), "message_data": []})
