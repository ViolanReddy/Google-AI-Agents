import streamlit as st
import asyncio
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent.agent import root_agent

#Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("Personal AI Assistant")
st.caption("Your intelligent companion, Powered by Google ADK.")

if "session_service" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()

if "runner" not in st.session_state:
    st.session_state.runner = Runner(
        agent=root_agent,
        app_name="personal_assistant",
        session_service=st.session_state.session_service
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can i help you today?"):
    #Display users message
    st.chat_message("user").markdown(prompt)

    #Save message to chat history
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

#Run the agent
with st.chat_message("assistant"):
    with st.spinner("Thinking..."):

        response_text = ""

        #Prepare users message
        content = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        #Execute the agent
        async def call_agent():
            response = ""

            events = st.session_state.runner.run_async(
                user_id="streamlit_user",
                session_id="streamlit_session",
                new_message=content
            )

            async for event in events:
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = "".join(
                            part.text
                            for part in event.content.parts
                            if part.text
                        )

            #Display reponse
            return response

        response_text = asyncio.run(call_agent())

#Save assistant response
st.session_state.messages.append(
    {"role":"assistant", "content": response_text}
)