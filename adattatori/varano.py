"""Varano: il calendario del circuito, che il sito carica in un riquadro da calendar.php.
Ogni evento ha una categoria; si tengono solo le "Prove Libere Moto"."""
import datetime
import json

from .comune import tipo_da_testo, turno

FONTE = {
    "id": "varano",
    "nome": "Autodromo di Varano, calendario eventi",
    "url": "https://www.autodromovarano.it/calendario/",
    "chi_vende": "il circuito (SO.GE.S.A.), più organizzatori esterni",
    "condizioni": "Il link \"Terms & Conditions\" del sito porta a una pagina che non esiste (404). Nessun divieto trovato. robots.txt non vieta niente. Letto il 2026-10-21.",
}
API = "https://www.autodromovarano.it/autodromo-core/calendar.php"
DETTAGLIO = "https://www.autodromovarano.it/event-detail/?event_id={}"


def raccogli(get, oggi):
    fine = oggi + datetime.timedelta(days=400)
    eventi = json.loads(get(API, {"start": oggi.isoformat(), "end": fine.isoformat()}))
    turni = []
    for e in eventi:
        if "moto" not in (e.get("category_name") or "").lower():
            continue
        org = e.get("organization_name") or e.get("title")
        del_circuito = "sogesa" in (org or "").lower().replace(".", "")
        turni.append(turno(
            "varano", e["start"][:10], org, data_fine=(e.get("end") or e["start"])[:10],
            tipo=tipo_da_testo(e.get("title")), orario=f"{e['start'][11:16]}-{(e.get('end') or '')[11:16]}".rstrip("-"),
            telefono="+39 0525 551211" if del_circuito else None,
            email="autodromo@varano.it" if del_circuito else None,
            sito="https://www.autodromovarano.it" if del_circuito else None,
            prenota=DETTAGLIO.format(e["id"]), pagina=FONTE["url"],
            note=" ".join(e.get("title", "").split()),
        ))
    return turni
