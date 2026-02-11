import json
import os
from pyexpat.errors import messages
import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
import requests 
from django.contrib import messages

from typing import Optional, Tuple
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from .models import BJPOffice, SMSMaster, SMSTransaction



def login_view(request):
    if 'user_id' in request.session:
        return redirect('Index')
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        api_url = "https://kukudku.in/LakshyaPratishthan/api/agentlogin/"
        payload = {"userMobileNo": mobile, "userPassword": password}
        error_message = None
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('message_code') == 1000 and data.get('message_data'):
                user_info = data['message_data'][0]
                request.session['user_id'] = user_info.get('UserId')
                request.session['user_name'] = user_info.get('UserFirstname')
                return redirect('Index')
            else:
                error_message = data.get('message_text', 'An unknown error occurred.')
        except requests.exceptions.RequestException as e:
            error_message = f"Could not connect to the login service. Please try again later."
        return render(request, 'login.html', {'error': error_message})
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')  


def Index(request):

    return render(request, 'index.html', context={})



def diwali_kirana_list(request):
    """
    Fetches data and sorts it by family before passing it to the template.
    """
    api_url = "https://kukudku.in/LakshyaPratishthan/api/list_all_registrations/"
    error_message = None
    sorted_registrations = []

    try:
        response = requests.post(api_url)
        response.raise_for_status()
        api_response = response.json()
        
        all_registrations = api_response.get('message_data', [])

        if all_registrations:
            family_groups = {}
            for reg in all_registrations:
                rc_no = reg.get('RationCardNo')
                if rc_no not in family_groups:
                    family_groups[rc_no] = []
                family_groups[rc_no].append(reg)
            
            for rc_no, members in family_groups.items():
                head = None
                other_members = []
                for member in members:
                    if member.get('ParentId') == 1:
                        head = member
                    else:
                        other_members.append(member)
                if head:
                    sorted_registrations.append(head)
                sorted_registrations.extend(other_members)

    except requests.exceptions.RequestException as e:
        error_message = f"Could not fetch data from API: {e}"
    except ValueError:
        error_message = "Error: Invalid JSON response from API."

    final_data_with_sr_no = []
    for i, reg in enumerate(sorted_registrations):
        reg['sr_no'] = i + 1  # Add the 'sr_no' key starting from 1
        final_data_with_sr_no.append(reg)

    context = {
        'registrations_json': json.dumps(final_data_with_sr_no),
        'error_message': error_message,
    }
    return render(request, 'diwali_kirana/diwali_kirana.html', context)



def proxy_bulk_update_view(request):
    """
    This view receives the grid data from the browser,
    forwards it to the backend API, and returns the API's response.
    """
    try:
        # 1. Get the data sent from the browser's fetch call
        data_from_frontend = json.loads(request.body)
        
        # 2. Define the actual backend API endpoint
        backend_api_url = "https://kukudku.in/LakshyaPratishthan/api/bulk_update_diwali_kirana/"

        # 3. Make the server-to-server request to the backend API
        response = requests.post(backend_api_url, json=data_from_frontend)
        
        # 4. Check for errors from the API
        response.raise_for_status() # This will raise an exception for 4xx or 5xx status codes

        # 5. Return the backend API's successful JSON response directly to the browser
        return JsonResponse(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        # Handle network errors (e.g., backend is down)
        return JsonResponse({'message_code': 999, 'message_text': f'Network error calling backend API: {e}'}, status=503)
    except json.JSONDecodeError:
        # Handle cases where the browser sends invalid JSON
        return JsonResponse({'message_code': 999, 'message_text': 'Invalid JSON data received.'}, status=400)
    except Exception as e:
        # Handle other unexpected errors
        return JsonResponse({'message_code': 999, 'message_text': f'An internal error occurred: {e}'}, status=500)


# NEW PROXY VIEW for Adding a Member

def proxy_add_member_view(request):
    """
    This view receives the new member data from the browser,
    forwards it to the backend API, and returns the API's response.
    """
    try:
        data_from_frontend = json.loads(request.body)
        backend_api_url = "https://kukudku.in/LakshyaPratishthan/api/add_diwali_family_member/"
        
        response = requests.post(backend_api_url, json=data_from_frontend)
        response.raise_for_status()

        return JsonResponse(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'message_code': 999, 'message_text': f'Network error calling backend API: {e}'}, status=503)
    except json.JSONDecodeError:
        return JsonResponse({'message_code': 999, 'message_text': 'Invalid JSON data received.'}, status=400)
    except Exception as e:
        return JsonResponse({'message_code': 999, 'message_text': f'An internal error occurred: {e}'}, status=500)
    


def proxy_upload_voter_id_view(request):
    """
    This proxy view handles multipart/form-data uploads.
    It forwards the file and data to the backend API.
    """
    try:
        backend_api_url = "https://kukudku.in/LakshyaPratishthan/api/upload_voter_id/"
        
        # The 'requests' library can intelligently forward multipart data
        # by passing the 'files' and 'data' parameters.
        response = requests.post(
            backend_api_url,
            data=request.POST, # Forwards form fields like 'registration_id'
            files=request.FILES # Forwards the uploaded file
        )
        response.raise_for_status()
        return JsonResponse(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'message_code': 999, 'message_text': f'Network error calling backend API: {e}'}, status=503)
    except Exception as e:
        return JsonResponse({'message_code': 999, 'message_text': f'An internal error occurred: {e}'}, status=500)    
    

def proxy_delete_member_view(request, reg_id):
    """
    This proxy view forwards a delete request for a specific registration ID
    to the main backend API.
    """
    if request.method != 'POST':
        return JsonResponse({'message_code': 999, 'message_text': 'Invalid request method.'}, status=405)

    try:
        # Construct the URL for the actual backend API endpoint
        backend_api_url = f"https://kukudku.in/LakshyaPratishthan/api/delete_diwali_member/{reg_id}/"
        
        # Make the server-to-server POST request
        response = requests.post(backend_api_url)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Return the backend API's response to the browser
        return JsonResponse(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'message_code': 999, 'message_text': f'Network error calling backend API: {e}'}, status=503)
    except Exception as e:
        return JsonResponse({'message_code': 999, 'message_text': f'An internal error occurred: {e}'}, status=500)
    



from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse
from .models import BJPOffice # Make sure the import matches your app name
from django.utils import timezone

# def complaint_dashboard(request):
#     # 1. Get Filters from the URL
#     status_filter = request.GET.get('status', '').strip()
#     search_filter = request.GET.get('mobile', '').strip()

#     # 2. Fetch all non-deleted records
#     complaints_qs = BJPOffice.objects.filter(is_deleted=False).order_by('-created_on')

#     # 3. Apply Filters if they exist
#     if status_filter:
#         complaints_qs = complaints_qs.filter(status=status_filter)
    
#     if search_filter:
#         complaints_qs = complaints_qs.filter(
#             Q(voter_mobile__icontains=search_filter) | 
#             Q(voter_name__icontains=search_filter)
#         )

#     # 4. Calculate Stats for the top card
#     resolved_count = BJPOffice.objects.filter(status='Resolved', is_deleted=False).count()

#     context = {
#         'complaints': complaints_qs,
#         'resolved_count': resolved_count,
#     }
#     return render(request, 'Office_managment/complaint_mgmt.html', context)

# import requests # Make sure requests is imported at the top

# def send_whatsapp_status(mobile, voter_name, category, note):
#     """
#     Helper to send WhatsApp. 
#     Update the API_URL and TOKEN with your provider (UltraMsg/Twilio/Wati)
#     """
#     api_url = "https://api.ultramsg.com/your_instance/messages/chat"
#     token = "your_token_here"
    
#     # Professional message template
#     message = (
#         f"✅ *Task Completed*\n\n"
#         f"Namaste *{voter_name}*,\n"
#         f"Your request regarding *{category}* has been resolved.\n\n"
#         f"📝 *Resolution:* {note}\n\n"
#         f"Regards,\n*Lakshya Pratishthan Office*"
#     )
    
#     payload = {
#         "token": token,
#         "to": mobile,
#         "body": message
#     }
#     # requests.post(api_url, data=payload) # Uncomment when you have API keys
#     print(f"DEBUG WHATSAPP: Sending to {mobile}")

# def update_complaint_direct(request):
#     if request.method == 'POST':
#         import json
#         data = json.loads(request.body)
#         obj_id = data.get('id')
#         new_status = data.get('status')
#         note = data.get('note', '')

#         try:
#             obj = BJPOffice.objects.get(bjp_office_id=obj_id)
#             old_status = obj.status
#             obj.status = new_status
            
#             # Format history with professional timeline markers
#             timestamp = timezone.now().strftime("%d %b %Y, %I:%M %p")
#             user_name = request.session.get('user_name', 'Admin')
            
#             new_history_entry = f"|{timestamp}|{user_name}|{new_status}|{note}"
            
#             # We store history in description or a separate field if you prefer
#             # Using description as a combined log for now
#             obj.description = (obj.description or "") + f"\n{new_history_entry}"
            
#             # WhatsApp Trigger only if newly resolved
#             if new_status == "Resolved" and old_status != "Resolved":
#                 obj.resolved_date = timezone.now().date()
#                 obj.resolution_note = note
#                 if obj.voter_mobile:
#                     send_whatsapp_status(obj.voter_mobile, obj.voter_name, obj.complaint_category, note)
            
#             obj.save()
#             return JsonResponse({'message_code': 1000})
#         except Exception as e:
#             return JsonResponse({'message_code': 999, 'message_text': str(e)})



















def complaint_dashboard(request):
    status_filter = request.GET.get('status', '').strip()
    search_filter = request.GET.get('mobile', '').strip()

    complaints_qs = BJPOffice.objects.filter(is_deleted=False).order_by('-created_on')

    if status_filter:
        complaints_qs = complaints_qs.filter(status=status_filter)

    if search_filter:
        complaints_qs = complaints_qs.filter(
            Q(voter_mobile__icontains=search_filter) |
            Q(voter_name__icontains=search_filter)
        )

    resolved_count = BJPOffice.objects.filter(status='Resolved', is_deleted=False).count()

    context = {
        'complaints': complaints_qs,
        'resolved_count': resolved_count,
    }
    return render(request, 'Office_managment/complaint_mgmt.html', context)


# ============================================================
# 2) SMS CONFIG (Same company / Same gateway)
# ============================================================

SMS_API_URL = "http://173.45.76.227/send.aspx"
SMS_CONFIG = {
    "username": "KUKUDKU",
    "pass": "KUKUDKU12$",
    "route": "trans1",
    "senderid": "KUKADU",
}


def clean_mobile(raw_number: str) -> str:
    digits = ''.join(filter(str.isdigit, str(raw_number)))
    return digits[-10:]


def fill_dlt_vars(template_body: str, v1: str, v2: str, v3: str) -> str:
    """
    DLT template supports {#var#} placeholders.
    Variable order:
    1) voter_name
    2) complaint_category
    3) resolution_note
    """
    out = template_body or ""
    out = out.replace("{#var#}", v1 or "", 1)
    out = out.replace("{#var#}", v2 or "", 1)
    out = out.replace("{#var#}", v3 or "", 1)
    return out


def build_resolved_sms_fallback(voter_name: str, complaint_category: str, resolution_note: str) -> str:
    voter_name = (voter_name or "विनंतीकर्ता").strip()
    complaint_category = (complaint_category or "तक्रार").strip()
    resolution_note = (resolution_note or "काम पूर्ण झाले आहे.").strip()

    return (
        f"नमस्कार {voter_name},\n\n"
        f"आपल्या \"{complaint_category}\" संदर्भातील तक्रार/विनंतीचे काम यशस्वीरित्या पूर्ण झाले आहे.\n\n"
        f"निवारण तपशील: {resolution_note}\n\n"
        f"आपल्याला अजून काही मदत हवी असल्यास कृपया कार्यालयाशी संपर्क साधावा.\n\n"
        f"धन्यवाद,\n"
        f"लक्ष प्रतिष्ठान कार्यालय\n"
        f"कालींदा मुरलीधर पुंडे (नगरसेविका)\n"
        f"महेश मुरलीधर पुंडे"
    )


def send_sms_kukudku(mobile: str, message: str) -> tuple[bool, str]:
    """
    Sends SMS using GET with params (auto-encoding like your CollectionsAddView).
    """
    mobile_number = clean_mobile(mobile)
    if len(mobile_number) != 10:
        return False, "Invalid mobile number"

    params = {
        **SMS_CONFIG,
        "numbers": mobile_number,
        "message": message
    }

    try:
        resp = requests.get(SMS_API_URL, params=params, timeout=10)
        return True, resp.text
    except requests.exceptions.RequestException as e:
        return False, str(e)


def log_sms_transaction(mobile: str, message: str, template_obj: SMSMaster | None = None, user_obj=None):
    """
    Saves SMS log into SMSTransaction.
    Note: user_obj should be TblUsers instance if you want to track.
    """
    SMSTransaction.objects.create(
        smsTemplateId=template_obj,
        smsBody=message,
        smsTo=clean_mobile(mobile),
        smsCategory=1,
        smsStatus=0,  # 0=Pending
        smsSendOn=int(timezone.now().timestamp()),
        smsRequestByUserId=user_obj
    )


# ============================================================
# 3) UPDATE DIRECT (Resolved -> Send SMS + Log)
# ============================================================


@api_view(['POST']) 
def update_complaint_direct(request):
    """
    Expected JSON:
    {
      "id": 123,
      "status": "Resolved",
      "note": "काम पूर्ण झाले"
    }
    """
    try:
        data = request.data if isinstance(request.data, dict) else json.loads(request.body.decode("utf-8"))

        obj_id = data.get("id")
        new_status = (data.get("status") or "").strip()
        note = (data.get("note") or "").strip()

        if not obj_id:
            return JsonResponse({"message_code": 999, "message_text": "Missing id"})

        obj = BJPOffice.objects.get(bjp_office_id=obj_id)
        old_status = obj.status

        obj.status = new_status

        # ---- HISTORY LOG ----
        timestamp = timezone.now().strftime("%d %b %Y, %I:%M %p")
        user_name = request.session.get("user_name", "Admin")
        obj.description = (obj.description or "") + f"\n|{timestamp}|{user_name}|{new_status}|{note}"

        # ---- ONLY WHEN NEWLY RESOLVED ----
        if new_status == "Resolved" and old_status != "Resolved":
            obj.resolved_date = timezone.now().date()
            obj.resolution_note = note

            if obj.voter_mobile:
                template_title = "Complaint Resolved"  # ✅ SMSMaster.templateTitle must match this
                tpl_obj = SMSMaster.objects.filter(templateTitle=template_title, is_deleted=False).first()

                if tpl_obj and tpl_obj.templateMessageBody:
                    sms_text = fill_dlt_vars(
                        tpl_obj.templateMessageBody,
                        obj.voter_name or "",
                        obj.complaint_category or "",
                        note or ""
                    )
                else:
                    sms_text = build_resolved_sms_fallback(obj.voter_name, obj.complaint_category, note)
                    tpl_obj = None

                # Log SMS in DB
                log_sms_transaction(obj.voter_mobile, sms_text, template_obj=tpl_obj, user_obj=None)

                # Send SMS via gateway
                ok, resp = send_sms_kukudku(obj.voter_mobile, sms_text)
                print("Resolved SMS Send:", ok, "Response:", resp)

        obj.save()
        return JsonResponse({"message_code": 1000})

    except BJPOffice.DoesNotExist:
        return JsonResponse({"message_code": 999, "message_text": "Complaint not found"})
    except Exception as e:
        return JsonResponse({"message_code": 999, "message_text": str(e)})