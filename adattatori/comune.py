"""Pezzi in comune agli adattatori: circuiti, scaricamento, pulizia del testo."""
import html
import re
import time
import urllib.parse
import urllib.request

# Circuiti coperti o da coprire. La regione serve alla pagina per raggruppare.
# lat/lon: dove porta "Portami al circuito" nell'app KneeDownMap. Un parcheggio o il paddock accanto al
# tracciato, presi da OpenStreetMap il 27/10/2026 (Overpass e Nominatim), non il centro della pista: il
# percorso si aggancia alla strada più vicina. Modena, Cremona e Franciacorta: centro dell'impianto.
# Da controllare con un percorso di prova quando si aggiunge o si sposta un circuito.
CIRCUITI = {
    "misano": {"nome": "Misano World Circuit Marco Simoncelli", "comune": "Misano Adriatico (RN)", "regione": "Emilia-Romagna", "lat": 43.96035, "lon": 12.68369},
    "imola": {"nome": "Autodromo Enzo e Dino Ferrari", "comune": "Imola (BO)", "regione": "Emilia-Romagna", "lat": 44.34392, "lon": 11.71374},
    "varano": {"nome": "Autodromo Riccardo Paletti", "comune": "Varano de' Melegari (PR)", "regione": "Emilia-Romagna", "lat": 44.68603, "lon": 10.01581},
    "modena": {"nome": "Autodromo di Modena", "comune": "Marzaglia (MO)", "regione": "Emilia-Romagna", "lat": 44.63374, "lon": 10.81405},
    "mugello": {"nome": "Mugello Circuit", "comune": "Scarperia e San Piero (FI)", "regione": "Toscana", "lat": 43.99717, "lon": 11.37221},
    "vallelunga": {"nome": "Autodromo di Vallelunga Piero Taruffi", "comune": "Campagnano di Roma (RM)", "regione": "Lazio", "lat": 42.15659, "lon": 12.37004},
    "monza": {"nome": "Autodromo Nazionale Monza", "comune": "Monza (MB)", "regione": "Lombardia", "lat": 45.61729, "lon": 9.28213},
    "tazio": {"nome": "Circuito Tazio Nuvolari", "comune": "Cervesina (PV)", "regione": "Lombardia", "lat": 45.07314, "lon": 8.99197},
    "cremona": {"nome": "Cremona Circuit", "comune": "San Martino del Lago (CR)", "regione": "Lombardia", "lat": 45.08544, "lon": 10.31046},
    "franciacorta": {"nome": "Autodromo di Franciacorta", "comune": "Castrezzato (BS)", "regione": "Lombardia", "lat": 45.51267, "lon": 10.0055},
    "adria": {"nome": "Adria International Raceway", "comune": "Adria (RO)", "regione": "Veneto", "lat": 45.04385, "lon": 12.14952},
    "magione": {"nome": "Autodromo dell'Umbria", "comune": "Magione (PG)", "regione": "Umbria", "lat": 43.1308, "lon": 12.23846},
}

# Parole nel nome del circuito, per le fonti che lo scrivono a modo loro.
_CHIAVI_CIRCUITO = [
    ("misano", "misano"), ("mugello", "mugello"), ("imola", "imola"), ("vallelunga", "vallelunga"),
    ("monza", "monza"), ("nuvolari", "tazio"), ("cervesina", "tazio"), ("cremona", "cremona"),
    ("varano", "varano"), ("adria", "adria"), ("franciacorta", "franciacorta"), ("magione", "magione"),
    ("modena", "modena"),
]

UA = "Mozilla/5.0 (compatible; TurniPista/0.1; calendario pubblico dei turni moto)"
PAUSA = 1.0  # secondi fra due richieste allo stesso sito: non diamo fastidio a nessuno


def circuito_da_nome(testo):
    t = (testo or "").lower()
    for chiave, cid in _CHIAVI_CIRCUITO:
        if chiave in t:
            return cid
    return None


def scarica(url, dati=None, timeout=30):
    """GET, o POST se ci sono dati (dict). Torna il testo della risposta."""
    corpo = None
    if dati is not None:
        corpo = urllib.parse.urlencode(dati).encode()
    req = urllib.request.Request(url, data=corpo, headers={"User-Agent": UA, "Accept-Language": "it-IT,it;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        grezzo = r.read()
        charset = r.headers.get_content_charset() or "utf-8"
    time.sleep(PAUSA)
    return grezzo.decode(charset, errors="replace")


def testo(frammento):
    """Da HTML a testo su una riga."""
    t = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", frammento or "")
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ").replace("�", " ")
    return re.sub(r"[ \t\r\f\v]+", " ", t).strip()


def pulisci_sito(url):
    if not url:
        return None
    u = url.strip().rstrip("/")
    if not u:
        return None
    if not re.match(r"(?i)https?://", u):
        u = "https://" + u
    return re.sub(r"(?i)^(https?://)", lambda m: m.group(1).lower(), u).replace("://WWW.", "://www.")


def tipo_da_testo(t):
    t = (t or "").lower()
    if "open pit" in t:
        return "open pit lane"
    if "turni" in t or "gruppi" in t:
        return "a turni"
    return None



def solo_fisso(numero):
    """Tiene solo i numeri fissi italiani (dopo +39 o 0039 iniziano con 0). Cellulari e numeri esteri
    degli organizzatori non si pubblicano: spesso sono personali. Scelta di Michael, 2026-10-21."""
    if not numero:
        return None
    cifre = re.sub(r"[^\d+]", "", numero)
    cifre = re.sub(r"^(\+39|0039)", "", cifre)
    estero = cifre.startswith(("+", "00"))  # prefisso di un altro paese
    return numero.strip() if cifre.startswith("0") and not estero else None


def turno(circuito, data_inizio, organizzatore, *, data_fine=None, tipo=None, orario=None, prezzo=None,
          telefono=None, email=None, sito=None, prenota=None, pagina=None, veicolo="moto", note=None):
    """Un turno come lo scrive ogni adattatore. Quello che la fonte non dice resta None."""
    return {
        "circuito": circuito,
        "data_inizio": data_inizio,
        "data_fine": data_fine or data_inizio,
        "organizzatore": (organizzatore or "").strip() or None,
        "veicolo": veicolo,
        "tipo": tipo,
        "orario": orario,
        "prezzo": prezzo,
        "contatti": {"telefono": solo_fisso(telefono), "email": email, "sito": pulisci_sito(sito)},
        "prenota": prenota,
        "pagina": pagina,
        "note": note,
    }
