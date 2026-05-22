import streamlit as st
from PIL import Image

upload = st.file_uploader("이미지 파일을 올려주세요 (jpg, png):", type=["jpg", "jpeg", "png"])

if upload is not None:
    img = Image.open(upload)
    st.image(img, caption=upload.name, use_column_width=True)

