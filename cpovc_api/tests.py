# from django.test import TestCase
import requests
# from django.utils.timezone import utc
# Create your tests here.

# default=datetime.datetime(2019, 8, 23, 17, 59, 40, 153036, tzinfo=utc)

# url = 'http://localhost:8001/api/v1/crs/'
url = 'http://childprotection.go.ke/api/v1/crs/'
headers = {'Authorization': 'Token 6bd468e9cf676af76a2d1d3a8207ffa5080aefc2'}

data = {"county": "001", "constituency": "001", "case_category": "CDIS",
        "child_dob": "2010-06-15", "perpetrator": "PKNW",
        "child_first_name": "Susan", "child_surname": "Atieno",
        "case_landmark": "Near kiroboto primary",
        "case_narration": "Child was abducted", "child_sex": "SMAL",
        "reporter_first_name": "Mark", "reporter_surname": "Masai",
        "reporter_telephone": "254722166058",
        "reporter_county": "001", "reporter_sub_county": "001",
        "case_reporter": "CRSF", "organization_unit": "Helpline",
        "hh_economic_status": "UINC", "family_status": "FSUK",
        "mental_condition": "MNRM", "physical_condition": "PNRM",
        "other_condition": "CHNM", "risk_level": "RLMD",
        "case_date": "2019-10-14",
        "perpetrators": [{"relationship": "RCPT", "first_name": "James",
                          "surname": "Kamau", "sex": "SMAL"}],
        "caregivers": [{"relationship": "CGPM", "first_name": "Mama",
                        "surname": "Atieno", "sex": "SMAL"}],
        "case_details": [{'category': 'CIDS',
                          'place_of_event': 'PEHF',
                          'date_of_event': '2019-09-01',
                          'nature_of_event': 'OOEV'}]}

response = requests.post(url, json=data, headers=headers)
# data = {"case_id": "64d2a692-ef3c-11e9-98c6-d4258b5a3abb"}
# response = requests.get(url, params=data, headers=headers)

# print (response)
print('==' * 50, 'HEADERS', '==' * 50)
print (response.headers)
print ('\n')
print('==' * 50, 'CONTENT', '==' * 50)
print (response.content)

'''
case_id = 'f6e09348-c5d2-11e9-9018-d4258b5a3abb'
response = requests.get(url, params={"case_id": case_id}, headers=headers)

print (response)
print (response.headers)
print (response.content)
'''
