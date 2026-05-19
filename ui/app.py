from __future__ import annotations
import os
import requests
import streamlit as st

API_URL = os.environ.get('COPILOT_API_URL', 'http://localhost:8000/analyze-case')

st.set_page_config(page_title='B2B Resolution Copilot', layout='wide')
st.title('B2B Resolution Copilot')
st.caption('Retrieve similar precedents, guide frontline teams, and escalate truly novel client issues.')

with st.sidebar:
    st.header('Scenario')
    scenario = st.selectbox('Choose a demo scenario', ['Known gift issue', 'Missing context', 'Novel refund issue'])

examples = {
    'Known gift issue': {
        'client_company': 'Alpine Robotics SA',
        'requester_role': 'HR Operations Manager',
        'channel': 'email',
        'subject': 'Gift budget cannot be assigned to one employee',
        'message': 'We tried to distribute a CHF 100 reward to a new employee, but the platform rejects the action. The employee was added yesterday and appears active in our HR export.',
        'metadata': {'employee_created_recently': True, 'gift_amount_chf': 100, 'employee_identifier_present': True, 'account_identifier_present': True}
    },
    'Missing context': {
        'client_company': 'Helvetia Labs AG',
        'requester_role': 'People Ops',
        'channel': 'form',
        'subject': 'Portal issue',
        'message': 'Something does not work. Please help.',
        'metadata': {'employee_identifier_present': False, 'account_identifier_present': False}
    },
    'Novel refund issue': {
        'client_company': 'Romandie Mobility SA',
        'requester_role': 'Finance & Benefits Lead',
        'channel': 'email',
        'subject': 'Card balance mismatch after a reversed food purchase',
        'message': 'A user reports that a restaurant transaction was reversed by the merchant, but the available card balance appears unchanged after 48 hours. We cannot tell whether the amount should already have been credited back.',
        'metadata': {'employee_identifier_present': True, 'account_identifier_present': True}
    }
}

payload = examples[scenario]
left, right = st.columns([1, 1])
with left:
    st.subheader('Incoming client issue')
    payload['client_company'] = st.text_input('Client company', payload['client_company'])
    payload['requester_role'] = st.text_input('Requester role', payload['requester_role'])
    payload['subject'] = st.text_input('Subject', payload['subject'])
    payload['message'] = st.text_area('Message', payload['message'], height=180)
    run = st.button('Analyze case', type='primary')

with right:
    st.subheader('Copilot output')
    if run:
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            st.metric('Decision', data['decision'])
            st.metric('Confidence', f"{data['confidence']:.0%}")
            st.write('**Operator summary**')
            st.write(data['operator_summary'])
            st.write('**Recommended steps**')
            for step in data['recommended_steps']:
                st.write(f'- {step}')
            if data['clarifying_questions']:
                st.write('**Clarifying questions**')
                for question in data['clarifying_questions']:
                    st.write(f'- {question}')
            st.write('**Draft client reply**')
            st.info(data['draft_client_reply'])
            st.write('**Similar cases**')
            st.json(data['similar_cases'])
            if data['ticket_payload']:
                st.write('**Generated escalation ticket**')
                st.json(data['ticket_payload'])
        except Exception as exc:
            st.error(f'Could not call the API: {exc}')
    else:
        st.info('Choose a scenario and click “Analyze case”.')
