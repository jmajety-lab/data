
from flask import Flask, redirect, render_template, request, url_for, jsonify, session
from flask_session import Session
import csv
import pandas as pd
import json
from datetime import datetime
global first_data
global second_data
from flask_cors import CORS

app = Flask(__name__)


# Initialize the session

CORS(app)
app.secret_key = 'secret_key'
county_dict = {
    'ALLEGANY': 1,
    'ANNE ARUNDEL': 2,
    'BALTIMORE': 3,
    'CALVERT': 4,
    'CAROLINE': 5,
    'CARROLL': 6,
    'CECIL': 7,
    'CHARLES': 8,
    'DORCHESTER': 9,
    'FREDERICK': 10,
    'GARRETT': 11,
    'HARFORD': 12,
    'HOWARD': 13,
    'KENT': 14,
    'MONTGOMERY': 15,
    'PRINCE GEORGES': 16,
    'QUEEN ANNES': 17,
    'ST. MARYS': 18,
    'SOMERSET': 19,
    'TALBOT': 20,
    'WASHINGTON': 21,
    'WICOMICO': 22,
    'WORCESTER': 23,
    'BALTIMORE CITY': 24,
}


def get_county_code(county_name):
    return county_dict.get(county_name.upper(), None)


def read_data():
    data = pd.read_csv("final_data.csv", encoding='unicode_escape' )
    return data
def read_crash_data():
    data = pd.read_csv("output.csv", encoding='unicode_escape' )
    return data




@app.route('/')
def index():
    if request.method == 'POST':
        selected_app = request.form.get('app')
        if selected_app == 'segment':
            return redirect(url_for('segment'))
        elif selected_app == 'intersection':
            return redirect(url_for('intersection'))
    
    return render_template('index.html')

@app.route('/process_selection', methods=['POST'])
def process_selection():
    # Read the CSV file and extract the data
    with open('./final_data.csv', 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    
    # Extract unique values for COUNTY, ROUTE_TYPE, and ROUTE_NUMBER
    counties = list(county_dict.keys())

    route_types = set(row['FINAL_ROUTE_TYPE'] for row in data)
    route_numbers = set(row['ROUTE_NUMBER'] for row in data)

    # Extract unique MILEPOINT values (you may need to adjust this based on your specific use case)
    milepoints = set(row['MILEPOINT'] for row in data)
    intersecting_road = set(row['ROAD_NAME'] for row in data)
    selected_option = request.form['selection']

    if selected_option == 'segment':
        return render_template('segment_form.html', counties=counties, route_types=route_types, route_numbers=route_numbers, milepoints=milepoints,data =data,county_dict=county_dict)
    elif selected_option == 'intersection':
        return render_template('intersection_form.html', counties=counties, route_types=route_types, route_numbers=route_numbers, milepoints=milepoints,data =data,county_dict=county_dict,intersecting_road=intersecting_road)
    # return render_template('table.html')


@app.route('/segment' , methods=['GET','POST'])
def segment():
    if request.method == 'POST':
        county_name = request.form.get('county', '')
        route_type = request.form.get('route_type', '')
        route_number = request.form.get('route_number', '')
        route_suffix =  request.form.get('route_suffix', '')
        milepoint_from = request.form.get('milepoint_from', 0)
        milepoint_to = request.form.get('milepoint_to', 10000)
        s_from_date = request.form['from_date']
        s_to_date = request.form['to_date']
        session['milepoint_to'] = milepoint_to
        session['milepoint_from'] = milepoint_from
        session['route_number'] = route_number
        session['route_suffix'] = route_suffix
        session['route_type'] = route_type
        session['s_from_date'] = s_from_date
        session['s_to_date'] = s_to_date
        df = read_data()
        df = df[['COUNTY', 'FINAL_ROUTE_TYPE', 'ROUTE_NUMBER','ROUTE_SUFFIX', 'MILEPOINT']]
        COUNTY = get_county_code(county_name)
        session['COUNTY'] = COUNTY
        df = df[(df['COUNTY'].astype(int) == COUNTY) & 
            (df['FINAL_ROUTE_TYPE'] == route_type) & 
            (df['ROUTE_NUMBER'].astype(int) == int(route_number))& 
            (df['ROUTE_SUFFIX'] == route_suffix)&
            (df['MILEPOINT'].astype(float) >= float(milepoint_from))&
            (df['MILEPOINT'].astype(float) <= float(milepoint_to))
            ]
        
        df = df.sort_values(by='MILEPOINT', ascending=True)
        df_json = df.to_json()
        
        # Convert the JSON string to a Python object
        data_dict = json.loads(df_json)

        # Check if all inner dictionaries in 'data' are empty
        if all(not bool(value) for value in data_dict.values()):
            message = "No road segments identified based on the input. Please check the input."
        else:
            message = None 

        response = {
            'message': message,
            'data': json.loads(df_json)
        }

        # Return the response as JSON
        return jsonify(response)

    # If the request method is GET, render the form template
    return render_template('segment_form.html')

@app.route('/intersection', methods=['GET','POST'])
def intersection():
    if request.method == 'POST':
        county_name = request.form.get('county', '')
        route_type = request.form.get('route_type', '')
        route_number = request.form.get('route_number', '')
        route_suffix =  request.form.get('route_suffix', '')
        milepoint = request.form.get('milepoint', '')
        i_from_date = request.form['from_date']
        i_to_date = request.form['to_date']
        session['route_type'] = route_type
        session['route_number'] = route_number
        session['route_suffix'] = route_suffix
        session['i_from_date'] = i_from_date
        session['i_to_date'] = i_to_date
        session['radius'] = request.form['radius']
        session['milepoint'] = milepoint
        df = read_data()
        df = df[['COUNTY', 'FINAL_ROUTE_TYPE', 'ROUTE_NUMBER', 'ROUTE_SUFFIX', 'MILEPOINT']]
        county = get_county_code(county_name)
        session['COUNTY'] = county
        df = df[(df['COUNTY'].astype(int) == int(county)) &
                (df['FINAL_ROUTE_TYPE'] == route_type) &
                (df['ROUTE_NUMBER'].astype(int) == int(route_number)) &
                (df['ROUTE_SUFFIX'] == route_suffix) 
              ]

        df_json = df.to_json()

        response = {
            'data': json.loads(df_json)
        }

        # Return the response as JSON
        return jsonify(response)
    

    return render_template('intersection_form.html')



@app.route('/segment/crash', methods=['GET','POST'])
def crash():
    values = ['Left turn','Rear end','Angle',  'Sideswipe','Fixed object-offroad','Pedestrian','Opposite direction','others']
    return render_template('segment_crash.html', values=values)

@app.route('/segment/crash/submit', methods=['POST'])
def segmentcrash():
    data = read_crash_data()
    # first_data, second_data
    checkbox_values = request.form.getlist('checkbox_values')
    cons_to_date = request.form['s_to_date']
    cons_from_date = request.form['s_from_date']
    milepoint_to = request.form['milepoint_to'] 
    route_number = request.form['route_number'] 
    route_suffix = request.form['route_suffix']  
    route_type = request.form['route_type']   
    county = request.form['COUNTY']
    milepoint_from = request.form['milepoint_from'] 
    bpyears = int(request.form['bpyears'])
    bpmonths = int(request.form['bpmonth'])
    bbtmonths = int(request.form['bbtmonths'])
    abtmonths = int(request.form['abtmonths'])
    Apyears = int(request.form['Apyears'])
    Apmonths = int(request.form['Apmonth'])
    

    cons_date_from = pd.Timestamp(cons_from_date)
    cons_date_to = pd.Timestamp(cons_to_date)
    first_date = cons_date_from - pd.DateOffset(years=bpyears, months=bpmonths)
    second_date = cons_date_from - pd.DateOffset(months=bbtmonths)
    third_date = cons_date_to + pd.DateOffset(months=abtmonths)
    fourth_date = cons_date_to + pd.DateOffset(years=Apyears, months=Apmonths)
    beforeperiodcrash = {c: 0 for c in ['Left turn', 'Rear end', 'Angle', 'Sideswipe', 'Fixed object-offroad', 'Pedestrian', 'Opposite direction', 'others']}
    afterperiodcrash = {c: 0 for c in ['Left turn', 'Rear end', 'Angle', 'Sideswipe', 'Fixed object-offroad', 'Pedestrian', 'Opposite direction', 'others']}
    beforeperiodseverity = {c: 0 for c in [1, 2, 3, 4, 5]}
    afterperiodseverity = {c: 0 for c in [1,2,3,4,5]}
    data = data[['DS_KEY', 'ACC_DATE','COUNTY_NO','ROUTE_TYPE_CODE', 'ROUTE_NUMBER','ROUTE_SUFFIX','collisiontype','severity','severity_index' ,'final_log_mile','flag','nighttime','wet_surface','intersection_related']]
    data['ACC_DATE'] = pd.to_datetime(data['ACC_DATE'])
    data = data[(data['ROUTE_NUMBER'].astype(int) == int(route_number)) & (data['ROUTE_TYPE_CODE'] == route_type) &
                (data['ROUTE_SUFFIX'] == route_suffix) & (data['COUNTY_NO'].astype(int) == int(county))& (data['final_log_mile'] >= int(milepoint_from)) & 
                (data['final_log_mile'] <= int(milepoint_to))]
    first_data = data[((data['ACC_DATE'] >= first_date)&(data['ACC_DATE']<second_date) )]  
    second_data = data[((data['ACC_DATE'] > third_date) & (data['ACC_DATE']<=fourth_date))]
    for index,row in first_data.iterrows():
        if row['collisiontype'] in beforeperiodcrash:
            beforeperiodcrash[row['collisiontype']] += 1
        else:
            beforeperiodcrash['others'] += 1
        
    for index,row in second_data.iterrows():
        if row['collisiontype'] in afterperiodcrash:
            afterperiodcrash[row['collisiontype']] += 1
        else:
            afterperiodcrash['others'] += 1
        
    
    for index,row in first_data.iterrows():
        beforeperiodseverity[row['severity']] += 1
        
    for index,row in second_data.iterrows():
        afterperiodseverity[row['severity']] += 1
   
    print(beforeperiodcrash)
    print(afterperiodcrash)
    print(beforeperiodseverity)
    print(afterperiodseverity)
    print(type(beforeperiodseverity))
    print("milepoint_to:", milepoint_to)
    print("Checkbox values:", checkbox_values)
    print("From date:", cons_from_date)
    print("To date:", cons_to_date)
    print("First date:",first_date)
    print("Second date:",second_date)
    print("Third date:",third_date)
    print("Fourth date:",fourth_date)
    # No need for intermediate conversion to JSON strings
   
    first_data['ACC_DATE'] = first_data['ACC_DATE'].dt.strftime('%Y-%m-%d %H:%M:%S')
    second_data['ACC_DATE'] = second_data['ACC_DATE'].dt.strftime('%Y-%m-%d %H:%M:%S')

    
    return json.dumps({
        'beforeperiodcrash': beforeperiodcrash,
        'afterperiodcrash': afterperiodcrash,
        'beforeperiodseverity': beforeperiodseverity,
        'afterperiodseverity': afterperiodseverity,
        'first_data': first_data.to_dict(orient='records'),
        'second_data': second_data.to_dict(orient='records')
     })

    

@app.route('/intersection/crash', methods=['GET', 'POST'])
def intersection_crash():
    values = ['Left turn', 'Rear end', 'Angle', 'Sideswipe', 'Fixed object-offroad', 'Pedestrian', 'Opposite direction', 'others']
    return render_template('intersection_crash.html', values=values)

@app.route('/intersection/crash/submit', methods=['POST'])
def intersection_crash_submit():
    data = read_crash_data()
    first_data, second_data
    checkbox_values = request.form.getlist('checkbox_values')
    cons_to_date = session.get('i_to_date')
    cons_from_date = session.get('i_from_date')
    milepoint = session.get('milepoint')
    radius = session.get('radius')
    route_number = session.get('route_number')
    route_suffix = session.get('route_suffix')
    route_type = session.get('route_type')
    county = session.get('COUNTY')
    bpyears = int(request.form['bpyears'])
    bpmonths = int(request.form['bpmonth'])
    bbtmonths = int(request.form['bbtmonths'])
    abtmonths = int(request.form['abtmonths'])
    Apyears = int(request.form['Apyears'])
    Apmonths = int(request.form['Apmonth'])
    milepoint_from = float(milepoint) - (float(radius)/5280)
    milepoint_to = float(milepoint) + (float(radius)/5280)
    cons_date_from = pd.Timestamp(cons_from_date)
    cons_date_to = pd.Timestamp(cons_to_date)
    first_date = cons_date_from - pd.DateOffset(years=bpyears, months=bpmonths)
    second_date = cons_date_from - pd.DateOffset(months=bbtmonths)
    third_date = cons_date_to + pd.DateOffset(months=abtmonths)
    fourth_date = cons_date_to + pd.DateOffset(years=Apyears, months=Apmonths)
    beforeperiodcrash = {c: 0 for c in ['Left turn', 'Rear end', 'Angle', 'Sideswipe', 'Fixed object-offroad', 'Pedestrian', 'Opposite direction', 'others']}
    afterperiodcrash = {c: 0 for c in ['Left turn', 'Rear end', 'Angle', 'Sideswipe', 'Fixed object-offroad', 'Pedestrian', 'Opposite direction', 'others']}
    beforeperiodseverity = {c: 0 for c in [1, 2, 3, 4, 5]}
    afterperiodseverity = {c: 0 for c in [1,2,3,4,5]}
    data = data[['DS_KEY', 'ACC_DATE','COUNTY_NO','ROUTE_TYPE_CODE', 'ROUTE_NUMBER','ROUTE_SUFFIX','collisiontype','severity','severity_index' ,'final_log_mile','flag']]
    data['ACC_DATE'] = pd.to_datetime(data['ACC_DATE'])
    data = data[(data['ROUTE_NUMBER'].astype(int) == int(route_number)) & (data['ROUTE_TYPE_CODE'] == route_type) &
                (data['ROUTE_SUFFIX'] == route_suffix) & (data['COUNTY_NO'].astype(int) == int(county))&(data['final_log_mile'] >= int(milepoint_from)) & 
                (data['final_log_mile'] <= int(milepoint_to))& (data['collisiontype'].isin(checkbox_values))]
    first_data = data[((data['ACC_DATE'] >= first_date)&(data['ACC_DATE']<second_date) )]  
    second_data = data[((data['ACC_DATE'] > third_date) & (data['ACC_DATE']<=fourth_date))]
    for index,row in first_data.iterrows():
        beforeperiodcrash[row['collisiontype']] += 1
    for index,row in second_data.iterrows():
        afterperiodcrash[row['collisiontype']] += 1
    
    for index,row in first_data.iterrows():
        beforeperiodseverity[row['severity']] += 1
        
    for index,row in second_data.iterrows():
        afterperiodseverity[row['severity']] += 1
    print(beforeperiodcrash)
    print(afterperiodcrash)
    print(beforeperiodseverity)
    print(afterperiodseverity)
    beforeperiodcrash_json = json.dumps(beforeperiodcrash, indent=4)
    afterperiodcrash_json = json.dumps(afterperiodcrash, indent=4)
    beforeperiodseverity_json = json.dumps(beforeperiodseverity, indent=4)
    afterperiodseverity_json = json.dumps(afterperiodseverity, indent=4)

    # Return JSON responses
    return jsonify(
        beforeperiodcrash=json.loads(beforeperiodcrash_json),
        afterperiodcrash=json.loads(afterperiodcrash_json),
        beforeperiodseverity=json.loads(beforeperiodseverity_json),
        afterperiodseverity=json.loads(afterperiodseverity_json)
    )
    
@app.route('/segment/crash/checkbox', methods=[ 'POST'])
# @app.route('/intersection/crash/checkbox', methods=['GET', 'POST'])
def display_checkbox(first_data, second_data):
    print(first_data.head(10))
    severity_checkbox_values = [1,2,3]
    print(first_data.head(10))
    # Filter the data based on the selected checkbox values
    
    first_data_filtered = first_data[first_data['severity'].isin(severity_checkbox_values)]
    second_data_filtered = second_data[second_data['severity'].isin(severity_checkbox_values)]
    print(first_data_filtered.head(10))
    first_data_filtered = first_data_filtered.head(10)
    # Convert the filtered data to JSON and return it
    return first_data_filtered, second_data_filtered


if __name__ == '__main__':
    app.run(debug=True)
