from __future__ import unicode_literals
import stripe
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
import bcrypt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta, date

stripe.api_key = settings.STRIPE_SECRET_KEY


def admin_login(request):
    return render(request, 'admin_dashboard/login.html')

# sigin in post req


def admin_for_login(request):
    if request.method == "POST":
        # add authentication that user is admin userlevel9
        return redirect('/admins/dashboard')


def dashboard(request):
    return render(request, 'admin_dashboard/index.html')
