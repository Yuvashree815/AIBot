import requests
import streamlit as st
import base64
import io
from PIL import Image

# Helper function to convert image to base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Set background image
img = get_img_as_base64("ai.jpg")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{img}");
background-size: cover;
}}
[data-testid="stHeader"] {{
background: rgba(0, 0, 0, 0);
}}
h1 {{
color: white;
}}
.caption-box {{
background-color: white;
color: black;
padding: 10px;
border-radius: 5px;
border: 1px solid #ccc;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# API URLs and headers
gen_api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
cap_api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
headers = {"Authorization": "Bearer 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"}

# Query function for image generation
def generate_image(payload):
    response = requests.post(gen_api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.error("Failed to generate image. Please try again.")
        return None

# Query function for image captioning
def generate_caption(image_data):
    response = requests.post(cap_api_url, headers=headers, data=image_data)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Streamlit interface
st.title("AIBot")

# Tabs for different functionalities
tab1, tab2 = st.tabs(["Image Generation", "Image Captioning"])

# Image Generation Tab
with tab1:
    st.header("Generate an Image from a Text Prompt")
    prompt = st.text_input('Enter a prompt:')
    
    if st.button('Generate Image'):
        if prompt:
            image_bytes = generate_image({"inputs": prompt})
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Generated Image", use_column_width=True)
        else:
            st.warning("Please enter a prompt.")

# Image Captioning Tab
with tab2:
    st.header("Generate a Caption for an Uploaded Image")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        image_data = uploaded_file.read()
        
        with st.spinner('Generating caption...'):
            result = generate_caption(image_data)

        if result:
            if "generated_text" in result[0]:
                st.markdown(f"""
                <div class="caption-box">
                <strong>Generated Caption:</strong> {result[0]['generated_text']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to generate a caption. Please try again.")
