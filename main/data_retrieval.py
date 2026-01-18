import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import os
import department_mapping2
import gophish_run
def get_access_token():
    params = {
        'grant_type':'client_credentials',
        'client_id':'SNOV.IO CLIENT ID',
        'client_secret': 'SNOV.IO CLIENT SECRET'
    }

    res = requests.post('https://api.snov.io/v1/oauth/access_token', data=params)
    resText = res.text.encode('ascii','ignore')

    return json.loads(resText)

token = get_access_token()["access_token"]
headers = {'authorization': f'Bearer {token}'}

def company_info_result(task_hash):

	res = requests.get(f'https://api.snov.io/v2/domain-search/result/{task_hash}', headers=headers)
	return json.loads(res.text)

def company_info_search(domain):
	params = {
	'domain': domain,
	}

	res = requests.post('https://api.snov.io/v2/domain-search/start', params=params, headers=headers)
	return company_info_result(json.loads(res.text))

def prospects_search(domain):
	params = {
	'domain': domain,
	'page': 1,
	}

	res = requests.post('https://api.snov.io/v2/domain-search/prospects/start', params=params, headers=headers)

	return prospects_result(json.loads(res.text)["meta"]["task_hash"])

def prospects_result(task_hash):

	res = requests.get(f'https://api.snov.io/v2/domain-search/prospects/result/{task_hash}', headers=headers)

	return json.loads(res.text)



def search_prospect_emails_start(getemail):

	res = requests.post(getemail, headers=headers)
	return json.loads(res.text)

def search_prospect_emails_result(getemail):
	task_hash = search_prospect_emails_start(getemail)["meta"]["task_hash"]

	res = requests.get(f'https://api.snov.io/v2/domain-search/prospects/search-emails/result/{task_hash}', headers=headers)

	print(json.loads(res.text))



def allinforetriever(domain):
	if not os.path.exists(domain):
		
		company_info = company_info_search(domain)
		prospects = prospects_search(domain)

		for i in prospects["data"]:
			if 'search_emails_start' in i:
				search_prospect_emails_result(i["search_emails_start"])
		prospects = prospects_search(domain)
		os.mkdir(domain)
		with open(f"{domain}/company_info.json","w") as file:
			file.write(json.dumps(company_info))
	with open('www.nibl.com.np/prospects.json', 'r', encoding='utf-8') as file:
		prospects = json.load(file)
		final_data = department_mapping2.process_people_safely(prospects)
		gophish_run.create_groups_by_department(final_data)
		prospects["data"] = final_data
		with open(f"{domain}/prospects.json","w") as file:
			file.write(json.dumps(prospects))
