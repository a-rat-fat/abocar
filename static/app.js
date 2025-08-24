async function api(path, opts={}){
  const r = await fetch(path, Object.assign({ headers: {"Content-Type":"application/json"} }, opts));
  return await r.json();
}

const fd = document.getElementById("form-demande");
if (fd){
  fd.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(fd).entries());
    const out = await api("/api/demandes", {method:"POST", body: JSON.stringify(data)});
    const span = document.getElementById("demande-result");
    if(out.ok){ span.textContent = `Demande enregistrée (id: ${out.data.id})`; fd.reset(); }
    else { span.textContent = "Erreur: " + (out.error||""); }
  });
  ["ville_depart","ville_arrivee"].forEach(id => {
    const el = document.getElementById(id);
    if(!el) return;
    let last = 0;
    el.addEventListener("input", async () => {
      const q = el.value.trim();
      const now = Date.now();
      if (q.length < 2 || (now - last) < 200) return;
      last = now;
      const res = await api("/api/communes?q="+encodeURIComponent(q));
      showSuggest(el, (res.data||[]).map(c => `${c.nom} (${c.cps})`));
    });
  });
}

function showSuggest(input, options) {
  document.querySelectorAll(".suggest").forEach(s => s.remove());
  if (!options || !options.length) return;
  const rect = input.getBoundingClientRect();
  const div = document.createElement("div");
  div.className = "suggest";
  div.style.left = rect.left + window.scrollX + "px";
  div.style.top = rect.bottom + window.scrollY + "px";
  options.slice(0,10).forEach(opt => {
    const item = document.createElement("div");
    item.className = "suggest-item";
    item.textContent = opt;
    item.addEventListener("mousedown", () => {
      input.value = opt.replace(/\s*\(.+\)$/, "");
      div.remove();
    });
    div.appendChild(item);
  });
  document.body.appendChild(div);
}

const tbodyPuit = document.querySelector("#table-puit tbody");
if (tbodyPuit){
  document.getElementById("btn-refresh-puit").addEventListener("click", loadPuit);
  async function loadPuit(){
    tbodyPuit.innerHTML = "<tr><td colspan='9'>Chargement…</td></tr>";
    const out = await api("/api/demandes?statut=PUIT");
    if(!out.ok){ tbodyPuit.innerHTML = `<tr><td colspan='9'>Erreur: ${out.error}</td></tr>`; return; }
    tbodyPuit.innerHTML = "";
    (out.data||[]).forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.cree_le||""}</td>
        <td>${r.cree_par||""}</td>
        <td>${r.type||""}</td>
        <td>${r.client_id||""}</td>
        <td>${(r.ville_depart||"")+" "+(r.cp_depart||"")}</td>
        <td>${(r.ville_arrivee||"")+" "+(r.cp_arrivee||"")}</td>
        <td>${r.date_souhaitee||""}</td>
        <td>${r.notes||""}</td>
        <td><button class="planifier">Planifier</button></td>
      `;
      tr.querySelector(".planifier").addEventListener("click", ()=>openPlanifier(r));
      tbodyPuit.appendChild(tr);
    });
  }
  loadPuit();
}

function openPlanifier(demande){
  const html = `
  <div class="dlg-backdrop">
    <div class="dlg">
      <h3>Planifier transport</h3>
      <label>Véhicule ID <input id="f-vehicule_id" placeholder="ex: id"/></label>
      <label>De (client id) <input id="f-de_client_id" value="${demande.client_id||""}"/></label>
      <label>Vers (client id) <input id="f-vers_client_id"/></label>
      <label>Ramassage (ville) <input id="f-ram_v" value="${demande.ville_depart||""}"/></label>
      <label>Ramassage (CP) <input id="f-ram_c" value="${demande.cp_depart||""}"/></label>
      <label>Livraison (ville) <input id="f-liv_v" value="${demande.ville_arrivee||""}"/></label>
      <label>Livraison (CP) <input id="f-liv_c" value="${demande.cp_arrivee||""}"/></label>
      <label>Date ramassage <input id="f-date_r" type="date" value="${demande.date_souhaitee||""}"/></label>
      <label>Date livraison <input id="f-date_l" type="date"/></label>
      <label>Km estimé <input id="f-km" type="number"/></label>
      <div class="dlg-actions">
        <button id="dlg-cancel">Annuler</button>
        <button id="dlg-ok">Planifier</button>
      </div>
    </div>
  </div>`;
  const wrap = document.createElement("div");
  wrap.innerHTML = html;
  document.body.appendChild(wrap);
  wrap.querySelector("#dlg-cancel").addEventListener("click",()=>wrap.remove());
  wrap.querySelector("#dlg-ok").addEventListener("click", async ()=>{
    const payload = {
      demande_id: demande.id,
      vehicule_id: document.querySelector("#f-vehicule_id").value,
      de_client_id: document.querySelector("#f-de_client_id").value,
      vers_client_id: document.querySelector("#f-vers_client_id").value,
      ramassage_ville: document.querySelector("#f-ram_v").value,
      ramassage_cp: document.querySelector("#f-ram_c").value,
      livraison_ville: document.querySelector("#f-liv_v").value,
      livraison_cp: document.querySelector("#f-liv_c").value,
      date_ramassage: document.querySelector("#f-date_r").value,
      date_livraison: document.querySelector("#f-date_l").value,
      km_estime: document.querySelector("#f-km").value
    };
    const out = await api("/api/transports",{method:"POST", body: JSON.stringify(payload)});
    if(!out.ok) alert("Erreur: " + out.error);
    wrap.remove();
    location.href="/transports";
  });
}

const tbodyParc = document.querySelector("#table-parc tbody");
if (tbodyParc){
  document.getElementById("btn-refresh-parc").addEventListener("click", loadParc);
  async function loadParc(){
    tbodyParc.innerHTML = "<tr><td colspan='8'>Chargement…</td></tr>";
    const out = await api("/api/vehicles");
    if(!out.ok){ tbodyParc.innerHTML = `<tr><td colspan='8'>Erreur: ${out.error}</td></tr>`; return; }
    tbodyParc.innerHTML = "";
    (out.data||[]).forEach(v => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${v.immatriculation||""}</td>
        <td>${v.marque||""}</td>
        <td>${v.modele||""}</td>
        <td>${v.km||""}</td>
        <td>${v.statut||""}</td>
        <td>${v.client_actuel_id||""}</td>
        <td>${v.prochain_client_id||""}</td>
        <td>${v.date_transfert||""}</td>
      `;
      tbodyParc.appendChild(tr);
    });
  }
  loadParc();
}

const tbodyTrans = document.querySelector("#table-transports tbody");
if (tbodyTrans){
  document.getElementById("btn-refresh-transports").addEventListener("click", loadTransports);
  async function loadTransports(){
    tbodyTrans.innerHTML = "<tr><td colspan='6'>Chargement…</td></tr>";
    const out = await api("/api/transports");
    if(!out.ok){ tbodyTrans.innerHTML = `<tr><td colspan='6'>Erreur: ${out.error}</td></tr>`; return; }
    tbodyTrans.innerHTML = "";
    (out.data||[]).forEach(t => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${(t.ramassage_ville||"")+" "+(t.ramassage_cp||"")}</td>
        <td>${(t.livraison_ville||"")+" "+(t.livraison_cp||"")}</td>
        <td>${(t.date_ramassage||"")+" → "+(t.date_livraison||"")}</td>
        <td>${t.vehicule_id||""}</td>
        <td>${t.km_estime||""}</td>
        <td>${t.statut||""}</td>
      `;
      tbodyTrans.appendChild(tr);
    });
  }
  loadTransports();
}

const fd2 = document.getElementById("form-maint");
if (fd2){
  fd2.addEventListener("submit", async (e)=>{
    e.preventDefault();
    const data = Object.fromEntries(new FormData(fd2).entries());
    const out = await api("/api/maintenances",{method:"POST", body: JSON.stringify(data)});
    const span = document.getElementById("maint-result");
    if(out.ok){ span.textContent = `Maintenance planifiée (id: ${out.data.id})`; fd2.reset(); loadMaint(); }
    else { span.textContent = "Erreur: " + (out.error||""); }
  });
  document.getElementById("btn-refresh-maint").addEventListener("click", loadMaint);
  const tbodyMaint = document.querySelector("#table-maint tbody");
  async function loadMaint(){
    tbodyMaint.innerHTML = "<tr><td colspan='5'>Chargement…</td></tr>";
    const out = await api("/api/maintenances");
    if(!out.ok){ tbodyMaint.innerHTML = `<tr><td colspan='5'>Erreur: ${out.error}</td></tr>`; return; }
    tbodyMaint.innerHTML = "";
    (out.data||[]).forEach(m => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${m.vehicule_id||""}</td>
        <td>${m.type||""}</td>
        <td>${(m.date_planifiee||"")+" / "+(m.km_planifie||"")}</td>
        <td>${m.prestataire||""}</td>
        <td>${m.statut||""}</td>
      `;
      tbodyMaint.appendChild(tr);
    });
  }
  loadMaint();
}
