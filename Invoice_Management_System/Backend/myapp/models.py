from django.db import models


# Create your models here.
class InvoiceDetails(models.Model):
    invoiceId = models.AutoField(primary_key=True)
    cust_num = models.CharField(max_length=200)
    cust_name = models.CharField(max_length=200)
    inv_num = models.CharField(max_length=200)
    clear_date = models.DateField()
    doc_id = models.CharField(max_length=200)
    posting_id = models.CharField(max_length=200)
    due_date = models.DateField()
    inv_currency = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=200)
    open_amt = models.CharField(max_length=200)
    payment_terms = models.CharField(max_length=200)
    is_open = models.CharField(max_length=200)
    business_code = models.CharField(max_length=200)
    create_date = models.DateField()
    update_date = models.DateField()

class Users(models.Model):
    userId = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    create_date = models.DateField()
    update_date = models.DateField()
    is_active = models.CharField(max_length=200)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Payments(models.Model):
    paymentId = models.AutoField(primary_key=True)
    payment_amount = models.CharField(max_length=200)
    invoice_id = models.CharField(max_length=200)
    payment_number = models.CharField(max_length=200)
    payment_date = models.DateField()
    cust_num = models.CharField(max_length=200)
    cust_name = models.CharField(max_length=200)
    create_date = models.DateField()
    update_date = models.DateField()
    invoice_num_payment = models.CharField(max_length=200)