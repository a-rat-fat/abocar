from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    db.create_all()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    contact = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(300))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(120))
    notes = db.Column(db.Text)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    immat = db.Column(db.String(30), unique=True)  # immatriculation
    brand = db.Column(db.String(80))
    model = db.Column(db.String(120))
    year = db.Column(db.String(10))
    vin = db.Column(db.String(80))
    km = db.Column(db.Integer)
    status = db.Column(db.String(40))
    current_client_id = db.Column(db.Integer)
    next_client_id = db.Column(db.Integer)
    transfer_date = db.Column(db.String(20))
    service_km_next = db.Column(db.Integer)
    service_date_next = db.Column(db.String(20))
    tire_season = db.Column(db.String(20))
    tire_due_date = db.Column(db.String(20))
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id, "immatriculation": self.immat, "marque": self.brand,
            "modele": self.model, "annee": self.year, "vin": self.vin, "km": self.km,
            "statut": self.status, "client_actuel_id": self.current_client_id,
            "prochain_client_id": self.next_client_id, "date_transfert": self.transfer_date,
            "service_km_prochain": self.service_km_next, "service_date_prochaine": self.service_date_next,
            "pneus_saison": self.tire_season, "pneus_date_echeance": self.tire_due_date, "notes": self.notes
        }

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer)
    client_id = db.Column(db.Integer)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    monthly_fee = db.Column(db.Float)
    status = db.Column(db.String(40))

class RequestDemande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(200))
    type = db.Column(db.String(40))
    client_id = db.Column(db.String(120))
    depart_city = db.Column(db.String(120))
    depart_postcode = db.Column(db.String(10))
    arrival_city = db.Column(db.String(120))
    arrival_postcode = db.Column(db.String(10))
    date_wanted = db.Column(db.String(20))
    date_end = db.Column(db.String(20))
    vehicle_pref = db.Column(db.String(120))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id, "cree_le": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "cree_par": self.created_by, "type": self.type, "client_id": self.client_id,
            "ville_depart": self.depart_city, "cp_depart": self.depart_postcode,
            "ville_arrivee": self.arrival_city, "cp_arrivee": self.arrival_postcode,
            "date_souhaitee": self.date_wanted, "date_fin": self.date_end,
            "vehicule_pref": self.vehicle_pref, "notes": self.notes, "statut": self.status
        }

class Transport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer)
    vehicle_id = db.Column(db.Integer)
    from_client_id = db.Column(db.Integer)
    to_client_id = db.Column(db.Integer)
    pickup_city = db.Column(db.String(120))
    pickup_postcode = db.Column(db.String(10))
    delivery_city = db.Column(db.String(120))
    delivery_postcode = db.Column(db.String(10))
    pickup_date = db.Column(db.String(20))
    delivery_date = db.Column(db.String(20))
    carrier = db.Column(db.String(120))
    driver = db.Column(db.String(120))
    km_estimate = db.Column(db.Integer)
    status = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id, "demande_id": self.request_id, "vehicule_id": self.vehicle_id,
            "de_client_id": self.from_client_id, "vers_client_id": self.to_client_id,
            "ramassage_ville": self.pickup_city, "ramassage_cp": self.pickup_postcode,
            "livraison_ville": self.delivery_city, "livraison_cp": self.delivery_postcode,
            "date_ramassage": self.pickup_date, "date_livraison": self.delivery_date,
            "transporteur": self.carrier, "chauffeur": self.driver,
            "km_estime": self.km_estimate, "statut": self.status
        }

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer)
    type = db.Column(db.String(40))
    planned_date = db.Column(db.String(20))
    planned_km = db.Column(db.Integer)
    vendor = db.Column(db.String(120))
    status = db.Column(db.String(20))
    completed_date = db.Column(db.String(20))
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id, "vehicule_id": self.vehicle_id, "type": self.type,
            "date_planifiee": self.planned_date, "km_planifie": self.planned_km,
            "prestataire": self.vendor, "statut": self.status, "date_realisee": self.completed_date,
            "cout": self.cost, "notes": self.notes
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    actor = db.Column(db.String(200))
    action = db.Column(db.String(80))
    entity = db.Column(db.String(80))
    entity_id = db.Column(db.String(120))
    detail = db.Column(db.Text)

class CommuneCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q = db.Column(db.String(120), unique=True)  # clé de recherche
    payload = db.Column(db.Text)                # JSON
    ts = db.Column(db.Float)                    # epoch seconds
