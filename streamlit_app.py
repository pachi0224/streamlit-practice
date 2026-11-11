import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Streamlit AI 실습", page_icon="🤖")

with st.sidebar:
    api_key = st.text_input("OpenAI API Key", type="password", key="api_key")

if api_key:
    st.session_state["openai_client"] = OpenAI(api_key=api_key)
else:
    st.session_state.pop("openai_client", None)

pg = st.navigation([
    st.Page("app_pages/Home.py", title="Home", icon=":material/home:"),
    st.Page("app_pages/Chat.py", title="Chat", icon=":material/chat:"),
    st.Page("app_pages/Chatbot.py", title="Chatbot", icon=":material/smart_toy:"),
    st.Page("app_pages/ChatPDF.py", title="ChatPDF", icon=":material/picture_as_pdf:"),
])
pg.run()
