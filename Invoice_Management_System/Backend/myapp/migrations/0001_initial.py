# Generated by Django 4.2.3 on 2023-08-03 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InvoiceDetails",
            fields=[
                ("invoiceId", models.AutoField(primary_key=True, serialize=False)),
                ("cust_num", models.CharField(max_length=200)),
                ("cust_name", models.CharField(max_length=200)),
                ("inv_num", models.IntegerField()),
                ("clear_date", models.DateField()),
                ("doc_id", models.CharField(max_length=200)),
                ("posting_id", models.CharField(max_length=200)),
                ("due_date", models.DateField()),
                ("inv_currency", models.CharField(max_length=200)),
                ("doc_type", models.CharField(max_length=200)),
                ("open_amt", models.CharField(max_length=200)),
                ("payment_terms", models.CharField(max_length=200)),
                ("is_open", models.CharField(max_length=200)),
                ("create_date", models.DateField()),
                ("update_date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Payments",
            fields=[
                ("paymentId", models.AutoField(primary_key=True, serialize=False)),
                ("payment_amount", models.CharField(max_length=200)),
                ("invoice_id", models.CharField(max_length=200)),
                ("payment_number", models.CharField(max_length=200)),
                ("payment_date", models.DateField()),
                ("cust_num", models.CharField(max_length=200)),
                ("cust_name", models.CharField(max_length=200)),
                ("create_date", models.DateField()),
                ("update_date", models.DateField()),
                ("invoice_num_payment", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Users",
            fields=[
                ("userId", models.AutoField(primary_key=True, serialize=False)),
                ("user_name", models.CharField(max_length=200)),
                ("first_name", models.CharField(max_length=200)),
                ("last_name", models.CharField(max_length=200)),
                ("full_name", models.CharField(max_length=200)),
                ("email", models.CharField(max_length=200)),
                ("phone", models.CharField(max_length=200)),
                ("create_date", models.DateField()),
                ("update_date", models.DateField()),
                ("is_active", models.CharField(max_length=200)),
            ],
        ),
    ]