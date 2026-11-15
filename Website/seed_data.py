"""Seed / demo data — deep-copied into each new session by state.init_state()."""

SEED_PATIENTS = [
    {"id": "p1", "name": "James Chen",      "dob": "1978-04-12", "gender": "Male",   "last_active": "about 3 hours ago"},
    {"id": "p2", "name": "Maria Santos",    "dob": "1962-09-23", "gender": "Female", "last_active": "1 day ago"},
    {"id": "p3", "name": "Robert Williams", "dob": "1985-01-05", "gender": "Male",   "last_active": "3 days ago"},
]

SEED_CONSULTATIONS = {
    "p1": [{"id": "c1", "title": "Chest pain radiating to left arm", "date": "Mar 31, 2026", "messages": [
        {"role": "user", "text": "Patient presents with chest pain radiating to left arm, onset 3 hours ago. Mild shortness of breath. No fever.", "time": "9:14 PM"},
        {"role": "ai", "text": "**Potential Diagnosis: Acute Coronary Syndrome / Pulmonary Etiology**\n\nBased on the reported symptoms, the following differential diagnosis has been generated.", "time": "9:14 PM"},
    ]}],
    "p2": [], "p3": [],
}

SEED_DOCTOR = {
    "name": "Dr. Sarah Mitchell",
    "specialty": "Internal Medicine",
    "email": "sarah.mitchell@smartcare.ai",
    "hospital": "City General Hospital",
}
