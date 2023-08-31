from rest_framework import serializers
from myapp.models import Users, InvoiceDetails, Payments

class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = ('paymentId','payment_amount','invoice_id','payment_number', 'payment_date','cust_num', 'cust_name', 'create_date','update_date','invoice_num_payment')

class InvoiceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDetails
        fields = ('invoiceId','cust_num','cust_name','inv_num','clear_date','doc_id','posting_id','due_date','inv_currency', 'doc_type','open_amt','payment_terms','is_open','create_date','update_date', 'business_code')

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('userId','user_name','first_name','last_name','full_name','email','phone','create_date','update_date','is_active')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

