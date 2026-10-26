"""Promo Racing (Scarperia, FI): organizzatore che vende turni al Mugello, a Misano e all'estero.
Il calendario è una griglia HTML; ogni casella ha la data completa in data-box."""
import re

from .comune import circuito_da_nome, testo, turno

FONTE = {
    "id": "promoracing",
    "nome": "Promo Racing, calendario prove libere moto",
    "url": "https://www.promoracing.it/it/calendario/moto",
    "chi_vende": "organizzatore",
    "condizioni": "Nessuna condizione d'uso del sito: ci sono solo \"Termini e Condizioni di Pagamento\" per chi compra, privacy e cookie. Nessun robots.txt. Letto il 2026-10-21.",
}
BASE = "https://www.promoracing.it"
CASELLA = re.compile(r'<a href="(/it/calendario/moto\.\d+/[^"#]*)#?\d*" class="(event__item[^"]*)">(.*?)</a>', re.S)


def contatti(dettaglio):
    t = testo(dettaglio)
    email = re.search(r"[\w.+-]+@promoracing\.it", t)
    tel = re.search(r"Telefonica al\s*([\d +]{6,})", t)
    return (email.group(0) if email else None), (tel.group(1).strip() if tel else None)


def raccogli(get, oggi):
    pagina = get(FONTE["url"])
    turni, dettagli = [], {}
    for href, classi, dentro in CASELLA.findall(pagina):
        circuito = re.search(r'<p class="event__type">(.*?)</p>', dentro, re.S)
        cid = circuito_da_nome(testo(circuito.group(1))) if circuito else None
        if not cid:
            continue  # circuito estero: fuori dalla pagina
        box = re.search(r'data-box="[^"]*-(\d{8})"', dentro)
        data_mese = re.search(r'mnt(\d{6})', classi)
        if box:
            d = box.group(1)
        else:
            # le caselle successive di un evento su più giorni non hanno data-box: anno e mese dalla classe, giorno dal testo
            giorno = re.search(r'event__date">\s*(\d{1,2})', dentro)
            if not (giorno and data_mese):
                continue
            d = data_mese.group(1) + giorno.group(1).zfill(2)
        stato = re.search(r'event__available">\s*(.*?)\s*</p>', dentro, re.S)
        titolo = re.search(r'event__place">(.*?)</p>', dentro, re.S)
        url = BASE + href
        if url not in dettagli:
            dettagli[url] = contatti(get(url))
        email, tel = dettagli[url]
        turni.append(turno(
            cid, f"{d[:4]}-{d[4:6]}-{d[6:]}", "Promo Racing", tipo="a turni",
            telefono=tel, email=email, sito=BASE, prenota=url, pagina=url,
            note=" · ".join(x for x in [testo(titolo.group(1)) if titolo else None, testo(stato.group(1)) if stato else None] if x),
        ))
    return turni
