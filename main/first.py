import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import data_retrieval
import asyncio
ports =[]
def httpx_scan(URL_list):
	working = []
	for i in range(len(URL_list)):
		if URL_list[i].strip():
			httpx_output = subprocess.run(['httpx','-silent','-u',URL_list[i],'-json'],capture_output=True)
			httpx_output = httpx_output.stdout.decode("utf-8")
			if httpx_output.strip():
				working.append(URL_list[i])
	print("URL scan complete")
	return working

def obtain_subs(URL):
	sub_output = subprocess.run(['subfinder','-d', URL[1]],capture_output=True)
	print("URLs obtained")
	return sub_output.stdout.decode("utf-8").split("\n")

def naabu_scan(working_URL):

	ports_list = subprocess.run(['naabu','-silent','-host',working_URL,'-json','-nmap-cli','-sV'],capture_output=True)
	ports_list = ports_list.stdout.decode("utf-8")
	if ports_list.strip():
		ports.extend([line for line in ports_list.splitlines() if line.startswith('{')])


def multithreader(func, iterator):
	with ThreadPoolExecutor(max_workers=10) as executor:
		executor.map(func, iterator)

def email_validater(email_path):
	with open(email_path, "r") as f:
		data = json.load(f)
	email_list = data["emails"]
	open("validemails.json","w").close()
	for email in email_list:
		response = requests.post("http://localhost:8080/api/validate",json = {"email":email})
		email_info = response.json()
		if email_info["status"]=="VALID":
			with open("validemails.json","a") as file:
				file.write(response.text)

def port_scan(i):
	# print("start")
	httpx_output = subprocess.run(['httpx','-silent','-u',f'{json.loads(i)["host"]}:{json.loads(i)["port"]}','-follow-redirects','-mc', ",".join([f"{200+i}" for i in range(100)])],capture_output=True)
	httpx_output = httpx_output.stdout.decode("utf-8")
	
	if httpx_output.strip():
		asyncio.run(retrieve_html(i))

async def retrieve_html(info):
	info = json.loads(info)
	scheme = "https" if info["port"] == 443 else "http"
	url = f"{scheme}://{info['host']}"

	async with async_playwright() as p:
		browser = await p.chromium.launch(headless=True)
		page = await browser.new_page()

		await page.goto(url, wait_until="domcontentloaded", timeout=15000)

		desc_el = await page.query_selector('meta[name="description" i]')
		key_el  = await page.query_selector('meta[name="keywords" i]')

		meta_description = await desc_el.get_attribute("content") if desc_el else None
		meta_keywords = await key_el.get_attribute("content") if key_el else None

		inner_text = None
		
		inner_text = await page.evaluate("""() => document.body ? document.body.innerText : null""")
		await browser.close()
	with open(f"{sys.argv}/Domain_services.json","a") as f:

		f.write({
			"host": info["host"],
			"port": info["port"],
			"description": meta_description,
			"keywords": meta_keywords,
			"inner_text": inner_text
		})


data_retrieval.allinforetriever(sys.argv)
URL = obtain_subs(sys.argv)
URL = httpx_scan(URL)
multithreader(naabu_scan,URL)
multithreader(port_scan,ports)

