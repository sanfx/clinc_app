import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Retrieve database credentials from Streamlit secrets
db_credentials = st.secrets["mysql"]

DATABASE_URL = f'mysql+pymysql://{db_credentials["username"]}:{db_credentials["password"]}@{db_credentials["host"]}:{db_credentials["port"]}/{db_credentials["database"]}'


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    home_address = Column(Text, nullable=False)
    email = Column(String(255), nullable=True)
    adhar_id = Column(String(20), unique=True, nullable=False)
    driving_licence_number = Column(String(20), nullable=True)
    photo = Column(String(255), nullable=True)
    clinical_history = relationship('ClinicalHistory', back_populates='patient')


class ClinicalHistory(Base):
    __tablename__ = 'clinical_history'
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    visit_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    patient = relationship('Patient', back_populates='clinical_history')

Base.metadata.create_all(bind=engine)
