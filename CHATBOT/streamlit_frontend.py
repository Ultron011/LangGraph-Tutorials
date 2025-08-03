# Streamlit UI imports and backend connection
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# Configuration for conversation thread
CONFIG = {"configurable" : {"thread_id" : "thread-1"}}

# Initialize session state for chat history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display existing chat history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Get user input from chat input widget
user_input = st.chat_input('Type here')

# Process user input when received
if user_input:
    
    # Add user message to history and display
    st.session_state['message_history'].append({'role' : 'user', 'content' : user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
    # Get AI response from LangGraph backend
    response = chatbot.invoke({'messages' : [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content
    
    # Add AI response to history and display
    st.session_state['message_history'].append({'role' : 'assistant', 'content' : ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)