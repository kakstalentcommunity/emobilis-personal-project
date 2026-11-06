import json
from django.http import JsonResponse
def json_body(request):
    try: return json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError): raise ValueError('Invalid JSON body')
def json_ok(data, status=200): return JsonResponse(data, status=status)
def json_error(message, status=400): return JsonResponse({'error':str(message)}, status=status)
