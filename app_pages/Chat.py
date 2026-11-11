import streamlit as st

st.title("Chat")
client = st.session_state.get("openai_client")
if not client:
    st.info("왼쪽 사이드바에서 OpenAI API Key를 입력하세요.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

def clear_chat():
    st.session_state.messages = []

st.button("Clear", on_click=clear_chat)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            stream = client.responses.create(model="gpt-6-luna", input=st.session_state.messages, stream=True)
            def text_chunks():
                for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta
            answer = st.write_stream(text_chunks())
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"답변 생성 실패: {e}")
            st.session_state.messages.pop()
