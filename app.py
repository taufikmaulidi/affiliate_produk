import os
import google.generativeai as genai
import requests
import streamlit as st
import re
import datetime
import markdown2

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

# Validasi API Key Google Gemini
def validate_google_gemini_api_key(api_key):
    headers = {'Content-Type': 'application/json'}
    params = {'key': api_key}
    json_data = {'contents': [{'role': 'user', 'parts': [{'text': 'Give me five subcategories of jazz?'}]}]}
    response = requests.post(
        'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent',
        params=params, headers=headers, json=json_data
    )
    return response.status_code == 200

def create_post(link, deskripsi):
    prompt_kesimpulan = f"""
    Buat sebuah posting ke website untuk kebutuhan affiliate produk. Link produk tersebut adalah: {link}, buat link produk ahref dan new_blank.
    Deskripsi produk adalah: {deskripsi}
    
    buat sebuah artikel blog yang menarik dan mengajak untuk melakukan pembelian. hasilkan dengan format markdown.
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 1.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain"
        },
        system_instruction="Saya ingin kamu menjadi seorang digital marketing dan seorang affiliator produk, kamu pintar dalam mengajak orang untuk membeli suatu produk.",
        safety_settings=safety_settings
    )
    
    response = model.generate_content(prompt_kesimpulan)
    return response.text.strip()

# Set page config
st.set_page_config(page_title='Affiliate Produk', layout='wide')

# Initialize session state for API key
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Title and sidebar
st.title('Generate Artikel Affiliate dengan AI')
st.subheader("Buat Artikel Affiliate Berkualitas dengan Kemudahan AI")
with st.sidebar:
    st.title("Affiliate Produk")
    st.subheader('by gudanginformatika.com')
    st.image("./qr.png", width=200, use_column_width=100)
    st.caption('Jika Anda ingin mendukung proyek kami, kami sangat menghargainya!')
    if not st.session_state.api_key_valid:
        api_key = st.text_input('Masukkan API Key Google Gemini Anda', type='password')
        if st.button('Validate API Key'):
            if validate_google_gemini_api_key(api_key):
                st.session_state.api_key_valid = True
                st.session_state.api_key = api_key
                st.success('API Key valid!')
            else:
                st.error('API Key tidak valid')

if st.session_state.api_key_valid:
    genai.configure(api_key=st.session_state.api_key)

    # Input fields for article generation
    link = st.text_input('Link Affiliate', placeholder="Masukkan link affiliate anda di sini")
    deskripsi = st.text_area('Deskripsi Produk', placeholder="Masukkan deskripsi produk di sini")
    foto = st.text_input('Link Foto Produk', placeholder="Masukkan link foto produk di sini")

    if st.button('Generate Article'):
        if link and deskripsi and foto:
            with st.spinner('Memproses artikel...'):
                artikel = create_post(link, deskripsi)
                # Meletakkan foto di awal artikel
                final_content = f'<img src="{foto}" alt="Gambar Produk" style="max-width:100%; height:auto;"/><br>' + artikel
                st.write("Artikel yang Dihasilkan:")
                st.markdown(final_content, unsafe_allow_html=True)
                st.code(markdown2.markdown(final_content), language='html')
        else:
            st.error("Semua input harus diisi.")
else:
    st.warning("Silakan masukkan API Key yang valid untuk melanjutkan.")
