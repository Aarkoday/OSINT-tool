# import requests
import json
import department_mapping2

with open('www.nibl.com.np/prospects.json', 'r', encoding='utf-8') as file:
        
        prospects = json.load(file)
        # print(type(prospects))

# print(prospects["data"])
print(department_mapping2.process_people_safely(prospects))
