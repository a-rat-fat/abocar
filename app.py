import os, json, time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from models import db, init_db, Client, Vehicle, Subscription, RequestDemande, Transport, Maintenance, Log, CommuneCache
import requests as pyrequests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    init_db()

@app.route("/")
def index(): return render_template("index.html")
@app.route("/demandes")
def page_demandes(): return render_template("demandes.html")
@app.route("/puits")
def page_puits(): return render_template("puits.html")
@app.route("/parc")
def page_parc(): return render_template("parc.html")
@app.route("/transports")
def page_transports(): return render_template("transports.html")
@app.route("/maintenance")
def page_maintenance(): return render_template("maintenance.html")

def actor_email(): return request.headers.get("X-User-Email", "inconnu")
def log(action, entity, entity_id, detail=None):
    lg = Log(ts=datetime.utcnow(), actor=actor_email(), action=action, entity=entity, entity_id=str(entity_id), detail=json.dumps(detail or {}))
    db.session.add(lg); db.session.commit()

@app.get("/api/ping")
def api_ping(): return jsonify(ok=True, pong=True, now=datetime.utcnow().isoformat())

@app.post("/api/demandes")
def api_add_demande():
    data = request.get_json(force=True)
    d = RequestDemande(
        created_at=datetime.utcnow(), created_by=actor_email(),
        type=(data.get("type") or "").upper(), client_id=data.get("client_id"),
        depart_city=data.get("ville_depart"), depart_postcode=data.get("cp_depart"),
        arrival_city=data.get("ville_arrivee"), arrival_postcode=data.get("cp_arrivee"),
        date_wanted=data.get("date_souhaitee"), date_end=data.get("date_fin"),
        vehicle_pref=data.get("vehicule_pref"), notes=data.get("notes"), status="PUIT"
    )
    db.session.add(d); db.session.commit(); log("ADD_DEMANDE","demande", d.id, data)
    return jsonify(ok=True, data={"id": d.id})

@app.get("/api/demandes")
def api_list_demandes():
    statut = request.args.get("statut"); q = RequestDemande.query
    if statut: q = q.filter_by(status=statut)
    rows = [r.to_dict() for r in q.order_by(RequestDemande.created_at.desc()).all()]
    return jsonify(ok=True, data=rows)

@app.post("/api/transports")
def api_plan_transport():
    data = request.get_json(force=True)
    t = Transport(
        request_id=data.get("demande_id"),
        vehicle_id=data.get("vehicule_id"),
        from_client_id=data.get("de_client_id"),
        to_client_id=data.get("vers_client_id"),
        pickup_city=data.get("ramassage_ville"),
        pickup_postcode=data.get("ramassage_cp"),
        delivery_city=data.get("livraison_ville"),
        delivery_postcode=data.get("livraison_cp"),
        pickup_date=data.get("date_ramassage"),
        delivery_date=data.get("date_livraison"),
        carrier=data.get("transporteur"),
        driver=data.get("chauffeur"),
        km_estimate=data.get("km_estime"),
        status="PLANIFIE"
    )
    db.session.add(t)
    if t.request_id:
        d = RequestDemande.query.get(t.request_id)
        if d: d.status = "PLANIFIE"
    db.session.commit(); log("PLAN_TRANSPORT","transport", t.id, data)
    return jsonify(ok=True, data={"id": t.id})

@app.get("/api/transports")
def api_list_transports():
    rows = [t.to_dict() for t in Transport.query.order_by(Transport.id.desc()).all()]
    return jsonify(ok=True, data=rows)

@app.get("/api/vehicles")
def api_list_vehicles():
    rows = [v.to_dict() for v in Vehicle.query.order_by(Vehicle.id.desc()).all()]
    return jsonify(ok=True, data=rows)

@app.post("/api/vehicles")
def api_upsert_vehicle():
    data = request.get_json(force=True)
    immat = (data.get("immatriculation") or "").strip().upper()
    if not immat: return jsonify(ok=False, error="immatriculation obligatoire"), 400
    v = Vehicle.query.filter_by(immat=immat).first()
    if not v: v = Vehicle(immat=immat); db.session.add(v)
    v.brand = data.get("marque"); v.model = data.get("modele"); v.year = data.get("annee")
    v.vin = data.get("vin"); v.km = data.get("km"); v.status = data.get("statut")
    v.current_client_id = data.get("client_actuel_id"); v.next_client_id = data.get("prochain_client_id")
    v.transfer_date = data.get("date_transfert"); v.service_km_next = data.get("service_km_prochain")
    v.service_date_next = data.get("service_date_prochaine"); v.tire_season = data.get("pneus_saison")
    v.tire_due_date = data.get("pneus_date_echeance"); v.notes = data.get("notes")
    db.session.commit(); log("UPSERT_VEHICULE","vehicule", v.id, data)
    return jsonify(ok=True, data={"id": v.id})

@app.post("/api/maintenances")
def api_schedule_maint():
    data = request.get_json(force=True)
    m = Maintenance(
        vehicle_id=data.get("vehicule_id"), type=(data.get("type") or "").upper(),
        planned_date=data.get("date_planifiee"), planned_km=data.get("km_planifie"),
        vendor=data.get("prestataire"), status="PLANIFIE",
        cost=data.get("cout"), notes=data.get("notes")
    )
    db.session.add(m); db.session.commit(); log("SCHEDULE_MAINT","maintenance", m.id, data)
    return jsonify(ok=True, data={"id": m.id})

@app.get("/api/maintenances")
def api_list_maint():
    rows = [m.to_dict() for m in Maintenance.query.order_by(Maintenance.id.desc()).all()]
    return jsonify(ok=True, data=rows)

@app.get("/api/communes")
def api_communes():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2: return jsonify(ok=True, data=[])
    key = q.lower()
    cached = CommuneCache.query.filter_by(q=key).first()
    import time
    if cached and (time.time() - cached.ts) < 86400:
        try: return jsonify(ok=True, data=json.loads(cached.payload))
        except Exception: pass
    url = "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux&format=json"
    try:
        rsp = pyrequests.get(url, timeout=8); arr = rsp.json()
        needle = key; out = []
        for c in arr:
            nom = c.get("nom","")
            if needle in nom.lower():
                out.append({ "code": c.get("code"), "nom": nom, "cps": "|".join(c.get("codesPostaux") or []) })
                if len(out) >= 25: break
        payload = json.dumps(out, ensure_ascii=False)
        if cached: cached.payload = payload; cached.ts = time.time()
        else:
            cached = CommuneCache(q=key, payload=payload, ts=time.time()); db.session.add(cached)
        db.session.commit()
        return jsonify(ok=True, data=out)
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
