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
    
    # Stream AI response in real-time with live updates
    with st.chat_message('assistant'):
        
        # Use streaming mode for token-by-token response display
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages' : [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'  # Enable message streaming
            )
        )
        
    # Store complete streamed response in chat history
    st.session_state['message_history'].append({'role' : 'assistant', 'content' : ai_message})
