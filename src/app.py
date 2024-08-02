import streamlit as st
from sqlalchemy.orm import Session
from models import SessionLocal, Patient, ClinicalHistory
import pandas as pd
import os
import random
import string


# Database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Generate random string
def generate_random_string(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))


# Save uploaded file
def save_uploaded_file(uploaded_file, name, phone, adhar):
    file_extension = os.path.splitext(uploaded_file.name)[1]
    file_name = f"{name}_{phone}_{adhar}{file_extension}"
    file_path = os.path.join("images", file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


# Add Patient Page
def add_patient():
    st.title("Add Patient")

    name = st.text_input("Name")
    phone_number = st.text_input("Phone Number")
    home_address = st.text_area("Home Address")
    email = st.text_input("Email (optional)")
    adhar_id = st.text_input("Adhar ID")
    driving_licence_number = st.text_input("Driving Licence Number")

    uploaded_file = st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"])
    camera_photo = st.camera_input("Take a Photo")

    if st.button("Add Patient"):
        if not phone_number:
            phone_number = generate_random_string(10)
        if not adhar_id:
            adhar_id = generate_random_string(12)
        
        photo_path = None
        if uploaded_file:
            photo_path = save_uploaded_file(uploaded_file, name, phone_number, adhar_id)
        elif camera_photo:
            photo_path = save_uploaded_file(camera_photo, name, phone_number, adhar_id)

        with next(get_db()) as db:
            new_patient = Patient(
                name=name,
                phone_number=phone_number,
                home_address=home_address,
                email=email,
                adhar_id=adhar_id,
                driving_licence_number=driving_licence_number,
                photo=photo_path
            )
            db.add(new_patient)
            db.commit()
            st.success("Patient added successfully")


# View Patient Clinical History Page
def view_patient_history():
    st.title("View Patient Clinical History")

    with next(get_db()) as db:
        patients = db.query(Patient).all()
        patient_names = [patient.name for patient in patients]
    
    selected_patient = st.selectbox("Select Patient", patient_names)
    
    if selected_patient:
        with next(get_db()) as db:
            patient = db.query(Patient).filter(Patient.name == selected_patient).first()
            history = db.query(ClinicalHistory).filter(ClinicalHistory.patient_id == patient.id).all()
            history_df = pd.DataFrame([(h.visit_date, h.notes) for h in history], columns=["Visit Date", "Notes"])
            st.write(history_df)
            
            if st.button("Prescribe Medicines"):
                st.session_state["selected_patient_id"] = patient.id
                st.experimental_rerun()

# Prescribe Medicines Page
def prescribe_medicines():
    st.title("Prescribe Medicines")

    if "selected_patient_id" not in st.session_state:
        st.warning("Please select a patient first.")
        return
    
    patient_id = st.session_state["selected_patient_id"]
    
    with next(get_db()) as db:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        st.write(f"Prescribing medicines for {patient.name}")

    medicine_name = st.text_input("Medicine Name")
    visit_date = st.date_input("Visit Date")
    notes = st.text_area("Notes")

    if st.button("Save Prescription"):
        with next(get_db()) as db:
            new_history = ClinicalHistory(patient_id=patient_id, visit_date=visit_date, notes=notes)
            db.add(new_history)
            db.commit()
            st.success("Prescription saved successfully")

# Streamlit Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Add Patient", "View Patient History", "Prescribe Medicines"])

if page == "Add Patient":
    add_patient()
elif page == "View Patient History":
    view_patient_history()
elif page == "Prescribe Medicines":
    prescribe_medicines()
