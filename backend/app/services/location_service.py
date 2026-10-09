from typing import List, Optional
from sqlalchemy.orm import Session as DBSession

from app.models.location import State, District, City, Village
from app.schemas.location import StateResponse, DistrictResponse, CityResponse, VillageResponse


def get_states(db: DBSession) -> List[StateResponse]:
    states = db.query(State).order_by(State.name).all()
    return [StateResponse.model_validate(s) for s in states]


def get_districts_by_state(db: DBSession, state_id: int) -> List[DistrictResponse]:
    districts = db.query(District).filter(District.state_id == state_id).order_by(District.name).all()
    return [DistrictResponse.model_validate(d) for d in districts]


def get_cities_by_district(db: DBSession, district_id: int) -> List[CityResponse]:
    cities = db.query(City).filter(City.district_id == district_id).order_by(City.name).all()
    return [CityResponse.model_validate(c) for c in cities]


def get_villages_by_city(db: DBSession, city_id: int) -> List[VillageResponse]:
    villages = db.query(Village).filter(Village.city_id == city_id).order_by(Village.name).all()
    return [VillageResponse.model_validate(v) for v in villages]


def get_state(db: DBSession, state_id: int) -> Optional[State]:
    return db.query(State).filter(State.id == state_id).first()


def get_district(db: DBSession, district_id: int) -> Optional[District]:
    return db.query(District).filter(District.id == district_id).first()


def get_city(db: DBSession, city_id: int) -> Optional[City]:
    return db.query(City).filter(City.id == city_id).first()


def get_village(db: DBSession, village_id: int) -> Optional[Village]:
    return db.query(Village).filter(Village.id == village_id).first()


def seed_locations(db: DBSession) -> None:
    if db.query(State).first():
        return

    ap = State(code="AP", name="Andhra Pradesh")
    kl = State(code="KL", name="Kerala")
    db.add_all([ap, kl])
    db.flush()

    ap_districts = [
        "Anantapur", "Chittoor", "East Godavari", "Guntur", "Kadapa", "Krishna",
        "Kurnool", "Nellore", "Prakasam", "Srikakulam", "Visakhapatnam",
        "Vizianagaram", "West Godavari"
    ]
    for dname in ap_districts:
        db.add(District(state_id=ap.id, name=dname))

    kl_districts = [
        "Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam",
        "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta",
        "Thiruvananthapuram", "Thrissur", "Wayanad"
    ]
    for dname in kl_districts:
        db.add(District(state_id=kl.id, name=dname))

    db.flush()

    district_cities = {
        "Anantapur": [("Anantapur", "city"), ("Hindupur", "city"), ("Kalyandurg", "town")],
        "Chittoor": [("Chittoor", "city"), ("Tirupati", "city"), ("Madanapalle", "town")],
        "East Godavari": [("Rajahmundry", "city"), ("Kakinada", "city"), ("Amalapuram", "town")],
        "Guntur": [("Guntur", "city"), ("Tenali", "city"), ("Narasaraopet", "town")],
        "Kadapa": [("Kadapa", "city"), ("Proddatur", "city"), ("Rayachoti", "town")],
        "Krishna": [("Vijayawada", "city"), ("Machilipatnam", "city"), ("Nuzvid", "town")],
        "Kurnool": [("Kurnool", "city"), ("Adoni", "city"), ("Nandyal", "city")],
        "Nellore": [("Nellore", "city"), ("Kavali", "city"), ("Gudur", "town")],
        "Prakasam": [("Ongole", "city"), ("Chirala", "city"), ("Markapur", "town")],
        "Srikakulam": [("Srikakulam", "city"), ("Palasa", "town"), ("Rajam", "town")],
        "Visakhapatnam": [("Visakhapatnam", "city"), ("Anakapalle", "city"), ("Narsipatnam", "town")],
        "Vizianagaram": [("Vizianagaram", "city"), ("Parvathipuram", "town"), ("Bobbili", "town")],
        "West Godavari": [("Eluru", "city"), ("Bhimavaram", "city"), ("Tadepalligudem", "city")],
        "Alappuzha": [("Alappuzha", "city"), ("Chengannur", "town"), ("Kayamkulam", "town")],
        "Ernakulam": [("Kochi", "city"), ("Aluva", "town"), ("Muvattupuzha", "town")],
        "Idukki": [("Thodupuzha", "town"), ("Munnar", "town"), ("Peerumedu", "town")],
        "Kannur": [("Kannur", "city"), ("Thalassery", "town"), ("Payyanur", "town")],
        "Kasaragod": [("Kasaragod", "town"), ("Kanhangad", "town"), ("Nileshwar", "town")],
        "Kollam": [("Kollam", "city"), ("Punalur", "town"), ("Karunagappally", "town")],
        "Kottayam": [("Kottayam", "city"), ("Changanassery", "town"), ("Pala", "town")],
        "Kozhikode": [("Kozhikode", "city"), ("Vatakara", "town"), ("Koyilandy", "town")],
        "Malappuram": [("Malappuram", "city"), ("Manjeri", "city"), ("Perinthalmanna", "town")],
        "Palakkad": [("Palakkad", "city"), ("Ottapalam", "town"), ("Chittur", "town")],
        "Pathanamthitta": [("Pathanamthitta", "town"), ("Adoor", "town"), ("Thiruvalla", "town")],
        "Thiruvananthapuram": [("Thiruvananthapuram", "city"), ("Neyyattinkara", "town"), ("Attingal", "town")],
        "Thrissur": [("Thrissur", "city"), ("Guruvayur", "town"), ("Kunnamkulam", "town")],
        "Wayanad": [("Kalpetta", "town"), ("Mananthavady", "town"), ("Sultan Bathery", "town")],
    }

    for district_name, cities in district_cities.items():
        district = db.query(District).filter(District.name == district_name).first()
        if district:
            for city_name, city_type in cities:
                db.add(City(district_id=district.id, name=city_name, type=city_type))

    db.flush()

    city_villages = {
        "Anantapur": ["Anantapur Rural", "Bukkarayasamudram", "Kudair"],
        "Tirupati": ["Tirupati Rural", "Chandragiri", "Renigunta"],
        "Vijayawada": ["Vijayawada Rural", "Gannavaram", "Nandigama"],
        "Visakhapatnam": ["Visakhapatnam Rural", "Anandapuram", "Bheemunipatnam"],
        "Kochi": ["Kochi Rural", "Kumbalangi", "Cheranallur"],
        "Thiruvananthapuram": ["Thiruvananthapuram Rural", "Kazhakkoottam", "Sreekaryam"],
    }

    for city_name, villages in city_villages.items():
        city = db.query(City).filter(City.name == city_name).first()
        if city:
            for village_name in villages:
                db.add(Village(city_id=city.id, name=village_name))

    db.commit()