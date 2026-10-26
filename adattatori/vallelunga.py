"""Vallelunga: la pagina delle prove libere moto del circuito, con calendario e prezzi.
Ogni giorno è un link con data-date; alcuni giorni sono di un partner (Ducati Appia, The Bike...)."""
import re

from .comune import testo, tipo_da_testo, turno

FONTE = {
    "id": "vallelunga",
    "nome": "Autodromo di Vallelunga, prove libere moto",
    "url": "https://motorsport.vallelunga.it/pl-moto-2/",
    "chi_vende": "il circuito, più giornate di partner",
    "condizioni": "Nessuna condizione d'uso trovata su motorsport.vallelunga.it (menu e piè di pagina). robots.txt blocca solo /wp-admin/. Letto il 2026-10-21.",
}
TELEFONO = None  # la pagina non lo scrive; i contatti stanno in /contatti/
GIORNO = re.compile(r'<a class="plmoto-day[^"]*"[^>]*?href="([^"]*)"[^>]*?data-date="(\d{4}-\d{2}-\d{2})"[^>]*>(.*?)</a>', re.S)


def prezzi(pagina):
    t = " ".join(testo(pagina).split())
    festivo = re.search(r"Prefestivo\s*/\s*Festivo\s*(.{0,40}?)\s(\d+)\s*€", t)
    feriale = re.search(r"Feriale\s*(.{0,40}?)\s(\d+)\s*€", t)
    if not (festivo and feriale):
        return None
    return (f"feriale {feriale.group(2)} € ({feriale.group(1).strip()}), "
            f"prefestivo e festivo {festivo.group(2)} € ({festivo.group(1).strip()})")


def raccogli(get, oggi):
    pagina = get(FONTE["url"])
    prezzo = prezzi(pagina)
    turni = []
    for href, data, dentro in GIORNO.findall(pagina):
        meta = re.search(r'<span class="meta">(.*?)</span>', dentro, re.S)
        partner = re.search(r'<span class="partner[^"]*">(.*?)</span>', dentro, re.S)
        meta = testo(meta.group(1)) if meta else None
        partner = testo(partner.group(1)) if partner else None
        turni.append(turno(
            "vallelunga", data, partner or "Autodromo di Vallelunga",
            tipo=tipo_da_testo(meta) or "a turni", orario=meta,
            prezzo=None if partner else prezzo,
            sito="https://motorsport.vallelunga.it", prenota=FONTE["url"], pagina=FONTE["url"],
            note=(f"Giornata con {partner}: il prezzo del circuito potrebbe non valere." if partner else None),
        ))
    return turni
