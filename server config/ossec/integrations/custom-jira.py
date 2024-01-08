#!/var/ossec/framework/python/bin/python3

import sys
import json
import requests
from requests.auth import HTTPBasicAuth

# Read configuration parameters
alert_file = open(sys.argv[1])
user = 'evgeniq.grigorova99@gmail.com'
api_key = 'ATATT3xFfGF0Yv80R2W1UkIXcYWI7hqmJrtOYQ9vw90ltpglpdCaXybkWBPmOv48FKbAiUFV9KEAaO5k-2Cptr04hE4AJaeYBNOoIaXx_RhI95iY04PJxJ4PcohRBSQUMiZs7nCyoPx2yfS7xbEH23Q-3IbiGWg30qZkJz686mMJh_h_f1ymL8w=F66AF392'
hook_url = 'https://test-wazuh.atlassian.net/rest/api/3/issue/'

# Read the alert file
alert_json = json.loads(alert_file.read())
alert_file.close()

# Extract issue fields
alert_level = alert_json['rule']['level']
ruleid = alert_json['rule']['id']
description = alert_json['rule']['description']
agentid = alert_json['agent']['id']
agentname = alert_json['agent']['name']
agentip = alert_json['agent']['ip']
#previous_output = alert_json['previous_output']

# Fields for vulnerability tickets
vuln_description = ''
if 'data' in alert_json and 'vulnerability' in alert_json['data']:
    vuln_data = alert_json['data']['vulnerability']
    if 'rationale' in vuln_data:
        vuln_description = (
            f"\n- CVSS3 Base score: {vuln_data['cvss']['cvss3']['base_score']}"
            f"\n- CVSS3 Exploitability score: {vuln_data['cvss']['cvss3']['exploitability_score']}"
            f"\n- CVSS3 Impact score: {vuln_data['cvss']['cvss3']['impact_score']}"
            f"\n- Vulnerability description: {vuln_data['rationale']}"
            f"\n- Vulnerability references: {', '.join(vuln_data['references'])}"
        )

# Base fields
base_description = '- State: ' + description + \
                   '\n- Rule ID: ' + str(ruleid) + \
                   '\n- Alert level: ' + str(alert_level) + \
                   '\n- Agent: ' + str(agentid) + ' ' + agentname + \
		   '\n'


# Check for 'data.win.eventdata.scriptBlockText' and append if exists
if 'data' in alert_json and 'win' in alert_json['data'] and 'eventdata' in alert_json['data']['win'] and 'scriptBlockText' in alert_json['data']['win']['eventdata']:
    script_block_text = alert_json['data']['win']['eventdata']['scriptBlockText']
    base_description += f"- Script Block Text: {script_block_text}\n"

# Check for 'previous_output' and append if exists
if 'previous_output' in alert_json:
    previous_output = alert_json['previous_output']
    base_description += f"- Previous Output: {previous_output}\n"

complete_description = base_description + vuln_description if vuln_description else base_description 

# Set the project attributes
project_key = 'WAZ'
issuetypeid = '10008'

# Generate request
headers = {'content-type': 'application/json'}
issue_data = {
    "update": {},
    "fields": {
        "summary": 'Wazuh Alert: [' + agentname + ': ' + description + ']',
        "issuetype": {
            "id": issuetypeid
        },
        "project": {
            "key": project_key
        },
        "description": {
            'version': 1,
            'type': 'doc',
            'content':  [
                    {
                      "type": "paragraph",
                      "content": [
                        {
                          "text": complete_description,
                          "type": "text"
                        }
                      ]
                    }
                  ],
        },
    }
}

# Send the request
response = requests.post(hook_url, data=json.dumps(issue_data), headers=headers, auth=(user, api_key))

sys.exit(0)