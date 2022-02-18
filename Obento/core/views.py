from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def send_json(request):
  data = {'result': 'ola'}
  return JsonResponse(data, safe=False)