from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from myapp.models import Users, Payments, InvoiceDetails
from myapp.serializers import UsersSerializer, PaymentsSerializer, InvoiceDetailsSerializer

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from myapp.templates.predictionModel import preprocessing, generatePlot, trainingModel


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required()
def login_user(request):
    if request.method == 'POST':
        user = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=user, password=password)
        if user is not None:
            auth_login(request, user)
            messages.info(request, 'Login successful.')
            return redirect('myapp:postLogin')
        else:
            messages.info(request, 'Login Error.')
            return redirect('myapp:login')
    else:
        return render(request, 'registration/login.html', {})

def home(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')

def postLogin(request):
    return render(request, 'postLogin.html')

def createInvoice(request):
    return render(request, 'createInvoice.html')

def logout_user(request):
    auth_logout(request)
    return redirect('login')

@csrf_exempt
def usersApi(request):
    if request.method == 'GET':
        users = Users.objects.all()
        users_serializer = UsersSerializer(users, many=True)
        return JsonResponse(users_serializer.data, safe=False)
    elif request.method == 'POST':
        users_data = JSONParser().parse(request)
        users_serializer = UsersSerializer(data=users_data)
        if users_serializer.is_valid():
            users_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method == 'PUT':
        users_data = JSONParser().parse(request)
        user = Users.objects.get(userId=users_data['userId'])
        users_serializer = UsersSerializer(user, data=users_data)
        if users_serializer.is_valid():
            users_serializer.save()
            return JsonResponse("Updated Successfully", safe=False)
        return JsonResponse("Failed to Update", safe=False)
    elif request.method == 'DELETE':
        users_data = JSONParser().parse(request)
        user = Users.objects.get(userId=users_data['userId'])
        user.delete()
        return JsonResponse("Deleted Successfully", safe=False)

@csrf_exempt
def invoiceApi(request):
    if request.method == 'GET':
        invoices = InvoiceDetails.objects.all()
        invoices_serializer = InvoiceDetailsSerializer(invoices, many=True)
        return JsonResponse(invoices_serializer.data, safe=False)
    elif request.method == 'POST':
        invoices_data = JSONParser().parse(request)
        invoices_serializer = InvoiceDetailsSerializer(data=invoices_data)
        if invoices_serializer.is_valid():
            invoices_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method == 'PUT':
        invoice_data = JSONParser().parse(request)
        invoice = InvoiceDetails.objects.get(invoiceId=invoice_data['invoiceId'])
        invoices_serializer = InvoiceDetailsSerializer(invoice, data=invoice_data)
        if invoices_serializer.is_valid():
            invoices_serializer.save()
            return JsonResponse("Updated Successfully", safe=False)
        return JsonResponse("Failed to Update", safe=False)
    elif request.method == 'DELETE':
        invoice_data = JSONParser().parse(request)
        invoice = InvoiceDetails.objects.get(invoiceId=invoice_data['invoiceId'])
        invoice.delete()
        return JsonResponse("Deleted Successfully", safe=False)

@csrf_exempt
def paymentApi(request):
    if request.method == 'GET':
        payments = Payments.objects.all()
        payments_serializer = PaymentsSerializer(payments, many=True)
        return JsonResponse(payments_serializer.data, safe=False)
    elif request.method == 'POST':
        payments_data = JSONParser().parse(request)
        payments_serializer = PaymentsSerializer(data=payments_data)
        if payments_serializer.is_valid():
            payments_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed to Add", safe=False)
    elif request.method == 'PUT':
        payment_data = JSONParser().parse(request)
        payment = Payments.objects.get(paymentId=payment_data['paymentId'])
        payment_serializer = PaymentsSerializer(payment, data=payment_data)
        if payment_serializer.is_valid():
            payment_serializer.save()
            return JsonResponse("Updated Successfully", safe=False)
        return JsonResponse("Failed to Update", safe=False)
    elif request.method == 'DELETE':
        payment_data = JSONParser().parse(request)
        payment = Payments.objects.get(paymentId=payment_data['paymentId'])
        payment.delete()
        return JsonResponse("Deleted Successfully", safe=False)

@csrf_exempt
def summary_by_business_code(request):
    if request.method == 'POST':
        try:
            # Call the generatePlot function from PredictionModel.py
            result = generatePlot("bc")
            return JsonResponse({"message": "Summary generated successfully", "result": result})
        except Exception as e:
            return JsonResponse({"message": "Error generating summary", "error": str(e)}, status=500)


@csrf_exempt
def summary_by_inv_currency(request):
    if request.method == 'POST':
        try:
            # Call the generatePlot function from PredictionModel.py
            result = generatePlot("ic")
            return JsonResponse({"message": "Summary generated successfully", "result": result})
        except Exception as e:
            return JsonResponse({"message": "Error generating summary", "error": str(e)}, status=500)

@csrf_exempt
def summary_by_cust_category(request):
    if request.method == 'POST':
        try:
            # Call the generatePlot function from PredictionModel.py
            result = generatePlot("cc")
            return JsonResponse({"message": "Summary generated successfully", "result": result})
        except Exception as e:
            return JsonResponse({"message": "Error generating summary", "error": str(e)}, status=500)


@csrf_exempt
def summary_by_doc_type(request):
    if request.method == 'POST':
        try:
            # Call the generatePlot function from PredictionModel.py
            result = generatePlot("dt")
            # result = predictDelay()
            return JsonResponse({"message": "Summary generated successfully", "result": result})
        except Exception as e:
            return JsonResponse({"message": "Error generating summary", "error": str(e)}, status=500)

@csrf_exempt
def invoice_delay_prediction(request):
    if request.method == 'POST':
        try:
            # Call the trainingModel function from PredictionModel.py
            result = trainingModel()
            return JsonResponse({"message": "Summary generated successfully", "result": result})
        except Exception as e:
            return JsonResponse({"message": "Error generating summary", "error": str(e)}, status=500)