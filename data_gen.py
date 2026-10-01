"""Generates ~300 synthetic records: 200 recipients + 60 organs + 40 hospitals."""
import random, os
import pandas as pd
from dsa import MAX_HOURS, BLOOD, blood_ok
random.seed(42); os.makedirs("data", exist_ok=True)

CITIES = ["Pune", "Mumbai", "Nashik", "Nagpur", "Thane", "Aurangabad", "Kolhapur", "Solapur", "Satara", "Ahmednagar"]
KINDS = ["General Hospital", "Heart Institute", "Medical Centre", "Care Hospital"]
hosp = [{"hospital_id": f"H{i+1:02d}", "name": f"{CITIES[i%10]} {random.choice(KINDS)} {i+1}",
         "city": CITIES[i % 10]} for i in range(40)]
names = [h["name"] for h in hosp]
W = [35, 4, 27, 4, 20, 3, 5, 2]
FIRST = ["Aarav","Diya","Kabir","Meera","Rohan","Isha","Vihaan","Anaya","Arjun","Sara","Neel","Tara"]
LAST = ["Patil","Sharma","Deshmukh","Joshi","Kulkarni","Shinde","More","Pawar","Gokhale","Rane"]

rec = []
for i in range(200):
    rec.append({"recipient_id": f"R{i+1:03d}", "name": f"{random.choice(FIRST)} {random.choice(LAST)}",
        "organ_needed": random.choices(list(MAX_HOURS), [45, 20, 12, 13, 10])[0],
        "blood_group": random.choices(BLOOD, W)[0],
        "urgency": random.choices(["High", "Medium", "Low"], [30, 45, 25])[0],
        "waiting_days": random.randint(5, 900), "hospital": random.choice(names), "status": "WAITING"})

org, used = [], set()
for i in range(60):
    t = random.choices(list(MAX_HOURS), [45, 20, 12, 13, 10])[0]; b = random.choices(BLOOD, W)[0]
    status, rid, off = "AVAILABLE", "", random.randint(5, int(MAX_HOURS[t] * 60 * 0.7))
    if i < 12:   # first 12 organs already in transit
        c = [r["recipient_id"] for r in rec if r["organ_needed"] == t and blood_ok(b, r["blood_group"]) and r["recipient_id"] not in used]
        if c: rid = random.choice(c); used.add(rid); status = "IN_TRANSIT"; off = random.randint(30, int(MAX_HOURS[t] * 60 * 0.85))
    org.append({"organ_id": f"O{101+i}", "organ_type": t, "blood_group": b, "donor_hospital": random.choice(names),
                "harvest_offset_min": off, "status": status, "recipient_id": rid})

pd.DataFrame(hosp).to_csv("data/hospitals.csv", index=False)
pd.DataFrame(rec).to_csv("data/recipients.csv", index=False)
pd.DataFrame(org).to_csv("data/organs.csv", index=False)
print("Generated", len(hosp) + len(rec) + len(org), "records")
