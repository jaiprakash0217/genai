import pandas as pd

# Configuration of the API parameters
deployment_name = 'gpt-4o'
endpoint = 'allinone-oai-sql'
key = '5e91f5ecba35458d992b5c51b11643f8'
version = '2024-05-13'

# Reading the csv files extracted from KPI database
df_kpi = pd.read_csv('KibaliValues.csv')
df_issues = pd.read_csv('KibaliKeyIssues.csv')

def kpi_context_creation(df_kpi, df_issues):

    # Building the context template for KPIs
    kpi_context_template = "For the KPI {kpi_name} for this week we forcasted that we will have for each day of the week accordingly: {daily_forecasts} However, we actually achieved the following values per day of the week: {daily_values}"
    # Building the context template for key issues
    key_issues_context_template = "Having the follwing issues: {issues} with key issue names {issue_name} and corresponding actions {issue_action} happend on {issue_date}"

    context_info = []
    # Find the unique KPIs of the page
    kpis = df_kpi.kpi_name.unique().tolist()
    # Finding the top 3 KPIs
    kpis = kpis[:3]

    for kpi in kpis:
        # Create the dictionary for these info
        week_info = {}
        week_info['kpi_name'] = kpi
        # Find the daily actuals subset of each kpi
        week_info['daily_values'] = df_kpi[(df_kpi['kpi_name'] == kpi) & (df_kpi['value_type'] == 'DailyActual')].value.to_list()
        # Find the daily actuals subset of each kpi
        week_info['daily_forecasts'] = df_kpi[(df_kpi['kpi_name'] == kpi) & (df_kpi['value_type'] == 'DailyForecast')].value.to_list()
        context_info.append(week_info)
    # Getting issues info
    key_issues_dict = {}
    key_issues_dict['issues'] = df_issues.description.to_list()
    key_issues_dict['issue_name'] = df_issues.key_issue_name.to_list()
    key_issues_dict['issue_action'] = df_issues.action.to_list()
    key_issues_dict['issue_date'] = df_issues.full_date.to_list()
    # Great the context prompt
    context_text = ''
    for  item in context_info:
        context_text = context_text + kpi_context_template.format(**item)
    context_text += key_issues_context_template.format(**key_issues_dict)
    return context_text
# Create the prompt template
llm_prompt_template = "Please summarize the context provided below comparing the weekly forcasted values with the actuals and along with any issue occured an to create a weekly summary to explaine the weekly performance of the mine: CONTEXT:{}"
# Create the context 
context = kpi_context_creation(df_kpi, df_issues)

# Create the prompt for LLM
llm_prompt= llm_prompt_template.format(context)
print(llm_prompt)

import requests
import asyncio
import js
from pyodide.http import pyfetch 
async def ask_llm(llm_prompt):

  # Configuration
  API_KEY = '5e91f5ecba35458d992b5c51b11643f8'
  headers = {
      "Content-Type": "application/json",
      "api-key": API_KEY
  }
  import re
  # Payload for the request - "api-key": API_KEY,
  payload ={"messages":[{"role":"system","content":[{"type":"text","text":re.escape(llm_prompt)}]}],"temperature":0.7,"top_p":0.95,"max_tokens":800}
  
  ENDPOINT = "https://allinone-oai-sql.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"

  # Send request
  #try:
  response = requests.post(ENDPOINT, headers=headers, json=payload)
  response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
  #response = await pyfetch(ENDPOINT, method="POST", headers=headers, body=payload)
  #result = await response.json()
  #js.document.getElementById("output").innerText = result["choices"][0]["text"]    
  #except requests.RequestException as e:
  #    raise SystemExit(f"Failed to make the request. Error: {e}")
  
  # Parse the API response
  generated_text = response.json()['choices'][0]['message']['content']

  # Print the response
  Element('output').write(generated_text) 

from pyscript import Element
def print_hello(event):
    Element('output').write('Hello, World!')
