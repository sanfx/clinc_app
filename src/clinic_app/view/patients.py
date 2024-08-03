"""Module representing the patient view for crud app."""
# Python Standard Imports
import os

# Third party imports
from sqlalchemy.orm import Session

# Local imports
from models import Patient


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
