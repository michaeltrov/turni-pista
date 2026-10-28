"""Un modulo per fonte. Ognuno ha FONTE (chi è, dove, cosa dicono le condizioni d'uso) e
raccogli(get, oggi), dove get(url, dati=None) scarica una pagina: così i test passano pagine salvate."""
from . import misano, mugello, portamiinpista, promoracing, rossocorsa, tazio, vallelunga, varano

TUTTI = [misano, vallelunga, varano, mugello, tazio, promoracing, portamiinpista, rossocorsa]

# Fonti viste e non raccolte, col motivo. Finiscono nel JSON e nella pagina, così si sa cosa manca.
SALTATE = [
    {"id": "imola", "nome": "Autodromo di Imola", "url": "https://www.autodromoimola.it/termini-e-condizioni-di-utilizzo/",
     "motivo": "Le condizioni d'uso vietano di copiare, ripubblicare o \"caricare da programma\" i contenuti senza consenso. Serve il permesso scritto."},
    {"id": "cremona", "nome": "Cremona Circuit", "url": "https://cremonacircuit.it/booking/",
     "motivo": "Le date moto stanno nel sistema di prenotazione, che risponde solo con un codice di sessione della pagina. Il calendario pubblico mostra auto e kart, ed è fermo a dicembre 2026. Da rifare."},
    {"id": "magione", "nome": "Autodromo di Magione", "url": "https://www.autodromomagione.com/calendario/",
     "motivo": "Il calendario del sito non ha eventi futuri (letto il 2026-10-21). Le prove libere si vendono nel negozio del sito: da guardare quando escono le date 2027."},
    {"id": "monza", "nome": "Autodromo di Monza", "url": "https://www.monzanet.it/",
     "motivo": "Nel calendario (58 eventi fino a dicembre 2026) nessuna giornata moto aperta al pubblico."},
    {"id": "adria", "nome": "Adria International Raceway", "url": "https://www.adriaraceway.com/",
     "motivo": "Il sito risponde 403 (accesso negato) allo script."},
    {"id": "franciacorta", "nome": "Autodromo di Franciacorta", "url": "https://www.autodromodifranciacorta.it/",
     "motivo": "Il dominio trovato porta al kartodromo. Il sito del circuito moto va ancora trovato."},
    {"id": "gully", "nome": "Gully Racing (organizzatore)", "url": "https://www.gullyracing.it/",
     "motivo": "Oggi vende solo date in Spagna. Le sue date a Misano arrivano dal calendario del circuito."},
    {"id": "proveliberemoto", "nome": "proveliberemoto.it / MES Experience (organizzatore)", "url": "https://www.proveliberemoto.it/it/28-calendario",
     "motivo": "Il 21/10/2026 nessuna giornata in vendita nei mesi del calendario, e le date sono scritte senza anno. Da riguardare quando esce la stagione 2027."},
    {"id": "gasss", "nome": "Gasss (organizzatore)", "url": "https://www.gasss.eu/impressum",
     "motivo": "La pagina legale vieta di riusare testi e informazioni del sito senza consenso. Le sue date a Misano e al Mugello arrivano dai circuiti, ma senza il prezzo (645-695 € sul suo sito)."},
    {"id": "eleven", "nome": "Eleven Riding Life / Team Mora Moto (organizzatore)", "url": "https://www.elevenridinglife.com/track-days/",
     "motivo": "Il 21/10/2026 nessuna giornata in vendita (solo simulatore e servizi). Ha un catalogo leggibile: si aggiunge quando escono le date 2027."},
    {"id": "emg", "nome": "EMG Eventi / MotoXRacing (organizzatore)", "url": "https://emgeventi.it/events/",
     "motivo": "La pagina degli eventi non elenca date il 21/10/2026."},
    {"id": "primainpista", "nome": "PrimainPista (organizzatore)", "url": "https://www.primainpista.it/",
     "motivo": "Il calendario del sito è vuoto. Le sue giornate al Tazio Nuvolari arrivano dal negozio del circuito."},
]
