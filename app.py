import streamlit as st
import spacy
import pdfplumber
from spacy import displacy
from io import StringIO
import pandas as pd  # Import pandas for creating the table

# Load spaCy NER model
nlp = spacy.load("ner_model")

# Custom entity colors
custom_colors = {
    "ORG": "#FF5733",  # Red-Orange
    "LAWYER": "#6A0DAD",  # Purple
    "DATE": "#FFD700",  # Gold
    "CASE_NUMBER": "#0000FF",  # Blue
    "JUDGE": "#32CD32",  # Green
    "STATUTE": "#FFA07A",  # Coral
    "COURT": "#20B2AA",  # Teal
    "RESPONDENT": "#800000",  # Dark Red
    "PRECEDENT": "#FF1493",  # Deep Pink
    "WITNESS": "#708090",  # Slate Grey
    "OTHER_PERSON": "#8B4513",  # Brown
    "GPE": "#4682B4",  # Steel Blue
    "PROVISION": "#9400D3",  # Violet
    "PETITIONER": "#556B2F"  # Olive Green
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# Function to process text and highlight NER
def highlight_entities(text):
    doc = nlp(text)
    options = {"ents": list(custom_colors.keys()), "colors": custom_colors}
    html = displacy.render(doc, style="ent", options=options, jupyter=False)

    # Wrap in a scrollable container to avoid text cutoff
    html = f"""
    <div style="overflow-x: auto; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9; max-width: 100%;">
        {html}
    </div>
    """
    return html

# Function to extract entities for analytics
def extract_entities_for_analytics(text):
    doc = nlp(text)
    entities_data = []
    for ent in doc.ents:
        entities_data.append({"Entity": ent.text, "Type": ent.label_})
    return entities_data

# Streamlit UI
st.set_page_config(layout="wide")  # Ensure full-screen width usage

st.title("📜 Legal NER Extraction Tool")
st.write("Upload a **text file** or **PDF**, or manually enter text to extract Named Entities.")

# Option for text input or file upload
input_option = st.radio("Choose how to input the text:", ("Upload File", "Write Text"))

if input_option == "Upload File":
    uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf"])

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        else:
            text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()

        if text:
            st.subheader("Extracted Text:")
            st.write(text[:1000])  # Show a preview (first 1000 chars)

            st.subheader("Named Entity Recognition:")
            html_output = highlight_entities(text)
            st.markdown(html_output, unsafe_allow_html=True)  # Render properly with `unsafe_allow_html`

            # Get analytics of entities
            entities_data = extract_entities_for_analytics(text)
            if entities_data:
                st.subheader("Entity Analytics")
                df = pd.DataFrame(entities_data)  # Create a DataFrame for table
                st.dataframe(df)  # Display the table
        else:
            st.error("Could not extract text. Please upload a valid file.")

elif input_option == "Write Text":
    user_input = st.text_area("Enter your text here:")

    if user_input:
        st.subheader("Entered Text:")
        st.write(user_input)

        # Add button to process text
        if st.button("Extract Named Entities"):
            st.subheader("Named Entity Recognition:")
            html_output = highlight_entities(user_input)
            st.markdown(html_output, unsafe_allow_html=True)  # Render properly with `unsafe_allow_html`

            # Get analytics of entities
            entities_data = extract_entities_for_analytics(user_input)
            if entities_data:
                st.subheader("Entity Analytics")
                df = pd.DataFrame(entities_data)  # Create a DataFrame for table
                st.dataframe(df)  # Display the table
