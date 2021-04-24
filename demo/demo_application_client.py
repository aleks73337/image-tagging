import streamlit as st
import sys, importlib
import time

from PIL import Image
from pathlib import Path
from request import Request

hash_funcs={'builtins.method_descriptor' : lambda _: None,}
@st.cache(allow_output_mutation=True, hash_funcs=hash_funcs)
def get_request():
    req = Request()
    return req

print(get_request())

img_data = st.file_uploader(label="Your photo", type=['png', 'jpg'])
if img_data is not None:
    uploaded_image = Image.open(img_data)
    st.image(uploaded_image)

    req = get_request()
    tags = req.send_img(uploaded_image)
    if not tags:
        tags = req.await_tags()
    print(tags)

    cols = st.beta_columns(4)
    result = ""
    for i in range(0, len(tags)):
        tag = tags[i]
        checked = cols[i % 4].checkbox("#" + tag, key=tag)
        if checked:
            result += "#" + tag + " "

    st.text_area("", value=result)
