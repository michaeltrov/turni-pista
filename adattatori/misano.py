"""Misano World Circuit: il calendario pista del sito. Ogni giornata è affittata a un organizzatore,
con nome, telefono e sito. Il sito lo carica da un'interfaccia sua, un mese per volta."""
import json

from .comune import turno

FONTE = {
    "id": "misano",
    "nome": "Misano World Circuit, calendario pista",
    "url": "https://www.misanocircuit.com/events",
    "chi_vende": "organizzatori esterni",
    "condizioni": "Nessuna condizione d'uso sul sito (solo privacy, cookie e regolamento di pista). robots.txt permette tutto tranne /admin. Letto il 2026-10-21.",
}
API = "https://api.misanocircuit.com/api/v1/remote/track-bookings?date={}"
MESI_AVANTI = 12


def mesi(oggi, quanti=MESI_AVANTI):
    a, m = oggi.year, oggi.month
    for _ in range(quanti + 1):
        yield f"{a}-{m:02d}"
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def raccogli(get, oggi):
    turni = []
    for mese in mesi(oggi):
        for e in json.loads(get(API.format(mese))):
            orario = None
            if e.get("startHour") and e.get("endHour"):
                orario = f"{e['startHour'][:5]}-{e['endHour'][:5]}"
            turni.append(turno(
                "misano", e["startDate"], e.get("name"), data_fine=e.get("endDate"), orario=orario,
                telefono=e.get("phoneNumber") or None, sito=e.get("website") or None,
                prenota=None, pagina=FONTE["url"],
                note="Il calendario di Misano elenca solo organizzatori di giornate moto (visto da ottobre 2026 a settembre 2027). Prezzo e prenotazione sul sito dell'organizzatore.",
            ))
    for t in turni:
        t["prenota"] = t["contatti"]["sito"]
    return turni

