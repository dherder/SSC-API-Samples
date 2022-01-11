import os
import requests
import csv
import json
import time

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# What does this script do?
# It will consume an array of portfolios that you have access to and use your
# private portfolio to temporarily add domains in question. Once the pdf reports
# (Issues, Detail, Summary) are generated, the companies will be destructed from
# your private portfolio.
# Script Origin: Sean McLaughlin, Holman Enterprises
# SecurityScorecard Contributor: Dave Herder


my_token = ""
#token = os.getenv('')
api_url = 'https://api.securityscorecard.io'

domains = ['arifleet.ca']
file_count = 0
dFile = 0
noFile = 0

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Token ' + my_token,
    'cache-control': 'no-cache',
    }

# generate issues report
#url = api_url + '/reports/summary'
#payload = "{\"domain\": \"arifleet.com\"}"
#response = requests.request("POST", url, data=payload, headers=headers)
#print(response.text)

for domain in domains:
    print("\n++++ Processing " + str(domain))

    # get portfolios
    url = api_url + '/portfolios'
    response = requests.get(api_url + '/portfolios', headers=headers, verify=False)
    response.raise_for_status()

    portfolios = response.json()['entries']
    my_portfolio = [
        item for item in portfolios
        # My Portfolio is read_only and private
        if 'read_only' in item and item['read_only'] == True and item['privacy'] == 'private'][0]

    # add arifleet.com to the portfolio
    print("+++ Adding " + str(domain) + " to portfolio group")
    url = api_url + '/portfolios/' + my_portfolio['id'] + '/companies/' + domain
    response = requests.put(url, headers=headers, verify=False)
    response.raise_for_status()

    # generate issues report
    print("+++ Generating Summary Report for " + str(domain))
    url = api_url + '/reports/summary'
    payload = "{\"domain\": \"" + str(domain) + "\"}"
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    file_count += 1

    # generate issues report
    print("+++ Generating Detailed Report for " + str(domain))
    url = api_url + '/reports/detailed'
    payload = "{\"domain\": \"" + str(domain) + "\"}"
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    file_count += 1

    # generate issues report
    print("+++ Generating Issues Report for " + str(domain))
    url = api_url + '/reports/issues'
    payload = "{\"domain\": \"" + str(domain) + "\"}"
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    file_count += 1

    # delete arifleet.com to the portfolio
    print("++++ Deleting " + str(domain) + " from portfolio group")
    url = api_url + '/portfolios/' + my_portfolio['id'] + '/companies/' + str(domain)
    response = requests.delete(url, headers=headers, verify=False)
    response.raise_for_status()


print("\n++++ Initiated Report Generation.  Total reports to download: " + str(file_count) + "\n")
#print("++++ Pausing Script for 60 Seconds to Allow for PDF Generation on SecurityScorecard's side...")
#print("++++ 60 Seconds...")
#time.sleep(60)
print("++++ Attempting to download Reports.")

# get list of recently generated reports
url = api_url + '/reports/recent'

response = requests.request("GET", url, headers=headers, verify=False)
responseLoad = response.content
responseJSON = json.loads(responseLoad)


while dFile != file_count:
    #print(responseJSON)
    print("++++ Beginning file # " + str(dFile + 1) + " of " + str(file_count))
    print("+++ File details :" + str(responseJSON['entries'][dFile]))

    if ('download_url' in (responseJSON['entries'][dFile])):
        try:
            print("+++ Retrieved path " + (responseJSON['entries'][dFile]['download_url']))
            get_file = requests.request("GET", responseJSON['entries'][dFile]['download_url'], headers=headers, verify=False)
            get_domain = str(responseJSON['entries'][dFile]['params']['domain'])
            file_name = get_domain + ' - '+ str(responseJSON['entries'][dFile]['title']) + '.pdf'

            with open(file_name, 'wb') as f:
                f.write(get_file.content)
                print("+++ Completed downloading file # " + str(dFile + 1) + " with Status Code: " + str(get_file.status_code))
                dFile += 1

                if (dFile + 1) < file_count:
                    print("++++ Pausing Script for 10 Seconds Before Downloading Next File...")
                    time.sleep(10)
                    #noFile = 0
                else:
                    #if (dFile + 1) == file_count:
                    print("++++ Report Download Attempts Completed.  Script Execution Completed.")
        except:
            print("Unable to process download URL for Report " + str(dFile +1))
            #noFile = 1
    else:
        print("++++ Pausing Script for 30 Seconds... Download URL Does Not Exist")
        time.sleep(15)
        response = requests.request("GET", url, headers=headers, verify=False)
        responseLoad = response.content
        responseJSON = json.loads(responseLoad)
    #if (noFile == 1):
    #    print("Skipping ..  File Does Not Exist")
