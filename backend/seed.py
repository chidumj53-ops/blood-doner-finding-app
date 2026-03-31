from models import db, Donor

sample_donors = [
    {
        "full_name": "Aarav Sharma",
        "blood_group": "A+",
        "city": "Bengaluru",
        "area": "Whitefield",
        "phone": "9876543210",
        "email": "aarav@example.com",
        "age": 27,
        "gender": "Male",
        "available": True,
        "last_donated": "2025-12-10"
    },
    {
        "full_name": "Priya Reddy",
        "blood_group": "O+",
        "city": "Bengaluru",
        "area": "Marathahalli",
        "phone": "9876501234",
        "email": "priya@example.com",
        "age": 24,
        "gender": "Female",
        "available": True,
        "last_donated": "2025-11-18"
    },
    {
        "full_name": "Rahul Kumar",
        "blood_group": "B+",
        "city": "Mysuru",
        "area": "VV Mohalla",
        "phone": "9988776655",
        "email": "rahul@example.com",
        "age": 30,
        "gender": "Male",
        "available": False,
        "last_donated": "2026-01-08"
    },
    {
        "full_name": "Sneha Patil",
        "blood_group": "AB+",
        "city": "Hubballi",
        "area": "Vidyanagar",
        "phone": "9123456780",
        "email": "sneha@example.com",
        "age": 29,
        "gender": "Female",
        "available": True,
        "last_donated": "2025-10-22"
    },
    {
        "full_name": "Kiran Das",
        "blood_group": "O-",
        "city": "Bengaluru",
        "area": "Indiranagar",
        "phone": "9012345678",
        "email": "kiran@example.com",
        "age": 33,
        "gender": "Male",
        "available": True,
        "last_donated": "2025-09-15"
    },
    {
        "full_name": "Divya Nair",
        "blood_group": "A-",
        "city": "Mangaluru",
        "area": "Kodialbail",
        "phone": "9090909090",
        "email": "divya@example.com",
        "age": 26,
        "gender": "Female",
        "available": True,
        "last_donated": "2025-12-01"
    }
]


def seed_data():
    if Donor.query.count() == 0:
        for donor_data in sample_donors:
            donor = Donor(**donor_data)
            db.session.add(donor)
        db.session.commit()
        print("Sample donor data inserted successfully.")
    else:
        print("Database already contains donor data.")