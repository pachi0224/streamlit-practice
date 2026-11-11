import hashlib
import io
import time
import streamlit as st

st.title("ChatPDF")
client = st.session_state.get("openai_client")
if not client:
    st.info("왼쪽 사이드바에서 OpenAI API Key를 입력하세요.")
    st.stop()

for key, default in (("pdf_messages", []), ("pdf_vector_store_id", None), ("pdf_hash", None)):
    if key not in st.session_state:
        st.session_state[key] = default

def clear_pdf_chat():
    st.session_state.pdf_messages = []

def leave_pdf():
    store_id = st.session_state.pdf_vector_store_id
    if store_id:
        try:
            client.vector_stores.delete(vector_store_id=store_id)
        except Exception as e:
            st.warning(f"Vector store 삭제 실패: {e}")
            return
    st.session_state.pdf_vector_store_id = None
    st.session_state.pdf_hash = None
    st.session_state.pdf_messages = []
    st.rerun()

if st.session_state.pdf_vector_store_id is None:
    uploaded = st.file_uploader("PDF 파일 하나를 업로드하세요", type=["pdf"], accept_multiple_files=False)
    if uploaded is not None:
        data = uploaded.getvalue()
        file_hash = hashlib.sha256(data).hexdigest()
        if st.button("PDF 분석 시작"):
            with st.spinner("PDF 업로드 및 검색 인덱스 생성 중..."):
                store_id = None
                try:
                    store = client.vector_stores.create(name=f"streamlit-chatpdf-{file_hash[:12]}")
                    store_id = store.id
                    file_obj = io.BytesIO(data)
                    file_obj.name = uploaded.name
                    client.vector_stores.file_batches.upload_and_poll(
                        vector_store_id=store_id, files=[file_obj]
                    )
                    st.session_state.pdf_vector_store_id = store_id
                    st.session_state.pdf_hash = file_hash
                    st.session_state.pdf_messages = []
                    st.rerun()
                except Exception as e:
                    if store_id:
                        try:
                            client.vector_stores.delete(vector_store_id=store_id)
                        except Exception:
                            pass
                    st.error(f"PDF 준비 실패: {e}")
else:
    st.success("PDF가 준비되었습니다. 질문을 입력하세요.")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Clear", on_click=clear_pdf_chat, use_container_width=True)
    with col2:
        st.button("Leave", on_click=leave_pdf, use_container_width=True)

    for msg in st.session_state.pdf_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("PDF 내용에 대해 질문하세요"):
        st.session_state.pdf_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                stream = client.responses.create(
                    model="gpt-6-luna",
                    instructions="업로드한 PDF의 내용에 근거하여 답변하세요. 문서에서 찾을 수 없는 내용은 찾을 수 없다고 답하세요.",
                    input=st.session_state.pdf_messages,
                    tools=[{"type": "file_search", "vector_store_ids": [st.session_state.pdf_vector_store_id]}],
                    stream=True,
                )
                def chunks():
                    for event in stream:
                        if event.type == "response.output_text.delta":
                            yield event.delta
                answer = st.write_stream(chunks())
                st.session_state.pdf_messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"PDF 답변 실패: {e}")
                st.session_state.pdf_messages.pop()
