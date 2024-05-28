import streamlit as st
import numpy as np
from PIL import Image, ImageOps
from keras.models import load_model
import os
import logging
from signal import signal, SIGPIPE, SIG_DFL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle SIGPIPE
signal(SIGPIPE, SIG_DFL)

@st.cache_resource
def load_keras_model():
    model_path = "keras_model.h5"
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return None
    return load_model(model_path, compile=False)

@st.cache_resource
def load_class_names():
    labels_path = "labels.txt"
    if not os.path.exists(labels_path):
        logger.error(f"Labels file not found: {labels_path}")
        return None
    return open(labels_path, "r").readlines()

def preprocess_image(image):
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    return np.expand_dims(normalized_image_array, axis=0)

def object_detection_image():
    st.title('Cat and Dog Detection for Images')
    st.subheader("Please scroll down to see the processed image.")

    file = st.file_uploader('Upload Image', type=['jpg', 'png', 'jpeg'])
    if file is not None:
        img1 = Image.open(file)
        st.image(img1, caption="Uploaded Image")
        my_bar = st.progress(0)

        np.set_printoptions(suppress=True)

        model = load_keras_model()
        if model is None:
            st.error("Model could not be loaded. Please check the logs for more details.")
            return

        class_names = load_class_names()
        if class_names is None:
            st.error("Class names could not be loaded. Please check the logs for more details.")
            return

        image_data = preprocess_image(img1)

        try:
            logger.info("Starting prediction...")
            prediction = model.predict(image_data)
            logger.info("Prediction completed.")
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            confidence_score = prediction[0][index]

            st.image(img1, caption=f"{class_name[2:]} with confidence {confidence_score:.2f}")
            my_bar.progress(100)

        except Exception as e:
            logger.error(f"An error occurred during prediction: {e}", exc_info=True)
            st.error(f"An error occurred during prediction: {e}")
            my_bar.progress(0)

def main():
    st.markdown('<p style="font-size: 42px;">Welcome to Cat and Dog Detection App!</p>', unsafe_allow_html=True)
    st.markdown("""
        This project was built using Streamlit
        to demonstrate Cat and Dog detection in images.
    """)

    choice = st.sidebar.selectbox("MODE", ("About", "Image"))

    if choice == "Image":
        st.subheader("Object Detection")
        object_detection_image()
    elif choice == "About":
        st.markdown("""
            This app uses a pre-trained neural network model to detect cats and dogs in images.
            Upload an image and see the prediction in action!
        """)

if __name__ == '__main__':
    main()
