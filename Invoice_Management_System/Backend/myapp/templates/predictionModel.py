import json
import sqlite3

import pandas as pd
import plotly
import plotly.express as px
from catboost import CatBoostClassifier
import shap
from django.contrib.admin import display
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def preprocessing():

    print("Inside Preprocessing Function!!!")

    conn = sqlite3.connect('db.sqlite3')
    query = "SELECT * FROM myapp_invoicedetails"

    # Read data from the database using the query
    data = pd.read_sql_query(query, conn)
    # print(data)
    # Close the database connection
    conn.close()

    # csv_file_path = os.path.join(os.path.dirname(__file__), 'InvoiceData_v4.csv')
    # data = pd.read_csv(csv_file_path)

    (data.isna().sum() / len(data)).sort_values(ascending=False)

    # changing the data type for some columns, where needed
    data['clear_date'] = pd.to_datetime(data['clear_date'], format='%Y-%m-%d')
    data['due_date'] = pd.to_datetime(data['due_date'], format='%Y-%m-%d')
    data['create_date'] = pd.to_datetime(data['create_date'], format='%Y-%m-%d')

    # checking if there are any duplicates in 'doc_id' column
    data['doc_id'].value_counts()


    # Remove duplicates
    data = data.drop_duplicates(subset=['doc_id'])

    # adding column with pyment delay for each invoice
    data['payment_delay_in_days'] = (data['clear_date'] - data['due_date']).dt.days

    # adding column with payment term for each invoice
    data['payment_term_in_days'] = (data['due_date'] - data['create_date']).dt.days

    # splitting the 'business_code' column into separate dummy varialble columns
    biz_code_cols = pd.get_dummies(data['business_code'], prefix='biz_code')
    data[biz_code_cols.columns] = biz_code_cols

    unique_values = data['payment_delay_in_days'].unique()

    # calculating the mean delay for each customer
    avg_customer_delay = data.groupby(['cust_name'])['payment_delay_in_days'].mean(numeric_only=True)

    # for customers with no prior invoices I use the average delay of all other customers
    avg_customer_delay.fillna(avg_customer_delay.mean(), inplace=True)

    avg_customer_delay.rename('avg_customer_delay', inplace=True)

    # adding average customer delay data to the main dataframe
    data = pd.merge(data, avg_customer_delay, on='cust_name', how='left')

    # checking for possible invoice currencies
    data['inv_currency'].value_counts()

    # adding new column with all invoice amounts in USD (amounts in CAD are converted to USD assuming 0.75 fx rate)
    # data['usd_amount'] = data['open_amt'].where(data['inv_currency'] == 'USD', data['open_amt'] * 0.75)
    data['usd_amount'] = data['open_amt'].apply(pd.to_numeric, errors='coerce')  # Convert to numeric, handle errors
    data['usd_amount'] = data.apply(
        lambda row: row['usd_amount'] * 0.75 if row['inv_currency'] != 'USD' else row['usd_amount'], axis=1)

    # creating dummy variable column for invoice currency
    data['invoice_in_USD'] = pd.get_dummies(data['inv_currency'])['USD']

    # checking for possible doc types
    data['doc_type'].value_counts()

    # creating dummy variable column for document type
    data['doc_type_RV'] = pd.get_dummies(data['doc_type'])['RV']

    # there seems to be a pattern among customer numbers. some start with 'CC', some with '0', etc
    data['cust_num'].str[:2].value_counts()

    # therefore I create separate dummy columns based on the first two characters in customer number
    data['customer_category'] = data['cust_num'].str[:2]

    cust_categories = pd.get_dummies(data['customer_category'], prefix='cust_category')
    data[cust_categories.columns] = cust_categories

    # separating closed invoices from the ones that are still open, in two different datasets
    global closed_invoices, open_invoices
    closed_invoices = data[~data['clear_date'].isna()]
    open_invoices = data[data['clear_date'].isna()]

    # adding a column that shows whether the invoice was delayed by more than 7 days or not
    closed_invoices['is_overdue'] = closed_invoices['payment_delay_in_days'] > 7
    closed_invoices['is_overdue'] = closed_invoices['is_overdue'].apply(lambda x: 1 if x == True else 0)
    closed_invoices[['payment_delay_in_days', 'is_overdue']].mean()

def generatePlot(plot_type):
    preprocessing()
    if plot_type=="bc":
        print("Inside Business Code Summary!!!")
        figData_business_code = overdue_summary('business_code', closed_invoices)
        return figData_business_code
    elif plot_type=="ic":
        figData_currency = overdue_summary('inv_currency', closed_invoices)
        return figData_currency
    elif plot_type=="dt":
        figData_doc_type = overdue_summary('doc_type', closed_invoices)
        return figData_doc_type
    elif plot_type=="cc":
        figData_cust_category = overdue_summary('customer_category', closed_invoices)
        return figData_cust_category
    else:
        return None

def payment_category():
    preprocessing()
    # invoices with shorter payment terms tend to have more delays
    closed_invoices['paym_term_categ'] = pd.cut(closed_invoices['payment_term_in_days'], 10)
    closed_invoices.groupby('paym_term_categ').agg(
        invoice_count=('doc_id', 'count'),
        overdue_share=('is_overdue', 'mean'),
        avg_overdue_days=('payment_delay_in_days', 'mean')).style.bar(subset=['invoice_count'], color='#B1DFB4').bar(subset=['overdue_share'], color='#B1DFE8').bar(
        subset=['avg_overdue_days'], color='#B1DFB4').bar(subset=['avg_overdue_days'], color='#ECC4C4').format(
        {'overdue_share': '{:.1%}', 'avg_overdue_days': '{:.1f}'})

def amount_category():
    preprocessing()
    # invoices for the amount of USD 2,829 - USD 24,744 seem to have more delays than invoices for other amounts
    closed_invoices['usd_amount_category'] = pd.qcut(closed_invoices['usd_amount'],[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    closed_invoices.groupby('usd_amount_category').agg(
        invoice_count=('doc_id', 'count'),
        overdue_share=('is_overdue', 'mean'),
        avg_overdue_days=('payment_delay_in_days', 'mean')
    ).style.bar(subset=['invoice_count'], color='#B1DFB4').bar(subset=['overdue_share'], color='#B1DFE8').bar(
        subset=['avg_overdue_days'], color='#B1DFB4').bar(subset=['avg_overdue_days'], color='#ECC4C4').format(
        {'overdue_share': '{:.1%}', 'avg_overdue_days': '{:.1f}'})

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

def trainingModel():
    preprocessing()
    # defining the columns that will be used to train the algorithm
    input_columns = [
        'payment_term_in_days',
        'biz_code_CA02',
        'biz_code_U001',
        'biz_code_U002',
        'biz_code_U005',
        'biz_code_U007',
        'biz_code_U013',
        'usd_amount',
        'invoice_in_USD',
        'doc_type_RV',
        'cust_category_10',
        'cust_category_14',
        'cust_category_20',
        'cust_category_CC'
    ]

    # defining the input variables and the column to predict
    X = closed_invoices[input_columns].values
    y = closed_invoices['is_overdue'].values

    # Splitting the dataset into the Training set and Test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Feature Scaling
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)

    # training the model
    classifier = CatBoostClassifier(silent=True)
    classifier.fit(X_train, y_train)

    # Making the Confusion Matrix and reading the accuracy of predictions
    y_pred = classifier.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    # determining feature importances on the model outcome
    feature_importance = pd.DataFrame()
    feature_importance['feature'] = closed_invoices[input_columns].columns
    feature_importance['importance'] = classifier.feature_importances_
    feature_importance.set_index('feature', inplace=True)
    feature_importance.sort_values(by='importance', ascending=False, inplace=True)

    # taking the input values from open_invoices data
    pred_2 = open_invoices[input_columns].values
    # feature scaling according to previosuly trained model
    pred_2 = sc.transform(pred_2)
    # making predictions whether any of the currently open invoices will be overdue or not
    # and adding the predictions in new column 'is_overdue_pred'
    open_invoices['is_overdue_pred'] = classifier.predict(pred_2)

    count_overdue = open_invoices['is_overdue_pred'].sum()
    return int(count_overdue)