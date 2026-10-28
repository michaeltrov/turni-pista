"""Rosso Corsa (GSA Organization, Ozzano dell'Emilia): organizzatore di prove libere in Italia e all'estero.
L'elenco /prove ha giorni e mese senza anno; la pagina di ogni prova ha la data intera nel titolo.
Il prezzo si mostra solo se lo pubblica il loro sito ("a partire da" nell'elenco): scelta di Michael, 2026-10-28."""
import re

from .comune import circuito_da_nome, testo, turno

FONTE = {
    "id": "rossocorsa",
    "nome": "Rosso Corsa, calendario prove",
    "url": "https://www.rossocorsaonline.com/prove",
    "chi_vende": "organizzatore",
    "condizioni": "Le condizioni d'uso vietano di riprendere i contenuti senza consenso. Consenso scritto di GSA Organization "
                  "(Veronica Amato) il 2026-10-28: date e link alla loro pagina per comprare. Il prezzo solo se lo pubblicano loro.",
}
BASE = "https://www.rossocorsaonline.com"
VOCE = re.compile(r'<a href="(/prove/detail/\d+)"[^>]*>.*?<h3[^>]*>(.*?)</h3>(.*?)</a>', re.S)
MESI = {m: i for i, m in enumerate(["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
                                     "agosto", "settembre", "ottobre", "novembre", "dicembre"], 1)}


def date_da_titolo(t):
    """'Valencia / 05 -06 -07 febbraio 2027' -> ('2027-02-05', '2027-02-07'). Regge anche '30 aprile -01 maggio 2027'.
    Un giorno senza mese prende il mese che viene dopo; senza anno o senza mese, None."""
    anno = re.search(r"\b(20\d\d)\b", t)
    if not anno:
        return None
    giorni, in_attesa = [], []
    for numero, mese in re.findall(r"\b(\d{1,2})\b(?:\s+([a-z]+))?", t[:anno.start()].lower()):
        in_attesa.append(int(numero))
        if mese in MESI:
            giorni += [(MESI[mese], g) for g in in_attesa]
            in_attesa = []
    if not giorni:
        return None
    a = int(anno.group(1))
    (m1, g1), (m2, g2) = giorni[0], giorni[-1]
    # una prova a cavallo d'anno (30 dicembre - 02 gennaio 2028) comincia l'anno prima
    return f"{a - (m1 > m2):04d}-{m1:02d}-{g1:02d}", f"{a:04d}-{m2:02d}-{g2:02d}"


def raccogli(get, oggi):
    pagina = get(FONTE["url"])
    turni = []
    for href, titolo, resto in VOCE.findall(pagina):
        cid = circuito_da_nome(testo(titolo))
        if not cid:
            continue  # estero o buoni regalo: la pagina della prova non si scarica neanche
        url = BASE + href
        h1 = re.search(r"<h1>(.*?)</h1>", get(url), re.S)
        date = date_da_titolo(testo(h1.group(1))) if h1 else None
        if not date:
            continue
        prezzo = re.search(r"a partire da\s*<strong>\s*([\d.,]+)", resto)
        turni.append(turno(
            cid, date[0], "Rossocorsa", data_fine=date[1], prezzo=f"da {prezzo.group(1)} €" if prezzo else None,
            telefono="+39 051 6511712", email="info@rossocorsaonline.com", sito=BASE, prenota=url, pagina=url,
        ))
    return turni
