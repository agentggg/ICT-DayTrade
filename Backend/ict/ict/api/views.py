from datetime import datetime, date, timedelta
from collections import Counter
from django.db import transaction
import random
import json
import logging
import threading
import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import IntegrityError, transaction as db_transaction
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from datetime import timezone
utc = timezone.utc
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# from exponent_server_sdk import (
#     DeviceNotRegisteredError,
#     PushClient,
#     PushMessage,
#     PushServerError,
#     PushTicketError,
# )

# import environ
# from faker import Faker
# from user_agents import parse
# import pytz
# from twilio.rest import Client
# import cloudinary.api
# import cloudinary.uploader
# from plaid import ApiClient, Configuration, Environment
# from plaid.api import plaid_api
# from pymongo import MongoClient
# from bson import ObjectId
# from plaid import ApiClient, Configuration, Environment
# from plaid.api import plaid_api
# import os
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

 
from .models import *
from .serializers import *
# from .tasks import * 
# from .reuseableFunctions.deliverableReminders import notifications
# from .reuseableFunctions.gameBoardStats import boardChangeNotification
# import pytz
# from django.utils import timezone
import requests
# import urllib #updated 02/08
from django.utils.html import escape

@api_view(['GET', 'POST'])
def test(request):
    print('test') 
    return Response("successful")


@api_view(['GET'])
def get_data(request): 
    instrument = request.GET.get('instrument', False)
    instrument_id = Instrument.objects.get(name=instrument)
    candles = Candle.objects.filter(instrument=instrument_id)
    response = CandleSerializers(candles, many=True).data    
    return Response(response) 

