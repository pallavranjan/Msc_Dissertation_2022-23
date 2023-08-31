import json
import sqlite3

import pandas as pd
import plotly
import plotly.express as px
from catboost import CatBoostClassifier
import shap


def preprocessing(plot_type):

    print("Inside Preprocessing Function!!!")

    conn = sqlite3.connect('db.sqlite3')
    query = "SELECT * FROM myapp_invoicedetails"

    # Read data from the database using the query
    data = pd.read_sql_query(query, conn)
    print(data)
    # Close the database connection
    conn.close()

    # csv_file_path = os.path.join(os.path.dirname(__file__), 'InvoiceData_v4.csv')
    # data = pd.read_csv(csv_file_path)

    (data.isna().sum() / len(data)).sort_values(ascending=False)

    data['clear_date'] = pd.to_datetime(data['clear_date'], format='%d/%m/%Y %H:%M')
    data['due_in_date'] = pd.to_datetime(data['due_in_date'], format='%Y%m%d')
    data['baseline_create_date'] = pd.to_datetime(data['baseline_create_date'], format='%Y%m%d')

    data['doc_id'].value_counts()

    data = data.drop_duplicates(subset=['doc_id'])

    data['payment_delay_in_days'] = (data['clear_date'] - data['due_date']).dt.days

    data['payment_term_in_days'] = (data['due_date'] - data['create_date']).dt.days

    biz_code_cols = pd.get_dummies(data['business_code'], prefix='biz_code')
    data[biz_code_cols.columns] = biz_code_cols

    unique_values = data['payment_delay_in_days'].unique()

    avg_customer_delay = data.groupby(['name_customer'])['payment_delay_in_days'].mean(numeric_only=True)

    avg_customer_delay.fillna(avg_customer_delay.mean(), inplace=True)

    avg_customer_delay.rename('avg_customer_delay', inplace=True)

    data = pd.merge(data, avg_customer_delay, on='name_customer', how='left')

    data['inv_currency'].value_counts()

    data['usd_amount'] = data['open_amt'].where(data['inv_currency'] == 'USD', data['open_amt'] * 0.75)

    data['invoice_in_USD'] = pd.get_dummies(data['inv_currency'])['USD']

    data['doc_type'].value_counts()

    data['doc_type_RV'] = pd.get_dummies(data['doc_type'])['RV']

    data['cust_number'].str[:2].value_counts()

    data['customer_category'] = data['cust_number'].str[:2]

    cust_categories = pd.get_dummies(data['customer_category'], prefix='cust_category')
    data[cust_categories.columns] = cust_categories

    closed_invoices = data[~data['clear_date'].isna()]
    open_invoices = data[data['clear_date'].isna()]

    closed_invoices['is_overdue'] = closed_invoices['payment_delay_in_days'] > 7
    closed_invoices['is_overdue'] = closed_invoices['is_overdue'].apply(lambda x: 1 if x == True else 0)
    closed_invoices[['payment_delay_in_days', 'is_overdue']].mean()

    # if plot_type=="bc":
    #     print("Inside Business Code Summary!!!")
    #     figData_business_code = overdue_summary('business_code', closed_invoices)
    #     return figData_business_code
    # elif plot_type=="ic":
    #     figData_currency = overdue_summary('inv_currency', closed_invoices)
    #     return figData_currency
    # elif plot_type=="dt":
    #     figData_doc_type = overdue_summary('doc_type', closed_invoices)
    #     return figData_doc_type
    # elif plot_type=="cc":
    #     figData_cust_category = overdue_summary('customer_category', closed_invoices)
    #     return figData_cust_category
    # else:
    #     return None



def overdue_summary(column_name, closed_invoices):
    print("Inside overdue summary function!!!")
    grp = closed_invoices.groupby(column_name).agg(
        invoice_count=('doc_id', 'count'),
        overdue_share=('is_overdue', 'mean')
    ).sort_values('invoice_count', ascending=False)

    fig = px.pie(
        grp,
        names=grp.index,
        values='invoice_count',
        title=f'Overdue Summary by {column_name}',
        labels={'invoice_count': 'Invoice Count'},
        height=500,
        hover_data=['overdue_share']
    )

    fig.update_traces(textinfo='percent+label')
    fig_json = fig.to_json()
    print("Converted the fig to JSON successfully")
    return fig.show()

preprocessing("bc")