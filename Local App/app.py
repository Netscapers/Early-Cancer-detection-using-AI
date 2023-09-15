import os
import subprocess
import streamlit as st
from PIL import Image
import base64
import re

st.set_page_config(page_title="MedAI", page_icon="logo.png")

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover

    }}
    </style>
    """,
    unsafe_allow_html=True
    )
add_bg_from_local('RWyvoC.jpeg')    

# Custom CSS styles
st.markdown(
    """
    <style>

    .stTitle {
        color: rgb(0, 27, 118);
        text-align: center;
        font-family: dosis; /* Change the font family */
        font-size: 42px; /* Change the font size */
    }
    .stMarkdown {
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

CFG_MODEL_PATH = "100epoch.pt"
CFG_ENABLE_URL_DOWNLOAD = True

def convert_to_rgb(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    rgb_image_path = os.path.splitext(image_path)[0] + "_rgb.jpg"
    img.save(rgb_image_path, format="JPEG")
    return rgb_image_path

def detect_objects(image_path):
    process = subprocess.Popen(["python", "detect.py", '--source', image_path, "--weights", CFG_MODEL_PATH], shell=True, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate()
    process.wait()

    output_lines = stdout.strip().split('\n')
    class_line = output_lines[10]
    class_names = re.findall(r'\b[A-Za-z]\b', class_line)
    cancer_type_mapping = {
        'A': 'Adenocarcinoma',
        'B': 'Small Cell Carcinoma',
        'E': 'Large Cell Carcinoma',
        'G': 'Squamous Cell Carcinoma'
    }

    # Get the corresponding cancer type for each class name
    detected_cancer_types = [cancer_type_mapping.get(class_name, class_name) for class_name in class_names]

    return detected_cancer_types

def get_latest_subfolder():
    folder_path = 'runs/detect'
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
    return latest_subfolder


def main():
    

    st.sidebar.title("MedAI :zap: -  Diagnosis Simplified")
    st.sidebar.title("About Lung Cancer")
    st.sidebar.write("Lung cancer is a leading cause of cancer-related deaths worldwide. Early detection can significantly improve patient outcomes. This app aims to assist medical professionals in diagnosing lung cancer using AI.")

    st.sidebar.title("Lung Cancer Types")
    st.sidebar.write("The AI model was trained to detect the following types of lung cancer:\n"
                     "1. Adenocarcinoma (A)\n"
                     "2. Small Cell Carcinoma (B) \n"
                     "3. Large Cell Carcinoma (E) \n"
                     "4. Squamous Cell Carcinoma (G)")

    st.sidebar.title("How to Use")
    st.sidebar.write("1. Upload a CT scan image of a patient's lungs.\n"
                     "2. The app will display the predicted type of lung cancer.")
    # Set the title with blue color
    # st.header("Lung Cancer Detection App :medical_symbol:")
    #
    st.markdown("<h1 class='stTitle'>Lung Cancer Detection App ⚕️</h1> ", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload an image", type=["jpg","jpeg","png", "mp4"])

    if uploaded_file:
        # Save the uploaded file temporarily
        with open(os.path.join("data/uploads", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getvalue())

        # Create a two-column layout using st.columns
        col1, col2 = st.columns(2)

        # Display the original uploaded image on the left
        with col1:
            col1.image(uploaded_file, caption = "Input Image", use_column_width=True, width=500)

        # Perform object detection if it's an image
        if uploaded_file.type.startswith("image"):
            with col2:
                with st.spinner("Predicting Cancer"):
                    # Convert uploaded image to RGB format
                    rgb_image_path = convert_to_rgb(os.path.join("data/uploads", uploaded_file.name))

                    # detect_objects(rgb_image_path)
                    detected_classes = detect_objects(rgb_image_path)
                    detected_classes_str = ', '.join(detected_classes)

                    latest_subfolder = get_latest_subfolder()
                    detected_image_path = os.path.join('runs/detect', latest_subfolder, os.path.basename(rgb_image_path))

                # Display the predicted image on the right
                st.image(Image.open(detected_image_path), caption="Detected Class", use_column_width=True, width=500)
            
            # st.write("Detected Cancer Types:", detected_classes_str)
            st.markdown(f"<p style='font-weight: bold; color: black; font-size: 20px;'>Detected Cancer : {detected_classes_str}</p>", unsafe_allow_html=True)


    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()