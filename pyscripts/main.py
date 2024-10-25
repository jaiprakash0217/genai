{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "from openai import AzureOpenAI\n",
    "import pandas as pd"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Configuration of the API parameters\n",
    "deployment_name = 'gpt-4o'\n",
    "endpoint = 'allinone-oai-sql'\n",
    "key = '5e91f5ecba35458d992b5c51b11643f8'\n",
    "version = '2024-05-13'"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Reading the csv files extracted from KPI database\n",
    "df_kpi = pd.read_csv('KibaliValues.csv')\n",
    "df_issues = pd.read_csv('KibaliKeyIssues.csv')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "def kpi_context_creation(df_kpi, df_issues):\n",
    "\n",
    "    # Building the context template for KPIs\n",
    "    kpi_context_template = \"\"\"\n",
    "    For the KPI {kpi_name} for this week we forcasted that we will have for each day of the week accordingly: {daily_forecasts}\n",
    "    However, we actually achieved the following values per day of the week: {daily_values}\n",
    "    \"\"\"\n",
    "    # Building the context template for key issues\n",
    "    key_issues_context_template = \"\"\"\n",
    "    Having the follwing issues: {issues} with key issue names {issue_name} and corresponding actions {issue_action} happend on {issue_date}\n",
    "    \"\"\"\n",
    "\n",
    "    context_info = []\n",
    "    # Find the unique KPIs of the page\n",
    "    kpis = df_kpi.kpi_name.unique().tolist()\n",
    "    # Finding the top 3 KPIs\n",
    "    kpis = kpis[:3]\n",
    "\n",
    "    for kpi in kpis:\n",
    "        # Create the dictionary for these info\n",
    "        week_info = {}\n",
    "        week_info['kpi_name'] = kpi\n",
    "        # Find the daily actuals subset of each kpi\n",
    "        week_info['daily_values'] = df_kpi[(df_kpi['kpi_name'] == kpi) & (df_kpi['value_type'] == 'DailyActual')].value.to_list()\n",
    "        # Find the daily actuals subset of each kpi\n",
    "        week_info['daily_forecasts'] = df_kpi[(df_kpi['kpi_name'] == kpi) & (df_kpi['value_type'] == 'DailyForecast')].value.to_list()\n",
    "        \n",
    "        context_info.append(week_info)\n",
    "\n",
    "\n",
    "    # Getting issues info\n",
    "    key_issues_dict = {}\n",
    "    key_issues_dict['issues'] = df_issues.description.to_list()\n",
    "    key_issues_dict['issue_name'] = df_issues.key_issue_name.to_list()\n",
    "    key_issues_dict['issue_action'] = df_issues.action.to_list()\n",
    "    key_issues_dict['issue_date'] = df_issues.full_date.to_list()\n",
    "\n",
    "\n",
    "    # Great the context prompt\n",
    "    context_text = ''\n",
    "    for  item in context_info:\n",
    "        context_text = context_text + kpi_context_template.format(**item)\n",
    "\n",
    "    context_text += key_issues_context_template.format(**key_issues_dict)\n",
    "\n",
    "    return context_text"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create the prompt template\n",
    "llm_prompt_template = \"\"\"Please summarize the context provided below comparing the weekly forcasted values with the actuals and along with any issue occured\n",
    " an to create a weekly summary to explaine the weekly performance of the mine:\n",
    "\n",
    "CONTEXT:\n",
    "{}\n",
    "\"\"\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create the context \n",
    "context = kpi_context_creation(df_kpi, df_issues)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create the prompt for LLM\n",
    "llm_prompt= llm_prompt_template.format(context)\n",
    "print(llm_prompt)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import requests\n",
    "import base64\n",
    " \n",
    "def ask_llm(llm_prompt):\n",
    "\n",
    "  # Configuration\n",
    "  API_KEY = '5e91f5ecba35458d992b5c51b11643f8'\n",
    "  #IMAGE_PATH = \"YOUR_IMAGE_PATH\"\n",
    "  #encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')\n",
    "  headers = {\n",
    "      \"Content-Type\": \"application/json\",\n",
    "      \"api-key\": API_KEY,\n",
    "  }\n",
    "  \n",
    "  # Payload for the request\n",
    "  payload = {\n",
    "    \"messages\": [\n",
    "      {\n",
    "        \"role\": \"system\",\n",
    "        \"content\": [\n",
    "          {\n",
    "            \"type\": \"text\",\n",
    "            \"text\": \"You are a senior geologist working as a mine GM.\"\n",
    "          }\n",
    "        ]\n",
    "      },\n",
    "      {\n",
    "        \"role\": \"user\",\n",
    "        \"content\": [\n",
    "          {\n",
    "            \"type\": \"text\",\n",
    "            \"text\": llm_prompt\n",
    "          }\n",
    "        ]\n",
    "      }\n",
    "    ],\n",
    "    \"temperature\": 0.7,\n",
    "    \"top_p\": 0.95,\n",
    "    \"max_tokens\": 800\n",
    "  }\n",
    "  \n",
    "  ENDPOINT = \"https://allinone-oai-sql.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview\"\n",
    "  \n",
    "  # Send request\n",
    "  try:\n",
    "      response = requests.post(ENDPOINT, headers=headers, json=payload)\n",
    "      response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code\n",
    "  except requests.RequestException as e:\n",
    "      raise SystemExit(f\"Failed to make the request. Error: {e}\")\n",
    "  \n",
    "  # Parse the API response\n",
    "  generated_text = response.json()['choices'][0]['message']['content']\n",
    "\n",
    "  # Print the response\n",
    "  return generated_text"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "summary = ask_llm(llm_prompt)\n",
    "print(summary)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
           "from pyscript import Element\n",
           "def print_hello(event):\n",
           "Element('output').write('Hello, World!')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
