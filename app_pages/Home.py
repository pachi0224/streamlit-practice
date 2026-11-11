import base64
import streamlit as st

st.title("GPT 질문 답변 웹 앱")
client = st.session_state.get("openai_client")
if not client:
    st.info("왼쪽 사이드바에서 OpenAI API Key를 입력하세요.")
    st.stop()

question = st.text_input("질문을 입력하세요")
if st.button("질문하기"):
    if not question.strip():
        st.warning("질문을 입력하세요.")
    else:
        with st.spinner("답변을 생성하고 있습니다..."):
            try:
                response = client.responses.create(model="gpt-6-luna", input=question)
                st.write(response.output_text)
            except Exception as e:
                st.error(f"답변 생성 실패: {e}")

st.divider()
st.subheader("이미지 생성")
prompt = st.text_input("이미지 프롬프트를 입력하세요")
if st.button("이미지 생성하기"):
    if not prompt.strip():
        st.warning("프롬프트를 입력하세요.")
    else:
        with st.spinner("이미지를 생성하고 있습니다..."):
            try:
                img = client.images.generate(model="gpt-image-2.6-flare", prompt=prompt)
                image_bytes = base64.b64decode(img.data[0].b64_json)
                st.image(image_bytes)
            except Exception as e:
                st.error(f"이미지 생성 실패: {e}")
