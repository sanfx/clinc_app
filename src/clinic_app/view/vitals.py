"""Module containing Patient's vital record for the crud app."""
from sqlalchemy.orm import Session
from models import Vitals


class PatientVitalsMeasurement:
    def __init__(self):
        pass

    def add(self, db: Session, patient_id, weight_in_kg, height_in_cm, systolic_bp, diastolic_bp, pulse, temperature_in_celsius, oxygen_levels, measurement_dt):
        new_vitals = Vitals(
            patient_id=patient_id,
            weight_in_kg=weight_in_kg,
            height_in_cm=height_in_cm,
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            pulse=pulse,
            temperature_in_celsius=temperature_in_celsius,
            oxygen_levels=oxygen_levels,
            measurement_dt=measurement_dt
        )
        db.add(new_vitals)
        db.commit()
        return new_vitals

    def read(self, db: Session, patient_id):
        return db.query(Vitals).filter(Vitals.patient_id == patient_id).all()
