import json
import requests
import os
import urllib3


GOPHISH_URL = "https://127.0.0.1:3333"
API_KEY = "YOUR API KEY HERE"
HEADERS = {
	"Authorization": f"Bearer {API_KEY}",
	"Content-Type": "application/json"
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_prospects(path):
	with open(path, "r") as f:
		return json.load(f)

def get_existing_groups():
	resp = requests.get(
		f"{GOPHISH_URL}/api/groups/",
		headers=HEADERS,
		verify=False
	)
	resp.raise_for_status()
	return {g["name"]: g for g in resp.json()}


def extract_email(user):

    emails_field = user.get("emails")

    if not emails_field:
        return None

    if isinstance(emails_field, list):
        for e in emails_field:
            if isinstance(e, dict):
                email = e.get("email")
                if email:
                    return email
        return None

    if isinstance(emails_field, dict):
        emails_list = emails_field.get("emails", [])
        for e in emails_list:
            if isinstance(e, dict):
                email = e.get("email")
                if email:
                    return email

    return None



def create_group(name, targets):
	payload = {
		"name": name,
		"targets": targets
	}

	resp = requests.post(
		f"{GOPHISH_URL}/api/groups/",
		headers=HEADERS,
		json=payload,
		verify=False
	)
	resp.raise_for_status()
	return resp.json()["id"]

def update_group(group_id, name, targets):
	payload = {
		"id": group_id,
		"name": name,
		"targets": targets
	}

	resp = requests.put(
		f"{GOPHISH_URL}/api/groups/{group_id}",
		headers=HEADERS,
		json=payload,
		verify=False
	)
	resp.raise_for_status()


def create_groups_by_department(prospects):

	existing_groups = get_existing_groups()

	department_map = {}


	for p in prospects:
		dept = p.get("department", "Unknown")
		department_map.setdefault(dept, []).append(p)


	for department, users in department_map.items():

		targets = []

		for u in users:
			email = extract_email(u)
			if not email:
				continue

			targets.append({
				"first_name": u.get("first_name", ""),
				"last_name": u.get("last_name", ""),
				"email": email,
				"position": u.get("position", "")
			})

		if not targets:
			continue

		# 3. Create or update group
		if department in existing_groups:
			group = existing_groups[department]
			existing_emails = {t["email"] for t in group["targets"]}

			merged_targets = group["targets"] + [
				t for t in targets if t["email"] not in existing_emails
			]

			update_group(group["id"], department, merged_targets)

		else:
			create_group(department, targets)


