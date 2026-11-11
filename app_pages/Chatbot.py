from pathlib import Path
import streamlit as st

st.title("국립부경대학교 도서관 챗봇")
client = st.session_state.get("openai_client")
if not client:
    st.info("왼쪽 사이드바에서 OpenAI API Key를 입력하세요.")
    st.stop()

rules_file = Path(__file__).resolve().parent.parent / "library_rules.txt"
if not rules_file.exists() or not rules_file.read_text(encoding="utf-8").strip():
    st.warning("library_rules.txt에 부경대학교 도서관 규정 원문을 붙여 넣어 주세요.")
    st.stop()

rules = rules_file.read_text(encoding="utf-8")
instructions = (
    "당신은 국립부경대학교 도서관 규정 안내 챗봇입니다. "
    "아래 규정 원문만 근거로 답변하세요. 규정에 없으면 확인할 수 없다고 답하세요. "
    "규정과 관계없는 질문은 도서관 규정 안내에 집중하세요.\n\n"
    "[국립부경대학교 도서관 규정 원문]\n" + rules
)

if "library_messages" not in st.session_state:
    st.session_state.library_messages = []

def clear_library():
    st.session_state.library_messages = []
st.button("Clear", on_click=clear_library)
for msg in st.session_state.library_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
if prompt := st.chat_input("도서관 규정을 질문하세요"):
    st.session_state.library_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            stream = client.responses.create(
                model="gpt-6-luna", instructions=instructions,
                input=st.session_state.library_messages, stream=True
            )
            def chunks():
                for event in stream:
                    if event.type == "response.output_text.delta":
                        yield event.delta
            answer = st.write_stream(chunks())
            st.session_state.library_messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"답변 생성 실패: {e}")
            st.session_state.library_messages.pop()
