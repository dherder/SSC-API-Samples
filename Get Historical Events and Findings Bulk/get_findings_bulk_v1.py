

# What does this script do?
# The script consumes a portfolio_id, start date, end date values.
# The intention is to extract events for scorecards within a portfolio of interest to an
# events.json file where further analysis can be performed against the
# detail_url if required.
# The purpose of this script is to be able to extract events from a historical perspective only.
# If you are interested in just active findings, do not use this script, as it returns active issues on the
# effective_date range queried, which may be differnt from the current date.

# SecurityScorecard Contributor: Dave Herder
# Date: 02-03-2022

import os
import requests
import sys
import json
import pandas as pd
from pandas import json_normalize
from datetime import datetime

ssc_token = ''
api_url = 'https://api.securityscorecard.io'

headers = {
    'Accept': 'application/json; charset=utf-8',
    'Content-Type': 'application/json',
    'Authorization': 'Token ' + ssc_token,
    'cache-control': 'no-cache',
    }

# get portfolios
portfolios_url = api_url + '/portfolios'
response = requests.get(portfolios_url, headers=headers)
portfolios = response.json()


# Step 1 Get Companies from a Portfolio
# Use a test portfolio first with only a few domains with relatively few findings.
portfolio_id = ''

# Step 2 Get Companies from a portfolio
# Scale the portfolio to a larger number of companies.
#portfolio_id = ''

companies_url = api_url + '/portfolios/' + portfolio_id + '/companies/'
response = requests.get(companies_url, headers=headers)
companies = response.json()
companies_df = json_normalize(companies['entries'])
#display(companies_df)

start_date = '2019-01-01'
end_date = '2022-02-28'

# Get all Events
companies_arr = companies_df.values
lst = []
for domain in companies_arr:
    #events_url = 'https://api.securityscorecard.io/companies/'+domain[0]+'/history/events/'
    events_url = 'https://api.securityscorecard.io/companies/'+domain[0]+'/history/events/?date_from='+start_date+'T00:00:00.000Z&date_to='+end_date+'T00:00:00.000Z'
    response = requests.get(events_url, headers=headers).json()
    events = response['entries']
    lst.extend(response['entries'])
events_df = json_normalize(lst)

#filter by event status
#is_active_event =  events_df['group_status']=='active'
all_vuln_issue_event =  ((events_df['issue_type']=='service_vuln_host_high') | (events_df['issue_type']=='service_vuln_host_medium') | (events_df['issue_type']=='service_vuln_host_low'))
#| events_df['group_status']=='resolved' &
#active_events = events_df[is_active_event]
all_events = events_df[all_vuln_issue_event]
#print(active_events)
print(all_events)

with open('events.json','w') as outfile:
    json.dump(lst, outfile, indent=4, sort_keys=True)

# new data frame with split value columns
#domain_split = active_events["detail_url"].str.split("/", 6, expand = True)
domain_split = all_events["detail_url"].str.split("/", 6, expand = True)


# making separate domain column split out of detail_url
#active_events["domain"]= domain_split[4]
all_events["domain"]= domain_split[4]

#display(active_events)

# Get Active Findings based on Events Table
# Improvement is required here to leverage a copied data frame instead of a filtered view.
#arr = active_events.values
arr = all_events.values

lst = []
results2 = []

for x in arr:
    detail_url = x[9]
    issue_type = x[6]
    issues_id = str(x[0])
    response = requests.get(detail_url, headers=headers).json()
    findings = response['entries']
    findings_df = json_normalize(findings)
    #print(findings_df)
    results2.append(findings_df)

domain_findings = pd.concat(results2, axis = 0)
#display(domain_findings)

date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
filename = str(portfolio_id+'_findings'+date+'.csv')

domain_findings.to_csv(filename, encoding='utf-8', index=False)
