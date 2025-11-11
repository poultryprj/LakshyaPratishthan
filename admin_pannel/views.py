import json
import os
from pyexpat.errors import messages
import uuid
from django.http import JsonResponse
from django.shortcuts import redirect, render
import requests 
from django.contrib import messages



def login_view(request):
    if 'user_id' in request.session:
        return redirect('Index')
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        api_url = "http://43.205.198.148/LakshyaPratishthan/api/agentlogin/"
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
    api_url = "http://43.205.198.148/LakshyaPratishthan/api/list_all_registrations/"
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
        backend_api_url = "http://43.205.198.148/LakshyaPratishthan/api/bulk_update_diwali_kirana/"

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
        backend_api_url = "http://43.205.198.148/LakshyaPratishthan/api/add_diwali_family_member/"
        
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
        backend_api_url = "http://43.205.198.148/LakshyaPratishthan/api/upload_voter_id/"
        
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
        backend_api_url = f"http://43.205.198.148/LakshyaPratishthan/api/delete_diwali_member/{reg_id}/"
        
        # Make the server-to-server POST request
        response = requests.post(backend_api_url)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Return the backend API's response to the browser
        return JsonResponse(response.json(), status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'message_code': 999, 'message_text': f'Network error calling backend API: {e}'}, status=503)
    except Exception as e:
        return JsonResponse({'message_code': 999, 'message_text': f'An internal error occurred: {e}'}, status=500)    