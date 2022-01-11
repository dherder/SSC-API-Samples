import requests
import json
import pandas as pd

# What does this script do?
# The script consumes a csv file with domain, start date, end date values.
# The intention is to extract events for that domain in question into separate
# events.json files where further analysis can be performed against the
# detail_url if required. 

# SecurityScorecard Contributor: Dave Herder

#filename = "Companies.csv"

token = ''


data = pd.read_csv('companies.csv')
df = data[['Company Domain','Start Date','End Date']]
arr = df.values
#print(arr)
lst = []

for x in arr:
    events_url = 'https://api.securityscorecard.io/companies/'+x[0]+'/history/events/?date_from='+x[1]+'T00:00:00.000Z&date_to='+x[2]+'T00:00:00.000Z'
    headers = {"Accept": "application/json; charset=utf-8",'Authorization': 'Token ' + token}
    response = requests.get(events_url, headers=headers).json()
    lst.extend(response['entries'])
    print(lst)

with open('events.json','w') as outfile:
    json.dump(lst, outfile, indent=4, sort_keys=True)
