import requests
import os
import csv

# What does this script do?
# Instead of bulk uploading, you can use this script to define a set of
# apex domains to add to a particular portfolio

# SecurityScorecard Contributor: Dave Herder

# Define your portfolio id:
portfolio_id = ''
url = 'https://api.securityscorecard.io/portfolios/'+portfolio_id+'/companies/'
token = 'Token <token>'

# Add csv with list of all domains to this applications folder called "domains.csv"
pathName1 ="my_csv.csv"
domain1 =[]
file = open(pathName1, "r", newline='')
reader = csv.reader(file)
for row in reader:
    for r in row:
        # print(row[0])
        domain1.append(r)
        print(r)


def create_multi_domains(domain):
    headers = {
        "Accept": "application/json; charset=utf-8",
        "Authorization": + token}
    for d in domain1:
        data = url+d
        print(data)
        response = requests.request("PUT", data , headers=headers)
        print(response.text)
        print(response.headers)
# run function
create_multi_domains(domain1)
