import streamlit as st
import tableauserverclient as TSC
import requests
from bs4 import BeautifulSoup
import os
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Set your OpenAI API key
openai.api_key = st.secrets.openai_key

# Set your IBM Watson Assistant credentials
watson_api_key = st.secrets.watson_key
watson_url = st.secrets.watson_url

# Set your Tableau Online server and personal access token information
tableau_server = "https://public.tableau.com/app/profile/hfuieti/vizzes"
tableau_token_name = ""  # No personal access token required for public Tableau sites
tableau_token_secret = ""  # No personal access token required for public Tableau sites
tableau_site = ""  # No site specified for public Tableau sites

# Set the URLs for additional information if not found in Tableau, knowledge base, or the specified webpages
additional_info_urls = [
    "https://www.holyfamily.edu/about/news-and-media/fast-facts",
    "https://www.holyfamily.edu/about",
    "https://nces.ed.gov/collegenavigator/?s=all&zc=19114&zd=0&of=3&id=212984",
    "https://collegescorecard.ed.gov/school/?212984-Holy-Family-University"
]

# Function to fetch Tableau information using IBM Watson Assistant
def get_tableau_info_from_watson(user_input):
    authenticator = IAMAuthenticator(watson_api_key)
    assistant = AssistantV2(
        version='2021-06-14',
        authenticator=authenticator
    )
    assistant.set_service_url(watson_url)

    response = assistant.message(
        assistant_id=watson_assistant_id,
        session_id="unique_session_id",
        input={
            'message_type': 'text',
            'text': user_input
        }
    ).get_result()

    # Extract relevant information from the Watson Assistant response
    # Modify this based on your Watson Assistant skill structure
    relevant_info = response.get('output', {}).get('generic', [])[0].get('text', 'No relevant information.')

    return relevant_info

# Function to fetch data from the specified websites
def get_website_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract relevant information from the website
        # Modify this based on the structure of the website
        data_from_website = f"Information from {url}."
        return data_from_website
    else:
        return f"Failed to fetch data from {url}."

# Function to read knowledge base entries from the 'data' subdirectory
def read_knowledge_base():
    knowledge_base_path = os.path.join("data", "knowledge_base.txt")
    with open(knowledge_base_path, "r", encoding="utf-8") as kb_file:
        knowledge_base_entries = {}
        for line in kb_file:
            entry, response = line.strip().split(":")
            knowledge_base_entries[entry.strip().lower()] = response.strip()
    return knowledge_base_entries

# Function to generate a bar graph
def generate_bar_graph(data):
    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots()
    ax.bar(labels, values)

    ax.set_xlabel("Categories")
    ax.set_ylabel("Values")
    ax.set_title("Bar Graph of Data")

    st.pyplot(fig)

# Streamlit app
def main():
    st.set_page_config(page_title="Chat with the Holy Family Factbook, Blue Facts 🐯 ", page_icon="🐾", layout="centered", initial_sidebar_state="auto", menu_items=None)

    sst.title("Chat with the Holy Family Factbook, Blue Facts 💬🐅 ")
    st.info("Check out the full Factbook at the our university page (https://public.tableau.com/app/profile/hfuieti/vizzes)", icon="📊")

    if "messages" not in st.session_state.keys(): # Initialize the chat messages history
        st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Holy Family University's data!"}
    ]


    # Fetch Tableau information using IBM Watson Assistant
    tableau_info_from_watson = get_tableau_info_from_watson(user_input)

    # Fetch knowledge base entries
    knowledge_base_entries = read_knowledge_base()

    # Chatbot response
    if user_input:
        # Check if the Watson Assistant response contains Tableau information
        if "tableau" in tableau_info_from_watson.lower():
            st.text_area("Watson Assistant (Tableau Information):", tableau_info_from_watson)
        else:
            # Check if the requested data matches Tableau information
            requested_data = user_input.lower()

            # You can continue with the existing code to check for matching workbooks and views
            # ...

            if matching_workbooks or matching_views:
                st.write("### Matching Tableau Information:")
                if matching_workbooks:
                    st.write("#### Workbooks:")
                    st.write("\n".join(matching_workbooks))
                if matching_views:
                    st.write("#### Views:")
                    st.write("\n".join(matching_views))
            else:
                # Use OpenAI API to get a response from the chatbot
                chatbot_response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"User: {user_input}\nChatGPT: "
                )

                # Check if the knowledge base has a response
                knowledge_base_response = knowledge_base_entries.get(requested_data, None)

                if knowledge_base_response:
                    st.text_area("ChatGPT (Knowledge Base):", knowledge_base_response)
                else:
                    # Fetch data from the specified websites if not found in Tableau or knowledge base
                    for url in additional_info_urls:
                        website_data = get_website_data(url)
                        st.text_area(f"ChatGPT (Website Data from {url}):", website_data)

                        # Check if the response is a data-related question
                        if "data" in user_input.lower():
                            # Generate a simple bar graph for demonstration purposes
                            data_example = {"Category 1": 10, "Category 2": 20, "Category 3": 15}
                            st.write("### Bar Graph:")
                            generate_bar_graph(data_example)

if __name__ == "__main__":
    main()
