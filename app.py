import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import os
from disease_info import get_disease_info
from treatment_recommender import get_treatment_recommendation
from weather_alerts import get_weather_risk
from multilingual_support import translate_text
from leaf_care_tips import get_care_tips
import json
from streamlit_lottie import st_lottie

# Page configuration
st.set_page_config(
    page_title="AgriLeaf Doctor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .disease-card {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .treatment-card {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1>rem 0;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Language selection
languages = {
    'English': 'en',
    'हिंदी': 'hi',
    'मराठी': 'mr'
}

selected_language = st.sidebar.selectbox("🌐 Select Language", list(languages.keys()))

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Header
st.markdown(f'<h1 class="main-header">🌿 {translate_text("AgriLeaf Doctor", languages[selected_language])}</h1>', unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #666;'>{translate_text('Smart Crop Disease Detection for Farmers', languages[selected_language])}</h3>", unsafe_allow_html=True)

# Load model at top level for better performance
try:
    model = tf.keras.models.load_model('models/mango_disease_model.h5')
except Exception as e:
    st.error(f"Error loading model: {e}")
    model = None

# Image preprocessing
def preprocess_image(image):
    try:
        img = Image.open(image)
        img = img.resize((224, 224))
        img_array = np.array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# Disease prediction
def predict_disease(model, image):
    processed_image = preprocess_image(image)
    predictions = model.predict(processed_image)
    class_names = ['Anthracnose', 'Bacterial Canker', 'Cutting Weevil', 
                   'Die Back', 'Gall Midge', 'Healthy', 'Powdery Mildew', 
                   'Sooty Mould']
    predicted_class = class_names[np.argmax(predictions)]
    confidence = np.max(predictions) * 100
    return predicted_class, confidence

# Main app
def main():
    # Model is already loaded at the top level
    if model is None:
        st.warning("Please upload a trained model file to continue.")
        return
    
    # Sidebar
    st.sidebar.title(translate_text("📱 Navigation", languages[selected_language]))
    page = st.sidebar.radio(translate_text("Go to", languages[selected_language]), 
                             [translate_text("Disease Detection", languages[selected_language]), 
                              translate_text("Care Tips", languages[selected_language]), 
                              translate_text("Weather Alerts", languages[selected_language]), 
                              translate_text("About", languages[selected_language])])
    
    if page == translate_text("Disease Detection", languages[selected_language]):
        show_disease_detection(model)
    elif page == translate_text("Care Tips", languages[selected_language]):
        show_care_tips()
    elif page == translate_text("Weather Alerts", languages[selected_language]):
        show_weather_alerts()
    elif page == translate_text("About", languages[selected_language]):
        show_about()

def show_disease_detection(model):
    st.header(translate_text("🦠 Disease Detection", languages[selected_language]))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            translate_text("Upload a leaf image", languages[selected_language]),
            type=['jpg', 'jpeg', 'png'],
            help=translate_text("Upload a clear image of the affected leaf", languages[selected_language])
        )
        st.markdown(f"**{translate_text('Drag and drop file here or click to select', languages[selected_language])}**")
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption=translate_text("Uploaded Image", languages[selected_language]), use_column_width=True)
        
        with col2:
            if st.button(translate_text("🔍 Analyze Disease", languages[selected_language])):
                with st.spinner(translate_text("Analyzing image...", languages[selected_language])):
                    predicted_class, confidence = predict_disease(model, uploaded_file)
                    
                    st.success(translate_text("Analysis Complete!", languages[selected_language]))
                    st.metric(
                        translate_text("Predicted Disease", languages[selected_language]),
                        translate_text(predicted_class, languages[selected_language])
                    )
                    st.metric(
                        translate_text("Confidence", languages[selected_language]),
                        f"{confidence:.2f}%"
                    )
        
        if 'predicted_class' in locals():
            display_disease_info(predicted_class)
            display_treatment_recommendation(predicted_class)

def display_disease_info(disease_name):
    st.subheader(translate_text("📋 Disease Information", languages[selected_language]))
    
    disease_info = get_disease_info(disease_name, languages[selected_language])
    
    with st.container():
        st.markdown('<div class="disease-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{translate_text('Disease Name', languages[selected_language])}:** {translate_text(disease_info['name'], languages[selected_language])}")
            st.markdown(f"**{translate_text('Scientific Name', languages[selected_language])}:** {translate_text(disease_info['scientific_name'], languages[selected_language])}")
        
        with col2:
            st.markdown(f"**{translate_text('Severity', languages[selected_language])}:** {translate_text(disease_info['severity'], languages[selected_language])}")
            st.markdown(f"**{translate_text('Spread Rate', languages[selected_language])}:** {translate_text(disease_info['spread_rate'], languages[selected_language])}")
        
        st.markdown(f"**{translate_text('Causes', languages[selected_language])}:**")
        for cause in disease_info['causes']:
            st.write(f"• {translate_text(cause, languages[selected_language])}")
        
        st.markdown(f"**{translate_text('Symptoms', languages[selected_language])}:**")
        for symptom in disease_info['symptoms']:
            st.write(f"• {translate_text(symptom, languages[selected_language])}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_treatment_recommendation(disease_name):
    st.subheader(translate_text("💊 Treatment Recommendations", languages[selected_language]))
    
    treatment = get_treatment_recommendation(disease_name, languages[selected_language])
    
    with st.container():
        st.markdown('<div class="treatment-card">', unsafe_allow_html=True)
        
        st.markdown(f"**{translate_text('Recommended Treatment', languages[selected_language])}:**")
        st.write(translate_text(treatment['treatment'], languages[selected_language]))
        
        if 'medicines' in treatment:
            st.markdown(f"**{translate_text('Medicines', languages[selected_language])}:**")
            for med in treatment['medicines']:
                st.write(f"• **{translate_text(med['name'], languages[selected_language])}**: {translate_text(med['dosage'], languages[selected_language])}")
        
        if 'organic_options' in treatment:
            st.markdown(f"**{translate_text('Organic Alternatives', languages[selected_language])}:**")
            for organic in treatment['organic_options']:
                st.write(f"• {translate_text(organic, languages[selected_language])}")
        
        if 'prevention' in treatment:
            st.markdown(f"**{translate_text('Prevention Tips', languages[selected_language])}:**")
            for tip in treatment['prevention']:
                st.write(f"• {translate_text(tip, languages[selected_language])}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_care_tips():
    st.header(translate_text("🌱 Healthy Leaf Care Tips", languages[selected_language]))
    
    tips = get_care_tips(languages[selected_language])
    
    for category, tip_list in tips.items():
        with st.expander(translate_text(category, languages[selected_language])):
            for tip in tip_list:
                st.write(f"• {translate_text(tip, languages[selected_language])}")

def show_weather_alerts():
    st.header(translate_text("🌦️ Weather-Based Disease Risk Alerts", languages[selected_language]))
    
    location = st.text_input(
        translate_text("Enter your location (City, State)", languages[selected_language]),
        placeholder=translate_text("e.g., Mumbai, Maharashtra", languages[selected_language])
    )
    
    if location:
        with st.spinner(translate_text("Fetching weather data...", languages[selected_language])):
            weather_data = get_weather_risk(location, languages[selected_language])
            
            if weather_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        translate_text("Temperature", languages[selected_language]),
                        f"{weather_data['temperature']}°C"
                    )
                
                with col2:
                    st.metric(
                        translate_text("Humidity", languages[selected_language]),
                        f"{weather_data['humidity']}%"
                    )
                
                with col3:
                    st.metric(
                        translate_text("Risk Level", languages[selected_language]),
                        translate_text(weather_data['risk_level'], languages[selected_language])
                    )
                
                st.info(translate_text(weather_data['recommendation'], languages[selected_language]))
            else:
                st.error(translate_text("Unable to fetch weather data. Please check your location.", languages[selected_language]))

def show_about():
    st.header(translate_text("About AgriLeaf Doctor", languages[selected_language]))
    
    st.markdown(f"""
    {translate_text('''
    **AgriLeaf Doctor** is an AI-powered agricultural application designed to help farmers identify and treat crop leaf diseases effectively.
    
    ### Features:
    - 🦠 **Disease Detection**: Upload leaf images to identify diseases using AI
    - 💊 **Treatment Recommendations**: Get detailed treatment plans with medicines and organic alternatives
    - 🌱 **Care Tips**: Learn how to maintain healthy plants
    - 🌦️ **Weather Alerts**: Receive disease risk alerts based on weather conditions
    - 🌐 **Multi-language Support**: Available in multiple Indian languages
    
    ### Benefits:
    - Reduce crop losses by early disease detection
    - Save money on unnecessary treatments
    - Increase crop yield through timely action
    - Access expert knowledge at your fingertips
    
    ### Technology Stack:
    - **AI Model**: TensorFlow/Keras for disease classification
    - **Frontend**: Streamlit for user-friendly interface
    - **Weather Data**: OpenWeatherMap API
    - **Translation**: Google Translate API
    
    **Made with ❤️ for Indian Farmers**
    ''', languages[selected_language])}
    """)

if __name__ == "__main__":
    main()
