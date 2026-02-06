from utils import templates

print("--- Testing Employment Agreement (Hindi) ---")
emp = templates.get_template(
    "Employment Agreement", 
    name="Raju Rastogi", 
    date="2024-01-01", 
    amount="10,00,000",
    language="Hindi"
)
print(emp)

print("\n--- Testing NDA (Hindi) ---")
nda = templates.get_template(
    "Non-Disclosure Agreement (NDA)", 
    name="Farhan Qureshi", 
    date="2024-02-01", 
    amount="Project Idiots",
    language="Hindi"
)
print(nda)

print("\n--- Testing Unsupported Template (Hindi) ---")
serv = templates.get_template(
    "Vendor Service Agreement", 
    name="TCS", 
    date="2024-03-01", 
    amount="50000",
    language="Hindi"
)
print(serv)
