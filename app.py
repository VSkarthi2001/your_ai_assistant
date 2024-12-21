import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai

load_dotenv()

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="centered",
)

# Set default system prompt
default_system_prompt = "You are an AI assistant"

# Sidebar options
st.sidebar.title("Options")
clear_button = st.sidebar.button("Clear Chat")
delete_button = st.sidebar.button("Delete Custom Prompt")

# Load API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Set or reset system prompt from session state
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = default_system_prompt

# Allow the user to customize the system prompt
custom_prompt = st.text_area("Customize the system prompt:", value=st.session_state.system_prompt, height=100)

if submit_button := st.button("Submit Custom Prompt"):
    st.session_state.system_prompt = custom_prompt
    st.success("Custom prompt applied!")

if delete_button:
    st.session_state.system_prompt = default_system_prompt
    st.success("Custom prompt deleted. Default prompt applied.")

# Initialize the model with the current system prompt
model = gen_ai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=st.session_state.system_prompt
)

# Initialize chat history if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Clear chat history
if clear_button:
    st.session_state.chat_history = []  

st.title("Personal AI Assistant 🤖")

def get_conversation_history():
    history = ""
    for message_type, text in st.session_state.chat_history:
        if message_type == "user":
            history += f"User: {text}\n"
        else:
            history += f"Assistant: {text}\n"
    return history

# Display conversation history
for message in st.session_state.chat_history:
    message_type, text = message
    with st.chat_message(message_type):
        st.markdown(text)

# Handle user input and generate response
if prompt := st.chat_input("What is up?"):
    st.session_state.chat_history.append(("user", prompt))
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    conversation_history = get_conversation_history()
    input_with_memory = f"{conversation_history}\nUser: {prompt}\nAssistant:"

    response = model.generate_content(input_with_memory)
    
    if response.candidates and len(response.candidates) > 0:
        generated_content = response.candidates[0].content.parts[0].text
        
        st.session_state.chat_history.append(("assistant", generated_content))
        
        with st.chat_message("assistant"):
            st.markdown(generated_content)
    else:
        error_message = "Sorry, I didn't get that. Can you try again?"
        st.session_state.chat_history.append(("assistant", error_message))
        
        with st.chat_message("assistant"):
            st.markdown(error_message)
