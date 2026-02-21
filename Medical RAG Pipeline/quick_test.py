from clinical_preprocessor import ClinicalPreprocessor

preprocessor = ClinicalPreprocessor()

query = "a 38-year-old pregnant woman at 10 weeks gestation with BP: 118/76 mmHg Hb: 11.5 g/dL FBS: 90 mg/dL"

result = preprocessor.process_query(query)
features = result['extracted_features']

print(f"Age: {features.age}")
print(f"Age Risk: {features.age_risk_category}")
print(f"Gestational Age: {features.gestational_age_weeks}")
print(f"BP: {features.systolic_bp}/{features.diastolic_bp}")
print(f"BP Risk: {features.bp_risk}")
print(f"Hb: {features.hemoglobin}")
print(f"Anemia Risk: {features.anemia_risk}")
print(f"FBS: {features.fasting_glucose}")
print(f"Glucose Risk: {features.glucose_risk}")
