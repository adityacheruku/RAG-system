import streamlit as st
import requests
import json
import os

# --------- App Configuration --------- #
st.set_page_config(page_title="LLM-based RAG Search", layout="wide")

# --------- File Paths and Constants --------- #
history_file = "query_history.json"
flask_url = "http://localhost:5004/query"  # Flask API URL

# --------- Helper Functions --------- #

# Load query history from file
def load_history():
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            st.session_state['history'] = json.load(f)
    else:
        st.session_state['history'] = []

# Save query history to file
def save_history():
    with open(history_file, 'w') as f:
        json.dump(st.session_state['history'], f)

# Clear query history and remove file
def clear_history():
    st.session_state['history'] = []
    if os.path.exists(history_file):
        os.remove(history_file)
    st.success("History cleared.")

# Send query to Flask API and handle response
def execute_search(query):
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}
    # Avoid duplicate queries
    existing = next((chat for chat in st.session_state['history'] if chat['query'] == query), None)
    if existing:
        return existing['answer']
    try:
        print(payload)
        response = requests.post(flask_url, json=payload,headers = headers)
        print(response.status_code)
        print(response.text)
        if response.status_code == 200:
            answer = response.json().get('answer', "No answer received.")
            st.session_state['history'].append({'query': query, 'answer': answer})
            save_history()
            return answer
        else:
            st.error(f"Error: {response.status_code}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

# Clear input by re-running the app
def clear_input():
    st.session_state['query_input'] = ''
    st.rerun()  # Force the app to rerun to reflect the input clearing

# Display the query and answer after search
def display_query_and_answer(query, answer):
    st.markdown(f"""
        <div style='background-color: #182518; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>
            <strong style='color: #f5f5f4;'>Query:</strong> {query}
        </div>
        <div style='background-color: #182518; padding: 10px; border-radius: 10px; margin-bottom: 15px;'>
            <strong style='color: #f5f5f4;'>Answer:</strong> {answer}
    """, unsafe_allow_html=True)

# --------- App Initialization --------- #
if 'history' not in st.session_state:
    load_history()

lis = ['dsagdgasdasdasdasa','bdsaddddddsa','csdasdasfdf','dsdasffrgger']
# --------- Main App Layout --------- #

# App Title
st.markdown("<h1 style='text-align: center; color: #25D366;'>LLM-based RAG Search</h1>", unsafe_allow_html=True)
st.session_state['query_input'] = ''

def ent(query):
    answer = execute_search(query)
    if answer:
        st.session_state['latest_query'] = query
        st.session_state['latest_answer'] = answer

def show_relevent(links):
    for ele in lis:
        st.button(ele)

relevent_pages = st.Page(f"show_relevent(lis)", title="Relevent links", icon=":material/delete:")
# Query input and search button layout
query_container,query_container1 = st.columns([6,1])
st.navigation([relevent_pages])
with query_container:
    col1, col2 = st.columns([6, 1])
    with col1:
        query = st.text_input(
            "Enter your query:",
            placeholder="Type your question here...",
            key='query_input',
            help="Enter any query related to your project or topic of interest.",
            on_change= ent(st.session_state['query_input'])
        )
    with col2:
        st.markdown("""
        <style>
            button#search_btn {
                background-color: #25D366;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 8px;
            }
        </style>
        """, unsafe_allow_html=True)

        # Search button with a click event
        if st.button("➣", key='search_btn') :
            if query:
                ent(query)
with query_container1:
    pass

# Display the latest query and answer after search

if 'latest_query' in st.session_state and 'latest_answer' in st.session_state:
    display_query_and_answer(st.session_state['latest_query'], st.session_state['latest_answer'])

# --------- Commented Out: History Bubbles --------- #
# Keeping this part commented for future use

# def display_history_bubbles():
#     col1, col2 = st.columns([6, 1])
#     with col1:
#         st.markdown("<h3 style='text-align: left; color: #128C7E;'>History</h3>", unsafe_allow_html=True)
#     with col2:
#         # Clear History button with custom style
#         st.markdown("""
#         <style>
#             button#clear_history_btn {
#                 background-color: #d9534f;
#                 color: white;
#                 padding: 5px 10px;
#                 font-size: 14px;
#                 border-radius: 5px;
#                 cursor: pointer;
#             }
#         </style>
#         """, unsafe_allow_html=True)
#         if st.button("Clear History", key="clear_history_btn"):
#             clear_history()

#     history_container = st.container()
#     with history_container:
#         cols = st.columns(len(st.session_state['history']) if st.session_state['history'] else 1)
#         for i, chat in enumerate(st.session_state['history']):
#             with cols[i]:
#                 if st.button(f"{chat['query']}", key=f"history_bubble_{i}"):
#                     st.session_state['selected_history'] = i
