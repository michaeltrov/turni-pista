"""Tazio Nuvolari: il negozio del circuito (shop.circuitotazionuvolari.it) ha una pagina per evento.
La lista si prende dalla mappa del sito; le giornate moto hanno "moto" nell'indirizzo."""
import datetime
import re

from .comune import testo, tipo_da_testo, turno

FONTE = {
    "id": "tazio",
    "nome": "Circuito Tazio Nuvolari, negozio online",
    "url": "https://shop.circuitotazionuvolari.it/",
    "chi_vende": "il circuito, per conto suo e degli operatori",
    "condizioni": "Termini e condizioni del negozio: riserva il diritto d'autore sui messaggi pubblicati, non vieta la raccolta automatica. Prendiamo solo fatti (data, prezzo) e rimandiamo alla pagina. robots.txt blocca solo /wp-admin/. Letto il 2026-10-21.",
}
MAPPE = ["https://shop.circuitotazionuvolari.it/ajde_events-sitemap1.xml",
         "https://shop.circuitotazionuvolari.it/ajde_events-sitemap2.xml"]
GIORNI_MODIFICA = 400  # pagine toccate nell'ultimo anno abbondante: le vecchie sono stagioni passate
MASSIMO_PAGINE = 60
ESCLUSI = ("corsi", "corso", "voucher", "gift")  # corsi di guida e buoni regalo non sono turni liberi


def candidati(mappe, oggi):
    visti, out = set(), []
    for xml in mappe:
        for url, mod in re.findall(r"<url>\s*<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", xml):
            if "moto" not in url.lower() or any(x in url.lower() for x in ESCLUSI) or url in visti:
                continue
            visti.add(url)
            if datetime.date.fromisoformat(mod[:10]) >= oggi - datetime.timedelta(days=GIORNI_MODIFICA):
                out.append((mod, url))
    return [u for _, u in sorted(out, reverse=True)[:MASSIMO_PAGINE]]


def leggi_evento(pagina, url):
    inizio = re.search(r"itemprop='startDate' content='(\d{4}-\d{2}-\d{2})'", pagina)
    if not inizio:
        return None
    fine = re.search(r"itemprop='endDate' content='(\d{4}-\d{2}-\d{2})'", pagina)
    nome = re.search(r"itemprop='name'\s*>([^<]+)<", pagina)
    nome = testo(nome.group(1)) if nome else ""
    if "moto" not in nome.lower():
        return None
    corpo = " ".join(testo(pagina).split())
    prezzo = None
    # la descrizione compare due volte (breve e intera): si prende il blocco prezzi che ha degli euro
    for blocco in re.findall(r"PREZZI:\s*(.*?)(?:Prezzi IVA|OBBLIGATORIO|NB:|Altro|$)", corpo):
        righe = [x.strip(" :") for x in blocco.split("•") if "€" in x]
        if righe:
            prezzo = " · ".join(righe)
            break
    # numero del circuito in testa alla pagina (X: cifre mascherate nelle pagine dei test)
    tel = re.search(r"eventi:\s*(\+?[\dX ]{8,}[\dX])", corpo)
    org = re.search(r"\bby ([A-Z][\w .&'-]{2,40})", nome)
    return turno(
        "tazio", inizio.group(1), org.group(1).strip() if org else "Circuito Tazio Nuvolari",
        data_fine=fine.group(1) if fine else None, tipo=tipo_da_testo(nome), prezzo=prezzo,
        telefono=tel.group(1).strip() if tel else None, email="info@circuitotazionuvolari.it", sito="https://www.circuitotazionuvolari.it",
        prenota=url, pagina=url, note=nome,
    )


def raccogli(get, oggi):
    mappe = [get(u) for u in MAPPE]
    turni = []
    for url in candidati(mappe, oggi):
        t = leggi_evento(get(url), url)
        if t:
            turni.append(t)
    return turni
