import os

from flask import Flask, render_template, request
from datetime import datetime
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# Connected Services
DB_SERVICE_URL = 'https://solar-python-cloud.wayscript.cloud'
TWILIO_SERVICE_URL = ''



# App Logic
app = Flask(__name__)

@app.route('/')
def example_sb_admin_home():
    import requests
    # Call to get annual earnings
    earnings_response = requests.get(DB_SERVICE_URL + '/total-earnings')
    annual_earnings = earnings_response.json().get('response')

    # Call for this month earnings
    # figure out month then send call to db with appropriate month
    current_month = datetime.now().month
    params = {'month': current_month}
    monthly_earnings_response = requests.get(DB_SERVICE_URL + '/monthly-earnings', params = params)
    monthly_earnings = monthly_earnings_response.json().get('response')

    # Call for tasks percentage
    open_tasks = requests.get(DB_SERVICE_URL + '/query-tasks-open').json()
    percentage = int(open_tasks.get('response')/20 * 100)

    #Calls for making home page graph
    response = requests.get(DB_SERVICE_URL + '/query-earnings')

    df = pd.DataFrame(response.json().get('response'))
    df = df.set_axis(['Name', 'Employee Number', 'Month', 'Day', 'Year', 'Amount', 'ID'], axis=1, inplace=False)
    df2 = df.groupby(['Month']).sum()

    fig = px.line(df2, x=df2.index, y="Amount", title='Earnings')
    fig.write_html("templates/home-earnings-graph.html")

    #Recent Earnings
    response = requests.get(DB_SERVICE_URL + '/query-earnings')

    earnings = response.json().get('response')
    earnings = earnings[-8:]
    recent_earnings = []
    for i in earnings:
        new_list = [i[0], i[5]]
        recent_earnings.append(new_list)


    #Pending Requests
    open_requests = requests.get(DB_SERVICE_URL + '/open-requests').json()
    requests = open_requests.get('response')
    return render_template('home.html',
                            amount=monthly_earnings,
                            earnings=annual_earnings,
                            percentage=percentage,
                            requests=requests,
                            recent_earnings=recent_earnings)

@app.route('/report')
def report():
    # more graphing for reports page
    import requests
    response = requests.get(DB_SERVICE_URL + '/query-earnings')

    df = pd.DataFrame(response.json().get('response'))
    df = df.set_axis(['Name', 'Employee Number', 'Month', 'Day', 'Year', 'Amount', 'ID'], axis=1, inplace=False)
    fig = px.histogram(df, x="Month", y="Amount",
             color='Name', barmode='group',
             height=400)
    fig.write_html("templates/individual-earnings-graph.html")
    return render_template('detail-report.html')

## Additional Report graphs
@app.route('/recent_earnings')
def recent_earnings():
    import requests
    response = requests.get(DB_SERVICE_URL + '/query-earnings')

    earnings = response.json().get('response')
    earnings = earnings[-5:]
    recent_earnings = []
    recent_employee = []
    for i in earnings:
        recent_earnings.append(i[5])
        recent_employee.append(i[0])

    fig = go.Figure(data=[go.Table(header=dict(values=['Employee', 'Most Recent Earning']),
                 cells=dict(values=[recent_employee, recent_earnings]))
                     ])
    fig.write_html("templates/recent_earnings.html")
    return render_template('recent_earnings.html')

@app.route('/database_form')
def index():

    # DATABASE OPTIONS GO HERE
    # this list supplies the options that are generated in the home page selector
    # to add or remove entries from home page selector, put them in the list SELECTOR_OPTIONS below

    SELECTOR_OPTIONS = ['customers']
    return render_template('form.html', selector_options = SELECTOR_OPTIONS )

@app.route('/twilio')
def twilio():
    return render_template('twilio.html')

@app.route('/submit_twilio', methods=['GET', 'POST'])
def submit_twilio():
    if request.method == 'POST':
        if not request.form['to'] or not request.form['body']:
            return 'Please fill out all fields.'
        else:
            payload = {'to':request.form['to'], 'body':request.form['body']}
            response = requests.post('https://friendly-kraken-vehicle.wayscript.cloud', json=payload)
            return response.content

    return 'Message Sent'

@app.route('/earnings')
def earnings():
    import requests
    response = requests.get(DB_SERVICE_URL + '/query-earnings')
    data = response.json()
    results = data.get('response')
    return render_template('earnings.html', results=results)

@app.route('/employee_earnings', methods=['GET','POST'])
def employee_earnings():
    import requests
    data = request.form['employee']
    employee = {'employee' : data }
    response = requests.post(DB_SERVICE_URL + '/query-earnings-employee', json = employee)
    data = response.json()
    results = data.get('response')
    return render_template('earnings.html', results=results)

@app.route('/tasks')
def tasks():
    import requests
    response = requests.get(DB_SERVICE_URL + '/query-tasks').json().get('response')
    return render_template('tasks.html', results = response)

@app.route('/filter-tasks')
def filter_tasks():
    return render_template('tasks.html')

@app.route('/requests')
def requests():
    import requests
    response = requests.get(DB_SERVICE_URL + '/query-requests').json().get('response')
    return render_template('requests.html', results = response)


@app.route('/submit_form', methods=['GET', 'POST'])
def submit_form():
    database_name = request.form.get('database_selection')
    # HERE YOUR ACTION CAN BE DONE TO YOUR DATABASE
    # we can access the database name from our form by database_name variable
    # We can connect to our database via python library, example:
    # connection = mysql.connector.connect(
    #        host=host_name,
    #        user=user_name,
    #        passwd=user_password,
    #        database=database_name
    #    )
    # select_users = "SELECT * from users"
    # connection.autocommit = True
    # cursor = connection.cursor()
    # try:
    #    cursor.execute(query)
    #    result = 'Success!'
    # except OperationalError as e:
    #    result = 'Operation Failure'
    result = 'Success!'
    return render_template('submit_form.html', selected_database = database_name, result = result)

if __name__ == '__main__':
    app.run()
