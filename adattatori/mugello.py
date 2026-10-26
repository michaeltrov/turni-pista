"""Mugello: la pagina "Track day moto" del circuito. Il Mugello non vende: elenca chi ha la pista,
con mail, telefono e sito. Niente prezzi."""
import re

from .comune import testo, turno

FONTE = {
    "id": "mugello",
    "nome": "Mugello Circuit, track day moto",
    "url": "https://www.mugellocircuit.it/it/eventi/prove-libere-moto",
    "chi_vende": "organizzatori esterni",
    "condizioni": "Nessuna condizione d'uso sul sito (piè di pagina: privacy, accessibilità, codice di condotta, cookie). robots.txt blocca solo cartelle di sistema. Letto il 2026-10-21.",
}
BASE = "https://www.mugellocircuit.it"
VOCE = re.compile(r'<div class="djev_item djev_clearfix">(.*?)<div class="djev_clear">', re.S)


def _data(gg_mm_aaaa):
    g, m, a = gg_mm_aaaa.strip().split(".")
    return f"{a}-{m}-{g}"


def raccogli(get, oggi):
    pagina = get(FONTE["url"])
    turni = []
    for voce in VOCE.findall(pagina):
        da = re.search(r'djev_time_from">\s*([\d.]+)', voce)
        a = re.search(r'djev_time_to">.*?([\d]{2}\.[\d]{2}\.[\d]{4})', voce, re.S)
        titolo = re.search(r'djev_item_title">\s*<a href="([^"]+)">(.*?)</a>', voce, re.S)
        if not (da and titolo):
            continue
        contatti = voce[voce.find("CONTATTI"):] if "CONTATTI" in voce else ""
        email = re.search(r'mailto:([^"]+)"', contatti)
        tel = re.search(r'href="tel:([^"]+)"', contatti) or re.search(r"(?:Tel|Prenotazioni)[:\s]*([+\d() ]{8,})", testo(contatti))
        siti = [u for u in re.findall(r'href="(https?://[^"]+)"', contatti)]
        sito = siti[0] if siti else None
        turni.append(turno(
            "mugello", _data(da.group(1)), testo(titolo.group(2)), data_fine=_data(a.group(1)) if a else None,
            telefono=" ".join(tel.group(1).split()) if tel else None, email=email.group(1) if email else None,
            sito=sito, prenota=sito, pagina=BASE + titolo.group(1),
        ))
    return turni
