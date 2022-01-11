import requests
import json
import pandas as pd
from datetime import datetime

# What does this script do?
# Reads a csv with a list of domains and with a user defined issue type,
# will return a json file timestamped to script run date and current issues for that
# domain

# SecurityScorecard Contributor: Dave Herder
token = ''

#filename = "Companies.csv"

data = pd.read_csv('companies.csv')
df = data[['domain']]
arr = df.values
print(arr)
lst = []
#issue_type = 'cookie_missing_http_only'
issue_type = 'uses_go_daddy_managed_wordpress'


for x in arr:
    issues_url = 'https://api.securityscorecard.io/companies/'+x[0]+'/issues/'+issue_type
    headers = {"Accept": "application/json; charset=utf-8","Authorization": "Token " + token}
    response = requests.get(issues_url, headers=headers).json()
    #lst.extend(response['entries'])
    #print(lst)
    print(response)

date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
filename = str(issue_type+'issues'+date)

with open(filename,'w') as outfile:
    json.dump(response, outfile, indent=4, sort_keys=True)
