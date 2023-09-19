import os
import streamlit as st
from pymongo import MongoClient
import datetime
import pandas as pd

def create_app():

    st.title('Medidas de Pressão Arterial:')

    MONGO_DB = os.environ['MONGO_DB']
    client = MongoClient(MONGO_DB)
    db = client.petridish
    patients = db.patients

    cpf = st.text_input('CPF')
    if not cpf:
        st.warning('Por favor, insira um CPF válido.')
        return

    patient = patients.find_one({"cpf": cpf})
    if not patient:
        patient_name = st.text_input('Nome Completo')
        if not patient_name: 
            st.warning('Por favor, insira um Nome Completo.')
            return
        result = patients.insert_one({"cpf": cpf, "name": patient_name, "measurements": []})
        if result.inserted_id:
            st.success("Os dados do paciente foram inseridos com sucesso!")
        else:
            st.error("Falha na inserção dos dados do paciente!")
        return

    patient_name = patient.get('name', '')
    measurements = patient.get('measurements', [])

    st.write('Paciente:', patient_name)

    date = st.date_input('Data da Aferição')
    time = st.time_input('Horário da Aferição')
    blood_pressure_systolic = st.number_input('Pressão Sistólica', min_value=0, max_value=300, step=1)
    blood_pressure_diastolic = st.number_input('Pressão Diastólica', min_value=0, max_value=200, step=1)

    if st.button('Salvar'):
        measurements.append({
            "date": datetime.datetime.combine(date, time),
            "blood_pressure_systolic": blood_pressure_systolic,
            "blood_pressure_diastolic": blood_pressure_diastolic})
            
        result = patients.update_one({"cpf": cpf}, {"$set": {"measurements": measurements}})
        if result.modified_count > 0:
            st.success("Aferição salva com sucesso!")
        else:
            st.error("Houve erro na gravação!")
    

    measurements_df = pd.DataFrame(measurements)
    if 'date' in measurements_df.columns:
        measurements_df["date"] = pd.to_datetime(measurements_df["date"], infer_datetime_format=True)
  
    # Rename columns
    measurements_df = measurements_df.rename(columns={"date": "Data", "blood_pressure_systolic": "Pressão Sistólica", "blood_pressure_diastolic": "Pressão Disastólica"})
    
    if not measurements_df.empty:
        st.write(measurements_df)
    else:
        st.write("No measurements available")

    if st.button('Logout'):
        st.experimental_rerun()

if __name__ == "__main__":
    create_app()
