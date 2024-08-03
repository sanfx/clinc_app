import streamlit as st
from sqlalchemy.orm import Session
from models import SessionLocal, Patient, ClinicalHistory, Vitals
from view.patients import Patients
from view.vitals import PatientVitalsMeasurement
import pandas as pd
import os
import random
import string
from datetime import datetime


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

# Patients Class
class Patients:
    def __init__(self):
        pass

    def add(self, db: Session, name, phone_number, home_address, email, adhar_id, driving_licence_number, photo_path):
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
        return new_patient

    def select(self, db: Session, patient_id):
        return db.query(Patient).filter(Patient.id == patient_id).first()

    def delete(self, db: Session, patient_id):
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if patient:
            # Delete the associated image
            if patient.photo and os.path.exists(patient.photo):
                os.remove(patient.photo)
            db.delete(patient)
            db.commit()
            return True
        return False

# Dashboard Page
def dashboard():
    st.title("Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add New Patient", key="add_new_patient"):
            st.session_state["page"] = "Add New Patient"
    with col2:
        if st.button("Select Patient", key="select_patient"):
            st.session_state["page"] = "Select Patient"
    with col3:
        if st.button("Prescribe Medicine", key="prescribe_medicine"):
            st.session_state["page"] = "Prescribe Medicine"
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("Check Vitals", key="check_vitals"):
            st.session_state["page"] = "Check Vitals"
    with col5:
        if st.button("Add New Action", key="add_new_action"):
            st.session_state["page"] = "Add New Action"


# Add Patient Page
def add_patient():
    st.title("Add Patient")

    name = st.text_input("Name")
    phone_number = st.text_input("Phone Number")
    home_address = st.text_area("Home Address")
    email = st.text_input("Email (optional)")
    adhar_id = st.text_input("Adhar ID")
    driving_licence_number = st.text_input("Driving Licence Number")

    tab1, tab2 = st.tabs(["Browse", "Take Photo"])

    photo_path = None
    with tab1:
        uploaded_file = st.file_uploader("Upload Photo", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            photo_path = save_uploaded_file(uploaded_file, name, phone_number, adhar_id)

    with tab2:
        camera_photo = st.camera_input("Take a Photo", disabled=True)
        if camera_photo:
            photo_path = save_uploaded_file(camera_photo, name, phone_number, adhar_id)

    if st.button("Add Patient"):
        if not phone_number:
            phone_number = generate_random_string(10)
        if not adhar_id:
            adhar_id = generate_random_string(12)

        with next(get_db()) as db:
            patients = Patients()
            patients.add(db, name, phone_number, home_address, email, adhar_id, driving_licence_number, photo_path)
            st.success("Patient added successfully")


# Select and Delete Patient Page
def select_delete_patient():
    st.title("View Patient")

    with next(get_db()) as db:
        patients = db.query(Patient).all()
        patient_names = {patient.name: patient.id for patient in patients}
    
    selected_patient_name = st.selectbox("Select Patient", list(patient_names.keys()), key="selected_patient")
    
    if selected_patient_name:
        patient_id = patient_names[selected_patient_name]
        with next(get_db()) as db:
            patients = Patients()
            patient = patients.select(db, patient_id)
            if patient:
                st.write(f"Name: {patient.name}")
                st.write(f"Phone Number: {patient.phone_number}")
                st.write(f"Home Address: {patient.home_address}")
                st.write(f"Email: {patient.email}")
                st.write(f"Adhar ID: {patient.adhar_id}")
                st.write(f"Driving Licence Number: {patient.driving_licence_number}")
                if patient.photo:
                    st.image(patient.photo, caption=f"{patient.name}'s Photo")

                if st.button("Delete Patient"):
                    if st.confirm("Are you sure you want to delete this patient? This action cannot be undone."):
                        with next(get_db()) as db:
                            if patients.delete(db, patient_id):
                                st.success("Patient deleted successfully")
                            else:
                                st.error("Failed to delete patient")


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

    with next(get_db()) as db:
        patients = db.query(Patient).all()
        patient_names = {patient.name: patient.id for patient in patients}
    
    selected_patient_name = st.selectbox("Select Patient", list(patient_names.keys()), key="selected_patient")
    
    if selected_patient_name:
        patient_id = patient_names[selected_patient_name]
        st.session_state["selected_patient_id"] = patient_id
        with next(get_db()) as db:
            patients = Patients()
            patient = patients.select(db, patient_id)
            if patient:
                st.write(f"Prescribing medicines for {patient.name}")

                # Display vitals
                vitals_measurement = PatientVitalsMeasurement()
                vitals = vitals_measurement.read(db, patient.id)
                if vitals:
                    latest_vitals = vitals[-1]
                    st.write(f"Weight: {latest_vitals.weight_in_kg} kg")
                    st.write(f"Height: {latest_vitals.height_in_cm} cm")
                    st.write(f"Systolic BP: {latest_vitals.systolic_bp}")
                    st.write(f"Diastolic BP: {latest_vitals.diastolic_bp}")
                    st.write(f"Pulse: {latest_vitals.pulse}")
                    st.write(f"Temperature: {latest_vitals.temperature_in_celsius} ℃")
                    st.write(f"SpO2: {latest_vitals.oxygen_levels}")
                else:
                    st.warning("No vitals recorded. Redirecting to add vitals page.")
                    st.session_state["page"] = "Check Vitals"
                    st.experimental_rerun()

    medicine_name = st.text_input("Medicine Name")
    visit_date = st.date_input("Visit Date")
    notes = st.text_area("Notes")

    if st.button("Prescribe"):
        with next(get_db()) as db:
            new_history = ClinicalHistory(patient_id=patient_id, visit_date=visit_date, notes=notes, prescribed_medicine=medicine_name)
            db.add(new_history)
            db.commit()
            st.success("Prescription saved successfully")


# Check Vitals Page
def check_vitals():
    st.title("Check Vitals")

    if "selected_patient_id" in st.session_state:
        patient_id = st.session_state["selected_patient_id"]
        with next(get_db()) as db:
            patients = Patients()
            patient = patients.select(db, patient_id)
            if patient:
                st.write(f"Checking vitals for {patient.name}")

                weight_in_kg = st.number_input("Weight (kg)", min_value=0.0, format="%.2f")
                weight_in_lbs = weight_in_kg * 2.20462
                st.write(f"Weight (lbs): {weight_in_lbs:.2f}")

                height_in_cm = st.number_input("Height (cm)", min_value=0.0, format="%.2f")
                height_in_ft = height_in_cm / 30.48
                height_in_inches = height_in_cm / 2.54
                st.write(f"Height (ft): {height_in_ft:.2f}")
                st.write(f"Height (inches): {height_in_inches:.2f}")

                systolic_bp = st.number_input("Systolic BP", min_value=0)
                diastolic_bp = st.number_input("Diastolic BP", min_value=0)
                pulse = st.number_input("Pulse", min_value=0)
                temperature_in_celsius = st.number_input("Temperature (℃)", min_value=0.0, format="%.2f")
                temperature_in_fahrenheit = (temperature_in_celsius * 9/5) + 32
                st.write(f"Temperature (℉): {temperature_in_fahrenheit:.2f}")

                oxygen_levels = st.number_input("SpO2", min_value=0)
                measurement_dt = datetime.now()

                if st.button("Save"):
                    with next(get_db()) as db:
                        vitals_measurement = PatientVitalsMeasurement()
                        vitals_measurement.add(db, patient_id, weight_in_kg, height_in_cm, systolic_bp, diastolic_bp, pulse, temperature_in_celsius, oxygen_levels, measurement_dt)
                        st.success("Vitals saved successfully")
    else:
        st.warning("No patient selected. Please select a patient first.")
        st.session_state["page"] = "Select Patient"
        st.experimental_rerun()


# Streamlit Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Attend", ["Dashboard", "Patients", "View Patient History", "Prescribe Medicines", "Check Vitals"])

if page == "Dashboard":
    dashboard()
elif page == "Patients":
    operation = st.sidebar.radio("Patient", ["Add New", "Existing Patient"])
    if operation == "Add New":
        add_patient()
    elif operation == "Existing Patient":
        select_delete_patient()
elif page == "View Patient History":
    view_patient_history()
elif page == "Prescribe Medicines":
    prescribe_medicines()
elif page == "Check Vitals":
    check_vitals()
