"""Portami in Pista: organizzatore (scuola riconosciuta CONI) con turni per capacità a Misano, Cremona, Varano
e altri. La pagina "Prove Libere Moto" ha l'anno nel titolo, poi per ogni circuito una riga per mese:
i giorni sono link di prenotazione, il prezzo è in fondo alla riga."""
import re

from .comune import circuito_da_nome, testo, turno

FONTE = {
    "id": "portamiinpista",
    "nome": "Portami in Pista, prove libere moto",
    "url": "https://www.portamiinpista.it/TrackDays/",
    "chi_vende": "organizzatore",
    "condizioni": "Nessuna condizione d'uso pubblicata (solo privacy, cookie, regolamento di pista; \"All Rights Reserved\" generico). robots.txt vieta solo il modulo di pagamento e l'area riservata: noi lo linkiamo, non lo apriamo. Letto il 2026-10-21.",
}
MESI = {m: i for i, m in enumerate(["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
                                     "agosto", "settembre", "ottobre", "novembre", "dicembre"], 1)}


def raccogli(get, oggi):
    pagina = get(FONTE["url"])
    anno = re.search(r"Giornate in Pista (\d{4})", pagina)
    if not anno:
        raise ValueError("anno della stagione non trovato nella pagina")  # meglio fallire che indovinare l'anno
    anno = int(anno.group(1))
    corpo = pagina[pagina.find("Giornate in Pista"):]
    turni, circuito = [], None
    for pezzo in re.finditer(r"<h3[^>]*>(.*?)</h3>|<li>(.*?)</li>", corpo, re.S):
        if pezzo.group(1) is not None:
            circuito = circuito_da_nome(testo(pezzo.group(1)))
            continue
        riga = pezzo.group(2)
        mese = MESI.get(testo(riga).split(" ")[0].strip().lower())
        if not (circuito and mese):
            continue
        prezzo = re.search(r"<em>(.*?)</em>", riga, re.S)
        prezzo = testo(prezzo.group(1)).replace("€", " €").replace("  ", " ").strip() if prezzo else None
        for href, giorno in re.findall(r'<a href="([^"]+)"[^>]*>\s*(\d{1,2})', riga):
            turni.append(turno(
                circuito, f"{anno}-{mese:02d}-{int(giorno):02d}", "Portami in Pista", tipo="a turni",
                prezzo=prezzo, email="info@portamiinpista.it", sito="https://www.portamiinpista.it",
                prenota=href.replace("&amp;", "&"), pagina=FONTE["url"],
                note="Turni per capacità. Il prezzo è quello indicato per il mese." if prezzo and "-" in prezzo else "Turni per capacità.",
            ))
    return turni
