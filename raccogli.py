"""Raccoglie i turni in pista da tutte le fonti e scrive dati/turni.json.

    python raccogli.py                # tutte le fonti
    python raccogli.py misano mugello # solo queste

Se una fonte fallisce, si tengono i suoi turni della raccolta prima, con la loro data di lettura:
meglio un dato vecchio dichiarato che un buco. L'errore finisce in "fonti" dentro il JSON.
"""
import datetime
import json
import pathlib
import re
import sys
import traceback

from adattatori import SALTATE, TUTTI
from adattatori.comune import CIRCUITI, scarica

QUI = pathlib.Path(__file__).parent
USCITA = QUI / "dati" / "turni.json"


def chiave(t):
    org = re.sub(r"[^a-z0-9]", "", (t["organizzatore"] or "").lower())
    return (t["circuito"], t["data_inizio"], org)


def unisci(turni):
    """Lo stesso turno visto da due fonti (Misano e Promo Racing, per esempio) diventa uno solo,
    con tutte e due le fonti e i campi riempiti da chi li ha."""
    uniti = {}
    for t in turni:
        k = chiave(t)
        if k not in uniti:
            uniti[k] = t
            continue
        u = uniti[k]
        for campo in ("tipo", "orario", "prezzo", "prenota", "note"):
            u[campo] = u[campo] or t[campo]
        for campo, valore in t["contatti"].items():
            u["contatti"][campo] = u["contatti"][campo] or valore
        u["data_fine"] = max(u["data_fine"], t["data_fine"])
        u["fonti"] += [f for f in t["fonti"] if f["id"] not in {x["id"] for x in u["fonti"]}]
    return list(uniti.values())


def precedenti():
    try:
        return json.loads(USCITA.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"turni": [], "fonti": {}}


def main(scelte):
    oggi = datetime.date.today()
    adesso = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    vecchio = precedenti()
    turni, stato = [], dict(vecchio.get("fonti", {}))
    for modulo in TUTTI:
        f = modulo.FONTE
        if scelte and f["id"] not in scelte:
            # fonte non richiesta: restano i suoi turni di prima, così com'erano
            turni += [dict(t, fonti=[x for x in t["fonti"] if x["id"] == f["id"]]) for t in vecchio["turni"]
                      if any(x["id"] == f["id"] for x in t["fonti"])]
            continue
        try:
            nuovi = modulo.raccogli(scarica, oggi)
            for t in nuovi:
                t["fonti"] = [{"id": f["id"], "nome": f["nome"], "url": t.pop("pagina") or f["url"], "letto_il": adesso}]
            turni += nuovi
            stato[f["id"]] = {**f, "ultima_lettura": adesso, "esito": "ok", "turni": len(nuovi)}
            print(f"{f['id']}: {len(nuovi)} turni")
        except Exception as e:  # una fonte rotta non deve fermare le altre
            tenuti = [dict(t, fonti=[x for x in t["fonti"] if x["id"] == f["id"]]) for t in vecchio["turni"]
                      if any(x["id"] == f["id"] for x in t["fonti"])]
            turni += tenuti
            ultima = vecchio.get("fonti", {}).get(f["id"], {}).get("ultima_lettura")
            stato[f["id"]] = {**f, "ultima_lettura": ultima, "esito": f"errore il {adesso}: {e}", "turni": len(tenuti)}
            print(f"{f['id']}: ERRORE {e} (tenuti {len(tenuti)} turni vecchi)", file=sys.stderr)
            traceback.print_exc()
    turni = [t for t in unisci(turni) if t["data_fine"] >= oggi.isoformat() and t["circuito"] in CIRCUITI]
    turni.sort(key=lambda t: (t["data_inizio"], t["circuito"], t["organizzatore"] or ""))
    uscita = {"generato_il": adesso, "circuiti": CIRCUITI, "fonti": stato, "non_coperte": SALTATE, "turni": turni}
    USCITA.parent.mkdir(exist_ok=True)
    USCITA.write_text(json.dumps(uscita, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"scritti {len(turni)} turni in {USCITA}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
