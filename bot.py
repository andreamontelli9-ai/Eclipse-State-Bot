import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import os
import json
import signal
import random
import io
from datetime import datetime, timezone
from typing import List
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# --- 🔑 TOKEN DISCORD E ID DEVELOPER ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.environ.get("DISCORD_TOKEN")

# 🔴 INSERISCI QUI IL TUO ID DISCORD REALE PER USARE I COMANDI WIPE 🔴
DEVELOPER_ID = 1275101244423405621

# ═══════════════════════════════════════════
# 💼 ID DIRETTORI PER LOCALE
# ═══════════════════════════════════════════
DIRETTORI_LOCALI = {
    "concessionario":   1495785188582494208,
    "ammunition":       1495785200012234783,
    "officina":         1495785195016818728,
    "supermarket":      1495785224372621502,
    "dynasty8":         1495785229795725342,
    "casino":           1497123003396259851,
    "airlines":         1495785234455592960,
    "isladeoro":        1520768764403253399,
    "foodless":         1495785221117837373,
    "vanilla":          1495785212796211363,
    "banca":            1494294109031239742,
    "ospedale":         1496597245909536863,
    "industriabellica": 1495785209424117940,
    "industriaalcolica": 1502348586359455864,
    "armeria":           1495785200012234783,  # 🔫 Direttore Armeria
}

# Configurazione dei permessi di Discord (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 🖼️ GRAFICHE E LOGHI ---
LOGO_SERVER = "https://i.postimg.cc/hzfPFQCK/IMG-0236.webp"

# --- 🗂️ STRUTTURA LAVORI E GRADI ---
LAVORI_DUE_GRADI = [
    "ltd", "concessionario", "meccanico", "pegasus", "armament-ind",
    "vanilla", "armeria", "wezel-news", "import-exsport", "downtown-cab-co",
    "ammunutation", "alcol-industries", "food-4less", "limited-gasoline",
    "msfd",
]

# Mappa lavoro -> nome del ruolo capo (per permessi assumi/promuovi)
CAPO_PER_LAVORO = {
    "concessionario": "direttore concessionario",
    "officina": "direttore officina",
    "supermarket": "direttore supermarket",
    "dynasty8": "direttore dynasty8",
    "casino": "direttore casino",
    "airlines": "direttore airlines",
    "banca": "direttore banca",
    "ospedale": "direttore ospedale",
    "fbi": "direttore federale dell'agenzia",
    "mspd": "primo dirigente della polizia",
    "msfd": "direttore msfd",
    "avvocato": "avvocato capo",
    "giudice": "giudice supremo",
}



STIPENDI_DUE_GRADI = {
    "dipendente": 2000,
    "direttore": 0,
}

GRADI_PER_LAVORO = {
    "fbi": [
        ("recluta d'agenzia", 3000),
        ("agente federale operativo", 4000),
        ("agente servizi segreti", 5000),
        ("infiltrato dell'intelligenze", 6500),
        ("operatore squadra d'assalto federale", 7500),
        ("agente supervisore speciale", 8000),
        ("direttore federale dell'agenzia", 10000),
    ],
    "scientifica": [
        ("recluta investigativa", 2000),
        ("tecnico di laboratorio", 3000),
        ("operativo della scientifica", 4000),
        ("analista informatico e digitale", 5000),
        ("medico esaminatore", 5500),
        ("capo reparto scientifica", 7000),
    ],
    "servizi-segreti": [
        ("detective trainee", 2500),
        ("detective junior", 3500),
        ("detective senior", 5000),
        ("agente sotto copertura", 6000),
        ("ispettore", 6500),
        ("vice capo sez. investigativa", 7500),
        ("capo della sezione investigativa", 9000),
    ],
    "navyseal": [
        ("recluta", 1000),          
        ("operatore", 5000),        
        ("sottufficiale", 10000),   
        ("ufficiale", 15000),       
        ("generale", 20000),
    ],
    "avvocato": [
        ("praticante avvocato", 2500),
        ("avvocato junior", 3000),
        ("avvocato", 4500),
        ("avvocato senior", 5500),
        ("avvocato capo", 7000),
    ],
    "giudice": [
        ("giudice tirocinante", 3000),
        ("giudice", 4500),
        ("giudice senior", 6000),
        ("giudice d'appello", 7500),
        ("giudice supremo", 9000),
    ],
    "mspd": [
        ("agente/allievo", 3500),
        ("agente scelto", 3750),
        ("assistente", 4000),
        ("assistente capo", 4250),
        ("vice sovrintendente", 4500),
        ("sovrintendente", 5000),
        ("sovrintendente capo", 5500),
        ("ispettore capo help", 6000),
        ("ispettore capo stradale", 6000),
        ("ispettore superiore metro", 6500),
        ("vice commissario", 7000),
        ("commissario", 7500),
        ("vice questore aggiunto", 8000),
        ("vice questore", 8500),
        ("primo dirigente della polizia", 9000),
    ],
}

STIPENDI_LAVORO = {
    "ems": 2000,
    "meccanico": 1500,
    "cittadino": 1000,
    "recluta": 1500,
    "avvocato": 4500,
    "praticante avvocato": 2500,
    "avvocato junior": 3000,
    "avvocato senior": 5500,
    "avvocato capo": 7000,
    "giudice tirocinante": 3000,
    "giudice": 4500,
    "giudice senior": 6000,
    "giudice d'appello": 7500,
    "giudice supremo": 9000,
    "primo dirigente della polizia": 9000,
    "vice questore aggiunto": 8000,
    "vice questore": 8500,
    "vice commissario": 7000,
    "commissario": 7500,
    "ispettore superiore metro": 6500,
    "ispettore capo help": 6000,
    "ispettore capo stradale": 6000,
    "sovrintendente capo": 5500,
    "vice sovrintendente": 4500,
    "sovrintendente": 5000,
    "assistente capo": 4250,
    "assistente": 4000,
    "agente scelto": 3750,
    "agente/allievo": 3500,
    "mspd": 4000,
    "msfd": 4000,
}

def ottieni_stipendio_grado(lavoro: str, grado: str) -> int:
    lavoro = lavoro.lower()
    grado = grado.lower()
    if lavoro in LAVORI_DUE_GRADI:
        return STIPENDI_DUE_GRADI.get(grado, 1000)
    if lavoro in GRADI_PER_LAVORO:
        for nome_grado, stipendio in GRADI_PER_LAVORO[lavoro]:
            if nome_grado == grado:
                return stipendio
    return 1000

VIE_CASE_POPOLARI = [
    "1561 San Vitas St",
    "1115 Blvd Del Perro",
    "2057 Vespucci Blvd",
    "0112 S Rockford Dr",
]

TIPI_PATENTE = {
    "A": "🏍️ Patente A — Moto",
    "B": "🚗 Patente B — Auto",
    "C": "⛵✈️ Patente C — Barche e Aerei",
}

TIPI_PORTO_ARMI = {
    "1": "🔫 Porto d'armi — Tipo 1",
    "2": "🔫 Porto d'armi — Tipo 2",
    "3": "🔫 Porto d'armi — Tipo 3",
}

# Inizializzazione Database in memoria
conti_bancari = {}
storico_transazioni = {}  # {uid: [{"tipo": str, "importo": int, "controparte": str, "ts": str, "segno": "+"/"−"}, ...]}
targhe_veicoli = {}     
documenti_identita = {} 
fascicoli_medici = {}
patenti_cittadini = {}    
prigione = {}           
inventari = {}          
registro_armi = {}        
ricercati = set()
whitelist_db = {}
proprieta_immobili = {}
case_popolari = {} 
turni_attivi = {} 
backgrounds_in_attesa = {}
schedario_warn = {}
zaini = {}
portafogli = {} 
inventari_cofani = {} 
contatti_telefono = {}
messaggi_telefono = {}
ultimi_mittenti_pm = {}
licenze_cittadini = {}
patenti = patenti_cittadini
porto_darmi = licenze_cittadini
statistiche_personaggio = {}
garage_veicoli = {} 
voti_sondaggi = {}
oggetti_creati = {
    "🌿 Marijuana": {
        "nome": "🌿 Marijuana",
        "quantita": 999,
        "prezzo": 40,
        "vendibile": False,
        "descrizione": "Marijuana coltivata nelle farm illegali. Si ottiene tramite la farm della marijuana.",
        "categoria": "Droga",
        "ruolo_richiesto": None
    },
    "💮 Cocaina": {
        "nome": "💮 Cocaina",
        "quantita": 999,
        "prezzo": 80,
        "vendibile": False,
        "descrizione": "Cocaina raffinata. Si ottiene tramite la farm della cocaina.",
        "categoria": "Droga",
        "ruolo_richiesto": None
    },
    "❄️ Blue Crystal": {
        "nome": "❄️ Blue Crystal",
        "quantita": 999,
        "prezzo": 120,
        "vendibile": False,
        "descrizione": "Metanfetamina di alta purezza. Si ottiene tramite il laboratorio del chimico.",
        "categoria": "Droga",
        "ruolo_richiesto": None
    },

    # ══════════════════════════════════════
    # ⚔️  ARMI DA MISCHIA
    # ══════════════════════════════════════
    "🔪 Coltello": {
        "nome": "🔪 Coltello",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Un coltello da combattimento. Silenzioso e letale a corto raggio.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "🪵 Manganello": {
        "nome": "🪵 Manganello",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Un manganello robusto, ideale per stordire senza far troppo rumore.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "⚾ Mazza da Baseball": {
        "nome": "⚾ Mazza da Baseball",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Una classica mazza da baseball. Ottima per chi preferisce fare a meno delle armi da fuoco.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "🔨 Martello": {
        "nome": "🔨 Martello",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Un pesante martello da costruzione, devastante a corto raggio.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "🛠️ Piede di Porco": {
        "nome": "🛠️ Piede di Porco",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Utile per forzare porte e come arma improvvisata in situazioni di emergenza.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "⛳ Golf Club": {
        "nome": "⛳ Golf Club",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Un ferro da golf riadattato a scopi meno sportivi.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "🗡️ Coltello a Serramanico": {
        "nome": "🗡️ Coltello a Serramanico",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Compatto e facile da nascondere. Lama affilata che si apre con un clic.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },
    "🍾 Bottiglia Rotta": {
        "nome": "🍾 Bottiglia Rotta",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Una bottiglia di vetro rotta, arma improvvisata pericolosa a corto raggio.",
        "categoria": "Armi da Mischia",
        "ruolo_richiesto": None
    },

    # ══════════════════════════════════════
    # 🔫  PISTOLE
    # ══════════════════════════════════════
    "🔫 Pistola Standard": {
        "nome": "🔫 Pistola Standard",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Pistola semi-automatica di uso comune. Affidabile e precisa a corto-medio raggio.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "🔫 Pistola da Combattimento": {
        "nome": "🔫 Pistola da Combattimento",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Versione potenziata della pistola standard, con maggiore cadenza di fuoco.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "💥 Pistola Pesante": {
        "nome": "💥 Pistola Pesante",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Pistola di grosso calibro. Ogni colpo è devastante ma il rinculo è elevato.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "🛡️ Pistola Perforante (AP Pistol)": {
        "nome": "🛡️ Pistola Perforante (AP Pistol)",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Pistola con proiettili perforanti capaci di bucare i blindati. Arma militare.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "🎯 Pistola Calibro .50": {
        "nome": "🎯 Pistola Calibro .50",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Pistola da cecchino tascabile. Calibro 50, un solo colpo può essere fatale.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "🏛️ Pistola Vintage": {
        "nome": "🏛️ Pistola Vintage",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Pistola d'epoca dal design classico. Meno potente ma ricercata dai collezionisti.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "⚡ Pistola Mitragliatrice (SNS Pistol)": {
        "nome": "⚡ Pistola Mitragliatrice (SNS Pistol)",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Piccola e compatta, spara in semi-automatico con alta cadenza di fuoco.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },
    "🎯 Marksman Pistol": {
        "nome": "🎯 Marksman Pistol",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Pistola di precisione per tiratori esperti. Alta accuratezza a medio raggio.",
        "categoria": "Pistole",
        "ruolo_richiesto": None
    },

    # ══════════════════════════════════════
    # 🔥  MITRA (SMG)
    # ══════════════════════════════════════
    "🔥 Micro SMG": {
        "nome": "🔥 Micro SMG",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Mitra tascabile con alta cadenza di fuoco. Ideale in spazi ristretti.",
        "categoria": "Mitra",
        "ruolo_richiesto": None
    },
    "💨 SMG (Mitragliatrice Standard)": {
        "nome": "💨 SMG (Mitragliatrice Standard)",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Mitra bilanciata con buona precisione e cadenza di fuoco elevata.",
        "categoria": "Mitra",
        "ruolo_richiesto": None
    },
    "⚡ Assault SMG": {
        "nome": "⚡ Assault SMG",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Versione d'assalto del mitra standard, con caricatore esteso e maggiore potenza.",
        "categoria": "Mitra",
        "ruolo_richiesto": None
    },
    "🛡️ Combat PDW": {
        "nome": "🛡️ Combat PDW",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Arma da difesa personale compatta, utilizzata da unità speciali. Caricatore da 50 colpi.",
        "categoria": "Mitra",
        "ruolo_richiesto": None
    },

    # ══════════════════════════════════════
    # 🪖  FUCILI D'ASSALTO
    # ══════════════════════════════════════
    "🪖 Carabina Standard": {
        "nome": "🪖 Carabina Standard",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Carabina semi-automatica leggera, precisa a medio raggio.",
        "categoria": "Fucili d'Assalto",
        "ruolo_richiesto": None
    },
    "⚔️ Fucile d'Assalto": {
        "nome": "⚔️ Fucile d'Assalto",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Fucile d'assalto militare, preciso e potente. L'arma preferita dalle gang organizzate.",
        "categoria": "Fucili d'Assalto",
        "ruolo_richiesto": None
    },
    "🔩 Fucile Avanzato": {
        "nome": "🔩 Fucile Avanzato",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Versione moderna e potenziata del fucile d'assalto, con accessori tattici integrati.",
        "categoria": "Fucili d'Assalto",
        "ruolo_richiesto": None
    },
    "🌟 Fucile Speciale": {
        "nome": "🌟 Fucile Speciale",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Fucile d'assalto di ultima generazione, usato da reparti speciali.",
        "categoria": "Fucili d'Assalto",
        "ruolo_richiesto": None
    },
    "💠 Bullpup Rifle": {
        "nome": "💠 Bullpup Rifle",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Design bullpup compatto con caricatore posteriore. Alta precisione e maneggevolezza.",
        "categoria": "Fucili d'Assalto",
        "ruolo_richiesto": None
    },
    "🔫 Compact Rifle": {
        "nome": "🔫 Compact Rifle",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Fucile d'assalto compatto, ideale per scontri a medio raggio in spazi urbani.",
        "categoria": "Fucili d'Assalto",
        "ruolo_richiesto": None
    },

    # ══════════════════════════════════════
    # 💣  FUCILI A POMPA
    # ══════════════════════════════════════
    "💣 Fucile a Pompa (Pump Shotgun)": {
        "nome": "💣 Fucile a Pompa (Pump Shotgun)",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Classico fucile a pompa. Devastante a corto raggio, letale in ambienti chiusi.",
        "categoria": "Fucili a Pompa",
        "ruolo_richiesto": None
    },
    "🔴 Fucile a Pompa d'Assalto (Assault Shotgun)": {
        "nome": "🔴 Fucile a Pompa d'Assalto (Assault Shotgun)",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Versione semi-automatica del fucile a pompa. Caricatore a tamburo da 12 colpi.",
        "categoria": "Fucili a Pompa",
        "ruolo_richiesto": None
    },
    "🔵 Bullpup Shotgun": {
        "nome": "🔵 Bullpup Shotgun",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Shotgun compatto a design bullpup. Bilanciato e preciso per un'arma da mischia.",
        "categoria": "Fucili a Pompa",
        "ruolo_richiesto": None
    },
    "🏴‍☠️ Musket": {
        "nome": "🏴‍☠️ Musket",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Arma d'epoca a carica singola. Un colpo solo, ma devastante. Per veri intenditori.",
        "categoria": "Fucili a Pompa",
        "ruolo_richiesto": None
    },
    "🌀 Sweeper Shotgun": {
        "nome": "🌀 Sweeper Shotgun",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Shotgun a tamburo rotante. Scarica proiettili rapidamente su bersagli multipli.",
        "categoria": "Fucili a Pompa",
        "ruolo_richiesto": None
    },
    "🎭 Double Barrel Shotgun": {
        "nome": "🎭 Double Barrel Shotgun",
        "quantita": 999,
        "prezzo": 0,
        "vendibile": False,
        "descrizione": "Doppia canna, doppia devastazione. Due colpi che non perdonano a corto raggio.",
        "categoria": "Fucili a Pompa",
        "ruolo_richiesto": None
    },
    # ══════════════════════════════════════
    # 🛍️  ITEM SUPERMARKET
    # ══════════════════════════════════════
    "🎒 Zaino": {
        "nome": "🎒 Zaino",
        "quantita": 999,
        "prezzo": 500,
        "vendibile": True,
        "descrizione": "Uno zaino capiente per trasportare oggetti extra. Aumenta la capacità di carico.",
        "categoria": "Item",
        "ruolo_richiesto": None
    },
    "🔗 Fascette da Elettricista": {
        "nome": "🔗 Fascette da Elettricista",
        "quantita": 999,
        "prezzo": 150,
        "vendibile": True,
        "descrizione": "Utili per immobilizzare temporaneamente qualcuno durante un'azione.",
        "categoria": "Item",
        "ruolo_richiesto": None
    },
    "🎭 Maschera": {
        "nome": "🎭 Maschera",
        "quantita": 999,
        "prezzo": 350,
        "vendibile": True,
        "descrizione": "Nascondi la tua identità durante le operazioni o i colpi in città.",
        "categoria": "Item",
        "ruolo_richiesto": None
    },
    "🧳 Borsone": {
        "nome": "🧳 Borsone",
        "quantita": 999,
        "prezzo": 800,
        "vendibile": True,
        "descrizione": "Un grande borsone per trasportare molti oggetti. Più capiente dello zaino, ideale per i colpi.",
        "categoria": "Item",
        "ruolo_richiesto": None
    },
}
bisogni_personaggio = {}   # {uid: {"fame": 100, "sete": 100}}

# Copia di backup degli item hardcoded (usata per il merge dopo _carica_dati)
from copy import deepcopy as _deepcopy
oggetti_creati_default = _deepcopy(oggetti_creati)

# Stock armeria persistente
stock_armeria: dict = {}
CATEGORIE_ARMI = ["Armi da Mischia", "Pistole", "Mitra", "Fucili d'Assalto", "Fucili a Pompa"]

personaggi_addormentati = set()  # {uid} — personaggi che stanno dormendo

DATA_FILE = os.environ.get("DATA_FILE", "/app/data/data.json")

_DIZIONARI_CHIAVE_INT = [
    "conti_bancari", "documenti_identita", "patenti_cittadini", "prigione", "inventari",
    "registro_armi", "whitelist_db", "backgrounds_in_attesa", "schedario_warn", "zaini",
    "portafogli", "contatti_telefono", "messaggi_telefono", "ultimi_mittenti_pm",
    "licenze_cittadini", "statistiche_personaggio", "garage_veicoli", "fascicoli_medici",
    "bisogni_personaggio", "storico_transazioni"
]
_DIZIONARI_CHIAVE_STR = [
    "targhe_veicoli", "proprieta_immobili", "case_popolari", "inventari_cofani", "voti_sondaggi", "oggetti_creati", "stock_armeria", "armadietto_fdo", "oggetti_nascosti"
]

def _salva_dati():
    stato = {nome: globals()[nome] for nome in _DIZIONARI_CHIAVE_INT}
    stato.update({nome: globals()[nome] for nome in _DIZIONARI_CHIAVE_STR})
    stato["ricercati"] = list(ricercati)
    stato["turni_attivi"] = {str(k): v.isoformat() for k, v in turni_attivi.items()}

    tmp_path = DATA_FILE + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(stato, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, DATA_FILE)
    except OSError as e:
        print(f"⚠️ Errore durante il salvataggio dei dati: {e}")

def _carica_dati():
    if not os.path.exists(DATA_FILE):
        print(f"💾 Nessun file dati trovato ({DATA_FILE}), parto con database vuoti.")
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            stato = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️ Impossibile leggere {DATA_FILE}, parto con dati vuoti: {e}")
        return

    for nome in _DIZIONARI_CHIAVE_INT:
        if nome not in globals():
            continue
        dizionario = globals()[nome]
        dizionario.clear()
        for k, v in stato.get(nome, {}).items():
            dizionario[int(k)] = v

    for nome in _DIZIONARI_CHIAVE_STR:
        if nome not in globals():
            continue
        dizionario = globals()[nome]
        dizionario.clear()
        dizionario.update(stato.get(nome, {}))

    ricercati.clear()
    ricercati.update(stato.get("ricercati", []))

    turni_attivi.clear()
    for k, v in stato.get("turni_attivi", {}).items():
        turni_attivi[int(k)] = datetime.fromisoformat(v)

    # Assicura che le armi hardcoded siano sempre presenti in oggetti_creati
    from copy import deepcopy
    _ARMI_HARDCODED_CATS = ["Armi da Mischia", "Pistole", "Mitra", "Fucili d'Assalto", "Fucili a Pompa"]
    for _nome, _dati in list(oggetti_creati_default.items()):
        if _dati.get("categoria") in _ARMI_HARDCODED_CATS:
            if _nome not in oggetti_creati:
                oggetti_creati[_nome] = deepcopy(_dati)

    print(f"💾 Dati ricaricati con successo da {DATA_FILE}")

_carica_dati()

def _popola_oggetti_supermarket():
    """Aggiunge al database oggetti_creati tutti gli item del supermarket se non esistono già."""
    # ── CIBO ──
    for p in SUPERMARKET_CIBO:
        nome = p["nome"]
        if nome not in oggetti_creati:
            oggetti_creati[nome] = {
                "nome": nome,
                "quantita": 999,
                "prezzo": p["prezzo"],
                "vendibile": True,
                "descrizione": f"+{p['recupero']} fame | Acquistabile al Supermarket.",
                "categoria": "Cibo",
                "ruolo_richiesto": None,
            }
    # ── BEVANDE ──
    for p in SUPERMARKET_BEVANDE:
        nome = p["nome"]
        if nome not in oggetti_creati:
            oggetti_creati[nome] = {
                "nome": nome,
                "quantita": 999,
                "prezzo": p["prezzo"],
                "vendibile": True,
                "descrizione": f"+{p['recupero']} sete | Acquistabile al Supermarket.",
                "categoria": "Cibo",
                "ruolo_richiesto": None,
            }
    # ── ITEM SPECIALI ──
    CAT_MAP = {
        "🕵️ Investigazione":   "Generale",
        "💰 Finanze Oscure":   "Generale",
        "🩸 Interrogatori":    "Generale",
        "Armi da Mischia":     "Armi da Mischia",
        "Pistole":             "Pistole",
        "Mitra":               "Mitra",
        "Fucili d'Assalto":    "Fucili d'Assalto",
        "Fucili a Pompa":      "Fucili a Pompa",
        "Cibo":                "Cibo",
        "Droga":               "Droga",
        "Medicina":            "Medicina",
    }
    for p in SUPERMARKET_ITEM:
        nome = p["nome"]
        if nome not in oggetti_creati:
            cat = CAT_MAP.get(p.get("categoria", "Generale"), "Generale")
            oggetti_creati[nome] = {
                "nome": nome,
                "quantita": 999,
                "prezzo": p["prezzo"],
                "vendibile": True,
                "descrizione": p.get("descrizione", "Item speciale del Supermarket."),
                "categoria": cat,
                "ruolo_richiesto": None,
            }
    # ── DROGHE (già presenti ma assicuriamoci) ──
    droghe = [
        {"nome": "🌿 Marijuana",    "prezzo": 40,  "desc": "Marijuana coltivata nelle farm illegali."},
        {"nome": "💮 Cocaina",      "prezzo": 80,  "desc": "Cocaina raffinata dalle farm."},
        {"nome": "❄️ Blue Crystal", "prezzo": 120, "desc": "Metanfetamina di alta purezza."},
    ]
    for d in droghe:
        if d["nome"] not in oggetti_creati:
            oggetti_creati[d["nome"]] = {
                "nome": d["nome"],
                "quantita": 999,
                "prezzo": d["prezzo"],
                "vendibile": False,
                "descrizione": d["desc"],
                "categoria": "Droga",
                "ruolo_richiesto": None,
            }

# Chiama subito dopo il caricamento dati
# _popola_oggetti_supermarket() — chiamata dopo la definizione delle liste, in fondo al file

@tasks.loop(seconds=20)
async def autosave_task():
    _salva_dati()


@tasks.loop(minutes=10)
async def decremento_bisogni_task():
    """Ogni 10 minuti scende fame e sete per tutti i giocatori registrati (esclusi chi dorme)."""
    for uid in list(bisogni_personaggio.keys()):
        if uid in personaggi_addormentati:
            continue  # Chi dorme non consuma fame/sete
        b = bisogni_personaggio[uid]
        b["fame"] = max(0, b["fame"] - DECREMENTO_FAME)
        b["sete"] = max(0, b["sete"] - DECREMENTO_SETE)
    _salva_dati()

def _salva_ed_esci(signum, frame):
    print(f"🛑 Segnale di arresto ricevuto ({signum}), salvo i dati prima di chiudere...")
    _salva_dati()
    exit(0)

signal.signal(signal.SIGTERM, _salva_ed_esci)
signal.signal(signal.SIGINT, _salva_ed_esci)

# --- 👮 CONTROLLI PERMESSI ---

import re as _re

def _pulisci_ruolo(nome: str) -> str:
    nome = nome.encode('ascii', 'ignore').decode('ascii')
    nome = _re.sub(r'[^a-z0-9 ]', '', nome.lower())
    return ' '.join(nome.split())

def _ha_ruolo(member, parole_chiave: list) -> bool:
    nomi_puliti = [_pulisci_ruolo(r.name) for r in member.roles]
    for nome in nomi_puliti:
        for kw in parole_chiave:
            if kw in nome:
                return True
    return False

_KW_STAFF = [
    "official staff", "try staff", "higher staff", "helper",
    "staff manager", "server manager", "whitelister manager",
    "eclipse city rp staff", "developer",
    "owner of eclipse", "deputy owner", "co owner",
    "addetto colloqui", "addetto forum", "addetto bandi",
    "addetto item", "addetto stipendi", "addetto droghe",
    "addetto partnership", "addetto antigrief", "addetto sanzioni",
    "gestore fdo", "gestore mspd", "gestore msfd",
    "gestore ems", "gestore criminalit",
    "events manager", "responsabile roleplay",
    "pg amministrativo",
]

_KW_POLIZIA = [
    "capo della polizia", "vice capo della polizia",
    "vicecomandante", "capitano", "tenente",
    "sergente maggiore", "sergente",
    "direttore mspd", "capo battaglione", "comandante in capo",
]

_KW_CONCESSIONARIO = [
    "direttore concessonario", "dipendente concessiona",
    "direttore officina", "dipendente officina",
]

def is_dev_or_owner():
    async def predicate(interaction: discord.Interaction):
        is_owner = interaction.guild is not None and interaction.user.id == interaction.guild.owner_id
        is_dev = interaction.user.id == DEVELOPER_ID
        if is_owner or is_dev:
            return True
        await interaction.response.send_message("❌ **Accesso Super-Admin negato:** Comando riservato esclusivamente al Developer e al Founder del server.", ephemeral=True)
        return False
    return app_commands.check(predicate)

# ID ruolo polizia specifico (ha accesso a tutti i comandi polizia)
RUOLO_POLIZIA_ID = 1494294119663796347

def _ha_ruolo_id(member: discord.Member, role_id: int) -> bool:
    """Controlla se un membro ha un ruolo tramite ID."""
    return any(r.id == role_id for r in member.roles)

async def _get_member(interaction: discord.Interaction):
    """Ritorna il membro aggiornato con i ruoli, facendo fetch se necessario."""
    if interaction.guild is None:
        return interaction.user
    membro = interaction.guild.get_member(interaction.user.id)
    if membro is None or not membro.roles:
        try:
            membro = await interaction.guild.fetch_member(interaction.user.id)
        except Exception:
            membro = interaction.user
    return membro

def has_police_permission():
    async def predicate(interaction: discord.Interaction):
        membro = await _get_member(interaction)
        if membro.guild_permissions.administrator or membro.guild_permissions.manage_messages:
            return True
        if _ha_ruolo_id(membro, RUOLO_POLIZIA_ID):
            return True
        if _ha_ruolo(membro, _KW_STAFF + _KW_POLIZIA):
            return True
        await interaction.response.send_message("❌ **Accesso negato:** Comando riservato alle Forze dell'Ordine.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def is_police_or_staff():
    async def predicate(interaction: discord.Interaction):
        membro = await _get_member(interaction)
        if membro.guild_permissions.administrator or membro.guild_permissions.manage_messages:
            return True
        if _ha_ruolo_id(membro, RUOLO_POLIZIA_ID):
            return True
        if _ha_ruolo(membro, _KW_STAFF + _KW_POLIZIA):
            return True
        await interaction.response.send_message("❌ **Accesso negato:** Comando riservato a Polizia o Staff.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def is_staff_or_direttore():
    async def predicate(interaction: discord.Interaction):
        membro = await _get_member(interaction)
        if membro.guild_permissions.administrator:
            return True
        if _ha_ruolo(membro, _KW_STAFF + ["direttore mspd", "capo battaglione", "comandante in capo"]):
            return True
        await interaction.response.send_message("❌ **Accesso negato:** Comando riservato allo Staff o al Direttore MSPD.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def is_concessionario_or_staff():
    async def predicate(interaction: discord.Interaction):
        membro = await _get_member(interaction)
        if membro.guild_permissions.administrator:
            return True
        if _ha_ruolo(membro, _KW_STAFF + _KW_CONCESSIONARIO):
            return True
        await interaction.response.send_message("❌ **Accesso negato:** Comando riservato al Concessionario o allo Staff.", ephemeral=True)
        return False
    return app_commands.check(predicate)

def _blocca_se_dorme():
    """Decoratore: impedisce l'uso del comando se il personaggio sta dormendo."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.id in personaggi_addormentati:
            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed.description = (
                "😴 | **PERSONAGGIO ADDORMENTATO**\n\n"
                "➢ Stai dormendo e non puoi usare comandi.\n"
                "➢ Usa `/sveglia` per alzarti."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

async def log_staff(guild: discord.Guild, descrizione: str, colore: discord.Color = discord.Color.from_rgb(255, 107, 53)):
    if guild is None:
        return
    canale = discord.utils.get(guild.text_channels, name="log-staff")
    if canale is None:
        return
    embed = discord.Embed(description=descrizione, color=colore, timestamp=datetime.now())
    try:
        await canale.send(embed=embed)
    except discord.Forbidden:
        pass

async def log_azione(guild: discord.Guild, utente: discord.Member, azione: str, dettagli: str = "", colore: discord.Color = discord.Color.from_rgb(255, 107, 53), canale_origine: discord.TextChannel = None):
    """📋 Log automatico di ogni azione utente nel canale dedicato."""
    if guild is None:
        return
    canale = guild.get_channel(CH_LOG_AZIONI)
    if canale is None:
        return
    embed = discord.Embed(color=colore, timestamp=datetime.now())
    embed.set_author(
        name=f"{utente.display_name} ({utente.id})",
        icon_url=utente.display_avatar.url
    )
    dettagli_str = f"**📝 Dettagli ➢** {dettagli}\n" if dettagli else ""
    canale_str = f"**📍 Canale ➢** {canale_origine.mention}\n" if canale_origine else ""
    embed.description = (
        f"**🎮 Azione ➢** {azione}\n"
        + dettagli_str
        + canale_str
    )
    embed.set_footer(text=f"UserID: {utente.id}")
    try:
        await canale.send(embed=embed)
    except discord.Forbidden:
        pass

# --- 💳 MODALITÀ DI GESTIONE SOLDI ---
class ModalDeposito(discord.ui.Modal, title="Deposita denaro in banca"):
    importo = discord.ui.TextInput(label="Importo in €", placeholder="Es. 5000", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valore = int(self.importo.value)
            if valore <= 0: raise ValueError
            contanti_attuali = portafogli.get(interaction.user.id, 0)
            if contanti_attuali < valore:
                return await interaction.response.send_message("❌ **Contanti insufficienti** nel tuo portafoglio.", ephemeral=True)
            portafogli[interaction.user.id] -= valore
            if interaction.user.id not in conti_bancari: conti_bancari[interaction.user.id] = 0
            conti_bancari[interaction.user.id] += valore
            _registra_transazione(interaction.user.id, "+", valore, "🏠 Deposito contanti", "Portafoglio")
            _salva_dati()
            await interaction.response.send_message(f"📥 Deposito di **{valore}$** effettuato con successo.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Inserisci un numero valido maggiore di zero.", ephemeral=True)

class ModalPreleva(discord.ui.Modal, title="Preleva denaro dalla banca"):
    importo = discord.ui.TextInput(label="Importo in $", placeholder="Es. 2000", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valore = int(self.importo.value)
            if valore <= 0: raise ValueError
            saldo_attuale = conti_bancari.get(interaction.user.id, 0)
            if saldo_attuale < valore:
                return await interaction.response.send_message("❌ **Fondi insufficienti** sul tuo conto.", ephemeral=True)
            conti_bancari[interaction.user.id] -= valore
            if interaction.user.id not in portafogli: portafogli[interaction.user.id] = 0
            portafogli[interaction.user.id] += valore
            _registra_transazione(interaction.user.id, "−", valore, "👜 Prelievo contanti", "Portafoglio")
            _salva_dati()
            await interaction.response.send_message(f"📤 Prelievo di **{valore}$** effettuato con successo.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Inserisci un numero valido maggiore di zero.", ephemeral=True)

class ViewBilancio(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
    @discord.ui.button(label="🏠 | DEPOSITA", style=discord.ButtonStyle.danger, custom_id="btn_deposito")
    async def btn_deposito(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModalDeposito())
    @discord.ui.button(label="👜 | PRELEVA", style=discord.ButtonStyle.green, custom_id="btn_preleva")
    async def btn_preleva(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ModalPreleva())

# ==========================================
# 0. 🏁 SONDAGGI E PANNELLI INTERATTIVI
# ==========================================

class ViewSondaggioPulsanti(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Sessione 15:00", style=discord.ButtonStyle.success, custom_id="btn_1500")
    async def btn_1500(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.genera_risultato_sondaggio(interaction, "15:00")

    @discord.ui.button(label="Sessione 21:00", style=discord.ButtonStyle.primary, custom_id="btn_2100")
    async def btn_2100(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.genera_risultato_sondaggio(interaction, "21:00")

    async def genera_risultato_sondaggio(self, interaction: discord.Interaction, orario: str):
        membro = await _get_member(interaction)
        is_staff = (
            membro.guild_permissions.administrator
            or membro.guild_permissions.manage_messages
            or _ha_ruolo(membro, _KW_STAFF)
        )
        if not is_staff:
            return await interaction.response.send_message("❌ **Accesso negato:** Comando riservato allo Staff.", ephemeral=True)

        await interaction.response.send_message(f"⌛ Genero il sondaggio per le ore {orario}...", ephemeral=True)

        embed = discord.Embed(
            title="📊 | Sondaggio Rp", 
            description=f"🚀 **Orario Sessione RP Selezionato: {orario}**\n\nPronti a iniziare una nuova avventura roleplay.\n➢ *Votate per partecipare alla sessione delle {orario} grazie!*", 
            color=discord.Color.from_rgb(255, 107, 53),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.set_footer(
            text=f"Sondaggio avviato da: {interaction.user.display_name}", 
            icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        )

        message = await interaction.channel.send("@everyone", embed=embed)
        await message.add_reaction("✅") 
        await message.add_reaction("❌") 
        await message.add_reaction("🕒") 

        await interaction.delete_original_response()

# --- Modulo e Tasto per Inviare il Background ---
CH_ESITI_BACKGROUND  = 1532127242048503868  # log background
CH_LOG_TICKET        = 1532127245215207624  # log ticket
CH_LOG_ECONOMIA      = 1532127253469724873  # log spese soldi
CH_LOG_MESSAGGI      = 1532127256271388733  # log messaggi
CH_LOG_ENTRATE       = 1532127259320651927  # log entrate server
CH_LOG_CANALI        = 1532127262139351150  # log crea/elimina canali
CH_LOG_RUOLI         = 1532127264420921417  # log ruoli
CH_LOG_VOCALI        = 1532127267512389743  # log vocali
CH_LOG_AZIONI        = 1532127256271388733  # log azioni generali (messaggi)

class ModalBg1(discord.ui.Modal, title="📋 Background Personaggio"):
    nome = discord.ui.TextInput(
        label="NOME",
        style=discord.TextStyle.short,
        placeholder="Es: Marco  (niente nomi famosi/troll)",
        required=True,
        max_length=30
    )
    cognome = discord.ui.TextInput(
        label="COGNOME",
        style=discord.TextStyle.short,
        placeholder="Es: Rossi",
        required=True,
        max_length=30
    )
    eta_ic = discord.ui.TextInput(
        label="ETÀ IC (del personaggio)",
        style=discord.TextStyle.short,
        placeholder="Es: 28",
        required=True,
        max_length=3
    )
    eta_ooc = discord.ui.TextInput(
        label="ETÀ OOC (la tua età reale)",
        style=discord.TextStyle.short,
        placeholder="Es: 20",
        required=True,
        max_length=3
    )
    storia = discord.ui.TextInput(
        label="STORIA DEL PERSONAGGIO",
        style=discord.TextStyle.paragraph,
        placeholder="Min. 5-10 righe. Carattere, infanzia, famiglia, lavoro, obiettivi, perché a Eclipse City.",
        required=True,
        min_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        # ⚡ Risposta immediata — DEVE essere la prima cosa, entro 3 secondi
        await interaction.response.send_message(
            "✅ Il tuo Background è stato inviato con successo!\n"
            "Lo staff lo valuterà a breve e riceverai l'esito nel canale dedicato. Attendi pazientemente. 🙏",
            ephemeral=True
        )

        # Tutto il resto viene fatto DOPO la risposta, senza limiti di tempo
        try:
            nome_completo = f"{self.nome.value} {self.cognome.value}"
            backgrounds_in_attesa[interaction.user.id] = {
                "utente": interaction.user.display_name,
                "nome": self.nome.value,
                "cognome": self.cognome.value,
                "eta_ic": self.eta_ic.value,
                "eta_ooc": self.eta_ooc.value,
                "storia": self.storia.value,
            }

            guild = interaction.guild
            canale_esiti = guild.get_channel(CH_ESITI_BACKGROUND) if guild else None

            embed_bg = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
            embed_bg.set_thumbnail(url=interaction.user.display_avatar.url)
            embed_bg.description = (
                f"💾 | **NUOVO BACKGROUND INVIATO**\n\n"
                f"**INFO OOC:**\n\n"
                f"```UTENTE```\n"
                f">> {interaction.user.mention}\n\n"
                f"```ETÀ OOC```\n"
                f">> {self.eta_ooc.value}\n\n"
                f"**INFO IC**\n\n"
                f"*NOME* >> *{self.nome.value}*\n"
                f"*COGNOME* >> *{self.cognome.value}*\n"
                f"*ETÀ* >> *{self.eta_ic.value}*\n"
                f"*STORIA* >> *{self.storia.value}*\n\n"
                f"──────────────────────\n\n"
                f"🔔 | Fai /accetta_background o /rifiuta_background nel canale: <#{CH_ESITI_BACKGROUND}>"
            )
            embed_bg.set_footer(text=f"ID utente: {interaction.user.id} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            if canale_esiti:
                await canale_esiti.send(content=interaction.user.mention, embed=embed_bg)
            else:
                print(f"⚠️ Canale esiti background non trovato! ID: {CH_ESITI_BACKGROUND}")

            await log_azione(
                interaction.guild, interaction.user,
                "📋 Background inviato",
                f"PG: {nome_completo} | Età IC: {self.eta_ic.value} | OOC: {self.eta_ooc.value}",
                discord.Color.from_rgb(255, 107, 53)
            )
        except Exception as e:
            print(f"⚠️ Errore invio background: {e}")

# Alias per compatibilità con il bottone esistente
ModalBg = ModalBg1

class ViewPannelloBg(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 INVIA BACKGROUND", style=discord.ButtonStyle.danger, custom_id="btn_bg")
    async def btn_bg(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"[BTN_BG] Click ricevuto da {interaction.user} ({interaction.user.id})", flush=True)
        try:
            await interaction.response.send_modal(ModalBg1())
            print(f"[BTN_BG] Modal inviato con successo", flush=True)
        except Exception as e:
            print(f"[BTN_BG] ERRORE: {e}", flush=True)

# --- PANNELLO TICKET ---
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="TICKET AMMINISTRAZIONE", style=discord.ButtonStyle.success, custom_id="tk_admin", emoji="🏛️")
    async def tk_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.crea_ticket(interaction, "amministrazione")

    @discord.ui.button(label="TICKET ASSISTENZA", style=discord.ButtonStyle.danger, custom_id="tk_assist", emoji="🎫")
    async def tk_assist(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.crea_ticket(interaction, "assistenza")

    @discord.ui.button(label="TICKET PERMA", style=discord.ButtonStyle.success, custom_id="tk_perma", emoji="☠️")
    async def tk_perma(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.crea_ticket(interaction, "perma")

    @discord.ui.button(label="TICKET ITEM", style=discord.ButtonStyle.secondary, custom_id="tk_item", emoji="🪖")
    async def tk_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.crea_ticket(interaction, "item")

    async def crea_ticket(self, interaction: discord.Interaction, tipo: str):
        guild = interaction.guild
        category = guild.get_channel(1527479376952692838)
        if not category:
            category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")
        
        ch_name = f"ticket-{interaction.user.name}-{tipo}"
        channel = await guild.create_text_channel(ch_name, category=category)
        
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.set_permissions(guild.default_role, read_messages=False)
        
        await interaction.response.send_message(f"🎫 Il tuo ticket è stato aperto qui: {channel.mention}", ephemeral=True)
        
        embed = discord.Embed(title="🎫 | TICKET APERTO", description=f"Benvenuto {interaction.user.mention}!\nUno staffer ti assisterà a breve.\nUsa `/close` per chiudere il ticket quando hai finito.", color=discord.Color.from_rgb(255, 107, 53))
        await channel.send(content=interaction.user.mention, embed=embed)

        # Log ticket nel canale dedicato
        log_ch = guild.get_channel(CH_LOG_TICKET)
        if log_ch:
            log_embed = discord.Embed(title="🎫 | TICKET CREATO", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
            log_embed.add_field(name="Pannello", value=f">>> Ticket {tipo}", inline=False)
            log_embed.add_field(name="Creato da", value=f">>> {interaction.user.mention}", inline=False)
            log_embed.add_field(name="Canale", value=f">>> {channel.mention}", inline=False)
            log_embed.add_field(name="Data", value=f">>> {datetime.now().strftime('%Y-%m-%d')}", inline=False)
            log_embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
            await log_ch.send(embed=log_embed)

@bot.tree.command(name="accetta_background", description="✅ Accetta il background di un utente (Solo Staff)")
@app_commands.describe(utente="L'utente a cui accettare il background")
@is_staff_or_direttore()
async def accetta_background(interaction: discord.Interaction, utente: discord.Member, nota: str = ""):
    colore = discord.Color.from_rgb(255, 107, 53)
    embed = discord.Embed(color=colore, timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    desc = (
        f"📝 | **ESITO BACKGROUND**\n\n"
        f"**Cittadino ➢**\n{utente.mention}\n\n"
        f"**Esito ➢**\n✅ Accettato\n\n"
    )
    if nota:
        desc += f"**Nota ➢**\n{nota}\n\n"
    desc += f"**Dallo staff ➢**\n{interaction.user.mention}\n\n*Preparati per la wl.*"
    embed.description = desc
    whitelist_db[utente.id] = "Approvato"

    # Assegna ruoli background accettato
    for ruolo_id in (1494294050319241356, 1532126894127059127):
        ruolo_bg = interaction.guild.get_role(ruolo_id)
        if ruolo_bg:
            try:
                await utente.add_roles(ruolo_bg, reason="Background accettato dallo staff")
            except Exception as e:
                print(f"⚠️ Errore assegnazione ruolo {ruolo_id}: {e}")

    await interaction.response.send_message(embed=embed)
    try:
        await utente.send(embed=embed)
    except Exception:
        pass
    await log_staff(interaction.guild, f"✅ {interaction.user.mention} ha accettato il background di {utente.mention}.", discord.Color.from_rgb(255, 107, 53))

@bot.tree.command(name="rifiuta_background", description="❌ Rifiuta il background di un utente (Solo Staff)")
@app_commands.describe(utente="L'utente a cui rifiutare il background", motivo="Motivo del rifiuto")
@is_staff_or_direttore()
async def rifiuta_background(interaction: discord.Interaction, utente: discord.Member, motivo: str):
    colore = discord.Color.red()
    embed = discord.Embed(color=colore, timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        f"📝 | **ESITO BACKGROUND**\n\n"
        f"**Cittadino ➢**\n{utente.mention}\n\n"
        f"**Esito ➢**\n❌ Rifiutato\n\n"
        f"**Motivazione ➢**\n{motivo}\n\n"
        f"**Dallo staff ➢**\n{interaction.user.mention}"
    )
    await interaction.response.send_message(embed=embed)
    try:
        await utente.send(embed=embed)
    except Exception:
        pass
    await log_staff(interaction.guild, f"❌ {interaction.user.mention} ha rifiutato il background di {utente.mention}. Motivo: {motivo}", discord.Color.red())






# on_ready spostato in fondo al file dopo tutti i comandi

# ==========================================
# 🟢 BENVENUTO / ADDIO AUTOMATICI
# ==========================================

# 🔴 INSERISCI QUI L'ID DEL CANALE BENVENUTI DEL TUO SERVER
CANALE_BENVENUTO_ID = 1532127042848424026  # Benvenuto Eclipse City
# 🔴 INSERISCI QUI L'ID DEL CANALE ARRIVEDERCI DEL TUO SERVER
CANALE_ADDIO_ID = 1532127045465804942    # Partenze

# Link immagine banner benvenuto
BANNER_BENVENUTO = "https://cdn.discordapp.com/attachments/1488275787873390752/1513128185003249734/file_000000006ff8722fb59a7770425a0fb2.png?ex=6a58b2ef&is=6a57616f&hm=12219a1c3525341141cb50b193f21eb2b6ec69c1da979121375a7fa934bf8bc6&"

# ID canali benvenuto
CH_INFO_GUIDA_WL      = 1493322735516913834
CH_MODULO_BACKGROUND  = 1493322744547246181
CH_CHAT_NO_WL         = 1493322740231569539
CH_STATO_WHITELIST    = 1502360586166468838

RUOLO_NON_WHITELISTATO_ID = 1532126898682069093

@bot.event
@bot.event
async def on_member_join(member: discord.Member):
    # Assegna SOLO il ruolo Non Whitelistato automaticamente
    ruolo_nwl = member.guild.get_role(RUOLO_NON_WHITELISTATO_ID)
    if ruolo_nwl:
        try:
            await member.add_roles(ruolo_nwl, reason="Nuovo membro — ruolo Non Whitelistato assegnato automaticamente")
        except Exception:
            pass
    # Rimuove eventuali altri ruoli assegnati automaticamente da Discord (es. ruoli di default)
    for ruolo in member.roles:
        if ruolo.is_default():
            continue  # @everyone non si può rimuovere
        if ruolo.id != RUOLO_NON_WHITELISTATO_ID:
            try:
                await member.remove_roles(ruolo, reason="Pulizia ruoli — solo Non Whitelistato consentito all'ingresso")
            except Exception:
                pass

    canale = member.guild.get_channel(CANALE_BENVENUTO_ID)
    if canale is None:
        canale = discord.utils.get(member.guild.text_channels, name="benvenuti")
    if canale is None:
        return

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f'✈️ **"Allacciate le cinture"** ✈️\n'
        f'{member.mention} è in città! 👋\n\n'
        '🫵  *Il tuo volo è appena atterrato a Eclipse City* 🌆\n'
        '🔥  *Che tu sia qui per scalare i vertici del crimine, fondare un\'azienda o semplicemente goderti la vita, la tua storia inizia adesso* 💫\n\n'
        '➢ ✍️ *Compila il* https://discord.com/channels/1532113882775163023/1532127154987339867\n'
        '➢  📜 *Studia i regolamenti e richiedi qui la tua WL* https://discord.com/channels/1532113882775163023/1532127148738085111\n\n'
        '<:emoji_1:1532539761477029958> **Buon RP e buona permanenza! 🚀**'
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1532127042848424026/1535800260461600929/Blue_and_Cream_Illustrative_Police_Instagram_Story_-_1.png?ex=6a7914f3&is=6a77c373&hm=68ef6d5ed209318f6ce8c3991dab86de7d765d20894bab6374acd12c4d57eb75&")
    embed.set_thumbnail(url=member.display_avatar.url)

    await canale.send(embed=embed)


@bot.event
async def on_member_remove(member: discord.Member):
    canale = member.guild.get_channel(CANALE_ADDIO_ID)
    if canale is None:
        # fallback: cerca canale per nome
        canale = discord.utils.get(member.guild.text_channels, name="addio")
        if canale is None:
            canale = discord.utils.get(member.guild.text_channels, name="arrivederci")
    if canale is None:
        return

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f'🛫 **"Allacciate le cinture"** 🛫\n'
        f'{member.mention} ha lasciato Eclipse City! 👋\n\n'
        '🧳 *Il tuo volo è appena partito da Eclipse City* 🏙️\n'
        '🌍 *Che tu vada a nuove avventure, torni presto o semplicemente ti prenda una pausa, ti salutiamo con affetto* ⭐\n\n'
        '> 🎭 *Speriamo di rivederti presto tra le strade di Los Santos!*\n\n'
        '🛬 **Buon viaggio e a presto! 🚀**'
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    await canale.send(embed=embed)


# ==========================================
# 1. 🟢 STATUS SERVER E SONDAGGI
# ==========================================

@bot.tree.command(name="creasondaggio", description="⌨️ Mostra i pulsanti per selezionare l'orario del sondaggio RP")
@is_staff_or_direttore()
async def crea_sondaggio(interaction: discord.Interaction):
    view = ViewSondaggioPulsanti()
    await interaction.response.send_message(
        "**Pannello di Controllo Sondaggi:**\nSeleziona l'orario della sessione RP cliccando uno dei pulsanti sottostanti.", 
        view=view, 
        ephemeral=True
    )

@bot.tree.command(name="debugruoli", description="DEBUG: mostra i tuoi ruoli")
async def debug_ruoli(interaction: discord.Interaction):
    import re as _re2
    def pulisci(nome):
        n = nome.encode('ascii', 'ignore').decode('ascii')
        n = _re2.sub(r'[^a-z0-9 ]', '', n.lower())
        return ' '.join(n.split())
    # Forza il fetch del membro aggiornato dal server
    try:
        membro = await interaction.guild.fetch_member(interaction.user.id)
    except Exception:
        membro = interaction.user
    righe = []
    for r in membro.roles:
        pulito = pulisci(r.name)
        righe.append(f"`{r.name}` -> `{pulito}`")
    testo = "\n".join(righe) if righe else "Nessun ruolo trovato"
    await interaction.response.send_message(f"**I tuoi ruoli ({len(membro.roles)}):**\n{testo}", ephemeral=True)

@bot.tree.command(name="annuncio", description="📢 Invia un messaggio/annuncio pubblico in chat")
@is_staff_or_direttore()
async def annuncio(interaction: discord.Interaction, messaggio: str):
    
    embed = discord.Embed(title="📢 | ANNUNCIO", color=discord.Color.red())
    embed.description = (
        f"**STAFF ➢**\n"
        f"{interaction.user.mention}\n\n"
        f"**INFORMA CHE ➢**\n"
        f"{messaggio}"
    )
    
    await interaction.response.send_message("✅ Annuncio inviato con successo!", ephemeral=True)
    await interaction.channel.send(content="@everyone @here", embed=embed)

@bot.tree.command(name="rpon", description="📢 Annuncia l'apertura del server RP")
@is_staff_or_direttore()
async def rpon(interaction: discord.Interaction):
    await interaction.response.send_message("⌛", ephemeral=True)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        "✅ **RP ON** ✅\n\n"
        "Ti auguriamo un buon Roleplay"
    )
    embed.set_thumbnail(url=LOGO_SERVER)
    await interaction.channel.send(content="@everyone", embed=embed)
    await interaction.delete_original_response()

@bot.tree.command(name="rpoff", description="🛑 Annuncia la chiusura del server RP")
@is_staff_or_direttore()
async def rpoff(interaction: discord.Interaction):
    await interaction.response.send_message("⌛", ephemeral=True)
    embed = discord.Embed(color=discord.Color.red())
    embed.description = (
        "❌ **RP OFF** ❌\n\n"
        "La sessione è terminata!! Attendi che torni Online per divertirti di nuovo con noi. "
        "Intanto che aspetti fai nuove amicizie con la nostra community!!"
    )
    embed.set_thumbnail(url=LOGO_SERVER)
    await interaction.channel.send(content="@everyone", embed=embed)
    await interaction.delete_original_response()

@bot.tree.command(name="convoca", description="📢 Convoca un utente in assistenza (Solo Staff)")
@is_staff_or_direttore()
async def convoca(interaction: discord.Interaction, utente: discord.Member, motivo: str):
    embed = discord.Embed(title="📢 | NUOVA CONVOCAZIONE", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        "**INFO OOC:**\n\n"
        "```text\nUTENTE\n```\n"
        f"➢ {utente.mention}\n\n"
        "**INFO CONVOCAZIONE**\n\n"
        f"*STAFF ➢* {interaction.user.mention}\n"
        f"*MESSAGGIO CONVOCAZIONE ➢* {motivo}\n"
        "───────────────\n\n"
        f"🔔 | **Il messaggio é stato mandato in dm a:** {utente.mention}"
    )
    
    try:
        dm_embed = discord.Embed(title="📢 CONVOCAZIONE STAFF", description=f"Sei stato convocato dallo staff.\n**Staffer:** {interaction.user.mention}\n**Motivo:** {motivo}\n\n*Recati immediatamente in un canale vocale Assistenza.*", color=discord.Color.red())
        await utente.send(embed=dm_embed)
    except discord.Forbidden:
        pass 
    
    await interaction.response.send_message(embed=embed)

# ==========================================
# 1.5 🎫 TICKET SYSTEM
# ==========================================
@bot.tree.command(name="ticket", description="🎫 Crea il pannello dei ticket (Solo Staff)")
@is_staff_or_direttore()
async def ticket_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 | PANNELLO TICKET:", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        "➢ **Benvenuto nella chat Ticket!**\n"
        "➢ *Clicca uno dei bottoni qui sotto per aprire un ticket in base alla propria esigenza.*"
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1532127388161544392/1534704553944027206/IMG_3349.png?ex=6a790cff&is=6a77bb7f&hm=cbc74dc1e122f8a3fc23979a681435cc426cb1d64b9795d3b5eb2fbc66ed61e5&")
    
    await interaction.channel.send(embed=embed, view=TicketPanelView())
    await interaction.response.send_message("✅ Pannello Ticket creato con successo.", ephemeral=True)

@bot.tree.command(name="close", description="🔒 Chiude il ticket corrente")
async def close_ticket(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("🔒 Chiusura del ticket in 3 secondi...")
        await asyncio.sleep(3)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ Questo comando può essere usato solo in un canale Ticket.", ephemeral=True)


# ==========================================
# 2. 🏦 ECONOMIA & PROPRIETÀ
# ==========================================

@bot.tree.command(name="apriconto", description="💳 Apri il tuo conto bancario istituzionale e ricevi bonus")
async def apriconto(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in conti_bancari:
        await interaction.response.send_message("❌ Possiedi già un conto corrente attivo!", ephemeral=True)
    else:
        conti_bancari[user_id] = 15000
        portafogli[user_id] = 100
        inventari[user_id] = ["📱 Telefono", "🔑 Chiavi di Casa", "💳 Carta Pacific Bank"]
        zaini[user_id] = ["Tramezzino"]
        
        embed = discord.Embed(title="🏦 PACIFIC BANK — CONTO CORRENTE ATTIVATO 💳", description="Conto attivato con 15.000€ in banca e 100€ in contanti.", color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
        await interaction.response.send_message(embed=embed)
        await log_azione(interaction.guild, interaction.user, "🏦 Conto bancario aperto", "Bonus iniziale: 15.000$ banca + 100$ contanti", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)

@bot.tree.command(name="bal", description="💵 Controlla il saldo e gestisci i tuoi averi")
async def bal(interaction: discord.Interaction, utente: discord.Member = None):
    target = utente if utente else interaction.user
    # Se stai guardando il tuo saldo e non hai un conto, blocca
    if utente is None and target.id not in conti_bancari:
        return await interaction.response.send_message(
            "❌ Non hai ancora un conto bancario! Usa `/apriconto` per aprirne uno.", ephemeral=True
        )
    # Se stai guardando il saldo di qualcun altro e non ha conto, avvisa
    if utente is not None and target.id not in conti_bancari:
        return await interaction.response.send_message(
            f"❌ {target.display_name} non ha ancora un conto bancario.", ephemeral=True
        )
    
    saldo_banca = conti_bancari.get(target.id, 0)
    saldo_contanti = portafogli.get(target.id, 0)
    saldo_totale = saldo_banca + saldo_contanti

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f"🧾 | *Saldo di {target.mention}*\n\n"
        f"💼**Saldo Totale: ➢** {saldo_totale}$\n\n"
        f"💼**Portafoglio ➢** {saldo_contanti}$\n\n"
        f"💼**Banca ➢** {saldo_banca}$\n"
    )
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    embed.set_footer(
        text=f"RICHIESTO DA {interaction.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    )

    if utente is not None and utente.id != interaction.user.id:
        # Stai guardando il saldo di qualcun altro → niente bottoni
        await interaction.response.send_message(embed=embed)
    else:
        # Sei tu, con o senza tag → mostra i bottoni
        view = ViewBilancio()
        await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="add-money", description="➕ Aggiungi denaro contante")
@is_staff_or_direttore()
async def add_money(interaction: discord.Interaction, utente: discord.Member, importo: int):
    if importo <= 0: return await interaction.response.send_message("❌ Importo maggiore di zero.", ephemeral=True)
    if utente.id not in portafogli: portafogli[utente.id] = 0
    portafogli[utente.id] += importo
    _salva_dati()
    await log_staff(interaction.guild, f"💰 {interaction.user.mention} ha aggiunto **{importo}$** in contanti a {utente.mention}.", discord.Color.from_rgb(255, 107, 53))
    await interaction.response.send_message(f"✅ Aggiunti **{importo}$** in contanti a {utente.mention}.")

@bot.tree.command(name="remove-money", description="➖ Rimuovi denaro contante o bancario a un utente")
@is_staff_or_direttore()
async def remove_money(interaction: discord.Interaction, utente: discord.Member, tipo: str, importo: int):
    if importo <= 0: return await interaction.response.send_message("❌ Importo maggiore di zero.", ephemeral=True)
    
    tipo_l = tipo.lower().strip()
    if tipo_l in ["contanti", "portafoglio"]:
        if utente.id not in portafogli: portafogli[utente.id] = 0
        portafogli[utente.id] = max(0, portafogli[utente.id] - importo)
        _salva_dati()
        await log_staff(interaction.guild, f"➖ {interaction.user.mention} ha rimosso **{importo}$** in contanti a {utente.mention}.", discord.Color.from_rgb(255, 107, 53))
        await interaction.response.send_message(f"➖ Rimossi **{importo}$** in contanti a {utente.mention}.")
    elif tipo_l in ["banca", "conto"]:
        if utente.id not in conti_bancari: conti_bancari[utente.id] = 0
        conti_bancari[utente.id] = max(0, conti_bancari[utente.id] - importo)
        _salva_dati()
        await log_staff(interaction.guild, f"➖ {interaction.user.mention} ha rimosso **{importo}$** dal conto bancario di {utente.mention}.", discord.Color.from_rgb(255, 107, 53))
        await interaction.response.send_message(f"➖ Rimossi **{importo}$** dal conto bancario di {utente.mention}.")
    else:
        return await interaction.response.send_message("❌ Tipo non valido. Usa: *contanti* o *banca*.", ephemeral=True)

@bot.tree.command(name="paga", description="💳 Paga un altro cittadino o il bot")
@_blocca_se_dorme()
async def paga(interaction: discord.Interaction, destinatario: discord.Member, importo: int):
    mittente_id = interaction.user.id
    if destinatario.id == mittente_id:
        return await interaction.response.send_message("❌ Non puoi pagare te stesso.", ephemeral=True)
    if importo <= 0:
        return await interaction.response.send_message("❌ Inserisci un importo maggiore di zero.", ephemeral=True)
    saldo_mittente = portafogli.get(mittente_id, 0)
    if saldo_mittente < importo:
        return await interaction.response.send_message("❌ Non hai abbastanza contanti nel portafoglio.", ephemeral=True)
    portafogli[mittente_id] = saldo_mittente - importo

    # Pagamento al bot — cassa del server
    if destinatario.bot:
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
        embed.description = (
            f"🏛️ | **PAGAMENTO ALLA CASSA DEL SERVER**\n\n"
            f"👤 **Pagante:** {interaction.user.mention}\n"
            f"💰 **Importo versato:** **{importo}$**\n"
            f"💳 **Saldo rimanente:** **{portafogli.get(mittente_id, 0)}$**\n\n"
            f"✅ Pagamento registrato con successo!"
        )
        await interaction.response.send_message(embed=embed)
        await log_azione(interaction.guild, interaction.user, "🏛️ Pagamento al Server", f"Importo: **{importo}$** → Cassa Server", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)
        return

    portafogli[destinatario.id] = portafogli.get(destinatario.id, 0) + importo
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.description = f"📲 | **PAGAMENTO EFFETTUATO**\n\nHai pagato **{importo}$** a {destinatario.mention}!"
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, "💸 Pagamento effettuato", f"Importo: **{importo}$** → {destinatario.mention}", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


# ==========================================
# 3. 📝 BACKGROUND & WHITELIST
# ==========================================

@bot.tree.command(name="pannello-bg", description="📝 Crea il pannello regolamento per inviare i background (Solo Staff)")
@is_staff_or_direttore()
async def pannello_bg(interaction: discord.Interaction):
    embed = discord.Embed(title="📝 | BACKGROUND", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.description = (
        "➢ *Gentile utente,*\n\n"
        "*al fine di procedere correttamente con la verifica e la gestione della richiesta, si invita cortesemente a compilare in modo completo e accurato il modulo “Background” riportato di seguito.*\n"
        "*Si raccomanda di inserire tutte le informazioni richieste con la massima precisione, così da consentire allo staff di effettuare le opportune verifiche nei tempi previsti.*\n\n"
        "*Una volta inviato il modulo, la richiesta verrà presa in carico dal team competente e sottoposta ai controlli necessari secondo le procedure interne.*\n\n"
        "───────────────\n\n"
        f"🔔 | **Lo staff provvederà successivamente ad aggiornare l'utente in merito all'esito del background effettuato tramite il canale : <#{CH_ESITI_BACKGROUND}>**"
    )
    await interaction.channel.send(embed=embed, view=ViewPannelloBg())
    await interaction.response.send_message("✅ Pannello creato con successo.", ephemeral=True)

class ModalNotaBg(discord.ui.Modal, title="Nota per il Background"):
    nota = discord.ui.TextInput(
        label="Nota per il cittadino",
        style=discord.TextStyle.paragraph,
        placeholder="Scrivi una nota opzionale...",
        required=False
    )
    def __init__(self, utente, staff, esito_val, is_accettato, canale):
        super().__init__()
        self.utente = utente
        self.staff = staff
        self.esito_val = esito_val
        self.is_accettato = is_accettato
        self.canale = canale

    async def on_submit(self, interaction: discord.Interaction):
        colore = discord.Color.from_rgb(255, 107, 53) if self.is_accettato else discord.Color.red()
        embed = discord.Embed(color=colore)
        embed.set_thumbnail(url=LOGO_SERVER)
        desc = (
            f"📝 | **ESITO BACKGROUND**\n\n"
            f"**Cittadino ➢**\n{self.utente.mention}\n\n"
            f"**Esito ➢**\n{self.esito_val}\n\n"
        )
        if self.nota.value:
            desc += f"**Nota ➢**\n{self.nota.value}\n\n"
        desc += f"**Dallo staff ➢**\n{self.staff.mention}"
        if self.is_accettato:
            desc += "\n\n*Preparati per la wl.*"
        embed.description = desc
        await interaction.response.send_message(embed=embed)
        if self.is_accettato:
            whitelist_db[self.utente.id] = "Approvato"
        try:
            dm_embed = discord.Embed(color=colore)
            dm_embed.description = desc
            await self.utente.send(embed=dm_embed)
        except Exception:
            pass

class ModalRifiutoBg(discord.ui.Modal, title="Motivazione Rifiuto Background"):
    motivazione = discord.ui.TextInput(
        label="Motivazione del rifiuto",
        style=discord.TextStyle.paragraph,
        placeholder="Scrivi il motivo del rifiuto...",
        required=True
    )
    def __init__(self, utente, staff):
        super().__init__()
        self.utente = utente
        self.staff = staff

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.red())
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.description = (
            f"📝 | **ESITO BACKGROUND**\n\n"
            f"**Cittadino ➢**\n{self.utente.mention}\n\n"
            f"**Esito ➢**\nRifiutato\n\n"
            f"**Motivazione ➢**\n{self.motivazione.value}\n\n"
            f"**Dallo staff ➢**\n{self.staff.mention}"
        )
        await interaction.response.send_message(embed=embed)
        try:
            await self.utente.send(embed=embed)
        except Exception:
            pass

class EsitoBgView(discord.ui.View):
    def __init__(self, utente, staff, canale):
        super().__init__(timeout=120)
        self.utente = utente
        self.staff = staff
        self.canale = canale

    @discord.ui.button(label="✅ Accetta", style=discord.ButtonStyle.green)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        await interaction.response.send_modal(ModalNotaBg(self.utente, self.staff, "Accettato", True, self.canale))

    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.red)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        await interaction.response.send_modal(ModalRifiutoBg(self.utente, self.staff))

@bot.tree.command(name="esito-bg", description="✅/❌ Dai l'esito a un background (Solo Staff)")
@app_commands.describe(utente="L'utente a cui dare l'esito")
@is_staff_or_direttore()
async def esito_bg(interaction: discord.Interaction, utente: discord.Member):
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f"📝 | **VALUTAZIONE BACKGROUND**\n\n"
        f"**Cittadino ➢**\n{utente.mention}\n\n"
        f"➢ Scegli se accettare o rifiutare il background."
    )
    embed.set_thumbnail(url=LOGO_SERVER)
    await interaction.response.send_message(embed=embed, view=EsitoBgView(utente, interaction.user, interaction.channel), ephemeral=True)

@bot.tree.command(name="wl-passata", description="✅ Annuncia che un utente ha superato il provino Whitelist (Solo Staff)")
@is_staff_or_direttore()
async def wl_passata(interaction: discord.Interaction, utente: discord.Member, errori: int):
    await interaction.response.defer()

    # ID ruoli da assegnare alla WL passata
    WL_RUOLI_IDS = [
        1532126913630572564,  # Ruolo WL 1
        1532126909939318926,  # Ruolo WL 2
        1532126905967313007,  # Ruolo WL 3
        1532126903060664411,  # Ruolo WL 4
        1532126900787609692,  # Ruolo WL 5
        1532126886900007032,  # Ruolo WL 6
        1532126867489030295,  # Ruolo WL 7
        1532126864192045066,  # Ruolo WL 8
    ]

    # ID ruoli da rimuovere alla WL passata
    WL_RUOLI_DA_RIMUOVERE = [
        1532126898682069093,  # ❌ Non Whitelistato
        1494294050319241356,  # ⏳ Attesa Background
    ]

    errori_ruoli = []

    # Rimuovi ruoli Non Whitelistato e Attesa Background
    for rid_rm in WL_RUOLI_DA_RIMUOVERE:
        ruolo_rm = interaction.guild.get_role(rid_rm)
        if ruolo_rm and ruolo_rm in utente.roles:
            try:
                await utente.remove_roles(ruolo_rm)
            except Exception as e:
                errori_ruoli.append(f"Rimozione ruolo {rid_rm}: {e}")

    ruoli_da_aggiungere = []
    for rid in WL_RUOLI_IDS:
        r = interaction.guild.get_role(rid)
        if r:
            ruoli_da_aggiungere.append(r)
        else:
            errori_ruoli.append(f"Ruolo ID {rid} non trovato nel server")

    if ruoli_da_aggiungere:
        try:
            await utente.add_roles(*ruoli_da_aggiungere, reason="WL Passata")
        except discord.Forbidden:
            errori_ruoli.append("❌ Il bot non ha il permesso di assegnare ruoli (controlla che il ruolo del bot sia sopra i ruoli da assegnare)")
        except Exception as e:
            errori_ruoli.append(f"Errore assegnazione ruoli: {e}")

    embed = discord.Embed(title="🟩 | WL PASSATA", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        f"**Cittadino** ➢ {utente.mention}\n"
        f"**Esito** ➢ Passata\n"
        f"**Errori** ➢ {errori}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Dallo staff:**\n"
        f"{interaction.user.mention}"
    )
    if errori_ruoli:
        embed.add_field(name="⚠️ Problemi ruoli (visibile solo allo staff):", value="\n".join(errori_ruoli), inline=False)

    await interaction.followup.send(embed=embed)


@bot.tree.command(name="wl-rifiutata", description="🟥 Annuncia che un utente ha fallito il provino Whitelist (Solo Staff)")
@is_staff_or_direttore()
@app_commands.describe(utente="L'utente che ha fallito la WL", errori="Numero di errori commessi")
async def wl_rifiutata(interaction: discord.Interaction, utente: discord.Member, errori: int):
    embed = discord.Embed(title="🟥 | WL RIFIUTATA", color=discord.Color.red(), timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        f"**Utente rifiutato** ➢ {utente.mention}\n"
        f"**Esito** ➢ Rifiutata\n"
        f"**Errori** ➢ {errori}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Da staff:**\n"
        f"{interaction.user.mention}"
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="wl-on", description="✅ Annuncia che le whitelist sono aperte (Solo Staff)")
@is_staff_or_direttore()
async def wl_on(interaction: discord.Interaction):
    embed = discord.Embed(title="✅ | WHITELIST ON", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        "➢ Le whitelist sono attualmente on, lo staff vi raccomanda di "
        "leggere il regolamento prima di affrontare la wl."
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="wl-off", description="🟥 Annuncia che le whitelist sono chiuse (Solo Staff)")
@is_staff_or_direttore()
async def wl_off(interaction: discord.Interaction):
    embed = discord.Embed(title="🟥 | WHITELIST OFF", color=discord.Color.red(), timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        "➢ Le wl sono attualmente off, verranno rimmesse online appena lo "
        "staff sarà disponibile."
    )
    await interaction.response.send_message(embed=embed)


# ==========================================
# 4. 🪪 ANAGRAFE E LAVORO
# ==========================================

@bot.tree.command(name="registra", description="🪪 Registra i tuoi dati all'anagrafe della città")
@_blocca_se_dorme()
@app_commands.describe(
    nome="Nome del personaggio",
    cognome="Cognome del personaggio",
    nazionalita="Nazionalità",
    eta="Età (numero)",
    sesso="Sesso (M/F)",
    colore_occhi="Colore occhi",
    colore_capelli="Colore capelli",
    psn="Il tuo PSN (es. MarioRossi99) — verrà formattato come +1-ID-PSN",
    foto="Foto del personaggio (OBBLIGATORIA)"
)
async def registra(
    interaction: discord.Interaction,
    nome: str,
    cognome: str,
    nazionalita: str,
    eta: str,
    sesso: str,
    colore_occhi: str,
    colore_capelli: str,
    psn: str,
    foto: discord.Attachment
):
    try:
        val_eta = int(eta)
        if val_eta <= 0:
            return await interaction.response.send_message("❌ Età non valida.", ephemeral=True)

        if not foto.content_type or not foto.content_type.startswith("image/"):
            return await interaction.response.send_message("❌ Il file allegato non è un'immagine valida.", ephemeral=True)

        user_id = interaction.user.id
        numero_formattato = f"+1-{psn}"

        documenti_identita[user_id] = {
            "nome": nome.strip(),
            "cognome": cognome.strip(),
            "nazionalita": nazionalita.strip(),
            "eta": str(val_eta),
            "sesso": sesso.strip().upper(),
            "occhi": colore_occhi.strip(),
            "capelli": colore_capelli.strip(),
            "numero_telefono": numero_formattato,
            "lavoro": "cittadino",
            "foto_url": foto.url
        }

        await interaction.response.send_message(
            f"✅ Identità registrata! Il tuo numero è `{numero_formattato}`", ephemeral=True
        )
        await log_azione(interaction.guild, interaction.user, "🪪 Documento registrato", f"Nome IC: {nome} {cognome} | Età: {val_eta} | Tel: {numero_formattato}", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)

        dati = documenti_identita[user_id]
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.description = (
            f"✅ | **DOCUMENTO REGISTRATO**\n"
            f"➢ Il tuo documento é stato registrato con successo.\n\n"
            f"🪪 | **UTENTE**\n{interaction.user.mention}"
        )
        embed.set_thumbnail(url=foto.url)
        await interaction.channel.send(embed=embed)

        doc_embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        doc_embed.description = (
            f"📄 | **DOCUMENTO D'IDENTITÀ**\n\n"
            f"**Cittadino:**\n➢ {interaction.user.mention}\n\n"
            f"**Telefono:**\n➢ 📞 `{numero_formattato}`\n\n"
            f"**Nome:**\n➢ *{dati['nome']}*\n\n"
            f"**Cognome:**\n➢ *{dati['cognome']}*\n\n"
            f"**Nazionalità:**\n➢ *{dati['nazionalita']}*\n\n"
            f"**Età:**\n➢ *{dati['eta']}*\n\n"
            f"**Sesso:**\n➢ *{dati['sesso']}*\n\n"
            f"**Colore Occhi:**\n➢ *{dati['occhi']}*\n\n"
            f"**Colore Capelli:**\n➢ *{dati['capelli']}*"
        )
        doc_embed.set_image(url=foto.url)
        await interaction.channel.send(embed=doc_embed)

    except ValueError:
        await interaction.response.send_message("❌ Inserisci un numero valido per l'età.", ephemeral=True)

@bot.tree.command(name="documenti", description="🪪 Visualizza i tuoi documenti personali formattati")
async def documenti(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in documenti_identita:
        return await interaction.response.send_message("❌ Non hai documenti registrati. Usa `/registra`.", ephemeral=True)
    
    dati = documenti_identita[user_id]
    embed = discord.Embed(title="📄 Documento d'identità", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.add_field(name="Cittadino ➢", value=interaction.user.mention, inline=False)
    embed.add_field(name="ID Univoco ➢", value=f"*{user_id}*", inline=False)
    embed.add_field(name="Telefono ➢", value=f"📞 ` {dati.get('numero_telefono', 'N/A')} `", inline=False)
    embed.add_field(name="Nome ➢", value=f"*{dati['nome']}*", inline=False)
    embed.add_field(name="Cognome ➢", value=f"*{dati['cognome']}*", inline=False)
    embed.add_field(name="Nazionalità ➢", value=f"*{dati['nazionalita']}*", inline=False)
    embed.add_field(name="Età ➢", value=f"*{dati['eta']}*", inline=False)
    embed.add_field(name="Sesso ➢", value=f"*{dati['sesso']}*", inline=False)
    embed.add_field(name="Colore Occhi ➢", value=f"*{dati['occhi']}*", inline=False)
    embed.add_field(name="Colore Capelli ➢", value=f"*{dati['capelli']}*", inline=False)
    embed.set_image(url=dati.get('foto_url', LOGO_SERVER))
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="mostradocumenti", description="👁️ Mostra i tuoi documenti a un altro utente")
async def mostra_documenti(interaction: discord.Interaction, utente: discord.Member):
    user_id = interaction.user.id
    if user_id not in documenti_identita: 
        return await interaction.response.send_message("❌ Non hai documenti registrati.", ephemeral=True)
    
    dati = documenti_identita[user_id]
    embed = discord.Embed(title="📄 Documento d'identità", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.add_field(name="Cittadino ➢", value=f"<@{user_id}>", inline=False)
    embed.add_field(name="ID Univoco ➢", value=f"*{user_id}*", inline=False)
    embed.add_field(name="Telefono ➢", value=f"📞 ` {dati.get('numero_telefono', 'N/A')} `", inline=False)
    embed.add_field(name="Nome ➢", value=f"*{dati['nome']}*", inline=False)
    embed.add_field(name="Cognome ➢", value=f"*{dati['cognome']}*", inline=False)
    embed.add_field(name="Nazionalità ➢", value=f"*{dati['nazionalita']}*", inline=False)
    embed.add_field(name="Età ➢", value=f"*{dati['eta']}*", inline=False)
    embed.add_field(name="Sesso ➢", value=f"*{dati['sesso']}*", inline=False)
    embed.add_field(name="Colore Occhi ➢", value=f"*{dati['occhi']}*", inline=False)
    embed.add_field(name="Colore Capelli ➢", value=f"*{dati['capelli']}*", inline=False)
    embed.set_image(url=dati.get('foto_url', LOGO_SERVER))
    await interaction.response.send_message(f"🪪 {interaction.user.display_name} mostra i documenti a {utente.mention}:", embed=embed)

def puo_gestire_lavoro(member: discord.Member, lavoro: str) -> bool:
    if member.guild_permissions.manage_messages:
        return True
    nome_capo = CAPO_PER_LAVORO.get(lavoro.lower())
    if nome_capo:
        return any(ruolo.name.lower() == nome_capo.lower() for ruolo in member.roles)
    return False

@bot.tree.command(name="assumi", description="🤝 Assumi un cittadino nel lavoro scelto")
async def assumi(interaction: discord.Interaction, utente: discord.Member, lavoro: str):
    lavoro_sel = lavoro.lower()
    if not puo_gestire_lavoro(interaction.user, lavoro_sel):
        return await interaction.response.send_message(f"❌ **Accesso negato:** solo lo staff o il capo di `{lavoro_sel.upper()}` può usare questo comando.", ephemeral=True)
    if lavoro_sel in LAVORI_DUE_GRADI:
        grado_iniziale = "dipendente"
    elif lavoro_sel in GRADI_PER_LAVORO:
        grado_iniziale = GRADI_PER_LAVORO[lavoro_sel][0][0]  
    else:
        grado_iniziale = "dipendente"
    stipendio = ottieni_stipendio_grado(lavoro_sel, grado_iniziale)
    etichetta_lavoro = f"{lavoro_sel} - {grado_iniziale}"
    if utente.id in documenti_identita:
        documenti_identita[utente.id]["lavoro"] = etichetta_lavoro
    else:
        documenti_identita[utente.id] = {"nome": utente.display_name, "eta": "18", "cognome": "", "nazionalita":"", "sesso":"", "occhi":"", "capelli":"", "lavoro": etichetta_lavoro, "foto_url": LOGO_SERVER}

    embed = discord.Embed(title="🤝 Assunzione Ufficiale", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.add_field(name="👤 Lavoratore assunto", value=utente.mention, inline=True)
    embed.add_field(name="💼 Lavoro", value=f"`{lavoro_sel.upper()}`", inline=True)
    embed.add_field(name="🎖️ Grado iniziale", value=f"`{grado_iniziale.upper()}`", inline=True)
    embed.add_field(name="💰 Stipendio (2h)", value=f"{stipendio}$", inline=True)
    embed.set_footer(text=f"Assunto da {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@assumi.autocomplete("lavoro")
async def assumi_lavoro_autocomplete(interaction: discord.Interaction, current: str):
    tutti_i_lavori = LAVORI_DUE_GRADI + list(GRADI_PER_LAVORO.keys())
    disponibili = [l for l in tutti_i_lavori if puo_gestire_lavoro(interaction.user, l)]
    return [app_commands.Choice(name=lav.upper(), value=lav) for lav in disponibili if current.lower() in lav.lower()][:25]

@bot.tree.command(name="promuovi", description="🎖️ Assegna un lavoro e un grado specifico a un membro")
async def promuovi(interaction: discord.Interaction, utente: discord.Member, lavoro: str, grado: str):
    lavoro_sel = lavoro.lower()
    grado_sel = grado.lower()
    if not puo_gestire_lavoro(interaction.user, lavoro_sel):
        return await interaction.response.send_message(f"❌ **Accesso negato:** solo lo staff o il capo di `{lavoro_sel.upper()}` può usare questo comando.", ephemeral=True)
    stipendio = ottieni_stipendio_grado(lavoro_sel, grado_sel)
    etichetta_lavoro = f"{lavoro_sel} - {grado_sel}"
    if utente.id in documenti_identita:
        documenti_identita[utente.id]["lavoro"] = etichetta_lavoro
    else:
        documenti_identita[utente.id] = {"nome": utente.display_name, "eta": "18", "cognome": "", "nazionalita":"", "sesso":"", "occhi":"", "capelli":"", "lavoro": etichetta_lavoro, "foto_url": LOGO_SERVER}

    embed = discord.Embed(title="🎖️ Promozione / Assegnazione Ufficiale", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.add_field(name="👤 Membro", value=utente.mention, inline=True)
    embed.add_field(name="💼 Lavoro", value=f"`{lavoro_sel.upper()}`", inline=True)
    embed.add_field(name="🎖️ Grado", value=f"`{grado_sel.upper()}`", inline=True)
    embed.add_field(name="💰 Stipendio (2h)", value=f"{stipendio}$", inline=True)
    embed.set_footer(text=f"Assegnato da {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@promuovi.autocomplete("lavoro")
async def promuovi_lavoro_autocomplete(interaction: discord.Interaction, current: str):
    tutti_i_lavori = LAVORI_DUE_GRADI + list(GRADI_PER_LAVORO.keys())
    disponibili = [l for l in tutti_i_lavori if puo_gestire_lavoro(interaction.user, l)]
    return [app_commands.Choice(name=lav.upper(), value=lav) for lav in disponibili if current.lower() in lav.lower()][:25]

@promuovi.autocomplete("grado")
async def promuovi_grado_autocomplete(interaction: discord.Interaction, current: str):
    lavoro_scelto = getattr(interaction.namespace, "lavoro", None)
    if not lavoro_scelto: return []
    lavoro_scelto = lavoro_scelto.lower()
    if lavoro_scelto in LAVORI_DUE_GRADI: gradi_disponibili = list(STIPENDI_DUE_GRADI.keys())
    elif lavoro_scelto in GRADI_PER_LAVORO: gradi_disponibili = [nome for nome, _ in GRADI_PER_LAVORO[lavoro_scelto]]
    else: gradi_disponibili = []
    return [app_commands.Choice(name=g.upper(), value=g) for g in gradi_disponibili if current.lower() in g.lower()][:25]

@bot.tree.command(name="licenzia", description="🫓 Licenzia un dipendente")
@is_police_or_staff()
async def licenzia(interaction: discord.Interaction, utente: discord.Member):
    if utente.id in documenti_identita: documenti_identita[utente.id]["lavoro"] = "cittadino"
    else: documenti_identita[utente.id] = {"nome": utente.display_name, "eta": "18", "cognome": "", "nazionalita":"", "sesso":"", "occhi":"", "capelli":"", "lavoro": "cittadino", "foto_url": LOGO_SERVER}
    _salva_dati()
    await log_staff(interaction.guild, f"🫓 {interaction.user.mention} ha licenziato {utente.mention}.", discord.Color.from_rgb(255, 107, 53))
    await interaction.response.send_message(f"🫓 {utente.mention} è stato licenziato ed è tornato allo stato di Cittadino.")


# ==========================================
# 5. 📝 REGISTRAZIONI TARGHE E PATENTI
# ==========================================

class FirmaVeicoloView(discord.ui.View):
    def __init__(self, dip_id, cli_id, targa, modello):
        super().__init__(timeout=None)
        self.dip_id = dip_id
        self.cli_id = cli_id
        self.targa = targa
        self.modello = modello
        self.dip_firmato = False
        self.cli_firmato = False

    @discord.ui.button(label="FIRMA", style=discord.ButtonStyle.danger, emoji="📝")
    async def btn_firma(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.dip_id:
            self.dip_firmato = True
        elif interaction.user.id == self.cli_id:
            self.cli_firmato = True
        else:
            return await interaction.response.send_message("❌ Non sei autorizzato a firmare questo documento.", ephemeral=True)
        
        if self.dip_firmato and self.cli_firmato:
            data_oggi = datetime.now().strftime("%Y-%m-%d")
            targhe_veicoli[self.targa] = {"proprietario": str(self.cli_id), "modello": self.modello, "data": data_oggi, "stato": "Libero"}
            if self.cli_id not in garage_veicoli: garage_veicoli[self.cli_id] = []
            garage_veicoli[self.cli_id].append({"targa": self.targa, "modello": self.modello, "data": data_oggi, "stato": "Libero"})
            
            self.btn_firma.disabled = True
            self.btn_firma.label = "FIRMATO"
            self.btn_firma.style = discord.ButtonStyle.success
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"✅ Veicolo `[{self.targa}]` registrato ufficialmente e firmato da entrambe le parti!")
        else:
            manca = []
            if not self.dip_firmato: manca.append("Dipendente")
            if not self.cli_firmato: manca.append("Cliente")
            await interaction.response.send_message(f"Firma acquisita. Manca ancora la firma di: **{', '.join(manca)}**", ephemeral=True)

@bot.tree.command(name="proprieta-immobili", description="🏢 Visualizza la lista di tutte le case popolari registrate")
async def lista_proprieta(interaction: discord.Interaction):
    if not case_popolari:
        return await interaction.response.send_message("🏢 Al momento non ci sono case popolari assegnate.", ephemeral=True)
    lista = ""
    for chiave_casa, info in case_popolari.items():
        proprietario = interaction.guild.get_member(info['proprietario'])
        nome_prop = proprietario.display_name if proprietario else info.get('nome_completo', "Sconosciuto")
        lista += f"• **{info['via']}, Apt {info['numero']}** - Proprietario: `{nome_prop}`\n"
    embed = discord.Embed(title="🏢 Registro Case Popolari", description=lista, color=discord.Color.from_rgb(255, 107, 53))
    await interaction.response.send_message(embed=embed, ephemeral=True)

class CasaPopolareView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.user_select = discord.ui.UserSelect(placeholder="👥 Seleziona il cittadino", min_values=1, max_values=1, custom_id="select_cittadino")
        self.user_select.callback = self.user_callback
        self.add_item(self.user_select)
        opzioni_vie = [discord.SelectOption(label=via, value=via) for via in VIE_CASE_POPOLARI]
        self.via_select = discord.ui.Select(placeholder="🏠 Seleziona la via", options=opzioni_vie, custom_id="select_via")
        self.via_select.callback = self.via_callback
        self.add_item(self.via_select)
        self.btn_conferma = discord.ui.Button(label="Assegna Casa", style=discord.ButtonStyle.success, disabled=True, custom_id="btn_assegna_casa")
        self.btn_conferma.callback = self.conferma_callback
        self.add_item(self.btn_conferma)
        self.utente_selezionato = None
        self.via_selezionata = None

    async def user_callback(self, interaction: discord.Interaction):
        self.utente_selezionato = self.user_select.values[0]
        await self.check_ready(interaction)

    async def via_callback(self, interaction: discord.Interaction):
        self.via_selezionata = self.via_select.values[0]
        await self.check_ready(interaction)

    async def check_ready(self, interaction: discord.Interaction):
        if self.utente_selezionato and self.via_selezionata:
            self.btn_conferma.disabled = False
        await interaction.response.edit_message(view=self)

    async def conferma_callback(self, interaction: discord.Interaction):
        user = self.utente_selezionato
        via = self.via_selezionata
        if user.id not in documenti_identita:
            return await interaction.response.send_message(f"❌ {user.mention} non è registrato all'anagrafe (deve usare `/registra`).", ephemeral=True)
        dati = documenti_identita[user.id]
        nome_completo = f"{dati['nome']} {dati['cognome']}"
        numeri_occupati = [info['numero'] for info in case_popolari.values() if info['via'] == via]
        numero_assegnato = max(numeri_occupati, default=0) + 1
        chiave_casa = f"{via}|{numero_assegnato}"
        case_popolari[chiave_casa] = {"proprietario": user.id, "nome_completo": nome_completo, "via": via, "numero": numero_assegnato}
        if user.id not in inventari:
            inventari[user.id] = []
        chiave_nome = f"🔑 Chiave - {via}, Apt {numero_assegnato}"
        inventari[user.id].append(chiave_nome)
        _salva_dati()
        indirizzo_completo = f"{via}, Apt {numero_assegnato}. Garage con 2 posti auto 🚗"
        embed = discord.Embed(title="🏢 Assegnazione Casa Popolare", description=f"La casa popolare è stata assegnata correttamente!\n\n**Cittadino:** {user.mention} ({nome_completo})\n**Alloggio:** {indirizzo_completo}", color=discord.Color.from_rgb(255, 107, 53))
        embed.set_footer(text=f"'{chiave_nome}' aggiunto all'inventario del cittadino.")
        await interaction.response.edit_message(content=None, embed=embed, view=None)

@bot.tree.command(name="registra-targa", description="🚗 Crea il documento di registrazione veicolo")
@is_concessionario_or_staff()
async def registra_targa(interaction: discord.Interaction, utente: discord.Member, targa: str, modello: str):
    targa_up = targa.upper().strip()
    
    dip_dati = documenti_identita.get(interaction.user.id, {})
    cli_dati = documenti_identita.get(utente.id, {})
    
    dip_nome = dip_dati.get('nome', interaction.user.name)
    dip_cognome = dip_dati.get('cognome', '')
    cli_nome = cli_dati.get('nome', utente.name)
    cli_cognome = cli_dati.get('cognome', '')
    data_oggi = datetime.now().strftime("%Y-%m-%d")

    embed = discord.Embed(title="🚘 | Registro Veicoli", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        f"➢ {interaction.user.mention} Hai registrato l'auto con successo a {utente.mention}!\n\n"
        f"🪪 **Dati Dipendente Concessionario**\n"
        f"➢ **Nome:** *{dip_nome}*\n"
        f"➢ **Cognome:** *{dip_cognome}*\n"
        f"🪪 **Dati Cittadino**\n"
        f"➢ **Destinatario:** *{cli_nome} {cli_cognome}*\n"
        f"➢ **Tag Destinatario:** {utente.mention}\n"
        f"🚘 **Dati Veicolo**\n"
        f"➢ **Targa:** {targa_up}\n"
        f"➢ **Modello:** {modello}\n"
        f"➢ **Data:** {data_oggi}"
    )
    
    view = FirmaVeicoloView(interaction.user.id, utente.id, targa_up, modello)
    await interaction.response.send_message(content=utente.mention, embed=embed, view=view)
    await log_azione(interaction.guild, interaction.user, "🚗 Registrazione targa", f"Targa: {targa_up} | Modello: {modello} | Cliente: {utente.mention}", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


@bot.tree.command(name="registra-pd", description="🪪 Assegna porto d'armi (Solo Staff/Direttore MSPD)")
@app_commands.describe(tipo="Tipo di porto d'armi da assegnare")
@app_commands.choices(tipo=[
    app_commands.Choice(name="Tipo 1", value="1"),
    app_commands.Choice(name="Tipo 2", value="2"),
    app_commands.Choice(name="Tipo 3", value="3"),
])
@is_staff_or_direttore()
async def registra_pd(interaction: discord.Interaction, utente: discord.Member, tipo: app_commands.Choice[str]):
    if utente.id not in licenze_cittadini: licenze_cittadini[utente.id] = []
    if licenze_cittadini[utente.id] == ["Nessuna licenza speciale"]: licenze_cittadini[utente.id] = []
    etichetta = TIPI_PORTO_ARMI[tipo.value]
    if etichetta not in licenze_cittadini[utente.id]: licenze_cittadini[utente.id].append(etichetta)
    await interaction.response.send_message(f"📜 **{etichetta}** registrato e assegnato a {utente.mention}.")

@bot.tree.command(name="revoca-pd", description="🪪 Revoca un tipo di porto d'armi a un cittadino (Solo Staff/Direttore MSPD)")
@app_commands.describe(tipo="Tipo di porto d'armi da revocare")
@app_commands.choices(tipo=[
    app_commands.Choice(name="Tipo 1", value="1"),
    app_commands.Choice(name="Tipo 2", value="2"),
    app_commands.Choice(name="Tipo 3", value="3"),
])
@is_staff_or_direttore()
async def revoca_pd(interaction: discord.Interaction, utente: discord.Member, tipo: app_commands.Choice[str]):
    etichetta = TIPI_PORTO_ARMI[tipo.value]
    lista = licenze_cittadini.get(utente.id, [])
    if etichetta not in lista: return await interaction.response.send_message(f"❌ {utente.mention} non possiede il **{etichetta}**.", ephemeral=True)
    lista.remove(etichetta)
    licenze_cittadini[utente.id] = lista
    await interaction.response.send_message(f"📜 **{etichetta}** revocato a {utente.mention}.")

@bot.tree.command(name="registra-patenti", description="🚘 Assegna patente (Solo Concessionario/Staff)")
@app_commands.describe(tipo="Tipo di patente da assegnare")
@app_commands.choices(tipo=[
    app_commands.Choice(name="A — Moto", value="A"),
    app_commands.Choice(name="B — Auto", value="B"),
    app_commands.Choice(name="C — Barche e Aerei", value="C"),
])
@is_concessionario_or_staff()
async def registra_patenti(interaction: discord.Interaction, utente: discord.Member, tipo: app_commands.Choice[str]):
    attuali = patenti_cittadini.get(utente.id)
    if not isinstance(attuali, list): attuali = []  
    if tipo.value not in attuali: attuali.append(tipo.value)
    patenti_cittadini[utente.id] = attuali
    await interaction.response.send_message(f"🚘 **{TIPI_PATENTE[tipo.value]}** registrata e attivata per {utente.mention}.")

@bot.tree.command(name="revoca-patente", description="🚘 Revoca un tipo di patente a un cittadino (Solo Concessionario/Staff)")
@app_commands.describe(tipo="Tipo di patente da revocare")
@app_commands.choices(tipo=[
    app_commands.Choice(name="A — Moto", value="A"),
    app_commands.Choice(name="B — Auto", value="B"),
    app_commands.Choice(name="C — Barche e Aerei", value="C"),
])
@is_concessionario_or_staff()
async def revoca_patente(interaction: discord.Interaction, utente: discord.Member, tipo: app_commands.Choice[str]):
    attuali = patenti_cittadini.get(utente.id)
    if not isinstance(attuali, list) or tipo.value not in attuali: return await interaction.response.send_message(f"❌ {utente.mention} non possiede la **{TIPI_PATENTE[tipo.value]}**.", ephemeral=True)
    attuali.remove(tipo.value)
    patenti_cittadini[utente.id] = attuali
    await interaction.response.send_message(f"🚘 **{TIPI_PATENTE[tipo.value]}** revocata a {utente.mention}.")


# ==========================================
# 6. 👮 POLIZIA & GIUSTIZIA
# ==========================================
@bot.tree.command(name="esamina", description="🛃 Esamina le informazioni complete di un cittadino dal database (Solo Polizia)")
@app_commands.describe(utente="Il cittadino da esaminare", psn="ID PSN del cittadino")
@has_police_permission()
async def esamina(interaction: discord.Interaction, utente: discord.Member, psn: str):
    uid = utente.id
    dati = documenti_identita.get(uid, {})
    ha_doc = bool(dati)

    # ── Dati anagrafici ──
    nome        = dati.get("nome", "—")
    cognome     = dati.get("cognome", "—")
    nazionalita = dati.get("nazionalita", "—")
    eta         = dati.get("eta", "—")
    sesso       = dati.get("sesso", "—")
    occhi       = dati.get("occhi", "—")
    capelli     = dati.get("capelli", "—")
    residenza   = proprieta_immobili.get(str(uid), {}).get("indirizzo", "—") if str(uid) in proprieta_immobili else "—"

    # ── Documento ──
    stato_doc = "✅ Registrato" if ha_doc else "❌ **CLANDESTINO** — Documento assente"

    # ── Patenti ──
    patenti_raw = patenti_cittadini.get(uid, [])
    if not isinstance(patenti_raw, list): patenti_raw = []
    patenti_map = {
        "A": "🏍️ **A** — Moto",
        "B": "🚗 **B** — Auto",
        "C": "⛵ **C** — Nautica",
        "D": "✈️ **D** — Aerea",
    }
    patenti_str = "\n".join(f"  ✅ {patenti_map.get(p, p)}" for p in patenti_raw) if patenti_raw else "  ❌ Nessuna patente"

    # ── Porto d'armi ──
    licenze = licenze_cittadini.get(uid, [])
    if not isinstance(licenze, list): licenze = []
    porto_livelli = [l for l in licenze if "Porto d'armi" in l or "Tipo" in l]
    porto_str = "\n".join(f"  ✅ {p}" for p in porto_livelli) if porto_livelli else "  ❌ Nessun porto d'armi"

    # ── Licenze d'arma (denunciate) ──
    licenze_arma = [l for l in licenze if "Porto d'armi" not in l and "Tipo" not in l and l != "Nessuna licenza speciale"]
    licenze_str = "\n".join(f"  🔫 {l}" for l in licenze_arma) if licenze_arma else "  ❌ Nessuna licenza d'arma"

    # ── Assicurazione sanitaria ──
    conto = conti_bancari.get(uid)
    assicurazione = "✅ **Sì** — Coperta dal piano sanitario" if conto is not None else "❌ **No** — Pagamento diretto richiesto"

    # ── Embed ──
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_author(name="🛃 Eclipse City RP Police Department", icon_url=LOGO_SERVER)
    if ha_doc and dati.get("foto_url"):
        embed.set_thumbnail(url=dati["foto_url"])
    else:
        embed.set_thumbnail(url=utente.display_avatar.url)

    embed.description = (
        f"**DS. OOC :** {utente.mention}\n"
        f"**ID. PSN :** `{psn}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛃 *Check informazioni del soggetto dal database* ℹ️"
    )

    embed.add_field(
        name="👤 __D A T I   A N A G R A F I C I__",
        value=(
            f"🪪 **Nome** ➢ {nome}\n"
            f"🪪 **Cognome** ➢ {cognome}\n"
            f"🌍 **Nazionalità** ➢ {nazionalita}\n"
            f"🎂 **Età** ➢ {eta}\n"
            f"⚧ **Sesso** ➢ {sesso}\n"
            f"🏠 **Residenza** ➢ {residenza}"
        ),
        inline=False
    )

    embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)

    embed.add_field(
        name="🪪 __D O C U M E N T A Z I O N E__",
        value=(
            f"📄 **Documento** ➢ {stato_doc}\n\n"
            f"🚘 **Patenti :**\n{patenti_str}\n\n"
            f"🏥 **Assicurazione Sanitaria** ➢ {assicurazione}\n\n"
            f"🔫 **Porto d'Armi :**\n{porto_str}\n\n"
            f"📋 **Licenze d'Arma :**\n{licenze_str}"
        ),
        inline=False
    )

    embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)

    embed.add_field(
        name="👀 __C A R A T T E R I   F E N O T I P I C I__",
        value=(
            f"👁️ **Colore Occhi** ➢ {occhi}\n"
            f"💇 **Colore Capelli** ➢ {capelli}"
        ),
        inline=False
    )

    embed.set_footer(text="ℹ️ Informazioni certificate del Eclipse City RP Police Department ❗")

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="esamina_pagamenti", description="💳 Visualizza gli ultimi pagamenti di un cittadino (Solo Staff/Polizia)")
@app_commands.describe(utente="Il cittadino di cui visualizzare i pagamenti")
@has_police_permission()
async def esamina_pagamenti(interaction: discord.Interaction, utente: discord.Member):
    uid = utente.id
    transazioni = storico_transazioni.get(uid, [])
    saldo_banca  = conti_bancari.get(uid, 0)
    saldo_wallet = portafogli.get(uid, 0)

    colore = discord.Color.from_rgb(255, 107, 53)

    embed = discord.Embed(color=colore, timestamp=datetime.now())
    embed.set_author(
        name=f"🏦 Storico Pagamenti — {utente.display_name}",
        icon_url=utente.display_avatar.url
    )
    embed.set_thumbnail(url=utente.display_avatar.url)

    # ── Intestazione con saldi ──
    saldo_b_fmt = f"{abs(saldo_banca):,}".replace(",", ".")
    saldo_w_fmt = f"{abs(saldo_wallet):,}".replace(",", ".")
    segno_b = "-" if saldo_banca < 0 else ""
    stato_b = "🔴 NEGATIVO" if saldo_banca < 0 else "🟢 Attivo"

    embed.description = (
        f"**👤 Cittadino :** {utente.mention}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏦 **Conto Bancario :** `{segno_b}{saldo_b_fmt} $`  ·  *{stato_b}*\n"
        f"👜 **Portafoglio :** `{saldo_w_fmt} $`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    # ── Lista transazioni ──
    if not transazioni:
        embed.add_field(
            name="📋  __U L T I M I   P A G A M E N T I__",
            value=(
                "```\n"
                "  Nessuna transazione registrata\n"
                "  per questo cittadino.\n"
                "```"
            ),
            inline=False
        )
    else:
        MAX_TX = 10  # mostra fino a 10 transazioni
        righe = ""
        entrate = 0
        uscite  = 0

        for i, t in enumerate(transazioni[:MAX_TX]):
            segno  = t.get("segno", "+")
            importo = t.get("importo", 0)
            tipo   = t.get("tipo", "Transazione")
            cp     = t.get("controparte", "")
            ts     = t.get("ts", "—")

            if segno == "+":
                emoji  = "🟢"
                segno_v = "+"
                entrate += importo
            else:
                emoji  = "🔴"
                segno_v = "−"
                uscite  += importo

            imp_fmt = f"{importo:,}".replace(",", ".")
            cp_str  = f"  ›  {cp}" if cp else ""

            righe += (
                f"{emoji}  **{tipo}**{cp_str}\n"
                f"> 🕐 `{ts}`　　💰 `{segno_v}{imp_fmt} $`\n"
            )
            if i < MAX_TX - 1 and i < len(transazioni) - 1:
                righe += "\n"

        embed.add_field(
            name=f"📋  __U L T I M I   P A G A M E N T I__  *(ultimi {min(len(transazioni), MAX_TX)})*",
            value=righe,
            inline=False
        )

        # ── Riepilogo ──
        e_fmt = f"{entrate:,}".replace(",", ".")
        u_fmt = f"{uscite:,}".replace(",", ".")
        embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", inline=False)
        embed.add_field(
            name="📊  __R I E P I L O G O__",
            value=(
                f"🟢 **Totale Entrate :** `+{e_fmt} $`\n"
                f"🔴 **Totale Uscite :**  `−{u_fmt} $`\n"
                f"📁 **Transazioni totali registrate :** `{len(transazioni)}`"
            ),
            inline=False
        )

    embed.set_footer(
        text=f"Consultato da {interaction.user.display_name}  ·  Eclipse City RP  ·  Pacific Bank",
        icon_url=LOGO_SERVER
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cerca", description="🔍 Cerca una targa nei registri")
@has_police_permission()
async def cerca_targa(interaction: discord.Interaction, targa: str):
    targa_up = targa.upper().strip()
    if targa_up in targhe_veicoli:
        info = targhe_veicoli[targa_up]
        stato = info.get("stato", "Libero")
        
        proprietario_id = int(info['proprietario'])
        membro = interaction.guild.get_member(proprietario_id)
        nome_prop = membro.display_name if membro else info['proprietario']
        
        await interaction.response.send_message(f"🔍 **REGISTRO TARGHE:** `[{targa_up}]` | Veicolo: `{info['modello']}` | Intestatario: `{nome_prop}` | Stato: **{stato}**")
    else:
        await interaction.response.send_message(f"🚨 Targa **`[{targa_up}]`** non presente.")

@bot.tree.command(name="garage", description="🚘 Vedi i veicoli posseduti (tuoi o di altri)")
async def garage_persona(interaction: discord.Interaction, utente: discord.Member = None):
    target = utente if utente else interaction.user
    tutti_veicoli = garage_veicoli.get(target.id, [])
    
    veicoli = [v for v in tutti_veicoli if v.get("stato", "Libero") != "Sequestrato"]
    
    embed = discord.Embed(title="🚘 | Garage Personale", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_thumbnail(url=LOGO_SERVER)
    
    if not veicoli:
        embed.description = f"🚗 {target.display_name} non possiede veicoli registrati o disponibili."
        return await interaction.response.send_message(embed=embed)
    
    dati = documenti_identita.get(target.id, {})
    nome = dati.get('nome', target.name)
    cognome = dati.get('cognome', '')
    nome_completo = f"{nome} {cognome}".strip()

    desc = ""
    for v in veicoli:
        desc += (
            "───────────────\n"
            "🪪 **Dati Cittadino**\n"
            f"➢ **Cittadino:** *{nome_completo}*\n"
            f"➢ **Tag Destinatario:** {target.mention}\n"
            "🚘 **Dati Veicolo**\n"
            f"➢ **Targa:** {v['targa']}\n"
            f"➢ **Modello:** {v['modello']}\n"
            f"➢ **Data:** {v.get('data', 'Sconosciuta')}\n\n"
        )
    embed.description = desc
    await interaction.response.send_message(embed=embed)


class RegistratoView(discord.ui.View):
    """Pulsante rosso → verde per confermare registrazione nel database."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔴 Non Registrato", style=discord.ButtonStyle.danger)
    async def registra(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label = "✅ Registrato nel Database"
        button.style = discord.ButtonStyle.success
        button.disabled = True
        await interaction.response.edit_message(view=self)

@bot.tree.command(name="sequestra", description="🚨 Sequestra un veicolo tramite targa")
@is_police_or_staff()
async def sequestra(interaction: discord.Interaction, targa: str, motivo: str):
    targa_up = targa.upper().strip()
    if targa_up not in targhe_veicoli:
        return await interaction.response.send_message("❌ Targa non trovata nel registro.", ephemeral=True)
    
    targhe_veicoli[targa_up]["stato"] = "Sequestrato"
    
    proprietario_id = int(targhe_veicoli[targa_up]["proprietario"])
    if proprietario_id in garage_veicoli:
        for v in garage_veicoli[proprietario_id]:
            if v["targa"] == targa_up:
                v["stato"] = "Sequestrato"
    
    await interaction.response.send_message(f"🚨 Veicolo con targa `[{targa_up}]` sequestrato.\n**Motivo:** {motivo}", view=RegistratoView())

@bot.tree.command(name="disequestra", description="🔓 Rimuove il sequestro da un veicolo")
@is_police_or_staff()
async def disequestra(interaction: discord.Interaction, targa: str):
    targa_up = targa.upper().strip()
    if targa_up not in targhe_veicoli:
        return await interaction.response.send_message("❌ Targa non trovata nel registro.", ephemeral=True)
    
    targhe_veicoli[targa_up]["stato"] = "Libero"
    
    proprietario_id = int(targhe_veicoli[targa_up]["proprietario"])
    if proprietario_id in garage_veicoli:
        for v in garage_veicoli[proprietario_id]:
            if v["targa"] == targa_up:
                v["stato"] = "Libero"
    
    await interaction.response.send_message(f"🔓 Veicolo con targa `[{targa_up}]` dissequestrato e restituito al proprietario.", view=RegistratoView())

@bot.tree.command(name="multa", description="📄 Emetti contravvenzione prelevando fondi")
@has_police_permission()
async def multa(interaction: discord.Interaction, cittadino: discord.Member, importo: int, motivo: str):
    if importo <= 0: return await interaction.response.send_message("❌ Inserisci un importo maggiore di zero.", ephemeral=True)
    if cittadino.id not in conti_bancari: return await interaction.response.send_message(f"❌ {cittadino.mention} non possiede un conto bancario attivo.", ephemeral=True)
    conti_bancari[cittadino.id] = max(0, conti_bancari[cittadino.id] - importo)
    await interaction.response.send_message(f"📄 **SANZIONE:** Multato {cittadino.mention} di **`{importo} €`**. Motivo: *`{motivo}`*", view=RegistratoView())

@bot.tree.command(name="arresta", description="🚨 Arresta un cittadino")
@app_commands.describe(
    utente="Il cittadino da arrestare",
    minuti="Durata della detenzione in minuti",
    motivo="Motivo dell'arresto",
    nome="Nome del detenuto",
    cognome="Cognome del detenuto",
    descrizione="Note aggiuntive sull'arresto",
    foto="Foto del fermo"
)
@has_police_permission()
async def arresta(
    interaction: discord.Interaction,
    utente: discord.Member,
    minuti: int,
    motivo: str,
    nome: str,
    cognome: str,
    descrizione: str,
    foto: discord.Attachment
):
    LIMITE_MASSIMO_MINUTI = 180
    if minuti <= 0: return await interaction.response.send_message("❌ Inserisci tempo valido.", ephemeral=True)
    if minuti > LIMITE_MASSIMO_MINUTI: return await interaction.response.send_message(f"❌ Massimo {LIMITE_MASSIMO_MINUTI} minuti.", ephemeral=True)
    prigione[utente.id] = minuti

    embed = discord.Embed(color=discord.Color.red())
    embed.description = (
        f"🚨 | **ARRESTO**\n\n"
        f"**AGENTE ➢**\n{interaction.user.mention}\n\n"
        f"**DETENUTO ➢**\n{utente.mention}\n\n"
        f"**NOME ➢**\n{nome} {cognome}\n\n"
        f"**DURATA ➢**\n{minuti} minuti\n\n"
        f"**ACCUSA ➢**\n{motivo}\n\n"
        f"**NOTE ➢**\n{descrizione}"
    )
    embed.set_image(url=foto.url)
    embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed, view=RegistratoView())
    await log_staff(interaction.guild, f"🚨 {interaction.user.mention} ha arrestato {utente.mention} per {minuti} min. Accusa: {motivo}", discord.Color.red())

    await asyncio.sleep(minuti * 60)
    if utente.id in prigione:
        del prigione[utente.id]
        try:
            embed_r = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed_r.description = f"🔓 | **RILASCIO**\n\n➢ {utente.mention} ha scontato la pena ed è stato rilasciato."
            await interaction.channel.send(embed=embed_r)
        except Exception: pass

@bot.tree.command(name="warn", description="⚠️ Avvertimento cittadino per infrazioni")
@has_police_permission()
async def warn(interaction: discord.Interaction, utente: discord.Member, motivo: str):
    if utente.id not in schedario_warn: schedario_warn[utente.id] = []
    schedario_warn[utente.id].append(motivo)
    totale = len(schedario_warn[utente.id])
    await interaction.response.send_message(f"⚠️ **WARN:** {utente.mention} è stato ammonito per: *{motivo}*. Totale warn: {totale}", view=RegistratoView())

@bot.tree.command(name="ricercato", description="🚨 Aggiungi o rimuovi un cittadino dalla lista dei ricercati")
@has_police_permission()
async def ricercato_toggle(interaction: discord.Interaction, utente: discord.Member, motivo: str = None):
    if utente.id in ricercati:
        ricercati.remove(utente.id)
        _salva_dati()
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
        embed.set_author(name="Eclipse City RP® — Polizia", icon_url=LOGO_SERVER)
        embed.set_thumbnail(url=utente.display_avatar.url)
        embed.description = (
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ **RICERCATO RIMOSSO**\n\n"
            f"**Cittadino →** {utente.mention}\n"
            f"**Agente →** {interaction.user.mention}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        embed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M"))
        await interaction.response.send_message(embed=embed, view=RegistratoView())
        await log_azione(interaction.guild, interaction.user, "✅ Ricercato Rimosso", utente.mention, discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)
    else:
        ricercati.add(utente.id)
        _salva_dati()
        embed = discord.Embed(color=discord.Color.red(), timestamp=datetime.now())
        embed.set_author(name="Eclipse City RP® — Polizia", icon_url=LOGO_SERVER)
        embed.set_thumbnail(url=utente.display_avatar.url)
        motivo_str = f"**Motivo →** {motivo}\n" if motivo else ""
        embed.description = (
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🚨 **RICERCATO**\n\n"
            f"**Cittadino →** {utente.mention}\n"
            f"**Agente →** {interaction.user.mention}\n"
            f"{motivo_str}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        embed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M"))
        await interaction.response.send_message(embed=embed, view=RegistratoView())
        await log_azione(interaction.guild, interaction.user, "🚨 Ricercato", f"{utente.mention} — {motivo or 'Nessun motivo'}", discord.Color.red(), canale_origine=interaction.channel)

# ==========================================
# 7. 💼 LAVORI E TURNI
# ==========================================

@bot.tree.command(name="servizio", description="🟢 Inizia il conteggio del turno per lo stipendio")
async def servizio_entra(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in conti_bancari:
        return await interaction.response.send_message("❌ **Conto non trovato:** Per iniziare il turno devi prima aprire un conto in banca con `/apriconto`.", ephemeral=True)
    turni_attivi[user_id] = datetime.now()
    lavoro = documenti_identita.get(user_id, {}).get("lavoro", "Cittadino")
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f"🟢 | **TURNO LAVORATIVO INIZIATO**\n\n"
        f"**CITTADINO ➢**\n{interaction.user.mention}\n\n"
        f"**LAVORO ➢**\n{lavoro.upper()}\n\n"
        f"**ORARIO/DATA ➢**\nOggi alle {datetime.now().strftime('%H:%M')}"
    )
    embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, "🟢 Entrato in servizio", f"Lavoro: {lavoro.upper()}", discord.Color.from_rgb(255, 107, 53))

class StipendioApprovaView(discord.ui.View):
    """View con bottoni Accetta/Rifiuta per approvazione stipendio da parte dello staff."""

    def __init__(self, lavoratore: discord.Member, guadagno: int, info_anagrafe: dict, ore: int, minuti_resto: int, stipendio_pieno: int):
        super().__init__(timeout=600)
        self.lavoratore = lavoratore
        self.guadagno = guadagno
        self.info_anagrafe = info_anagrafe
        self.ore = ore
        self.minuti_resto = minuti_resto
        self.stipendio_pieno = stipendio_pieno
        self.gestito = False

    def _is_staff(self, member: discord.Member) -> bool:
        if member.guild_permissions.administrator or member.guild_permissions.manage_messages:
            return True
        if _ha_ruolo_id(member, RUOLO_POLIZIA_ID):
            return True
        if _ha_ruolo(member, _KW_STAFF):
            return True
        return False

    @discord.ui.button(label="✅ ACCETTA STIPENDIO", style=discord.ButtonStyle.success, emoji="✅")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        membro_staff = await _get_member(interaction)
        if not self._is_staff(membro_staff):
            return await interaction.response.send_message("❌ Solo lo staff può approvare gli stipendi!", ephemeral=True)
        if self.gestito:
            return await interaction.response.send_message("❌ Questo stipendio è già stato gestito.", ephemeral=True)
        self.gestito = True
        uid = self.lavoratore.id
        if uid not in conti_bancari:
            conti_bancari[uid] = 0
        conti_bancari[uid] += self.guadagno
        _salva_dati()

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        embed = discord.Embed(title="✅ STIPENDIO APPROVATO", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
        embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
        embed.add_field(name="👤 Lavoratore", value=self.lavoratore.mention, inline=False)
        embed.add_field(name="💼 Lavoro", value=self.info_anagrafe.get("lavoro", "N/A").upper(), inline=True)
        embed.add_field(name="⏱️ Tempo", value=f"{self.ore}h {self.minuti_resto}min", inline=True)
        embed.add_field(name="💵 Accreditato", value=f"+{self.guadagno}$", inline=True)
        embed.add_field(name="✅ Approvato da", value=interaction.user.mention, inline=False)
        embed.set_footer(text="Fondi depositati sul conto Pacific Bank.")
        await interaction.response.send_message(embed=embed)
        await log_staff(interaction.guild, f"✅ {interaction.user.mention} ha approvato lo stipendio di {self.lavoratore.mention}: **+{self.guadagno}$**", discord.Color.from_rgb(255, 107, 53))
        await log_azione(interaction.guild, interaction.user, "💰 Stipendio approvato", f"{self.lavoratore.mention} → +{self.guadagno}$ | Lavoro: {self.info_anagrafe.get('lavoro','N/A').upper()}", discord.Color.from_rgb(255, 107, 53))

    @discord.ui.button(label="❌ RIFIUTA STIPENDIO", style=discord.ButtonStyle.danger, emoji="❌")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        membro_staff = await _get_member(interaction)
        if not self._is_staff(membro_staff):
            return await interaction.response.send_message("❌ Solo lo staff può rifiutare gli stipendi!", ephemeral=True)
        if self.gestito:
            return await interaction.response.send_message("❌ Questo stipendio è già stato gestito.", ephemeral=True)
        self.gestito = True

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        embed = discord.Embed(title="❌ STIPENDIO RIFIUTATO", color=discord.Color.red(), timestamp=datetime.now())
        embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
        embed.add_field(name="👤 Lavoratore", value=self.lavoratore.mention, inline=False)
        embed.add_field(name="💼 Lavoro", value=self.info_anagrafe.get("lavoro", "N/A").upper(), inline=True)
        embed.add_field(name="⏱️ Tempo", value=f"{self.ore}h {self.minuti_resto}min", inline=True)
        embed.add_field(name="💵 Stipendio (non erogato)", value=f"{self.guadagno}$", inline=True)
        embed.add_field(name="❌ Rifiutato da", value=interaction.user.mention, inline=False)
        embed.set_footer(text="Lo stipendio NON è stato accreditato.")
        await interaction.response.send_message(embed=embed)
        await log_staff(interaction.guild, f"❌ {interaction.user.mention} ha rifiutato lo stipendio di {self.lavoratore.mention} ({self.guadagno}$)", discord.Color.red())


@bot.tree.command(name="fuoriservizio", description="🔴 Stacca dal turno, calcola il tempo ed eroga i soldi in base al lavoro")
async def servizio_esci(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in turni_attivi:
        return await interaction.response.send_message("❌ **Turno non iniziato:** Non risulti in servizio attivo. Usa prima `/servizio`.", ephemeral=True)

    info_anagrafe = documenti_identita.get(user_id, {"lavoro": "cittadino"})
    nome_lavoro = info_anagrafe["lavoro"].lower()

    stipendio_pieno = 1000
    for chiave, stipendio in STIPENDI_LAVORO.items():
        if chiave in nome_lavoro:
            stipendio_pieno = stipendio
            break

    DURATA_TURNO_MINUTI = 120
    ora_inizio = turni_attivi[user_id]
    tempo_trascorso = datetime.now() - ora_inizio
    minuti_lavorati = max(1, int(tempo_trascorso.total_seconds() / 60))
    guadagno = round((minuti_lavorati / DURATA_TURNO_MINUTI) * stipendio_pieno)

    del turni_attivi[user_id]

    ore = minuti_lavorati // 60
    minuti_resto = minuti_lavorati % 60

    embed = discord.Embed(title="🔴 FINE TURNO — IN ATTESA DI APPROVAZIONE", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.add_field(name="👤 Lavoratore", value=interaction.user.mention, inline=False)
    embed.add_field(name="💼 Lavoro Registrato", value=info_anagrafe['lavoro'].upper(), inline=False)
    embed.add_field(name="⏱️ Tempo lavorato", value=f"{ore}h {minuti_resto}min", inline=True)
    embed.add_field(name="💰 Stipendio pieno (2h)", value=f"{stipendio_pieno}$", inline=True)
    embed.add_field(name="💵 Stipendio calcolato", value=f"**{guadagno}$**", inline=True)
    embed.set_footer(text="⏳ In attesa di approvazione da parte dello staff.")
    view = StipendioApprovaView(interaction.user, guadagno, info_anagrafe, ore, minuti_resto, stipendio_pieno)
    await interaction.response.send_message(embed=embed, view=view)
    await log_azione(interaction.guild, interaction.user, "🔴 Fine turno (in attesa)", f"Lavoro: {info_anagrafe['lavoro'].upper()} | Tempo: {ore}h {minuti_resto}min | Guadagno: {guadagno}$", discord.Color.from_rgb(255, 107, 53))

@bot.tree.command(name="apri-attivita", description="🟢 Comunica in chat IC che la tua attività è aperta")
@_blocca_se_dorme()
@app_commands.describe(lavoro="Scrivi il nome della tua attività")
async def apri_attivita(interaction: discord.Interaction, lavoro: str):
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f"🟢 | **ATTIVITÀ APERTA**\n\n"
        f"➢ **{lavoro}** è ora **APERTO** e pronto a servirvi!\n\n"
        f"👤 Responsabile ➢ {interaction.user.mention}"
    )
    embed.set_footer(
        text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.response.send_message("✅ Annuncio apertura inviato!", ephemeral=True)
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="chiudi-attivita", description="🔴 Comunica in chat IC che la tua attività è chiusa")
@_blocca_se_dorme()
@app_commands.describe(lavoro="Scrivi il nome della tua attività")
async def chiudi_attivita(interaction: discord.Interaction, lavoro: str):
    embed = discord.Embed(color=discord.Color.red())
    embed.description = (
        f"🔴 | **ATTIVITÀ CHIUSA**\n\n"
        f"➢ **{lavoro}** è ora **CHIUSO**.\n\n"
        f"👤 Responsabile ➢ {interaction.user.mention}"
    )
    embed.set_footer(
        text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.response.send_message("✅ Annuncio chiusura inviato!", ephemeral=True)
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="spaccia", description="🌿 Vendi droga a un cliente — con purezza casuale e trattativa")
@_blocca_se_dorme()
@app_commands.describe(
    tipo="Tipo di droga",
    quantita="Quantità in grammi"
)
@app_commands.choices(tipo=[
    app_commands.Choice(name="🌿 Marijuana", value="marijuana"),
    app_commands.Choice(name="💮 Cocaina", value="cocaina"),
    app_commands.Choice(name="❄️ Blue Crystal", value="crystal"),
])
async def spaccia(interaction: discord.Interaction, tipo: app_commands.Choice[str], quantita: int):
    if quantita <= 0:
        return await interaction.response.send_message("❌ Quantità non valida.", ephemeral=True)

    NOMI = {
        "marijuana": "🌿 Marijuana",
        "cocaina": "💮 Cocaina",
        "crystal": "❄️ Blue Crystal",
    }
    PREZZI_BASE = {
        "marijuana": 15,
        "cocaina": 100,
        "crystal": 100,
    }

    # Controlla che lo spacciatore abbia la droga nell'inventario
    inv = inventari.get(interaction.user.id, [])
    ha_droga = any(
        ("🌿" in item and tipo.value == "marijuana") or
        ("💮" in item and tipo.value == "cocaina") or
        ("❄️" in item and tipo.value == "crystal")
        for item in inv
    )
    if not ha_droga:
        return await interaction.response.send_message(
            f"❌ Non hai **{NOMI[tipo.value]}** nel tuo inventario.", ephemeral=True
        )

    # Purezza casuale 1-100%
    purezza = random.randint(1, 100)
    prezzo_grammo = PREZZI_BASE[tipo.value]
    prezzo_totale = prezzo_grammo * quantita

    # Icona purezza
    if purezza >= 80:
        icona_purezza = "🟢"
    elif purezza >= 50:
        icona_purezza = "🟡"
    elif purezza >= 25:
        icona_purezza = "🟠"
    else:
        icona_purezza = "🔴"

    frasi_pusher = [
        "Roba appena arrivata, non la trovi così in giro.",
        "Prezzo onesto per quello che è. Affare?",
        "Non fare il furbo fratè, il prezzo è quello.",
        "Hai 60 secondi, poi sparisco.",
        "Roba mia, personale. Puoi fidarti.",
    ]
    frase = random.choice(frasi_pusher)

    # Modal per l'offerta del cliente
    class ModalTrattativa(discord.ui.Modal, title="💬 Fai un'offerta"):
        offerta_input = discord.ui.TextInput(
            label="La tua offerta (prezzo totale in $)",
            style=discord.TextStyle.short,
            placeholder=f"Es: {int(prezzo_totale * 0.8)}",
            required=True,
            max_length=10
        )

        def __init__(self, view_ref):
            super().__init__()
            self.view_ref = view_ref

        async def on_submit(self, inter: discord.Interaction):
            try:
                offerta = int(self.offerta_input.value)
            except ValueError:
                return await inter.response.send_message("❌ Inserisci un numero valido.", ephemeral=True)

            if offerta <= 0:
                return await inter.response.send_message("❌ Offerta non valida.", ephemeral=True)

            # Disabilita i bottoni e aggiorna l'embed in attesa della risposta del venditore
            for child in self.view_ref.children:
                child.disabled = True
            await inter.response.edit_message(view=self.view_ref)

            # Notifica al venditore con bottoni accetta/rifiuta offerta
            class RispostaTrattativaView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)

                @discord.ui.button(label="✅ ACCETTO L'OFFERTA", style=discord.ButtonStyle.green)
                async def accetta_offerta(self, inter2: discord.Interaction, button2: discord.ui.Button):
                    if inter2.user.id != interaction.user.id:
                        return await inter2.response.send_message("❌ Solo lo spacciatore può rispondere.", ephemeral=True)

                    # Controlla inventario venditore
                    inv_venditore = inventari.get(interaction.user.id, [])
                    item_trovato = next((i for i in inv_venditore if NOMI[tipo.value].lower() in i.lower()), None)
                    if not item_trovato:
                        for c in self.children: c.disabled = True
                        embed_err = discord.Embed(color=discord.Color.red())
                        embed_err.description = f"❌ Non hai più **{NOMI[tipo.value]}** nell'inventario. Affare annullato."
                        return await inter2.response.edit_message(embed=embed_err, view=self)

                    saldo_cliente = portafogli.get(inter.user.id, 0)
                    if saldo_cliente < offerta:
                        for c in self.children: c.disabled = True
                        embed_err = discord.Embed(color=discord.Color.red())
                        embed_err.description = f"❌ {inter.user.mention} non ha abbastanza soldi per l'offerta di **{offerta}$**. Affare annullato."
                        return await inter2.response.edit_message(embed=embed_err, view=self)

                    portafogli[inter.user.id] = saldo_cliente - offerta
                    portafogli[interaction.user.id] = portafogli.get(interaction.user.id, 0) + offerta
                    inventari[interaction.user.id].remove(item_trovato)
                    if inter.user.id not in inventari:
                        inventari[inter.user.id] = []
                    inventari[inter.user.id].append(f"{NOMI[tipo.value]} x{quantita}g (purezza {purezza}%)")
                    _salva_dati()

                    for c in self.children: c.disabled = True
                    embed_ok = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                    embed_ok.description = (
                        f"✅ | **TRATTATIVA CONCLUSA**\n\n"
                        f"➢ {inter.user.mention} ha acquistato **{quantita}g di {NOMI[tipo.value]}** ({icona_purezza} purezza {purezza}%)\n"
                        f"➢ Prezzo trattato: **{offerta}$** → {interaction.user.mention}\n\n"
                        f"*Affare concluso dopo trattativa.*"
                    )
                    await inter2.response.edit_message(embed=embed_ok, view=self)

                @discord.ui.button(label="❌ RIFIUTO L'OFFERTA", style=discord.ButtonStyle.red)
                async def rifiuta_offerta(self, inter2: discord.Interaction, button2: discord.ui.Button):
                    if inter2.user.id != interaction.user.id:
                        return await inter2.response.send_message("❌ Solo lo spacciatore può rispondere.", ephemeral=True)
                    for c in self.children: c.disabled = True
                    embed_no = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                    embed_no.description = (
                        f"❌ | **OFFERTA RIFIUTATA**\n\n"
                        f"➢ {interaction.user.mention} ha rifiutato l'offerta di **{offerta}$** da {inter.user.mention}.\n"
                        f"*Il prezzo originale era **{prezzo_totale}$**.*"
                    )
                    await inter2.response.edit_message(embed=embed_no, view=self)

            embed_tratt = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed_tratt.description = (
                f"💬 | **OFFERTA IN ARRIVO**\n\n"
                f"➢ {inter.user.mention} offre **{offerta}$** per {quantita}g di {NOMI[tipo.value]}\n"
                f"➢ Prezzo originale: **{prezzo_totale}$**\n\n"
                f"{interaction.user.mention}, accetti questa offerta?"
            )
            await inter.followup.send(embed=embed_tratt, view=RispostaTrattativaView())

    # View principale con 3 bottoni
    class SpacciaView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=90)

        @discord.ui.button(label="✅ ACCETTO", style=discord.ButtonStyle.green)
        async def accetta(self, inter: discord.Interaction, button: discord.ui.Button):
            if inter.user.id == interaction.user.id:
                return await inter.response.send_message("❌ Non puoi accettare il tuo stesso affare.", ephemeral=True)

            inv_venditore = inventari.get(interaction.user.id, [])
            item_trovato = next((i for i in inv_venditore if NOMI[tipo.value].lower() in i.lower()), None)
            if not item_trovato:
                for c in self.children: c.disabled = True
                embed_err = discord.Embed(color=discord.Color.red())
                embed_err.description = f"❌ {interaction.user.mention} non ha più **{NOMI[tipo.value]}**. Affare annullato."
                return await inter.response.edit_message(embed=embed_err, view=self)

            saldo = portafogli.get(inter.user.id, 0)
            if saldo < prezzo_totale:
                return await inter.response.send_message(
                    f"❌ Non hai abbastanza soldi. Ti servono **{prezzo_totale}$**.", ephemeral=True
                )

            portafogli[inter.user.id] = saldo - prezzo_totale
            portafogli[interaction.user.id] = portafogli.get(interaction.user.id, 0) + prezzo_totale
            inventari[interaction.user.id].remove(item_trovato)
            if inter.user.id not in inventari:
                inventari[inter.user.id] = []
            inventari[inter.user.id].append(f"{NOMI[tipo.value]} x{quantita}g (purezza {purezza}%)")
            _salva_dati()

            for c in self.children: c.disabled = True
            embed_ok = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed_ok.description = (
                f"✅ | **AFFARE CONCLUSO**\n\n"
                f"➢ {inter.user.mention} ha acquistato **{quantita}g di {NOMI[tipo.value]}** ({icona_purezza} purezza {purezza}%)\n"
                f"➢ Pagati **{prezzo_totale}$** a {interaction.user.mention}\n\n"
                f"*La droga è stata aggiunta all'inventario del cliente.*"
            )
            await inter.response.edit_message(embed=embed_ok, view=self)

        @discord.ui.button(label="💬 TRATTA", style=discord.ButtonStyle.blurple)
        async def tratta(self, inter: discord.Interaction, button: discord.ui.Button):
            if inter.user.id == interaction.user.id:
                return await inter.response.send_message("❌ Non puoi trattare con te stesso.", ephemeral=True)
            await inter.response.send_modal(ModalTrattativa(self))

        @discord.ui.button(label="❌ RIFIUTO", style=discord.ButtonStyle.red)
        async def rifiuta(self, inter: discord.Interaction, button: discord.ui.Button):
            if inter.user.id == interaction.user.id:
                return await inter.response.send_message("❌ Non puoi rifiutare il tuo stesso affare.", ephemeral=True)
            for c in self.children: c.disabled = True
            embed_no = discord.Embed(color=discord.Color.red())
            embed_no.description = (
                f"❌ | **AFFARE RIFIUTATO**\n\n"
                f"➢ {inter.user.mention} ha rifiutato l'offerta di {interaction.user.mention}."
            )
            await inter.response.edit_message(embed=embed_no, view=self)

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name=f"🤝 {interaction.user.display_name} propone un affare", icon_url=interaction.user.display_avatar.url)
    embed.description = (
        f"*\"{frase}\"*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌿 **Sostanza ➢** {NOMI[tipo.value]}\n"
        f"⚖️ **Quantità ➢** {quantita}g\n"
        f"{icona_purezza} **Purezza ➢** {purezza}%\n"
        f"💵 **Prezzo al grammo ➢** {prezzo_grammo}$\n"
        f"💰 **Totale ➢** {prezzo_totale}$\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"*Puoi accettare, trattare il prezzo o rifiutare.*"
    )
    embed.set_footer(text="Hai 90 secondi per decidere.")

    view = SpacciaView()
    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="bdaperto", description="🟩 Apri i bandi della città")
@is_staff_or_direttore()
async def bdaperto(interaction: discord.Interaction):
    img = "https://cdn.discordapp.com/attachments/1532127388161544392/1534704553944027206/IMG_3349.png?ex=6a790cff&is=6a77bb7f&hm=cbc74dc1e122f8a3fc23979a681435cc426cb1d64b9795d3b5eb2fbc66ed61e5&"
    embed = discord.Embed(title="🟩 |BANDO APERTO", color=discord.Color.from_rgb(255, 107, 53))
    embed.set_image(url=img)
    
    await interaction.response.send_message("✅ Bando aperto inviato!", ephemeral=True)
    await interaction.channel.send(content="@everyone", embed=embed)

@bot.tree.command(name="bdchiuso", description="🛑 Chiudi i bandi della città")
@is_staff_or_direttore()
async def bdchiuso(interaction: discord.Interaction):
    img_chiuso = "https://cdn.discordapp.com/attachments/1532127388161544392/1534704553944027206/IMG_3349.png?ex=6a790cff&is=6a77bb7f&hm=cbc74dc1e122f8a3fc23979a681435cc426cb1d64b9795d3b5eb2fbc66ed61e5&"
    embed = discord.Embed(title="🟥 | BANDO CHIUSO", color=discord.Color.red())
    embed.set_image(url=img_chiuso)
    await interaction.response.send_message("✅ Bando chiuso inviato!", ephemeral=True)
    await interaction.channel.send(content="@everyone", embed=embed)

@bot.tree.command(name="rapina", description="💣 Segnala una rapina in corso")
@_blocca_se_dorme()
async def rapina(interaction: discord.Interaction):
    TIPI_RAPINA = [
        discord.SelectOption(label="Negozietto", emoji="🏪"),
        discord.SelectOption(label="ATM", emoji="💳"),
        discord.SelectOption(label="Pacific Bank", emoji="🏛️"),
        discord.SelectOption(label="Ponsoboys", emoji="🍔"),
        discord.SelectOption(label="Farmacia", emoji="💊"),
    ]

    class RapinaSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="Seleziona tipo di rapina...", options=TIPI_RAPINA)

        async def callback(self, inter: discord.Interaction):
            tipo = self.values[0]
            for child in self.view.children:
                child.disabled = True
            await inter.response.edit_message(view=self.view)

            embed = discord.Embed(color=discord.Color.red())
            embed.description = (
                "🔫 | **RAPINA IN CORSO**\n\n"
                "Attenzione é appena scattata una rapina, lontani dalla zona "
                "sennò possono scambiarvi per rapinatori e arrestarvi, la polizia sta arrivando. "
                "Mantenete la calma e scappate dalla zona.\n\n"
                f"**POSIZIONE ➢**\n{inter.user.mention}\n\n"
                f"**TIPO DI RAPINA ➢**\n{tipo}"
            )
            embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")

            canale_pd = discord.utils.get(inter.guild.text_channels, name="radio-pd")
            target = canale_pd if canale_pd else inter.channel
            await target.send(content="@everyone", embed=embed)
            await log_staff(inter.guild, f"🔫 {inter.user.mention} ha avviato una rapina: **{tipo}**", discord.Color.red())
            await log_azione(inter.guild, inter.user, "🔫 Rapina avviata", f"Tipo: **{tipo}**", discord.Color.red())

    class RapinaView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.add_item(RapinaSelect())

    embed_sel = discord.Embed(color=discord.Color.red())
    embed_sel.description = "🔫 | **RAPINA**\n\n➢ Seleziona il tipo di rapina dal menu qui sotto."
    await interaction.response.send_message(embed=embed_sel, view=RapinaView(), ephemeral=True)


# ==========================================
# 8. 📜 SISTEMA ITEM E VENDITA
# ==========================================

@bot.tree.command(name="item-use", description="💊 Utilizza un oggetto dal tuo inventario o zaino")
@_blocca_se_dorme()
async def item_use(interaction: discord.Interaction, oggetto: str):
    inv = inventari.get(interaction.user.id, [])
    zai = zaini.get(interaction.user.id, [])
    
    if oggetto in inv:
        inv.remove(oggetto)
        await interaction.response.send_message(f"✅ Hai utilizzato: **{oggetto}** dall'inventario.", ephemeral=True)
    elif oggetto in zai:
        zai.remove(oggetto)
        await interaction.response.send_message(f"✅ Hai utilizzato: **{oggetto}** dallo zaino.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Oggetto **{oggetto}** non trovato nei tuoi averi.", ephemeral=True)

@item_use.autocomplete("oggetto")
async def item_use_autocomplete(interaction: discord.Interaction, current: str):
    uid = interaction.user.id
    tutti_oggetti = list(set(inventari.get(uid, []) + zaini.get(uid, [])))
    return [app_commands.Choice(name=o, value=o) for o in tutti_oggetti if current.lower() in o.lower()][:25]

CATEGORIE_NEGOZIO = ["Armi", "Cibo", "Droga", "Medicina", "Veicoli", "Abbigliamento", "Elettronica", "Generale"]


# ==========================================
# 📦 ITEM VIEW — Pannello staff completo
# ==========================================

# Emoji e colori per categoria
CATEGORIA_STILE = {
    "Armi":                {"emoji": "🔫", "colore": discord.Color.red()},
    "Armi da Mischia":     {"emoji": "⚔️",  "colore": discord.Color.from_rgb(180, 60, 60)},
    "Pistole":             {"emoji": "🔫", "colore": discord.Color.from_rgb(200, 50, 50)},
    "Mitra":               {"emoji": "💨", "colore": discord.Color.from_rgb(160, 40, 40)},
    "Fucili d'Assalto":    {"emoji": "🪖", "colore": discord.Color.from_rgb(140, 30, 30)},
    "Fucili a Pompa":      {"emoji": "💣", "colore": discord.Color.from_rgb(120, 20, 20)},
    "Cibo":                {"emoji": "🍽️", "colore": discord.Color.from_rgb(255, 107, 53)},
    "Droga":               {"emoji": "🌿", "colore": discord.Color.from_rgb(255, 107, 53)},
    "Medicina":            {"emoji": "💊", "colore": discord.Color.from_rgb(255, 107, 53)},
    "Veicoli":             {"emoji": "🚗", "colore": discord.Color.from_rgb(255, 107, 53)},
    "Abbigliamento":       {"emoji": "👕", "colore": discord.Color.from_rgb(255, 107, 53)},
    "Elettronica":         {"emoji": "📱", "colore": discord.Color.from_rgb(255, 107, 53)},
    "Generale":            {"emoji": "📦", "colore": discord.Color.from_rgb(255, 107, 53)},
    # Categorie supermarket
    "🕵️ Investigazione": {"emoji": "🕵️", "colore": discord.Color.from_rgb(100, 100, 120)},
    "💰 Finanze Oscure":  {"emoji": "💰", "colore": discord.Color.from_rgb(180, 140, 20)},
    "🩸 Interrogatori":   {"emoji": "🩸", "colore": discord.Color.from_rgb(160, 30, 30)},
}

def _get_cat_emoji(categoria: str) -> str:
    return CATEGORIA_STILE.get(categoria, {}).get("emoji", "📦")

def _get_cat_colore(categoria: str) -> discord.Color:
    return CATEGORIA_STILE.get(categoria, {}).get("colore", discord.Color.from_rgb(255, 107, 53))


class ItemViewCategoriaPagina(discord.ui.View):
    """Pagina item di una categoria specifica — con paginazione e bottone Aggiungi."""
    PAGE_SIZE = 5

    def __init__(self, categoria: str, items: list, staff: discord.Member, pagina: int = 0):
        super().__init__(timeout=120)
        self.categoria = categoria
        self.items = items        # lista di (nome, dati)
        self.staff = staff
        self.pagina = pagina
        self.max_pagine = max(1, -(-len(items) // self.PAGE_SIZE))  # ceil division
        self._aggiorna_bottoni()

    def _aggiorna_bottoni(self):
        self.clear_items()
        # ← Precedente
        btn_prec = discord.ui.Button(
            label="◀ Precedente", style=discord.ButtonStyle.secondary,
            disabled=(self.pagina == 0), custom_id="prec"
        )
        btn_prec.callback = self.prec_callback
        self.add_item(btn_prec)
        # → Successivo
        btn_succ = discord.ui.Button(
            label="Successivo ▶", style=discord.ButtonStyle.secondary,
            disabled=(self.pagina >= self.max_pagine - 1), custom_id="succ"
        )
        btn_succ.callback = self.succ_callback
        self.add_item(btn_succ)
        # ➕ Aggiungi item a utente
        btn_add = discord.ui.Button(
            label="➕ Aggiungi Item a Utente", style=discord.ButtonStyle.success, custom_id="add"
        )
        btn_add.callback = self.add_callback
        self.add_item(btn_add)
        # 🗑️ Elimina item
        btn_del = discord.ui.Button(
            label="🗑️ Elimina Item", style=discord.ButtonStyle.danger, custom_id="del"
        )
        btn_del.callback = self.del_callback
        self.add_item(btn_del)
        # 🔙 Torna alle categorie
        btn_back = discord.ui.Button(
            label="🔙 Categorie", style=discord.ButtonStyle.primary, custom_id="back"
        )
        btn_back.callback = self.back_callback
        self.add_item(btn_back)

    def _build_embed(self) -> discord.Embed:
        emoji = _get_cat_emoji(self.categoria)
        colore = _get_cat_colore(self.categoria)
        embed = discord.Embed(color=colore, timestamp=datetime.now())
        embed.set_author(name=f"{emoji} ITEM VIEW — {self.categoria.upper()}", icon_url=LOGO_SERVER)

        start = self.pagina * self.PAGE_SIZE
        slice_ = self.items[start: start + self.PAGE_SIZE]

        if not slice_:
            embed.description = "❌ Nessun item in questa categoria."
            return embed

        righe = []
        for nome, dati in slice_:
            cat_e = _get_cat_emoji(dati.get("categoria", "Generale"))
            vendibile = "✅ Vendibile" if dati.get("vendibile") else "🔒 Non vendibile"
            prezzo = dati.get("prezzo", 0)
            qty = dati.get("quantita", 0)
            peso = PESI_OGGETTI.get(nome, 0.2)
            desc_breve = dati.get("descrizione", "—")[:60]
            riga = (
                f"{cat_e} **{nome}**\n"
                f"┣ 💰 Prezzo: `{prezzo}$`  |  📦 Stock: `{qty}`  |  ⚖️ Peso: `{peso} kg`\n"
                f"┣ {vendibile}\n"
                f"┗ 📝 _{desc_breve}_"
            )
            righe.append(riga)

        embed.description = "\n\n".join(righe)


        embed.set_footer(text=f"Pagina {self.pagina+1}/{self.max_pagine} • Totale: {len(self.items)} item")
        return embed

    async def prec_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        self.pagina -= 1
        self._aggiorna_bottoni()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    async def succ_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        self.pagina += 1
        self._aggiorna_bottoni()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    async def back_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        view = ItemViewHomeView(self.staff)
        await interaction.response.edit_message(embed=view.build_embed(), view=view)

    async def add_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        # Mostra select per scegliere l'item da questa categoria
        nomi_pag = [nome for nome, _ in self.items][:25]
        opzioni = [discord.SelectOption(label=n[:100], value=n, emoji=_get_cat_emoji(self.categoria)) for n in nomi_pag]

        class SceltaItemSelect(discord.ui.Select):
            def __init__(self_inner):
                super().__init__(placeholder="📦 Scegli item da dare...", options=opzioni)
            async def callback(self_inner, inter: discord.Interaction):
                item_scelto = self_inner.values[0]
                await inter.response.send_modal(ModalDaiItem(item_scelto, interaction.user))

        class SceltaItemView(discord.ui.View):
            def __init__(self_inner):
                super().__init__(timeout=60)
                self_inner.add_item(SceltaItemSelect())

        await interaction.response.send_message(
            f"📦 **Seleziona l'item da dare al cittadino:**",
            view=SceltaItemView(), ephemeral=True
        )

    async def del_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.staff.id:
            return await interaction.response.send_message("❌ Non autorizzato.", ephemeral=True)
        nomi_pag = [nome for nome, _ in self.items][:25]
        opzioni = [discord.SelectOption(label=n[:100], value=n, emoji="🗑️") for n in nomi_pag]

        class EliminaSelect(discord.ui.Select):
            def __init__(self_inner):
                super().__init__(placeholder="🗑️ Scegli item da eliminare...", options=opzioni)
            async def callback(self_inner, inter: discord.Interaction):
                nome_el = self_inner.values[0]
                if nome_el in oggetti_creati:
                    del oggetti_creati[nome_el]
                    _salva_dati()
                    await log_staff(inter.guild, f"🗑️ {inter.user.mention} ha eliminato l'item **{nome_el}**.", discord.Color.red())
                    await inter.response.send_message(f"🗑️ Item **{nome_el}** eliminato con successo.", ephemeral=True)
                else:
                    await inter.response.send_message("❌ Item non trovato.", ephemeral=True)

        class EliminaView(discord.ui.View):
            def __init__(self_inner):
                super().__init__(timeout=60)
                self_inner.add_item(EliminaSelect())

        await interaction.response.send_message("🗑️ **Seleziona l'item da eliminare:**", view=EliminaView(), ephemeral=True)


class ModalDaiItem(discord.ui.Modal, title="➕ Dai Item a Cittadino"):
    utente_nome = discord.ui.TextInput(
        label="Nome Discord del cittadino",
        style=discord.TextStyle.short,
        placeholder="Es: Mario123  (oppure incolla l'ID numerico)",
        required=True,
        max_length=100
    )
    quantita_input = discord.ui.TextInput(
        label="Quantità",
        style=discord.TextStyle.short,
        placeholder="Es: 1",
        required=True,
        max_length=4,
        default="1"
    )

    def __init__(self, item_nome: str, staff: discord.Member):
        super().__init__()
        self.item_nome = item_nome
        self.staff = staff

    async def on_submit(self, interaction: discord.Interaction):
        valore = self.utente_nome.value.strip()
        qty_str = self.quantita_input.value.strip()

        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Quantità non valida.", ephemeral=True)

        # Cerca prima per ID numerico, poi per nome/display_name
        membro = None
        if valore.isdigit():
            uid_try = int(valore)
            membro = interaction.guild.get_member(uid_try)
            if membro is None:
                try:
                    membro = await interaction.guild.fetch_member(uid_try)
                except Exception:
                    pass
        if membro is None:
            valore_lower = valore.lower()
            membro = discord.utils.find(
                lambda m: m.name.lower() == valore_lower or m.display_name.lower() == valore_lower,
                interaction.guild.members
            )
        if membro is None:
            return await interaction.response.send_message(
                f"❌ Nessun membro trovato con il nome **{valore}**.\n"
                "Controlla il nome esatto oppure usa l'ID numerico.",
                ephemeral=True
            )

        uid = membro.id
        peso_item = PESI_OGGETTI.get(self.item_nome, 0.2) * qty
        peso_attuale = _calcola_peso_inventario(uid)
        if peso_attuale + peso_item > PESO_MAX_INVENTARIO:
            return await interaction.response.send_message(
                f"⚠️ Inventario troppo pesante! Peso: **{peso_attuale} kg** + **{peso_item} kg** > **{PESO_MAX_INVENTARIO} kg**",
                ephemeral=True
            )

        if uid not in inventari:
            inventari[uid] = []
        for _ in range(qty):
            inventari[uid].append(self.item_nome)
        _salva_dati()

        emoji = _get_cat_emoji(oggetti_creati.get(self.item_nome, {}).get("categoria", "Generale"))
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
        embed.set_author(name="📦 ITEM ASSEGNATO", icon_url=LOGO_SERVER)
        desc_msg = (
            f"{emoji} **{self.item_nome}**\n\n"
            f"**Cittadino ➢** {membro.mention}\n"
            f"**Quantità ➢** `{qty}`\n"
            f"**Peso aggiunto ➢** `{peso_item} kg`\n"
            f"**Staff ➢** {interaction.user.mention}"
        )
        embed.description = desc_msg
        embed.set_thumbnail(url=membro.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        await log_staff(interaction.guild, f"📦 {interaction.user.mention} ha dato **{self.item_nome}** x{qty} a {membro.mention}.", discord.Color.from_rgb(255, 107, 53))
        await log_azione(interaction.guild, interaction.user, "📦 Item dato via Item View", f"**{self.item_nome}** x{qty} → {membro.mention}", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


class ModalCreaItem(discord.ui.Modal, title="📦 Crea Nuovo Item"):
    nome_item = discord.ui.TextInput(
        label="Nome dell'item",
        style=discord.TextStyle.short,
        placeholder="Es: Coltello a Serramanico",
        required=True,
        max_length=80
    )
    descrizione_item = discord.ui.TextInput(
        label="Descrizione",
        style=discord.TextStyle.paragraph,
        placeholder="Breve descrizione dell'oggetto",
        required=True,
        max_length=200
    )
    categoria_item = discord.ui.TextInput(
        label="Categoria",
        style=discord.TextStyle.short,
        placeholder="Armi / Cibo / Droga / Medicina / Veicoli / Abbigliamento / Elettronica / Generale",
        required=True,
        max_length=30
    )
    prezzo_item = discord.ui.TextInput(
        label="Prezzo ($)",
        style=discord.TextStyle.short,
        placeholder="Es: 500",
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        nome_k = self.nome_item.value.strip()
        cat = self.categoria_item.value.strip()
        desc = self.descrizione_item.value.strip()

        # Valida categoria
        categorie_valide = ["Armi", "Cibo", "Droga", "Medicina", "Veicoli", "Abbigliamento", "Elettronica", "Generale"]
        if cat not in categorie_valide:
            cat = "Generale"

        # Valida prezzo
        try:
            prezzo = int(self.prezzo_item.value.strip())
            if prezzo < 0:
                raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Prezzo non valido. Inserisci un numero intero positivo.", ephemeral=True)

        if nome_k in oggetti_creati:
            return await interaction.response.send_message(f"❌ L'item **{nome_k}** esiste già.", ephemeral=True)

        oggetti_creati[nome_k] = {
            "nome": nome_k,
            "quantita": 999,
            "prezzo": prezzo,
            "vendibile": True,
            "descrizione": desc,
            "categoria": cat,
            "ruolo_richiesto": None
        }
        _salva_dati()

        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
        embed.set_author(name="📦 NUOVO ITEM CREATO", icon_url=LOGO_SERVER)
        embed.description = (
            f"**Nome ➢** {nome_k}\n\n"
            f"**Categoria ➢** {cat}\n\n"
            f"**Prezzo ➢** {prezzo}$\n\n"
            f"**Descrizione ➢** {desc}"
        )
        embed.set_footer(text=f"Creato da {interaction.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_staff(interaction.guild, f"📦 {interaction.user.mention} ha creato l'item **{nome_k}** ({cat}) a {prezzo}$.", discord.Color.from_rgb(255, 107, 53))
        await log_azione(interaction.guild, interaction.user, "📦 Item creato", f"Nome: **{nome_k}** | Categoria: {cat} | Prezzo: {prezzo}$", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


class ItemViewHomeView(discord.ui.View):
    """Home del pannello Item View: mostra categorie con select."""
    def __init__(self, staff: discord.Member):
        super().__init__(timeout=120)
        self.staff = staff
        # Raggruppa per categoria
        self.categorie: dict[str, list] = {}
        for nome, dati in oggetti_creati.items():
            cat = dati.get("categoria", "Generale")
            self.categorie.setdefault(cat, []).append((nome, dati))

        if not self.categorie:
            return

        opzioni = []
        for cat, items in self.categorie.items():
            emoji = _get_cat_emoji(cat)
            opzioni.append(discord.SelectOption(
                label=f"{cat}  ({len(items)} item)",
                value=cat,
                emoji=emoji,
                description=f"{len(items)} oggetti registrati"
            ))

        select = discord.ui.Select(placeholder="📂 Seleziona categoria...", options=opzioni[:25])

        async def select_callback(inter: discord.Interaction):
            if inter.user.id != self.staff.id:
                return await inter.response.send_message("❌ Non autorizzato.", ephemeral=True)
            cat_scelta = select.values[0]
            items_cat = self.categorie.get(cat_scelta, [])
            pag_view = ItemViewCategoriaPagina(cat_scelta, items_cat, self.staff)
            await inter.response.edit_message(embed=pag_view._build_embed(), view=pag_view)

        select.callback = select_callback
        self.add_item(select)

        # ➕ Bottone Crea Nuovo Item
        btn_crea = discord.ui.Button(
            label="➕ Crea Nuovo Item", style=discord.ButtonStyle.success, custom_id="iv_crea_item", row=1
        )
        async def btn_crea_callback(inter: discord.Interaction):
            if inter.user.id != self.staff.id:
                return await inter.response.send_message("❌ Non autorizzato.", ephemeral=True)
            await inter.response.send_modal(ModalCreaItem())
        btn_crea.callback = btn_crea_callback
        self.add_item(btn_crea)

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
        embed.set_author(name="🗃️ ITEM VIEW — PANNELLO STAFF", icon_url=LOGO_SERVER)

        totale_item = len(oggetti_creati)
        totale_stock = sum(d.get("quantita", 0) for d in oggetti_creati.values())

        righe = []
        for cat, items in self.categorie.items():
            emoji = _get_cat_emoji(cat)
            nomi_brevi = ", ".join(n[:20] for n, _ in items[:3])
            if len(items) > 3:
                nomi_brevi += f" +{len(items)-3} altri"
            riga_cat = f"{emoji} **{cat}** — `{len(items)} item`\n┗ _{nomi_brevi}_"
            righe.append(riga_cat)

        corpo = "\n\n".join(righe)
        embed.description = (
            f"📊 **Riepilogo Database Item**\n"
            f"┣ 🗂️ Categorie: `{len(self.categorie)}`\n"
            f"┣ 📦 Item totali: `{totale_item}`\n"
            f"┗ 🔢 Stock totale: `{totale_stock}`\n\n"
            "━" * 24 + "\n\n"
            + corpo
        )
        embed.set_footer(text="Seleziona una categoria dal menu per gestire gli item")
        return embed


@bot.tree.command(name="item-view", description="🗃️ Pannello staff: visualizza e gestisci tutti gli item del server")
@is_staff_or_direttore()
async def item_view(interaction: discord.Interaction):
    view = ItemViewHomeView(interaction.user)
    embed = view.build_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)



class ItemSellView(discord.ui.View):
    def __init__(self, venditore_id: int, compratore_id: int, item: str, prezzo: int):
        super().__init__(timeout=300)
        self.venditore_id = venditore_id
        self.compratore_id = compratore_id
        self.item = item
        self.prezzo = prezzo

    @discord.ui.button(label="✅ ACCETTA", style=discord.ButtonStyle.green)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.compratore_id:
            return await interaction.response.send_message("❌ Non sei tu il destinatario.", ephemeral=True)
        saldo = portafogli.get(self.compratore_id, 0)
        if saldo < self.prezzo:
            return await interaction.response.send_message(f"❌ Non hai abbastanza soldi. Ti servono **{self.prezzo}$**.", ephemeral=True)
        inv_vend = inventari.get(self.venditore_id, [])
        zai_vend = zaini.get(self.venditore_id, [])
        if self.item in inv_vend:
            inv_vend.remove(self.item)
        elif self.item in zai_vend:
            zai_vend.remove(self.item)
        else:
            return await interaction.response.send_message("❌ Il venditore non ha più questo oggetto.", ephemeral=True)
        portafogli[self.compratore_id] = saldo - self.prezzo
        portafogli[self.venditore_id] = portafogli.get(self.venditore_id, 0) + self.prezzo
        if self.compratore_id not in inventari: inventari[self.compratore_id] = []
        inventari[self.compratore_id].append(self.item)
        _salva_dati()
        for child in self.children: child.disabled = True
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.description = f"✅ Vendita completata! **{self.item}** trasferito per **{self.prezzo}$**."
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ RIFIUTA", style=discord.ButtonStyle.red)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.compratore_id:
            return await interaction.response.send_message("❌ Non sei tu il destinatario.", ephemeral=True)
        for child in self.children: child.disabled = True
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Vendita rifiutata."
        await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name="item-sell", description="🤝 Vendi un oggetto dal tuo inventario a un cittadino")
@_blocca_se_dorme()
@app_commands.describe(member="Il cittadino a cui vuoi vendere", item="Oggetto da vendere", price="Prezzo in $")
async def item_sell(interaction: discord.Interaction, member: discord.Member, item: str, price: int):
    if price < 0: return await interaction.response.send_message("❌ Prezzo non valido.", ephemeral=True)
    if interaction.user.id == member.id: return await interaction.response.send_message("❌ Non puoi vendere a te stesso.", ephemeral=True)
    
    uid = interaction.user.id
    if item not in inventari.get(uid, []) and item not in zaini.get(uid, []):
        return await interaction.response.send_message("❌ Non possiedi questo oggetto nel tuo inventario o zaino.", ephemeral=True)
        
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = f"{interaction.user.mention} wants to sell you 1 **{item}** for 💳{price}\n\n**5 minutes to respond**"
    
    view = ItemSellView(interaction.user.id, member.id, item, price)
    await interaction.response.send_message(content=member.mention, embed=embed, view=view)

@item_sell.autocomplete("item")
async def item_sell_autocomplete(interaction: discord.Interaction, current: str):
    uid = interaction.user.id
    tutti_oggetti = list(set(inventari.get(uid, []) + zaini.get(uid, [])))
    return [app_commands.Choice(name=o, value=o) for o in tutti_oggetti if current.lower() in o.lower()][:25]

# ==========================================
# 9. 📜 COMANDI RP GENERALI & INTERAZIONI
# ==========================================

@bot.tree.command(name="post-instagram", description="📸 Pubblica un post su Instagram")
@_blocca_se_dorme()
@app_commands.describe(testo="Il testo del tuo post", foto="Immagine da allegare (opzionale)")
async def post_instagram(interaction: discord.Interaction, testo: str, foto: discord.Attachment = None):
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        "**📱 POST INSTAGRAM 📱**\n\n"
        f"**CITTADINO ➢** {interaction.user.mention}\n\n"
        f"**POST ➢** *{testo}*"
    )
    if foto:
        embed.set_image(url=foto.url)
    
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, "📸 Post Instagram", f"Testo: {testo[:80]}", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)

@bot.tree.command(name="fattura", description="🧾 Emetti una fattura a un cliente")
async def fattura(interaction: discord.Interaction, dipendente: discord.Member, cliente: str, oggetto_acquistato: str, importo: str):
    EMOJI_MONEY = "💰"   
    EMOJI_FRECCIA = "➢"
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    embed.description = (
        f"{EMOJI_MONEY} **Fattura** {EMOJI_MONEY}\n\n"
        f"**Dipendente {EMOJI_FRECCIA}**\n{dipendente.mention}\n\n"
        f"**Cliente {EMOJI_FRECCIA}**\n{cliente}\n\n"
        f"**Oggetto acquistato {EMOJI_FRECCIA}**\n{oggetto_acquistato}\n\n"
        f"**Importo {EMOJI_FRECCIA}**\n{importo}$"
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="fascicolo-medico", description="🩺 Visualizza il tuo fascicolo medico")
async def fascicolo_medico(interaction: discord.Interaction):
    user_id = interaction.user.id
    dati = fascicoli_medici.get(user_id)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="Eclipse City RP®", icon_url=LOGO_SERVER)
    if not dati: embed.description = "🩺 | **Fascicolo Medico**\n\n✅ Nessun precedente medico registrato. Cartella clinica pulita."
    else: embed.description = f"🩺 | **Fascicolo Medico**\n\n**Cittadino ➢**\n{interaction.user.mention}\n\n**Diagnosi/Interventi ➢**\n{dati.get('note', 'N/A')}\n\n**Ultimo aggiornamento ➢**\n{dati.get('data', 'N/A')}"
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="me", description="🎭 Descrivi un'azione del tuo personaggio")
@_blocca_se_dorme()
async def me(interaction: discord.Interaction, azione: str):
    embed = discord.Embed(color=0x00ffff) 
    embed.set_author(name="🎬 AZIONE RP 💬")
    embed.description = f"{interaction.user.mention} ➢ *{azione}*"
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, "🎭 Azione RP /me", f"{azione[:100]}", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


@bot.tree.command(name="messaggio", description="✉️ Invia un messaggio privato IC (in game)")
@_blocca_se_dorme()
async def messaggio_privato(interaction: discord.Interaction, utente: discord.Member, messaggio: str):
    ultimi_mittenti_pm[utente.id] = interaction.user.id
    try:
        await utente.send(f"💌 **Messaggio Privato (IC) da {interaction.user.display_name}:** {messaggio}")
        await interaction.response.send_message(f"✅ Messaggio privato inviato a {utente.display_name}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ Impossibile inviare il messaggio. L'utente ha i DM chiusi.", ephemeral=True)

@bot.tree.command(name="rispondi", description="↩️ Rispondi all'ultimo messaggio privato ricevuto")
@_blocca_se_dorme()
async def rispondi(interaction: discord.Interaction, messaggio: str):
    mittente_id = ultimi_mittenti_pm.get(interaction.user.id)
    if not mittente_id: return await interaction.response.send_message("❌ Nessun mittente a cui rispondere.", ephemeral=True)
    mittente = interaction.guild.get_member(mittente_id)
    if mittente:
        try:
            await mittente.send(f"↩️ **Risposta da {interaction.user.display_name}:** {messaggio}")
            await interaction.response.send_message("✅ Risposta inviata.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Impossibile inviare la risposta. L'utente ha i DM chiusi.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Utente non più nel server.", ephemeral=True)

@bot.tree.command(name="segnala", description="🛠️ Segnala un problema o un giocatore allo staff")
async def segnala(interaction: discord.Interaction, giocatore: discord.Member, motivo: str):
    canale_supporto = discord.utils.get(interaction.guild.text_channels, name="segnalazioni")
    if canale_supporto:
        await canale_supporto.send(f"🚨 **SEGNALAZIONE STAFF** da {interaction.user.mention} su {giocatore.mention} per: *{motivo}*")
    await interaction.response.send_message("🛠️ Segnalazione inviata allo staff con successo.", ephemeral=True)

# ==========================================
# 9.1 📱 TELEFONO E INVENTARI (Visualizzazione)
# ==========================================

@bot.tree.command(name="portafoglio", description="💳 Controlla i documenti e i contanti nel portafoglio")
@_blocca_se_dorme()
async def portafoglio(interaction: discord.Interaction):
    soldi = portafogli.get(interaction.user.id, 0)
    uid = interaction.user.id

    class PortafoglioSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="DOCUMENTO", description="Vedi il tuo documento", emoji="\U0001faaa"),
                discord.SelectOption(label="PATENTE", description="Vedi la tua patente", emoji="\U0001f4cb"),
                discord.SelectOption(label="PORTO D'ARMI", description="Vedi il tuo porto d'armi", emoji="\U0001f52b"),
                discord.SelectOption(label="FASCICOLO MEDICO", description="Vedi il tuo fascicolo medico", emoji="\U0001fa7a"),
            ]
            super().__init__(placeholder="Seleziona", options=options)

        async def callback(self, inter: discord.Interaction):
            scelta = self.values[0]
            if scelta == "DOCUMENTO":
                if uid not in documenti_identita:
                    return await inter.response.send_message("\u274c Nessun documento registrato.", ephemeral=True)
                dati = documenti_identita[uid]
                embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                embed.description = (
                    f"\U0001f4c4 | **DOCUMENTO D'IDENTIT\u00c0**\n\n"
                    f"**Nome:**\n\u27a2 *{dati.get('nome','N/A')}*\n\n"
                    f"**Cognome:**\n\u27a2 *{dati.get('cognome','N/A')}*\n\n"
                    f"**Et\u00e0:**\n\u27a2 *{dati.get('eta','N/A')}*\n\n"
                    f"**Nazionalit\u00e0:**\n\u27a2 *{dati.get('nazionalita','N/A')}*\n\n"
                    f"**Sesso:**\n\u27a2 *{dati.get('sesso','N/A')}*"
                )
                if dati.get('foto_url'): embed.set_image(url=dati['foto_url'])
                await inter.response.send_message(embed=embed, ephemeral=True)
            elif scelta == "PATENTE":
                patenti_utente = patenti.get(uid, [])
                if not patenti_utente:
                    return await inter.response.send_message("\u274c Nessuna patente registrata.", ephemeral=True)
                embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                embed.description = "\U0001f4cb | **PATENTE**\n\n" + "\n".join([f"\u27a2 {p}" for p in patenti_utente])
                await inter.response.send_message(embed=embed, ephemeral=True)
            elif scelta == "PORTO D'ARMI":
                porto_utente = porto_darmi.get(uid, [])
                if not porto_utente:
                    return await inter.response.send_message("\u274c Nessun porto d'armi registrato.", ephemeral=True)
                embed = discord.Embed(color=discord.Color.from_rgb(200, 50, 50))
                embed.description = "\U0001f52b | **PORTO D'ARMI**\n\n" + "\n".join([f"\u27a2 {p}" for p in porto_utente])
                await inter.response.send_message(embed=embed, ephemeral=True)
            elif scelta == "FASCICOLO MEDICO":
                dati_med = fascicoli_medici.get(uid, {})
                if not dati_med:
                    return await inter.response.send_message("\u2705 Nessun precedente medico.", ephemeral=True)
                embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                embed.description = (
                    f"\U0001fa7a | **FASCICOLO MEDICO**\n\n"
                    f"**Gruppo Sanguigno:**\n\u27a2 {dati_med.get('gruppo_sanguigno','N/A')}\n\n"
                    f"**Allergie:**\n\u27a2 {dati_med.get('allergie','Nessuna')}\n\n"
                    f"**Note:**\n\u27a2 {dati_med.get('note','Nessuna')}"
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

    class PortafoglioView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(PortafoglioSelect())

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = (
        f"\U0001f4b3 | **PORTAFOGLIO**\n\n"
        f"**CONTANTI \u27a2**\n{soldi}$\n\n"
        f"\u27a2 Seleziona un documento dal menu qui sotto."
    )
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
    await interaction.response.send_message(embed=embed, view=PortafoglioView(), ephemeral=True)

@bot.tree.command(name="zaino", description="🎒 Controlla cosa hai nello zaino")
@_blocca_se_dorme()
async def zaino_cmd(interaction: discord.Interaction):
    items = zaini.get(interaction.user.id, ["Zaino vuoto"])
    await interaction.response.send_message(f"🎒 **ZAINO:**\n" + ", ".join(items), ephemeral=True)

@bot.tree.command(name="inventario", description="📦 Guarda gli oggetti che hai indosso (o quelli di un altro cittadino)")
@_blocca_se_dorme()
@app_commands.describe(utente="Il cittadino di cui vuoi vedere l'inventario (lascia vuoto per il tuo)")
async def inventario(interaction: discord.Interaction, utente: discord.Member = None):
    from collections import Counter
    target = utente if utente is not None else interaction.user
    uid = target.id
    items = inventari.get(uid, [])
    peso_tot = _calcola_peso_inventario(uid)
    if not items:
        righe = "➢ Inventario vuoto"
    else:
        conteggio = Counter(items)
        # Trova oggetti che questo utente ha nascosto
        nascosti_uid = {v["oggetto"] for v in oggetti_nascosti.values() if v.get("uid") == uid}
        righe_list = []
        for nome, qty in conteggio.items():
            tag_nascosto = " *(nascosto)*" if nome in nascosti_uid else ""
            riga = f"➢ **{nome}** x{qty}{tag_nascosto}" if qty > 1 else f"➢ **{nome}**{tag_nascosto}"
            righe_list.append(riga)
        righe = "\n".join(righe_list)
    # Barra peso
    perc = min(peso_tot / PESO_MAX_INVENTARIO, 1.0)
    blocchi_pieni = round(perc * 10)
    if perc < 0.5:   colore_peso = "🟩"
    elif perc < 0.8: colore_peso = "🟨"
    else:            colore_peso = "🟥"
    barra_peso = colore_peso * blocchi_pieni + "⬛" * (10 - blocchi_pieni)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    intestazione = f"📦 | **INVENTARIO DI {target.display_name.upper()}**" if utente else "📦 | **IL MIO INVENTARIO**"
    embed.description = (
        f"{intestazione}\n\n{righe}\n\n"
        f"⚖️ **PESO**\n{barra_peso}  `{peso_tot}/{PESO_MAX_INVENTARIO} kg`"
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, "📦 Inventario consultato", f"Target: {target.display_name} | Peso: {peso_tot} kg", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)

class ChiamataView(discord.ui.View):
    def __init__(self, chiamante: discord.Member, ricevente: discord.Member, messaggio: str, dm_message):
        super().__init__(timeout=30)
        self.chiamante = chiamante
        self.ricevente = ricevente
        self.messaggio = messaggio
        self.dm_message = dm_message
        self.risposto = False

    @discord.ui.button(label="✅ Rispondi", style=discord.ButtonStyle.green)
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ricevente.id:
            return await interaction.response.send_message("❌ Questa chiamata non è per te.", ephemeral=True)
        self.risposto = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        guild = self.ricevente.guild

        categoria = discord.utils.get(guild.categories, name="📞 CHIAMATE")
        if not categoria:
            categoria = await guild.create_category("📞 CHIAMATE")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
            self.chiamante: discord.PermissionOverwrite(connect=True, view_channel=True, speak=True),
            self.ricevente: discord.PermissionOverwrite(connect=True, view_channel=True, speak=True),
            guild.me: discord.PermissionOverwrite(connect=True, view_channel=True, move_members=True),
        }
        vc_privata = await guild.create_voice_channel(
            name=f"📞 {self.chiamante.display_name} ↔ {self.ricevente.display_name}",
            category=categoria,
            overwrites=overwrites
        )

        embed_ok = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed_ok.description = (
            f"📞 | **CHIAMATA ATTIVA**\n\n"
            f"**DA ➢**\n{self.chiamante.mention}\n\n"
            f"**A ➢**\n{self.ricevente.mention}\n\n"
            f"➢ Entra nel canale vocale **{vc_privata.name}** per parlare.\n"
            f"➢ Solo voi due potete vederlo ed entrare.\n"
            f"➢ La VC si chiuderà automaticamente dopo **5 minuti**."
        )
        embed_ok.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")

        try:
            await self.chiamante.send(embed=embed_ok)
        except discord.Forbidden:
            pass
        try:
            await self.ricevente.send(embed=embed_ok)
        except discord.Forbidden:
            pass

        asyncio.get_event_loop().create_task(self._cancella_vc(vc_privata, categoria))

    async def _cancella_vc(self, vc: discord.VoiceChannel, categoria):
        await asyncio.sleep(300)
        for member in list(vc.members):
            try:
                await member.move_to(None)
            except Exception:
                pass
        try:
            await vc.delete(reason="Chiamata terminata automaticamente dopo 5 minuti")
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"[CHIAMA] Errore cancellazione VC: {e}")
        try:
            if categoria and len(categoria.channels) == 0:
                await categoria.delete(reason="Nessuna chiamata attiva")
        except Exception:
            pass
        embed_fine = discord.Embed(color=discord.Color.red())
        embed_fine.description = (
            f"📵 | **CHIAMATA TERMINATA**\n\n"
            f"➢ Il canale vocale privato è stato chiuso automaticamente."
        )
        embed_fine.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
        for member in [self.chiamante, self.ricevente]:
            try:
                await member.send(embed=embed_fine)
            except Exception:
                pass

    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.red)
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ricevente.id:
            return await interaction.response.send_message("❌ Questa chiamata non è per te.", ephemeral=True)
        self.risposto = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        embed_rif = discord.Embed(color=discord.Color.red())
        embed_rif.description = (
            f"📵 | **CHIAMATA RIFIUTATA**\n\n"
            f"➢ {self.ricevente.mention} ha rifiutato la chiamata."
        )
        embed_rif.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
        try:
            await self.chiamante.send(embed=embed_rif)
        except discord.Forbidden:
            pass

    async def on_timeout(self):
        if not self.risposto:
            for child in self.children:
                child.disabled = True
            try:
                await self.dm_message.edit(view=self)
            except Exception:
                pass
            embed_timeout = discord.Embed(color=discord.Color.red())
            embed_timeout.description = (
                f"📵 | **NESSUNA RISPOSTA**\n\n"
                f"➢ {self.ricevente.mention} non ha risposto alla chiamata."
            )
            embed_timeout.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
            try:
                await self.chiamante.send(embed_timeout)
            except Exception:
                pass


@bot.tree.command(name="metti-zaino", description="🎒 Metti un oggetto dall'inventario nello zaino")
@_blocca_se_dorme()
async def metti_zaino(interaction: discord.Interaction):
    uid = interaction.user.id
    inv = inventari.get(uid, [])
    if not inv:
        return await interaction.response.send_message("❌ Il tuo inventario è vuoto.", ephemeral=True)

    from collections import Counter
    conteggio = Counter(inv)
    opzioni = [
        discord.SelectOption(label=f"{nome} (x{qty})", value=nome)
        for nome, qty in conteggio.items()
    ][:25]

    class ZainoSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="Scegli oggetto da mettere nello zaino...", options=opzioni)
        async def callback(self, inter: discord.Interaction):
            scelta = self.values[0]
            if scelta not in inventari.get(uid, []):
                return await inter.response.send_message("❌ Oggetto non più disponibile.", ephemeral=True)
            inventari[uid].remove(scelta)
            if uid not in zaini: zaini[uid] = []
            zaini[uid].append(scelta)
            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed.description = f"🎒 | **OGGETTO NELLO ZAINO**\n\n➢ **{scelta}** spostato dall'inventario allo zaino."
            await inter.response.edit_message(embed=embed, view=None)

    class ZainoView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.add_item(ZainoSelect())

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.description = "🎒 | **METTI NELLO ZAINO**\n\n➢ Seleziona un oggetto dall'inventario da spostare nello zaino."
    await interaction.response.send_message(embed=embed, view=ZainoView(), ephemeral=True)


@bot.tree.command(name="wipe-persona", description="🗑️ Azzera TUTTO di un utente (Solo Dev/Founder)")
@is_dev_or_owner()
async def wipe_persona(interaction: discord.Interaction, utente: discord.Member):
    uid = utente.id
    inventari[uid] = []
    zaini[uid] = []
    portafogli[uid] = 0
    conti_bancari[uid] = 0
    documenti_identita.pop(uid, None)
    patenti_cittadini.pop(uid, None)
    licenze_cittadini.pop(uid, None)
    registro_armi.pop(uid, None)
    fascicoli_medici.pop(uid, None)
    bisogni_personaggio.pop(uid, None)
    garage_veicoli.pop(uid, None)
    statistiche_personaggio.pop(uid, None)
    schedario_warn.pop(uid, None)
    prigione.pop(uid, None)
    whitelist_db.pop(uid, None)
    contatti_telefono.pop(uid, None)
    messaggi_telefono.pop(uid, None)
    personaggi_addormentati.discard(uid)
    _salva_dati()
    embed = discord.Embed(color=discord.Color.red())
    embed.description = (
        f"🗑️ | **WIPE PERSONA**\n\n"
        f"**UTENTE ➢**\n{utente.mention}\n\n"
        f"➢ Inventario, zaino, soldi, documenti, patenti,\n"
        f"➢ armi, fascicolo medico, garage, statistiche,\n"
        f"➢ warn, prigione e whitelist — tutto azzerato."
    )
    embed.set_footer(text=f"{interaction.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed)
    await log_staff(interaction.guild, f"🗑️ {interaction.user.mention} ha eseguito WIPE TOTALE su {utente.mention}.", discord.Color.red())


@bot.tree.command(name="wipe-generale", description="☢️ Azzera TUTTI gli inventari e saldi del server (Solo Dev/Founder)")
@is_dev_or_owner()
async def wipe_generale(interaction: discord.Interaction):
    class ConfirmWipe(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)

        @discord.ui.button(label="✅ CONFERMA WIPE", style=discord.ButtonStyle.danger)
        async def conferma(self, inter: discord.Interaction, button: discord.ui.Button):
            if inter.user.id != interaction.user.id:
                return await inter.response.send_message("❌ Non sei tu ad aver avviato il wipe.", ephemeral=True)
            inventari.clear()
            zaini.clear()
            portafogli.clear()
            conti_bancari.clear()
            documenti_identita.clear()
            patenti_cittadini.clear()
            licenze_cittadini.clear()
            registro_armi.clear()
            fascicoli_medici.clear()
            bisogni_personaggio.clear()
            garage_veicoli.clear()
            statistiche_personaggio.clear()
            schedario_warn.clear()
            prigione.clear()
            whitelist_db.clear()
            contatti_telefono.clear()
            messaggi_telefono.clear()
            personaggi_addormentati.clear()
            ricercati.clear()
            _salva_dati()
            for child in self.children: child.disabled = True
            embed = discord.Embed(color=discord.Color.red())
            embed.description = "☢️ | **WIPE GENERALE COMPLETATO**\n\n➢ Tutti i dati del server sono stati azzerati."
            embed.set_footer(text=f"{inter.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            await inter.response.edit_message(embed=embed, view=self)
            await log_staff(inter.guild, f"☢️ {inter.user.mention} ha eseguito WIPE GENERALE.", discord.Color.red())

        @discord.ui.button(label="❌ Annulla", style=discord.ButtonStyle.secondary)
        async def annulla(self, inter: discord.Interaction, button: discord.ui.Button):
            for child in self.children: child.disabled = True
            await inter.response.edit_message(content="❌ Wipe annullato.", view=self)

    embed = discord.Embed(color=discord.Color.red())
    embed.description = "☢️ | **WIPE GENERALE**\n\n⚠️ Stai per azzerare **TUTTI** gli inventari, zaini e saldi del server.\n➢ Sei sicuro?"
    await interaction.response.send_message(embed=embed, view=ConfirmWipe(), ephemeral=True)


@bot.tree.command(name="pesca", description="🎣 Vai a pescare e guadagna qualcosa")
@_blocca_se_dorme()
async def pesca(interaction: discord.Interaction):
    import random
    uid = interaction.user.id
    pescate = [
        ("Pesce Piccolo", 50), ("Carpa", 80), ("Trota", 120),
        ("Salmone", 200), ("Tonno", 350), ("Pesce Spada", 500),
        ("Vecchia Scarpa", 0), ("Bottiglia Vuota", 0), ("Niente", 0),
    ]
    pesca_pesi = [20, 18, 15, 12, 8, 4, 10, 8, 5]
    risultato, valore = random.choices(pescate, weights=pesca_pesi, k=1)[0]

    if valore > 0:
        portafogli[uid] = portafogli.get(uid, 0) + valore
        if uid not in inventari: inventari[uid] = []
        inventari[uid].append(risultato)
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.description = (
            f"🎣 | **PESCA**\n\n"
            f"➢ Hai pescato un **{risultato}**!\n"
            f"➢ Guadagnato **{valore}$** e aggiunto all'inventario."
        )
    else:
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.description = f"🎣 | **PESCA**\n\n➢ Hai pescato... **{risultato}**. Meglio la prossima volta!"
    embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed)






# ─────────────────────────────────────────────
#   🍽️  SISTEMA FAME & SETE
# ─────────────────────────────────────────────

FAME_MAX  = 100
SETE_MAX  = 100
# Quanti punti scendono ogni 10 minuti
DECREMENTO_FAME = 3
DECREMENTO_SETE = 4

# Tag item: se un item nell'inventario contiene queste parole → è cibo o bevanda
TAG_CIBO     = ["cibo", "panino", "pizza", "hamburger", "mela", "bistecca", "sushi",
                "pasta", "barretta", "patatine", "gelato", "frutta", "snack", "pane",
                "riso", "pollo", "pesce", "torta", "biscotto", "insalata"]
TAG_BEVANDA  = ["acqua", "succo", "birra", "caffè", "energy", "latte", "cola",
                "sprite", "tè", "smoothie", "vino", "aranciata", "bevanda", "drink"]

# Mappa item → recupero (nome item in inventario → {fame/sete: X})
EFFETTI_ITEM: dict[str, dict] = {
    # — Cibi —
    "Panino":        {"fame": 20},
    "Pizza":         {"fame": 40},
    "Hamburger":     {"fame": 35},
    "Mela":          {"fame": 10},
    "Bistecca":      {"fame": 55},
    "Sushi":         {"fame": 45},
    "Pasta":         {"fame": 50},
    "Barretta":      {"fame": 12},
    "Patatine":      {"fame": 15},
    "Gelato":        {"fame": 18},
    "Pesce Piccolo": {"fame": 15},
    "Carpa":         {"fame": 25},
    "Trota":         {"fame": 30},
    "Salmone":       {"fame": 40},
    "Tonno":         {"fame": 50},
    "Pesce Spada":              {"fame": 60},
    # — Bevande —
    "Acqua":         {"sete": 30},
    "Succo":         {"sete": 25},
    "Birra":         {"sete": 20},
    "Caffè":         {"sete": 10},
    "Latte":         {"sete": 22},
    "Coca-Cola":     {"sete": 28},
    "Sprite":        {"sete": 28},
    "Smoothie":      {"sete": 32},
    # 🛒 Snack e Cibi Confezionati (Supermarket)
    "🥔 Patatine Classiche":           {"fame": 12},
    "🌶️ Patatine Paprika":            {"fame": 12},
    "🔥 Patatine Piccanti":           {"fame": 12},
    "🍫 Barretta Cioccolato al Latte":{"fame": 10},
    "🍫 Barretta Fondente":           {"fame": 10},
    "🍫 Barretta Mandorle":           {"fame": 11},
    "💪 Barretta Proteica":           {"fame": 25},
    "🍬 Caramelle Gommose":           {"fame": 6},
    "🪥 Chewing Gum":                 {"fame": 2},
    "🥪 Tramezzino Tonno e Maionese": {"fame": 30},
    "🥪 Tramezzino Prosciutto e Formaggio": {"fame": 30},
    "🍜 Cup Noodles":                 {"fame": 28},
    "🧁 Muffin Confezionato":         {"fame": 14},
    "🥐 Brioche Confezionata":        {"fame": 14},
    # 🧊 Bevande da Frigo (Supermarket)
    "💧 Acqua Minerale 0.5L":         {"sete": 35},
    "💧 Acqua Minerale 1.5L":         {"sete": 60},
    "🥤 Lattina di Cola":             {"sete": 28},
    "🍊 Lattina Aranciata":           {"sete": 25},
    "🍋 Lemon Soda":                  {"sete": 25},
    "⚡ Energy Drink":               {"sete": 35},
    "🧊 Tè Freddo":                   {"sete": 28},
    "🧃 Succo ACE Vitaminico":        {"sete": 30},
    "🥛 Latte Fresco":               {"sete": 30},
}

# ─────────────────────────────────────────────
#   ⚖️  SISTEMA PESI OGGETTI (realistici in kg)
# ─────────────────────────────────────────────
PESI_OGGETTI: dict[str, float] = {
    # 📦 Inventario base
    "📱 Telefono": 0.2,
    "🔑 Chiavi di Casa": 0.1,
    "💳 Carta Pacific Bank": 0.01,
    # 🍽️ Cibo
    "Panino": 0.2,
    "Pizza": 0.5,
    "Hamburger": 0.3,
    "Mela": 0.2,
    "Bistecca": 0.4,
    "Sushi": 0.3,
    "Pasta": 0.4,
    "Barretta": 0.08,
    "Patatine": 0.15,
    "Gelato": 0.2,
    # 🐟 Pesce
    "Pesce Piccolo": 0.3,
    "Carpa": 1.5,
    "Trota": 2.0,
    "Salmone": 3.0,
    "Tonno": 5.0,
    "Pesce Spada": 8.0,
    "Vecchia Scarpa": 0.5,
    "Bottiglia Vuota": 0.1,
    # 💧 Bevande
    "Acqua": 0.5,
    "Succo": 0.4,
    "Birra": 0.5,
    "Caffè": 0.1,
    "Latte": 0.5,
    "Coca-Cola": 0.33,
    "Sprite": 0.33,
    "Smoothie": 0.35,
    # 🛒 Supermarket cibo
    "🥔 Patatine Classiche": 0.1,
    "🌶️ Patatine Paprika": 0.1,
    "🔥 Patatine Piccanti": 0.1,
    "🍫 Barretta Cioccolato al Latte": 0.05,
    "🍫 Barretta Fondente": 0.05,
    "🍫 Barretta Mandorle": 0.05,
    "💪 Barretta Proteica": 0.07,
    "🍬 Caramelle Gommose": 0.08,
    "🪥 Chewing Gum": 0.02,
    "🥪 Tramezzino Tonno e Maionese": 0.18,
    "🥪 Tramezzino Prosciutto e Formaggio": 0.18,
    "🍜 Cup Noodles": 0.12,
    "🧁 Muffin Confezionato": 0.1,
    "🥐 Brioche Confezionata": 0.08,
    # 🧊 Bevande supermarket
    "💧 Acqua Minerale 0.5L": 0.5,
    "💧 Acqua Minerale 1.5L": 1.5,
    "🥤 Lattina di Cola": 0.35,
    "🍊 Lattina Aranciata": 0.35,
    "🍋 Lemon Soda": 0.33,
    "⚡ Energy Drink": 0.25,
    "🧊 Tè Freddo": 0.33,
    "🧃 Succo ACE Vitaminico": 0.2,
    "🥛 Latte Fresco": 1.0,
    # 🕵️ Investigazione
    "🐛 Microspia / Cimice Ambientale": 0.05,
    "📡 Rilevatore di Microspie": 0.3,
    "🎙️ Registratore Vocale Portatile": 0.15,
    "📷 Macchina Fotografica Usa e Getta": 0.2,
    # 💰 Finanze oscure
    "💼 Valigetta con Fondo Falso": 2.0,
    "🛍️ Buste con Banconote": 0.5,
    "🧱 Mattoni di Denaro Sigillati": 1.0,
    # 🩸 Interrogatori
    "🔧 Pinze / Tenaglie": 0.8,
    "🧪 Bottiglietta di Acido": 0.5,
    "🎭 Sacchetto per Ostaggi": 0.1,
    "🧤 Guanti Medici": 0.05,
    "🖤 Vernice Nera per Targhe": 0.4,
    # 🌿 Droghe
    "🌿 Marijuana": 0.1,
    "💮 Cocaina": 0.1,
    "❄️ Blue Crystal": 0.1,
    # 🔑 Chiavi veicoli e case
    "🔑 Chiave": 0.05,
}

PESO_MAX_INVENTARIO = 15.0  # kg massimo trasportabile

def _calcola_peso_inventario(uid: int) -> float:
    """Calcola il peso totale dell'inventario di un utente."""
    items = inventari.get(uid, [])
    totale = 0.0
    for item in items:
        # Cerca il peso (anche per item con nome parziale come chiavi casa)
        for chiave_peso, peso in PESI_OGGETTI.items():
            if chiave_peso.lower() in item.lower() or item.lower() in chiave_peso.lower():
                totale += peso
                break
        else:
            totale += 0.2  # peso default per oggetti non mappati
    return round(totale, 2)

EMOJI_ITEM: dict[str, str] = {
    "Panino": "🥪", "Pizza": "🍕", "Hamburger": "🍔", "Mela": "🍎",
    "Bistecca": "🥩", "Sushi": "🍣", "Pasta": "🍝", "Barretta": "🍫",
    "Patatine": "🍟", "Gelato": "🍦", "Pesce Piccolo": "🐟", "Carpa": "🐠",
    "Trota": "🐡", "Salmone": "🍣", "Tonno": "🐟", "Pesce Spada": "🗡️",
    "Acqua": "💧", "Succo": "🧃", "Birra": "🍺", "Caffè": "☕",
    "Energy Drink": "⚡", "Latte": "🥛", "Coca-Cola": "🥤", "Sprite": "🥤",
    "Tè Freddo": "🧊", "Smoothie": "🍹",
    # Bevande supermarket
    "Cocacola": "🥤", "Redbull": "⚡", "Monster Mango Loco": "🍹",
    # Cibo supermarket
    "boccaciuccio da jay massa": "🥪",
}


def _paga_direttore(locale: str, importo: int):
    """Accredita l'importo al portafoglio del direttore del locale."""
    dir_id = DIRETTORI_LOCALI.get(locale)
    if dir_id:
        portafogli[dir_id] = portafogli.get(dir_id, 0) + importo


def _init_bisogni(uid: int) -> dict:
    if uid not in bisogni_personaggio:
        bisogni_personaggio[uid] = {"fame": FAME_MAX, "sete": SETE_MAX}
    return bisogni_personaggio[uid]


def _barra_fame(valore: int, massimo: int = 100, lunghezza: int = 10) -> str:
    """Barra FAME 10 pixel: verde pieno → giallo → rosso critico."""
    riempiti = round((valore / massimo) * lunghezza)
    vuoti    = lunghezza - riempiti
    if valore >= 70:   pieno = "🟩"
    elif valore >= 35: pieno = "🟨"
    else:              pieno = "🟥"
    return pieno * riempiti + "⬛" * vuoti

def _barra_sete(valore: int, massimo: int = 100, lunghezza: int = 10) -> str:
    """Barra SETE 10 pixel: blu pieno → azzurro → rosso critico."""
    riempiti = round((valore / massimo) * lunghezza)
    vuoti    = lunghezza - riempiti
    if valore >= 70:   pieno = "🟦"
    elif valore >= 35: pieno = "🟪"
    else:              pieno = "🟥"
    return pieno * riempiti + "⬛" * vuoti

def _barra_pixel(valore: int, massimo: int = 100, lunghezza: int = 10) -> str:
    """Alias generico — usa fame di default."""
    return _barra_fame(valore, massimo, lunghezza)


def _stato_testo(valore: int) -> str:
    """Stato basato sul ciclo ore (sessione fino a 5 ore, decremento ogni 10 min = 3/4 punti)."""
    # 100 = 0-1h normale | 80 = 1-2h leggero | 60 = 2-3h evidente | 40 = 3-4h debolezza | 20 = 4-5h critico | 0 = 5h+ collasso
    if valore > 80:  return "0–1 ora — Stato normale ✅"
    if valore > 60:  return "1–2 ore — Fastidio, calo concentrazione 😐"
    if valore > 40:  return "2–3 ore — Irritabilità, meno reattività 😣"
    if valore > 20:  return "3–4 ore — Debolezza, riduzione fisica ⚠️"
    if valore > 0:   return "4–5 ore — Stato critico, vertigini 🆘"
    return "5+ ore — Collasso / rischio morte RP 💀"





# ── /mangia ──────────────────────────────────
@bot.tree.command(name="mangia", description="🍽️ Mangia qualcosa dal tuo inventario")
@_blocca_se_dorme()
async def mangia(interaction: discord.Interaction):
    uid = interaction.user.id
    b = _init_bisogni(uid)
    inv = inventari.get(uid, [])
    # Solo item che esistono DAVVERO nell'inventario e hanno effetto fame
    cibi_inv = [item for item in inv if item in EFFETTI_ITEM and "fame" in EFFETTI_ITEM[item]]

    barra_f = _barra_fame(b["fame"], FAME_MAX)
    barra_s = _barra_sete(b["sete"], SETE_MAX)

    if not cibi_inv:
        embed = discord.Embed(color=discord.Color.from_rgb(200, 50, 50))
        embed.set_author(name="🍽️  Menu Cibo", icon_url=interaction.user.display_avatar.url)
        embed.description = (
            "❌ **Nessun cibo nell'inventario!**\n"
            "> Acquistane dal negozio o pescane.\n\n"
            f"🍽️ **FAME**\n{barra_f}  `{b['fame']}/{FAME_MAX}` — {_stato_testo(b['fame'])}\n\n"
            f"💧 **SETE**\n{barra_s}  `{b['sete']}/{SETE_MAX}` — {_stato_testo(b['sete'])}"
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    from collections import Counter
    conteggio = Counter(cibi_inv)
    opzioni = []
    for nome, qty in conteggio.items():
        emoji_i = EMOJI_ITEM.get(nome, "🍴")
        recupero = EFFETTI_ITEM[nome]["fame"]
        label = f"{emoji_i} {nome}" + (f" x{qty}" if qty > 1 else "")
        opzioni.append(discord.SelectOption(
            label=label[:100], value=nome,
            description=f"+{recupero} fame"
        ))

    class MangiaSel(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="🍴  Scegli cosa mangiare...",
                options=opzioni[:25], min_values=1, max_values=1
            )
        async def callback(self, inter: discord.Interaction):
            if inter.user.id != uid:
                return await inter.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
            scelta = self.values[0]
            inv_cur = inventari.get(uid, [])
            if scelta not in inv_cur:
                return await inter.response.send_message("❌ Non hai più quell'item!", ephemeral=True)
            inv_cur.remove(scelta)
            inventari[uid] = inv_cur
            cur = _init_bisogni(uid)
            recupero = EFFETTI_ITEM[scelta]["fame"]
            vecchia = cur["fame"]
            cur["fame"] = min(FAME_MAX, cur["fame"] + recupero)
            guadagnato = cur["fame"] - vecchia
            _salva_dati()
            bf = _barra_fame(cur["fame"], FAME_MAX)
            bs = _barra_sete(cur["sete"], SETE_MAX)
            emoji_i = EMOJI_ITEM.get(scelta, "🍴")
            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed.set_author(name=f"Hai mangiato: {scelta}", icon_url=inter.user.display_avatar.url)
            embed.description = (
                f"{emoji_i}  **+{guadagnato} fame recuperata!**\n\n"
                f"🍽️ **FAME**\n{bf}  `{cur['fame']}/{FAME_MAX}` — {_stato_testo(cur['fame'])}\n\n"
                f"💧 **SETE**\n{bs}  `{cur['sete']}/{SETE_MAX}` — {_stato_testo(cur['sete'])}"
            )
            embed.set_footer(text=f"{inter.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            await inter.response.edit_message(embed=embed, view=None)
            await log_azione(inter.guild, inter.user, "🍽️ Ha mangiato", f"Item: **{scelta}** | +{guadagnato} fame", discord.Color.from_rgb(255, 107, 53))

    class MangiaView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=45)
            self.add_item(MangiaSel())

    embed_sel = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed_sel.set_author(name="🍽️  Menu Cibo", icon_url=interaction.user.display_avatar.url)
    embed_sel.description = (
        f"🍽️ **FAME**\n{barra_f}  `{b['fame']}/{FAME_MAX}` — {_stato_testo(b['fame'])}\n\n"
        f"💧 **SETE**\n{barra_s}  `{b['sete']}/{SETE_MAX}` — {_stato_testo(b['sete'])}\n\n"
        "> Seleziona un cibo dal tuo inventario qui sotto."
    )
    await interaction.response.send_message(embed=embed_sel, view=MangiaView(), ephemeral=True)


# ── /bevi ────────────────────────────────────
@bot.tree.command(name="bevi", description="💧 Bevi qualcosa dal tuo inventario")
@_blocca_se_dorme()
async def bevi(interaction: discord.Interaction):
    uid = interaction.user.id
    b = _init_bisogni(uid)
    inv = inventari.get(uid, [])
    bev_inv = [item for item in inv if item in EFFETTI_ITEM and "sete" in EFFETTI_ITEM[item]]

    barra_f = _barra_fame(b["fame"], FAME_MAX)
    barra_s = _barra_sete(b["sete"], SETE_MAX)

    if not bev_inv:
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="💧  Menu Bevande", icon_url=interaction.user.display_avatar.url)
        embed.description = (
            "❌ **Nessuna bevanda nell'inventario!**\n"
            "> Acquistane dal negozio.\n\n"
            f"🍽️ **FAME**\n{barra_f}  `{b['fame']}/{FAME_MAX}` — {_stato_testo(b['fame'])}\n\n"
            f"💧 **SETE**\n{barra_s}  `{b['sete']}/{SETE_MAX}` — {_stato_testo(b['sete'])}"
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    from collections import Counter
    conteggio = Counter(bev_inv)
    opzioni = []
    for nome, qty in conteggio.items():
        emoji_i = EMOJI_ITEM.get(nome, "🥤")
        recupero = EFFETTI_ITEM[nome]["sete"]
        label = f"{emoji_i} {nome}" + (f" x{qty}" if qty > 1 else "")
        opzioni.append(discord.SelectOption(
            label=label[:100], value=nome,
            description=f"+{recupero} sete"
        ))

    class BeviSel(discord.ui.Select):
        def __init__(self):
            super().__init__(
                placeholder="🥤  Scegli cosa bere...",
                options=opzioni[:25], min_values=1, max_values=1
            )
        async def callback(self, inter: discord.Interaction):
            if inter.user.id != uid:
                return await inter.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
            scelta = self.values[0]
            inv_cur = inventari.get(uid, [])
            if scelta not in inv_cur:
                return await inter.response.send_message("❌ Non hai più quell'item!", ephemeral=True)
            inv_cur.remove(scelta)
            inventari[uid] = inv_cur
            cur = _init_bisogni(uid)
            recupero = EFFETTI_ITEM[scelta]["sete"]
            vecchia = cur["sete"]
            cur["sete"] = min(SETE_MAX, cur["sete"] + recupero)
            guadagnato = cur["sete"] - vecchia
            _salva_dati()
            bf = _barra_fame(cur["fame"], FAME_MAX)
            bs = _barra_sete(cur["sete"], SETE_MAX)
            emoji_i = EMOJI_ITEM.get(scelta, "🥤")
            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
            embed.set_author(name=f"Hai bevuto: {scelta}", icon_url=inter.user.display_avatar.url)
            embed.description = (
                f"{emoji_i}  **+{guadagnato} sete recuperata!**\n\n"
                f"🍽️ **FAME**\n{bf}  `{cur['fame']}/{FAME_MAX}` — {_stato_testo(cur['fame'])}\n\n"
                f"💧 **SETE**\n{bs}  `{cur['sete']}/{SETE_MAX}` — {_stato_testo(cur['sete'])}"
            )
            embed.set_footer(text=f"{inter.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            await inter.response.edit_message(embed=embed, view=None)
            await log_azione(inter.guild, inter.user, "💧 Ha bevuto", f"Item: **{scelta}** | +{guadagnato} sete", discord.Color.from_rgb(255, 107, 53))

    class BeviView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=45)
            self.add_item(BeviSel())

    embed_sel = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed_sel.set_author(name="💧  Menu Bevande", icon_url=interaction.user.display_avatar.url)
    embed_sel.description = (
        f"🍽️ **FAME**\n{barra_f}  `{b['fame']}/{FAME_MAX}` — {_stato_testo(b['fame'])}\n\n"
        f"💧 **SETE**\n{barra_s}  `{b['sete']}/{SETE_MAX}` — {_stato_testo(b['sete'])}\n\n"
        "> Seleziona una bevanda dal tuo inventario qui sotto."
    )
    await interaction.response.send_message(embed=embed_sel, view=BeviView(), ephemeral=True)


# ── /stato ───────────────────────────────────
@bot.tree.command(name="stato", description="📊 Visualizza le barre di fame e sete del personaggio")
@app_commands.describe(utente="Lascia vuoto per vedere il tuo stato")
async def stato(interaction: discord.Interaction, utente: discord.Member = None):
    target = utente or interaction.user
    uid    = target.id
    b      = _init_bisogni(uid)
    fame   = b["fame"]
    sete   = b["sete"]
    barra_f = _barra_fame(fame, FAME_MAX)
    barra_s = _barra_sete(sete, SETE_MAX)
    media = (fame + sete) / 2
    if media >= 75:   icona_gen, stato_gen = "🟢", "In ottima forma"
    elif media >= 50: icona_gen, stato_gen = "🟡", "Nella norma"
    elif media >= 25: icona_gen, stato_gen = "🟠", "Inizia a stare male"
    else:             icona_gen, stato_gen = "🔴", "Stato critico!"
    if media >= 65:   colore = discord.Color.from_rgb(255, 107, 53)
    elif media >= 35: colore = discord.Color.from_rgb(255, 107, 53)
    else:             colore = discord.Color.from_rgb(231, 76, 60)
    embed = discord.Embed(color=colore)
    embed.set_author(
        name=f"Stato vitale — {target.display_name}",
        icon_url=target.display_avatar.url
    )
    embed.description = (
        f"**🍽️ FAME**\n"
        f"{barra_f}  `{fame}/{FAME_MAX}`\n"
        f"╰ {_stato_testo(fame)}\n\n"
        f"**💧 SETE**\n"
        f"{barra_s}  `{sete}/{SETE_MAX}`\n"
        f"╰ {_stato_testo(sete)}\n\n"
        f"**Condizione:** {icona_gen} {stato_gen}\n"
        f"-# ⏱️ Fame −{DECREMENTO_FAME} | Sete −{DECREMENTO_SETE} ogni 10 min"
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(
        text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
        icon_url=interaction.user.display_avatar.url
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="dormi", description="😴 Fai dormire il tuo personaggio (blocca tutti i comandi)")
async def dormi(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid in personaggi_addormentati:
        return await interaction.response.send_message(
            "😴 Stai già dormendo! Usa `/sveglia` per alzarti.", ephemeral=True
        )
    personaggi_addormentati.add(uid)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name=f"😴  {interaction.user.display_name} si è addormentato/a", icon_url=interaction.user.display_avatar.url)
    embed.description = (
        "🛏️ | **PERSONAGGIO ADDORMENTATO**\n\n"
        "➢ Il tuo personaggio sta dormendo.\n"
        "➢ Durante il sonno **non puoi usare comandi**.\n"
        "➢ **Fame e sete non scendono** mentre dormi.\n\n"
        "*Usa `/sveglia` quando vuoi alzarti.*"
    )
    embed.set_footer(text=f"Addormentato alle {datetime.now().strftime('%H:%M')} del {datetime.now().strftime('%d/%m/%Y')}")
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, "😴 Personaggio addormentato", "", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


@bot.tree.command(name="sveglia", description="☀️ Sveglia il tuo personaggio")
async def sveglia(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid not in personaggi_addormentati:
        return await interaction.response.send_message(
            "☀️ Il tuo personaggio è già sveglio!", ephemeral=True
        )
    personaggi_addormentati.discard(uid)
    b = _init_bisogni(uid)
    barra_f = _barra_fame(b["fame"], FAME_MAX)
    barra_s = _barra_sete(b["sete"], SETE_MAX)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name=f"☀️  {interaction.user.display_name} si è svegliato/a", icon_url=interaction.user.display_avatar.url)
    embed.description = (
        "🌅 | **BUONGIORNO!**\n\n"
        "➢ Il tuo personaggio si è svegliato.\n"
        "➢ Puoi di nuovo usare tutti i comandi.\n\n"
        f"🍽️ **FAME**\n{barra_f}  `{b['fame']}/{FAME_MAX}` — {_stato_testo(b['fame'])}\n\n"
        f"💧 **SETE**\n{barra_s}  `{b['sete']}/{SETE_MAX}` — {_stato_testo(b['sete'])}"
    )
    embed.set_footer(text=f"Svegliato alle {datetime.now().strftime('%H:%M')} del {datetime.now().strftime('%d/%m/%Y')}")
    await interaction.response.send_message(embed=embed)


# ==========================================
# 🛒 SUPERMARKET
# ==========================================

SUPERMARKET_CIBO = [
    # 🛒 Snack e Cibi Confezionati
    {"nome": "🥔 Patatine Classiche",          "prezzo": 10,  "effetto": "fame", "recupero": 12},
    {"nome": "🌶️ Patatine Paprika",            "prezzo": 10,  "effetto": "fame", "recupero": 12},
    {"nome": "🔥 Patatine Piccanti",           "prezzo": 10,  "effetto": "fame", "recupero": 12},
    {"nome": "🍫 Barretta Cioccolato al Latte","prezzo": 8,   "effetto": "fame", "recupero": 10},
    {"nome": "🍫 Barretta Fondente",           "prezzo": 8,   "effetto": "fame", "recupero": 10},
    {"nome": "🍫 Barretta Mandorle",           "prezzo": 9,   "effetto": "fame", "recupero": 11},
    {"nome": "💪 Barretta Proteica",           "prezzo": 20,  "effetto": "fame", "recupero": 25},
    {"nome": "🍬 Caramelle Gommose",           "prezzo": 6,   "effetto": "fame", "recupero": 6},
    {"nome": "🪥 Chewing Gum",                 "prezzo": 3,   "effetto": "fame", "recupero": 2},
    {"nome": "🥪 Tramezzino Tonno e Maionese", "prezzo": 18,  "effetto": "fame", "recupero": 30},
    {"nome": "🥪 Tramezzino Prosciutto e Formaggio","prezzo": 18, "effetto": "fame", "recupero": 30},
    {"nome": "🍜 Cup Noodles",                 "prezzo": 12,  "effetto": "fame", "recupero": 28},
    {"nome": "🧁 Muffin Confezionato",         "prezzo": 7,   "effetto": "fame", "recupero": 14},
    {"nome": "🥐 Brioche Confezionata",        "prezzo": 7,   "effetto": "fame", "recupero": 14},
]

SUPERMARKET_BEVANDE = [
    # 🧊 Bevande da Frigo
    {"nome": "💧 Acqua Minerale 0.5L",         "prezzo": 5,   "effetto": "sete", "recupero": 35},
    {"nome": "💧 Acqua Minerale 1.5L",         "prezzo": 10,  "effetto": "sete", "recupero": 60},
    {"nome": "🥤 Lattina di Cola",             "prezzo": 15,  "effetto": "sete", "recupero": 28},
    {"nome": "🍊 Lattina Aranciata",           "prezzo": 15,  "effetto": "sete", "recupero": 25},
    {"nome": "🍋 Lemon Soda",                  "prezzo": 15,  "effetto": "sete", "recupero": 25},
    {"nome": "⚡ Energy Drink",               "prezzo": 30,  "effetto": "sete", "recupero": 35},
    {"nome": "🧊 Tè Freddo",                   "prezzo": 12,  "effetto": "sete", "recupero": 28},
    {"nome": "🧃 Succo ACE Vitaminico",        "prezzo": 14,  "effetto": "sete", "recupero": 30},
    {"nome": "🥛 Latte Fresco",               "prezzo": 12,  "effetto": "sete", "recupero": 30},
]

SUPERMARKET_ITEM = [
# ═══════════════════════════════════════════
# 🕵️ INVESTIGAZIONE & CONTRO-SPIONAGGIO
# ═══════════════════════════════════════════
    {
        "nome":        "🐛 Microspia / Cimice Ambientale",
        "prezzo":      850,
        "descrizione": "Nascondila in un covo o ufficio rivale per intercettare piani e conversazioni.",
        "categoria":   "🕵️ Investigazione"
    },
    {
        "nome":        "📡 Rilevatore di Microspie",
        "prezzo":      1200,
        "descrizione": "Scanner tascabile per bonificare auto e covi da cimici di polizia o rivali.",
        "categoria":   "🕵️ Investigazione"
    },
    {
        "nome":        "🎙️ Registratore Vocale Portatile",
        "prezzo":      600,
        "descrizione": "Registra confessioni, contratti loschi o materiale per ricatti.",
        "categoria":   "🕵️ Investigazione"
    },
    {
        "nome":        "📷 Macchina Fotografica Usa e Getta",
        "prezzo":      300,
        "descrizione": "Foto compromettenti per estorsioni o prove da consegnare a giudici corrotti.",
        "categoria":   "🕵️ Investigazione"
    },
    # ═══════════════════════════════════════════
    # 💰 RICICLAGGIO & FINANZE OSCURE
    # ═══════════════════════════════════════════
    {
        "nome":        "💼 Valigetta con Fondo Falso",
        "prezzo":      1500,
        "descrizione": "Trasporta denaro sporco o armi passando inosservato ai controlli rapidi.",
        "categoria":   "💰 Finanze Oscure"
    },
    {
        "nome":        "🛍️ Buste con Banconote",
        "prezzo":      500,
        "descrizione": "Consegne di denaro sporco stile film, nei vicoli bui.",
        "categoria":   "💰 Finanze Oscure"
    },
    {
        "nome":        "🧱 Mattoni di Denaro Sigillati",
        "prezzo":      750,
        "descrizione": "Grossa somma di denaro sporco sigillata sottovuoto, pronta per il riciclaggio.",
        "categoria":   "💰 Finanze Oscure"
    },
    # ═══════════════════════════════════════════
    # 🩸 INTERROGATORI & PRESSIONE PSICOLOGICA
    # ═══════════════════════════════════════════
    {
        "nome":        "🔧 Pinze / Tenaglie",
        "prezzo":      400,
        "descrizione": "Strumento scenico per fare pressione su ostaggi durante interrogatori RP.",
        "categoria":   "🩸 Interrogatori"
    },
    {
        "nome":        "🧪 Bottiglietta di Acido",
        "prezzo":      600,
        "descrizione": "Liquido corrosivo usato a scopo scenico per convincere un ostaggio a parlare.",
        "categoria":   "🩸 Interrogatori"
    },
    {
        "nome":        "🎭 Sacchetto per Ostaggi",
        "prezzo":      150,
        "descrizione": "Da infilare in testa a un rapito per non fargli vedere la strada verso il covo.",
        "categoria":   "🩸 Interrogatori"
    },
    {
        "nome":        "🧤 Guanti Medici",
        "prezzo":      80,
        "descrizione": "Non lasciare impronte. Indispensabili per qualsiasi operazione pulita.",
        "categoria":   "🩸 Interrogatori"
    },
    {
        "nome":        "🖤 Vernice Nera per Targhe",
        "prezzo":      200,
        "descrizione": "Rendi illeggibile la targa del veicolo durante colpi e fughe.",
        "categoria":   "🩸 Interrogatori"
    },
    # ═══════════════════════════════════════════
    # 🎒 EQUIPAGGIAMENTO & ACCESSORI (Nuovi Item)
    # ═══════════════════════════════════════════
    {
        "nome":        "🎒 Zaino",
        "prezzo":      1200,
        "descrizione": "Aumenta la capacità di trasporto e lo spazio per i tuoi oggetti.",
        "categoria":   "Generale"
    },
    {
        "nome":        "🧳 Borsone",
        "prezzo":      2500,
        "descrizione": "Un borsone capiente ideale per trasportare attrezzatura o refurtiva.",
        "categoria":   "Generale"
    },
    {
        "nome":        "🔗 Fascette da Elettricista",
        "prezzo":      150,
        "descrizione": "Utili per immobilizzare temporaneamente qualcuno durante un'azione.",
        "categoria":   "Item"
    },
    {
        "nome":        "🎭 Maschera",
        "prezzo":      350,
        "descrizione": "Nascondi la tua identità durante le operazioni o i colpi in città.",
        "categoria":   "Item"
    },
    {
        "nome":        "🎒 Zaino",
        "prezzo":      500,
        "descrizione": "Uno zaino capiente per trasportare oggetti extra. Aumenta la capacità di carico.",
        "categoria":   "Item"
    },
    {
        "nome":        "🧳 Borsone",
        "prezzo":      800,
        "descrizione": "Un grande borsone per trasportare molti oggetti. Più capiente dello zaino, ideale per i colpi.",
        "categoria":   "Item"
    },
]


_popola_oggetti_supermarket()
# ── Popola oggetti_creati con tutti gli item supermarket ──

class SupermarketCiboView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=60)
        self.uid = uid
        # Prima prende da oggetti_creati categoria "Cibo", poi fallback lista hardcoded
        items_dyn = [v for v in oggetti_creati.values() if v.get("categoria") == "Cibo" and v.get("vendibile", True)]
        if items_dyn:
            opzioni = [
                discord.SelectOption(
                    label=p["nome"][:100],
                    description=f"{p['prezzo']}$ | +{p.get('recupero','?')} fame",
                    value=p["nome"],
                    emoji="🍽️"
                ) for p in items_dyn[:25]
            ]
        else:
            opzioni = [
                discord.SelectOption(
                    label=p["nome"],
                    description=f"{p['prezzo']}$ | +{p['recupero']} fame",
                    value=p["nome"],
                    emoji="🍽️"
                ) for p in SUPERMARKET_CIBO
            ]
        self.add_item(self._make_select(opzioni, "🍽️  Scegli un cibo...", "cibo"))

    def _make_select(self, opzioni, placeholder, tipo):
        uid = self.uid

        class CiboSelect(discord.ui.Select):
            def __init__(self_inner):
                super().__init__(placeholder=placeholder, options=opzioni, min_values=1, max_values=1)

            async def callback(self_inner, inter: discord.Interaction):
                if inter.user.id != uid:
                    return await inter.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
                nome_item = self_inner.values[0]
                prodotto = oggetti_creati.get(nome_item) or next((p for p in SUPERMARKET_CIBO if p["nome"] == nome_item), None)
                if not prodotto:
                    return await inter.response.send_message("❌ Prodotto non trovato.", ephemeral=True)
                saldo = portafogli.get(uid, 0)
                prezzo = prodotto.get("prezzo", 0)
                if saldo < prezzo:
                    return await inter.response.send_message(
                        f"❌ Non hai abbastanza contanti! Ti servono **{prezzo}$**.", ephemeral=True
                    )
                portafogli[uid] = saldo - prezzo
                _paga_direttore("supermarket", prezzo)
                if uid not in inventari:
                    inventari[uid] = []
                inventari[uid].append(nome_item)
                _registra_transazione(uid, "−", prezzo, "🛒 Acquisto Supermarket", nome_item)
                _salva_dati()
                embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                embed.set_author(name="🛒 Supermarket — Acquisto completato")
                embed.description = (
                    f"✅ Hai acquistato **{nome_item}** per **{prezzo}$**!\n"
                    f"➢ Aggiunto all'inventario.\n"
                    f"➢ Usa `/mangia` per consumarlo e recuperare fame."
                )
                embed.set_footer(text=f"Saldo rimasto: {portafogli[uid]}$")
                await inter.response.edit_message(embed=embed, view=None)
                await log_azione(inter.guild, inter.user, "🛒 Acquisto Supermarket (Cibo)", f"Item: **{nome_item}** | Prezzo: {prezzo}$", discord.Color.from_rgb(255, 107, 53))

        return CiboSelect()


class SupermarketBevandeView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=60)
        self.uid = uid
        items_dyn = [v for v in oggetti_creati.values() if v.get("categoria") == "Bevande" and v.get("vendibile", True)]
        if items_dyn:
            opzioni = [
                discord.SelectOption(
                    label=p["nome"][:100],
                    description=f"{p['prezzo']}$ | +{p.get('recupero','?')} sete",
                    value=p["nome"],
                    emoji="🥤"
                ) for p in items_dyn[:25]
            ]
        else:
            opzioni = [
                discord.SelectOption(
                    label=p["nome"],
                    description=f"{p['prezzo']}$ | +{p['recupero']} sete",
                    value=p["nome"],
                    emoji="🥤"
                ) for p in SUPERMARKET_BEVANDE
            ]
        self.add_item(self._make_select(opzioni))

    def _make_select(self, opzioni):
        uid = self.uid

        class BevandeSelect(discord.ui.Select):
            def __init__(self_inner):
                super().__init__(placeholder="🥤  Scegli una bevanda...", options=opzioni, min_values=1, max_values=1)

            async def callback(self_inner, inter: discord.Interaction):
                if inter.user.id != uid:
                    return await inter.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
                nome_item = self_inner.values[0]
                prodotto = oggetti_creati.get(nome_item) or next((p for p in SUPERMARKET_BEVANDE if p["nome"] == nome_item), None)
                if not prodotto:
                    return await inter.response.send_message("❌ Prodotto non trovato.", ephemeral=True)
                saldo = portafogli.get(uid, 0)
                prezzo = prodotto.get("prezzo", 0)
                if saldo < prezzo:
                    return await inter.response.send_message(
                        f"❌ Non hai abbastanza contanti! Ti servono **{prezzo}$**.", ephemeral=True
                    )
                portafogli[uid] = saldo - prezzo
                _paga_direttore("supermarket", prezzo)
                if uid not in inventari:
                    inventari[uid] = []
                inventari[uid].append(nome_item)
                _registra_transazione(uid, "−", prezzo, "🛒 Acquisto Supermarket", nome_item)
                _salva_dati()
                embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                embed.set_author(name="🛒 Supermarket — Acquisto completato")
                embed.description = (
                    f"✅ Hai acquistato **{nome_item}** per **{prezzo}$**!\n"
                    f"➢ Aggiunto all'inventario.\n"
                    f"➢ Usa `/bevi` per consumarla e recuperare sete."
                )
                embed.set_footer(text=f"Saldo rimasto: {portafogli[uid]}$")
                await inter.response.edit_message(embed=embed, view=None)
                await log_azione(inter.guild, inter.user, "🛒 Acquisto Supermarket (Bevanda)", f"Item: **{nome_item}** | Prezzo: {prezzo}$", discord.Color.from_rgb(255, 107, 53))

        return BevandeSelect()


class SupermarketItemView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=60)
        self.uid = uid
        items_nuovi = {v["nome"]: v for v in oggetti_creati.values() if v.get("categoria") == "Item" and v.get("vendibile", True)}
        items_fissi = {p["nome"]: p for p in SUPERMARKET_ITEM}
        tutti = {**items_fissi, **items_nuovi}
        opzioni = [
            discord.SelectOption(
                label=p["nome"][:100],
                description=f"{p['prezzo']}$ — {p.get('descrizione','')[:80]}",
                value=p["nome"],
            )
            for p in list(tutti.values())[:25]
        ]
        if not opzioni:
            opzioni = [discord.SelectOption(label="Nessun item disponibile", value="__vuoto__")]
        self.add_item(self._make_select(opzioni))

    def _make_select(self, opzioni):
        uid = self.uid

        class ItemSelect(discord.ui.Select):
            def __init__(self_inner):
                super().__init__(placeholder="🎒  Scegli un item...", options=opzioni, min_values=1, max_values=1)

            async def callback(self_inner, inter: discord.Interaction):
                if inter.user.id != uid:
                    return await inter.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
                nome_item = self_inner.values[0]
                if nome_item == "__vuoto__":
                    return await inter.response.send_message("❌ Nessun item disponibile al momento.", ephemeral=True)
                # Cerca prima in oggetti_creati (include item creati dallo staff), poi in SUPERMARKET_ITEM
                prodotto = oggetti_creati.get(nome_item)
                if not prodotto:
                    prodotto = next((p for p in SUPERMARKET_ITEM if p["nome"] == nome_item), None)
                if not prodotto:
                    return await inter.response.send_message("❌ Prodotto non trovato.", ephemeral=True)
                saldo = portafogli.get(uid, 0)
                prezzo = prodotto.get("prezzo", 0)
                if saldo < prezzo:
                    return await inter.response.send_message(
                        f"❌ Non hai abbastanza contanti! Ti servono **{prezzo}$**.", ephemeral=True
                    )
                portafogli[uid] = saldo - prezzo
                _paga_direttore("supermarket", prezzo)
                if uid not in inventari:
                    inventari[uid] = []
                inventari[uid].append(nome_item)
                _registra_transazione(uid, "−", prezzo, "🛒 Acquisto Supermarket", nome_item)
                _salva_dati()
                embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
                embed.set_author(name="🛒 Supermarket — Acquisto completato")
                embed.description = (
                    f"✅ Hai acquistato **{nome_item}** per **{prezzo}$**!\n"
                    f"➢ *{prodotto.get('descrizione','')}*\n"
                    f"➢ Aggiunto all'inventario."
                )
                embed.set_footer(text=f"Saldo rimasto: {portafogli[uid]}$")
                await inter.response.edit_message(embed=embed, view=None)
                await log_azione(inter.guild, inter.user, "🛒 Acquisto Supermarket (Item)", f"Item: **{nome_item}** | Prezzo: {prezzo}$", discord.Color.from_rgb(255, 107, 53))

        return ItemSelect()


def _is_direttore_supermarket(member: discord.Member) -> bool:
    """Controlla se il membro è il Direttore Supermarket o ha ruoli staff/admin."""
    if member.guild_permissions.administrator:
        return True
    ruolo_dir_id = DIRETTORI_LOCALI.get("supermarket")
    for r in member.roles:
        if r.id == ruolo_dir_id:
            return True
        if "direttore supermarket" in r.name.lower():
            return True
    if _ha_ruolo(member, _KW_STAFF):
        return True
    return False


class ModalCreaItemSupermarket(discord.ui.Modal):
    """Modal per creare un item nel supermarket con categoria preimpostata."""

    nome_item = discord.ui.TextInput(
        label="Nome dell'item",
        style=discord.TextStyle.short,
        placeholder="Es: Patatine Fritte",
        required=True,
        max_length=80
    )
    descrizione_item = discord.ui.TextInput(
        label="Descrizione",
        style=discord.TextStyle.paragraph,
        placeholder="Breve descrizione del prodotto",
        required=True,
        max_length=200
    )
    prezzo_item = discord.ui.TextInput(
        label="Prezzo ($)",
        style=discord.TextStyle.short,
        placeholder="Es: 150",
        required=True,
        max_length=10
    )
    quantita_item = discord.ui.TextInput(
        label="Quantità in stock",
        style=discord.TextStyle.short,
        placeholder="Es: 50 (lascia 999 per illimitato)",
        required=False,
        max_length=6,
        default="999"
    )

    def __init__(self, categoria: str):
        super().__init__(title=f"🛒 Crea Item — {categoria}")
        self.categoria_sel = categoria

    async def on_submit(self, interaction: discord.Interaction):
        nome_k = self.nome_item.value.strip()
        desc = self.descrizione_item.value.strip()

        try:
            prezzo = int(self.prezzo_item.value.strip())
            if prezzo < 0:
                raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Prezzo non valido. Inserisci un numero intero positivo.", ephemeral=True)

        try:
            qty_val = self.quantita_item.value.strip()
            quantita = int(qty_val) if qty_val else 999
            if quantita <= 0:
                raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Quantità non valida.", ephemeral=True)

        if nome_k in oggetti_creati:
            return await interaction.response.send_message(f"❌ L'item **{nome_k}** esiste già.", ephemeral=True)

        oggetti_creati[nome_k] = {
            "nome": nome_k,
            "quantita": quantita,
            "prezzo": prezzo,
            "vendibile": True,
            "descrizione": desc,
            "categoria": self.categoria_sel,
            "ruolo_richiesto": None
        }
        _salva_dati()

        emoji_cat = {"Cibo": "🍽️", "Bevande": "🥤", "Item": "🎒"}.get(self.categoria_sel, "📦")
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
        embed.set_author(name="🛒 NUOVO ITEM SUPERMARKET CREATO", icon_url=LOGO_SERVER)
        embed.description = (
            f"{emoji_cat} **Nome ➢** {nome_k}\n\n"
            f"**Categoria ➢** {self.categoria_sel}\n\n"
            f"**Prezzo ➢** {prezzo}$\n\n"
            f"**Stock ➢** {quantita}\n\n"
            f"**Descrizione ➢** {desc}"
        )
        embed.set_footer(text=f"Creato da {interaction.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_staff(interaction.guild, f"🛒 {interaction.user.mention} ha creato l'item supermarket **{nome_k}** ({self.categoria_sel}) a {prezzo}$.", discord.Color.from_rgb(255, 107, 53))
        await log_azione(interaction.guild, interaction.user, "🛒 Item Supermarket creato", f"Nome: **{nome_k}** | Cat: {self.categoria_sel} | Prezzo: {prezzo}$", discord.Color.from_rgb(255, 107, 53), canale_origine=interaction.channel)


class SupermarketStaffCategoriaView(discord.ui.View):
    """View per il Direttore: sceglie in quale categoria creare il nuovo item."""

    def __init__(self, direttore: discord.Member):
        super().__init__(timeout=60)
        self.direttore = direttore

    @discord.ui.button(label="🍽️ Cibo", style=discord.ButtonStyle.success, row=0)
    async def btn_crea_cibo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        await interaction.response.send_modal(ModalCreaItemSupermarket("Cibo"))

    @discord.ui.button(label="🥤 Bevande", style=discord.ButtonStyle.primary, row=0)
    async def btn_crea_bevande(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        await interaction.response.send_modal(ModalCreaItemSupermarket("Bevande"))

    @discord.ui.button(label="🎒 Item", style=discord.ButtonStyle.secondary, row=0)
    async def btn_crea_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        await interaction.response.send_modal(ModalCreaItemSupermarket("Item"))


class SupermarketView(discord.ui.View):
    def __init__(self, uid: int, is_direttore: bool = False):
        super().__init__(timeout=120)
        self.uid = uid
        self.is_direttore = is_direttore

    @discord.ui.button(label="🍽️ Cibo", style=discord.ButtonStyle.success, custom_id="sm_cibo")
    async def btn_cibo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
        items = [v for v in oggetti_creati.values() if v.get("categoria") == "Cibo" and v.get("vendibile", True)]
        if not items:
            items = [{"nome": p["nome"], "prezzo": p["prezzo"], "recupero": p["recupero"]} for p in SUPERMARKET_CIBO]
        righe = "\n".join([f"➢ **{p['nome']}** — {p['prezzo']}$ | +{p.get('recupero','?')} fame" for p in items])
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="🛒 Supermarket — 🍽️ Cibo")
        embed.description = f"Seleziona un prodotto dal menu:\n\n{righe}"
        embed.set_footer(text=f"Il tuo saldo: {portafogli.get(self.uid, 0)}$")
        await interaction.response.send_message(embed=embed, view=SupermarketCiboView(self.uid))

    @discord.ui.button(label="🥤 Bevande", style=discord.ButtonStyle.primary, custom_id="sm_bevande")
    async def btn_bevande(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
        items = [v for v in oggetti_creati.values() if v.get("categoria") == "Bevande" and v.get("vendibile", True)]
        if not items:
            items = [{"nome": p["nome"], "prezzo": p["prezzo"], "recupero": p["recupero"]} for p in SUPERMARKET_BEVANDE]
        righe = "\n".join([f"➢ **{p['nome']}** — {p['prezzo']}$ | +{p.get('recupero','?')} sete" for p in items])
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="🛒 Supermarket — 🥤 Bevande")
        embed.description = f"Seleziona una bevanda dal menu:\n\n{righe}"
        embed.set_footer(text=f"Il tuo saldo: {portafogli.get(self.uid, 0)}$")
        await interaction.response.send_message(embed=embed, view=SupermarketBevandeView(self.uid))

    @discord.ui.button(label="🎒 Item", style=discord.ButtonStyle.secondary, custom_id="sm_item")
    async def btn_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
        # Item da oggetti_creati con categoria "Item" (creati dallo staff)
        items_nuovi = {v["nome"]: v for v in oggetti_creati.values() if v.get("categoria") == "Item" and v.get("vendibile", True)}
        # Item dalla lista fissa (tutte le categorie speciali del supermarket)
        items_fissi = {p["nome"]: p for p in SUPERMARKET_ITEM}
        # Unisci: prima i fissi, poi sovrascrivi/aggiungi i nuovi
        tutti = {**items_fissi, **items_nuovi}
        righe = "\n".join([f"➢ **{p['nome']}** — {p['prezzo']}$" for p in tutti.values()])
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="🛒 Supermarket — 🎒 Item")
        embed.description = f"Seleziona un item dal menu:\n\n{righe}"
        embed.set_footer(text=f"Il tuo saldo: {portafogli.get(self.uid, 0)}$")
        await interaction.response.send_message(embed=embed, view=SupermarketItemView(self.uid))

    @discord.ui.button(label="➕ Crea Item [STAFF]", style=discord.ButtonStyle.danger, custom_id="sm_staff_crea", row=1)
    async def btn_staff_crea(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
        membro = await _get_member(interaction)
        if not _is_direttore_supermarket(membro):
            return await interaction.response.send_message("❌ **Accesso negato.** Riservato al Direttore Supermarket o allo Staff.", ephemeral=True)
        embed = discord.Embed(color=discord.Color.red(), timestamp=datetime.now())
        embed.set_author(name="🛒 Supermarket — Crea Nuovo Item", icon_url=LOGO_SERVER)
        embed.description = (
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Scegli la **categoria** in cui vuoi creare il nuovo item:\n\n"
            "🍽️ **Cibo** — prodotti alimentari (ripristinano la fame)\n"
            "🥤 **Bevande** — bibite e liquidi (ripristinano la sete)\n"
            "🎒 **Item** — oggetti speciali acquistabili\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await interaction.response.send_message(embed=embed, view=SupermarketStaffCategoriaView(membro), ephemeral=True)

    @discord.ui.button(label="🗑️ Elimina Item [STAFF]", style=discord.ButtonStyle.danger, custom_id="sm_staff_elimina", row=1)
    async def btn_staff_elimina(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("❌ Non è il tuo menu!", ephemeral=True)
        membro = await _get_member(interaction)
        if not _is_direttore_supermarket(membro):
            return await interaction.response.send_message("❌ **Accesso negato.**", ephemeral=True)
        # Item del supermarket = categoria Cibo, Bevande o Item
        items_sm = [
            v for v in oggetti_creati.values()
            if v.get("categoria") in ("Cibo", "Bevande", "Item")
        ]
        if not items_sm:
            return await interaction.response.send_message("❌ Nessun item nel supermarket.", ephemeral=True)
        opzioni = [
            discord.SelectOption(
                label=p["nome"][:100],
                description=f"{p['categoria']} — {p['prezzo']}$",
                value=p["nome"]
            ) for p in items_sm[:25]
        ]
        uid = self.uid
        class EliminaSelect(discord.ui.Select):
            def __init__(self_i):
                super().__init__(placeholder="Scegli item da eliminare...", options=opzioni)
            async def callback(self_i, inter: discord.Interaction):
                if inter.user.id != uid:
                    return await inter.response.send_message("❌", ephemeral=True)
                nome = self_i.values[0]
                oggetti_creati.pop(nome, None)
                _salva_dati()
                await inter.response.send_message(f"🗑️ Item **{nome}** eliminato dal supermarket.", ephemeral=True)
                await log_staff(inter.guild, f"🗑️ {inter.user.mention} ha eliminato l'item **{nome}** dal supermarket.", discord.Color.red())
        view = discord.ui.View(timeout=60)
        view.add_item(EliminaSelect())
        await interaction.response.send_message("Scegli l'item da eliminare:", view=view, ephemeral=True)

@bot.tree.command(name="supermarket", description="🛒 Interagisci con il commerciante del supermarket")
@_blocca_se_dorme()
async def supermarket(interaction: discord.Interaction):
    uid = interaction.user.id
    saldo = portafogli.get(uid, 0)
    membro = await _get_member(interaction)
    is_dir = _is_direttore_supermarket(membro)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name="🛒 Supermarket — Benvenuto!", icon_url=LOGO_SERVER)
    desc = (
        "🏪 **Commerciante:**\n"
        "*\"Benvenuto! Cosa posso fare per te oggi?\n"
        "Abbiamo cibo fresco, bevande fredde e tutto il necessario!\"*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🛒 **Snack & Cibi** — Patatine, barrette, tramezzini, noodles e altro\n"
        "🧊 **Bevande da Frigo** — Acqua, cola, energy drink, succhi e altro\n"
        "🎒 **Item Speciali** — Microspie, valigette, guanti, vernice targhe e altro\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Il tuo saldo: **{saldo}$**\n\n"
        "➢ *Scegli una categoria qui sotto:*"
    )
    if is_dir:
        desc += "\n\n🔑 *Sei il Direttore: puoi creare nuovi item con il bottone Staff.*"
    embed.description = desc
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed, view=SupermarketView(uid, is_direttore=is_dir))



# ==========================================
# 🏢 SISTEMA BANDI DI LAVORO
# ==========================================

CH_BANDI_CANDIDATURE  = 1532891367611826187  # canale log dove arrivano le candidature
CH_BANDI_ESITI        = 1532127581409640478  # canale dove arriva accettato/rifiutato
CH_FORUM_BANDI        = 1538353622654517398  # canale forum con i post/thread dei bandi
RUOLO_STAFF_BANDI     = 1532126930151669952  # ruolo che può accettare/rifiutare candidature

LAVORI_EMOJI = {
    "ammunation":    "🔫",
    "dynasty8":      "🏠",
    "concessionario":"🚗",
    "polizia":       "👮",
    "swat":          "🪖",
    "banca":         "🏦",
    "ems":           "🚑",
    "msfd":          "🚒",
    "avvocato":      "⚖️",
    "giudice":       "🔨",
    "minimarket":    "🛒",
    "vanilla":       "🍸",
    "meccanico":     "🔧",
    "import_export": "📦",
    "casino":        "🎰",
    "pegasus":       "✈️",
    "isla_de_oro":   "🍽️",
}

LAVORI_NOMI = {
    "ammunation":    "Ammunation",
    "dynasty8":      "Dynasty 8",
    "concessionario":"Concessionario",
    "polizia":       "Polizia",
    "swat":          "S.W.A.T.",
    "banca":         "Banca",
    "ems":           "EMS",
    "msfd":          "MSFD",
    "avvocato":      "Avvocato",
    "giudice":       "Giudice",
    "minimarket":    "Minimarket",
    "vanilla":       "Vanilla Unicorn",
    "meccanico":     "Meccanico",
    "import_export": "Import-Export",
    "casino":        "Casino",
    "pegasus":       "Pegasus",
    "isla_de_oro":   "Isla De Oro",
}

# ─── MODALI ───────────────────────────────────────────────────────────────────

class ModalBandoGenerico(discord.ui.Modal):
    nome_cognome = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta          = discord.ui.TextInput(label="Età IC", placeholder="Es: 28", required=True, max_length=3)
    motivazione  = discord.ui.TextInput(label="Perché vuoi questo lavoro?", style=discord.TextStyle.paragraph, required=True, max_length=500)
    esperienza   = discord.ui.TextInput(label="Hai esperienza precedente?", style=discord.TextStyle.paragraph, required=True, max_length=300)
    disponibilita= discord.ui.TextInput(label="Disponibilità oraria", placeholder="Es: sera nei giorni feriali", required=True, max_length=100)

    def __init__(self, lavoro_key: str):
        self.lavoro_key = lavoro_key
        super().__init__(title=f"📋 Candidatura — {LAVORI_NOMI[lavoro_key]}")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, self.lavoro_key, {
            "Nome e Cognome IC":       self.nome_cognome.value,
            "Età IC":                  self.eta.value,
            "Motivazione":             self.motivazione.value,
            "Esperienza precedente":   self.esperienza.value,
            "Disponibilità":           self.disponibilita.value,
        })


class ModalBandoForzeOrdine(discord.ui.Modal):
    nome_cognome = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta          = discord.ui.TextInput(label="Età IC", placeholder="Min. 21 anni IC", required=True, max_length=3)
    motivazione  = discord.ui.TextInput(label="Perché vuoi servire la città?", style=discord.TextStyle.paragraph, required=True, max_length=500)
    casellario   = discord.ui.TextInput(label="Hai precedenti penali IC?", placeholder="Sì/No — specificare", required=True, max_length=200)
    situazione_fis= discord.ui.TextInput(label="Condizione fisica e mentale IC", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self, lavoro_key: str):
        self.lavoro_key = lavoro_key
        super().__init__(title=f"📋 Candidatura — {LAVORI_NOMI[lavoro_key]}")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, self.lavoro_key, {
            "Nome e Cognome IC":     self.nome_cognome.value,
            "Età IC":                self.eta.value,
            "Motivazione":           self.motivazione.value,
            "Precedenti penali IC":  self.casellario.value,
            "Condizione fisica/mentale": self.situazione_fis.value,
        })


class ModalBandoLegge(discord.ui.Modal):
    nome_cognome = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta          = discord.ui.TextInput(label="Età IC", placeholder="Min. 25 anni IC", required=True, max_length=3)
    titolo_studio= discord.ui.TextInput(label="Titolo di studio IC", placeholder="Es: Laurea in Giurisprudenza", required=True, max_length=100)
    casi_trattati= discord.ui.TextInput(label="Casi o esperienze legali precedenti", style=discord.TextStyle.paragraph, required=True, max_length=500)
    motivazione  = discord.ui.TextInput(label="Perché questa professione?", style=discord.TextStyle.paragraph, required=True, max_length=400)

    def __init__(self, lavoro_key: str):
        self.lavoro_key = lavoro_key
        super().__init__(title=f"📋 Candidatura — {LAVORI_NOMI[lavoro_key]}")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, self.lavoro_key, {
            "Nome e Cognome IC":   self.nome_cognome.value,
            "Età IC":              self.eta.value,
            "Titolo di studio IC": self.titolo_studio.value,
            "Esperienze legali":   self.casi_trattati.value,
            "Motivazione":         self.motivazione.value,
        })


class ModalBandoMeccanico(discord.ui.Modal):
    nome_cognome  = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta           = discord.ui.TextInput(label="Età IC", placeholder="Es: 24", required=True, max_length=3)
    specializzaz  = discord.ui.TextInput(label="Specializzazione (auto, moto, entrambi?)", placeholder="Es: auto sportive", required=True, max_length=100)
    esperienza    = discord.ui.TextInput(label="Esperienza come meccanico IC", style=discord.TextStyle.paragraph, required=True, max_length=400)
    motivazione   = discord.ui.TextInput(label="Perché vuoi lavorare qui?", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self):
        super().__init__(title="📋 Candidatura — Meccanico")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, "meccanico", {
            "Nome e Cognome IC":   self.nome_cognome.value,
            "Età IC":              self.eta.value,
            "Specializzazione":    self.specializzaz.value,
            "Esperienza IC":       self.esperienza.value,
            "Motivazione":         self.motivazione.value,
        })


class ModalBandoCasino(discord.ui.Modal):
    nome_cognome = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta          = discord.ui.TextInput(label="Età IC", placeholder="Min. 21 anni IC", required=True, max_length=3)
    ruolo_desid  = discord.ui.TextInput(label="Ruolo desiderato", placeholder="Es: Croupier, Barman, Sicurezza", required=True, max_length=100)
    esperienza   = discord.ui.TextInput(label="Esperienza nel settore", style=discord.TextStyle.paragraph, required=True, max_length=400)
    gestione_conf= discord.ui.TextInput(label="Come gestiresti un cliente problematico?", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self):
        super().__init__(title="📋 Candidatura — Casino")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, "casino", {
            "Nome e Cognome IC":    self.nome_cognome.value,
            "Età IC":               self.eta.value,
            "Ruolo desiderato":     self.ruolo_desid.value,
            "Esperienza":           self.esperienza.value,
            "Gestione conflitti":   self.gestione_conf.value,
        })


class ModalBandoPegasus(discord.ui.Modal):
    nome_cognome  = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta           = discord.ui.TextInput(label="Età IC", placeholder="Min. 23 anni IC", required=True, max_length=3)
    licenze       = discord.ui.TextInput(label="Licenze di volo/nautica IC possedute", placeholder="Es: Licenza pilota civile", required=True, max_length=200)
    esperienza    = discord.ui.TextInput(label="Ore di volo/navigazione IC", style=discord.TextStyle.paragraph, required=True, max_length=300)
    motivazione   = discord.ui.TextInput(label="Perché vuoi lavorare per Pegasus?", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self):
        super().__init__(title="📋 Candidatura — Pegasus")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, "pegasus", {
            "Nome e Cognome IC":  self.nome_cognome.value,
            "Età IC":             self.eta.value,
            "Licenze IC":         self.licenze.value,
            "Esperienza di volo": self.esperienza.value,
            "Motivazione":        self.motivazione.value,
        })


class ModalBandoRistorante(discord.ui.Modal):
    nome_cognome = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es: Marco Rossi", required=True, max_length=50)
    eta          = discord.ui.TextInput(label="Età IC", placeholder="Es: 22", required=True, max_length=3)
    ruolo_desid  = discord.ui.TextInput(label="Ruolo desiderato", placeholder="Es: Chef, Cameriere, Barman", required=True, max_length=100)
    esperienza   = discord.ui.TextInput(label="Esperienza nella ristorazione", style=discord.TextStyle.paragraph, required=True, max_length=400)
    piatto_firma = discord.ui.TextInput(label="Descrivimi un piatto che sapresti fare IC", style=discord.TextStyle.paragraph, required=True, max_length=300)

    def __init__(self, lavoro_key: str):
        self.lavoro_key = lavoro_key
        super().__init__(title=f"📋 Candidatura — {LAVORI_NOMI[lavoro_key]}")

    async def on_submit(self, interaction: discord.Interaction):
        await _invia_candidatura(interaction, self.lavoro_key, {
            "Nome e Cognome IC":  self.nome_cognome.value,
            "Età IC":             self.eta.value,
            "Ruolo desiderato":   self.ruolo_desid.value,
            "Esperienza":         self.esperienza.value,
            "Piatto firma IC":    self.piatto_firma.value,
        })


# ─── FUNZIONE INVIO CANDIDATURA ───────────────────────────────────────────────

async def _invia_candidatura(interaction: discord.Interaction, lavoro_key: str, campi: dict):
    emoji = LAVORI_EMOJI.get(lavoro_key, "📋")
    nome  = LAVORI_NOMI.get(lavoro_key, lavoro_key)

    embed = discord.Embed(
        title=f"{emoji} CANDIDATURA — {nome.upper()}",
        color=discord.Color.from_rgb(255, 107, 53),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.set_author(name=f"{interaction.user.display_name} ({interaction.user})", icon_url=interaction.user.display_avatar.url)

    for label, valore in campi.items():
        embed.add_field(name=label, value=valore, inline=False)

    embed.set_footer(text=f"ID candidato: {interaction.user.id}")

    canale = interaction.guild.get_channel(CH_BANDI_CANDIDATURE)
    if canale:
        view = ViewEsitoBando(interaction.user.id, lavoro_key)
        await canale.send(embed=embed, view=view)

    await interaction.response.send_message(
        f"✅ **Candidatura inviata con successo!**\nAttendi una risposta dallo staff per **{nome}**.",
        ephemeral=True
    )


# ─── VIEW ESITO (Accetta/Rifiuta) ─────────────────────────────────────────────

class ViewEsitoBando(discord.ui.View):
    def __init__(self, candidato_id: int, lavoro_key: str):
        super().__init__(timeout=None)
        self.candidato_id = candidato_id
        self.lavoro_key   = lavoro_key

    @discord.ui.button(label="✅ Accetta", style=discord.ButtonStyle.success, custom_id="bando_accetta")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.name.lower() in ["staff", "admin", "developer", "direttore"] for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai i permessi.", ephemeral=True)
        nome  = LAVORI_NOMI.get(self.lavoro_key, self.lavoro_key)
        emoji = LAVORI_EMOJI.get(self.lavoro_key, "📋")
        canale_esiti = interaction.guild.get_channel(CH_BANDI_ESITI)
        candidato = interaction.guild.get_member(self.candidato_id)
        embed = discord.Embed(
            title=f"✅ CANDIDATURA ACCETTATA — {nome.upper()}",
            color=discord.Color.from_rgb(255, 107, 53),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="Candidato", value=candidato.mention if candidato else f"ID: {self.candidato_id}", inline=True)
        embed.add_field(name="Lavoro", value=f"{emoji} {nome}", inline=True)
        embed.add_field(name="Approvato da", value=interaction.user.mention, inline=True)
        if canale_esiti:
            await canale_esiti.send(embed=embed)
        if candidato:
            try:
                dm_embed = discord.Embed(
                    title=f"✅ Candidatura Accettata — {nome}",
                    description=f"Congratulazioni! La tua candidatura per **{emoji} {nome}** su **Eclipse City RP** è stata **accettata**.\nContatta lo staff per ulteriori informazioni.",
                    color=discord.Color.from_rgb(255, 107, 53)
                )
                dm_embed.set_thumbnail(url=LOGO_SERVER)
                await candidato.send(embed=dm_embed)
            except Exception:
                pass
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"✅ Candidatura di {candidato.mention if candidato else self.candidato_id} accettata.", ephemeral=True)

    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.danger, custom_id="bando_rifiuta")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.name.lower() in ["staff", "admin", "developer", "direttore"] for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai i permessi.", ephemeral=True)
        nome  = LAVORI_NOMI.get(self.lavoro_key, self.lavoro_key)
        emoji = LAVORI_EMOJI.get(self.lavoro_key, "📋")
        canale_esiti = interaction.guild.get_channel(CH_BANDI_ESITI)
        candidato = interaction.guild.get_member(self.candidato_id)
        embed = discord.Embed(
            title=f"❌ CANDIDATURA RIFIUTATA — {nome.upper()}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="Candidato", value=candidato.mention if candidato else f"ID: {self.candidato_id}", inline=True)
        embed.add_field(name="Lavoro", value=f"{emoji} {nome}", inline=True)
        embed.add_field(name="Rifiutato da", value=interaction.user.mention, inline=True)
        if canale_esiti:
            await canale_esiti.send(embed=embed)
        if candidato:
            try:
                dm_embed = discord.Embed(
                    title=f"❌ Candidatura Rifiutata — {nome}",
                    description=f"Purtroppo la tua candidatura per **{emoji} {nome}** su **Eclipse City RP** è stata **rifiutata**.\nPuoi riprovare in futuro!",
                    color=discord.Color.red()
                )
                dm_embed.set_thumbnail(url=LOGO_SERVER)
                await candidato.send(embed=dm_embed)
            except Exception:
                pass
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"❌ Candidatura di {candidato.mention if candidato else self.candidato_id} rifiutata.", ephemeral=True)


# ─── SELECT MENU MODULO ───────────────────────────────────────────────────────

class SelectBando(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Ammunation",       value="ammunation",    emoji="🔫", description="Negozio di armi"),
            discord.SelectOption(label="Dynasty 8",        value="dynasty8",      emoji="🏠", description="Agenzia immobiliare"),
            discord.SelectOption(label="Concessionario",   value="concessionario",emoji="🚗", description="Vendita veicoli"),
            discord.SelectOption(label="Polizia",          value="polizia",       emoji="👮", description="Forze dell'ordine"),
            discord.SelectOption(label="S.W.A.T.",         value="swat",          emoji="🪖", description="Unità speciale"),
            discord.SelectOption(label="Banca",            value="banca",         emoji="🏦", description="Istituto bancario"),
            discord.SelectOption(label="EMS",              value="ems",           emoji="🚑", description="Servizio medico"),
            discord.SelectOption(label="MSFD",             value="msfd",          emoji="🚒", description="Vigili del fuoco"),
            discord.SelectOption(label="Avvocato",         value="avvocato",      emoji="⚖️", description="Studio legale"),
            discord.SelectOption(label="Giudice",          value="giudice",       emoji="🔨", description="Tribunale"),
            discord.SelectOption(label="Minimarket",       value="minimarket",    emoji="🛒", description="Negozio alimentari"),
            discord.SelectOption(label="Vanilla Unicorn",  value="vanilla",       emoji="🍸", description="Locale notturno"),
            discord.SelectOption(label="Meccanico",        value="meccanico",     emoji="🔧", description="Officina"),
            discord.SelectOption(label="Import-Export",    value="import_export", emoji="📦", description="Commercio internazionale"),
            discord.SelectOption(label="Casino",           value="casino",        emoji="🎰", description="Casa da gioco"),
            discord.SelectOption(label="Pegasus",          value="pegasus",       emoji="✈️", description="Trasporti aerei e nautici"),
            discord.SelectOption(label="Isla De Oro",      value="isla_de_oro",   emoji="🍽️", description="Ristorante di lusso"),
        ]
        super().__init__(placeholder="🏢 Seleziona il lavoro per cui candidarti...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        lavoro = self.values[0]
        if lavoro in ("polizia", "swat"):
            modal = ModalBandoForzeOrdine(lavoro)
        elif lavoro in ("avvocato", "giudice"):
            modal = ModalBandoLegge(lavoro)
        elif lavoro == "meccanico":
            modal = ModalBandoMeccanico()
        elif lavoro == "casino":
            modal = ModalBandoCasino()
        elif lavoro == "pegasus":
            modal = ModalBandoPegasus()
        elif lavoro in ("vanilla", "isla_de_oro"):
            modal = ModalBandoRistorante(lavoro)
        else:
            modal = ModalBandoGenerico(lavoro)
        await interaction.response.send_modal(modal)


# ─── STORAGE BANDI PERSONALIZZATI ────────────────────────────────────────────
# Struttura: { "nome_bando": { "titolo": str, "descrizione": str, "domande": [str, ...] } }
RUOLO_GESTIONE_BANDI = 1532134838650278002  # Unico ruolo che può creare/eliminare bandi

bandi_personalizzati: dict = {}   # dizionario in memoria


def _ha_ruolo_bandi(interaction: discord.Interaction) -> bool:
    return any(r.id == RUOLO_GESTIONE_BANDI for r in interaction.user.roles)


# ─── MODAL: STEP 1 — Informazioni del bando (titolo + 7 domande) ──────────────

# ─── MODAL CREA BANDO ─────────────────────────────────────────────────────────
# Struttura fissa candidatura: Nome/Cognome IC, Età IC (sempre presenti) + 3 domande custom.
# Il modal di creazione chiede: Titolo + le 3 domande personalizzabili.

class ModalCreaBando(discord.ui.Modal, title="📝 Crea Nuovo Bando"):
    # Form candidatura avrà SEMPRE: Nome/Cognome IC + Età IC (fissi) + queste 3 domande
    titolo_bando = discord.ui.TextInput(
        label="Titolo del bando",
        placeholder="Es: Bando Polizia Municipale",
        required=True, max_length=80
    )
    domanda1 = discord.ui.TextInput(
        label="Domanda 1",
        placeholder="Es: Motivazione — Perché vuoi questo ruolo?",
        required=True, max_length=100
    )
    domanda2 = discord.ui.TextInput(
        label="Domanda 2",
        placeholder="Es: Hai esperienza precedente?",
        required=True, max_length=100
    )
    domanda3 = discord.ui.TextInput(
        label="Domanda 3",
        placeholder="Es: Disponibilità oraria",
        required=True, max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        titolo = self.titolo_bando.value.strip()
        key    = titolo.lower().replace(" ", "_")[:40]
        bandi_personalizzati[key] = {
            "titolo":  titolo,
            "domande": [
                self.domanda1.value.strip(),
                self.domanda2.value.strip(),
                self.domanda3.value.strip(),
            ],
        }
        await interaction.response.send_message(
            f"✅ **Bando `{titolo}` creato!**\n\n"
            f"Il form di candidatura avrà:\n"
            f"`1.` Nome e Cognome IC *(fisso)*\n"
            f"`2.` Età IC *(fisso)*\n"
            f"`3.` {self.domanda1.value.strip()}\n"
            f"`4.` {self.domanda2.value.strip()}\n"
            f"`5.` {self.domanda3.value.strip()}\n\n"
            f"Usa `/bandi` per pubblicare il pannello aggiornato.",
            ephemeral=True
        )


# ─── MODAL CANDIDATURA BANDO PERSONALIZZATO ───────────────────────────────────
# Struttura fissa: Nome/Cognome IC, Età IC + le 3 domande custom del bando.

class ModalCandidaturaBandoCustom(discord.ui.Modal):
    def __init__(self, key: str):
        bando = bandi_personalizzati[key]
        super().__init__(title=f"📋 Candidatura — {bando['titolo'][:40]}")
        self.key = key

        # Campi fissi
        self._nome_cognome = discord.ui.TextInput(
            label="Nome e Cognome IC",
            placeholder="Es: Marco Rossi",
            required=True, max_length=60
        )
        self._eta = discord.ui.TextInput(
            label="Età IC",
            placeholder="Es: 24",
            required=True, max_length=3
        )
        self.add_item(self._nome_cognome)
        self.add_item(self._eta)

        # 3 domande personalizzate
        self._custom = []
        for domanda in bando["domande"][:3]:
            campo = discord.ui.TextInput(
                label=domanda[:45],
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=500
            )
            self.add_item(campo)
            self._custom.append(campo)

    async def on_submit(self, interaction: discord.Interaction):
        bando = bandi_personalizzati.get(self.key)
        if not bando:
            return await interaction.response.send_message("❌ Bando non trovato.", ephemeral=True)
        campi = {
            "Nome e Cognome IC": self._nome_cognome.value,
            "Età IC":            self._eta.value,
            **{f.label: f.value for f in self._custom}
        }
        embed  = discord.Embed(
            title=f"📋 CANDIDATURA — {bando['titolo'].upper()}",
            color=discord.Color.from_rgb(255, 107, 53),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.set_author(
            name=f"{interaction.user.display_name} ({interaction.user})",
            icon_url=interaction.user.display_avatar.url
        )
        for label, valore in campi.items():
            embed.add_field(name=label, value=valore, inline=False)
        embed.set_footer(text=f"Bando: {bando['titolo']} | ID candidato: {interaction.user.id}")

        canale = interaction.guild.get_channel(CH_BANDI_CANDIDATURE)
        if canale:
            view = ViewEsitoBandoCustom(interaction.user.id, self.key)
            await canale.send(embed=embed, view=view)

        await interaction.response.send_message(
            f"✅ **Candidatura per {bando['titolo']} inviata!**\nRiceverai una risposta dallo staff.",
            ephemeral=True
        )


# ─── VIEW ESITO BANDO CUSTOM (Accetta/Rifiuta) ────────────────────────────────

class ViewEsitoBandoCustom(discord.ui.View):
    def __init__(self, candidato_id: int, key: str):
        super().__init__(timeout=None)
        self.candidato_id = candidato_id
        self.key = key

    @discord.ui.button(label="✅ Accetta", style=discord.ButtonStyle.success, custom_id="bandocustom_accetta")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.name.lower() in ["staff", "admin", "developer", "direttore"] for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai i permessi.", ephemeral=True)
        bando     = bandi_personalizzati.get(self.key, {})
        nome      = bando.get("titolo", self.key)
        candidato = interaction.guild.get_member(self.candidato_id)
        canale_esiti = interaction.guild.get_channel(CH_BANDI_ESITI)
        embed = discord.Embed(
            title=f"✅ CANDIDATURA ACCETTATA — {nome.upper()}",
            color=discord.Color.green(), timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="Candidato", value=candidato.mention if candidato else f"ID: {self.candidato_id}", inline=True)
        embed.add_field(name="Bando", value=nome, inline=True)
        embed.add_field(name="Approvato da", value=interaction.user.mention, inline=True)
        if canale_esiti:
            await canale_esiti.send(embed=embed)
        if candidato:
            try:
                dm = discord.Embed(
                    title=f"✅ Candidatura Accettata — {nome}",
                    description=f"La tua candidatura per **{nome}** è stata **accettata**.\nContatta lo staff per ulteriori informazioni.",
                    color=discord.Color.green()
                )
                dm.set_thumbnail(url=LOGO_SERVER)
                await candidato.send(embed=dm)
            except Exception:
                pass
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"✅ Candidatura accettata.", ephemeral=True)

    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.danger, custom_id="bandocustom_rifiuta")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.name.lower() in ["staff", "admin", "developer", "direttore"] for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai i permessi.", ephemeral=True)
        bando     = bandi_personalizzati.get(self.key, {})
        nome      = bando.get("titolo", self.key)
        candidato = interaction.guild.get_member(self.candidato_id)
        canale_esiti = interaction.guild.get_channel(CH_BANDI_ESITI)
        embed = discord.Embed(
            title=f"❌ CANDIDATURA RIFIUTATA — {nome.upper()}",
            color=discord.Color.red(), timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="Candidato", value=candidato.mention if candidato else f"ID: {self.candidato_id}", inline=True)
        embed.add_field(name="Bando", value=nome, inline=True)
        embed.add_field(name="Rifiutato da", value=interaction.user.mention, inline=True)
        if canale_esiti:
            await canale_esiti.send(embed=embed)
        if candidato:
            try:
                dm = discord.Embed(
                    title=f"❌ Candidatura Rifiutata — {nome}",
                    description=f"Purtroppo la tua candidatura per **{nome}** è stata **rifiutata**.\nPuoi riprovare in futuro!",
                    color=discord.Color.red()
                )
                dm.set_thumbnail(url=LOGO_SERVER)
                await candidato.send(embed=dm)
            except Exception:
                pass
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(f"❌ Candidatura rifiutata.", ephemeral=True)


# ─── SELECT BANDI PERSONALIZZATI ─────────────────────────────────────────────

class SelectBandoCustom(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=b["titolo"][:50],
                value=key,
                emoji="📋",
                description=b["descrizione"][:50]
            )
            for key, b in list(bandi_personalizzati.items())[:25]
        ]
        if not options:
            options = [discord.SelectOption(label="Nessun bando attivo", value="__vuoto__", emoji="📭")]
        super().__init__(
            placeholder="📋 Seleziona un bando personalizzato...",
            min_values=1, max_values=1, options=options,
            custom_id="select_bando_custom"
        )

    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]
        if key == "__vuoto__":
            return await interaction.response.send_message("ℹ️ Non ci sono bandi attivi al momento.", ephemeral=True)
        if key not in bandi_personalizzati:
            return await interaction.response.send_message("❌ Bando non trovato.", ephemeral=True)
        modal = ModalCandidaturaBandoCustom(key)
        await interaction.response.send_modal(modal)


# ─── VIEW PANNELLO BANDI (con bottoni staff) ──────────────────────────────────

class ViewBandi(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # Select menu bandi personalizzati (se ce ne sono)
        if bandi_personalizzati:
            self.add_item(SelectBandoCustom())

    @discord.ui.button(
        label="➕ Crea Bando",
        style=discord.ButtonStyle.success,
        custom_id="bandi_crea",
        row=2
    )
    async def crea_bando(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _ha_ruolo_bandi(interaction):
            return await interaction.response.send_message(
                "❌ Non hai il permesso per creare bandi.", ephemeral=True
            )
        await interaction.response.send_modal(ModalCreaBando())

    @discord.ui.button(
        label="🗑️ Elimina Bando",
        style=discord.ButtonStyle.danger,
        custom_id="bandi_elimina",
        row=2
    )
    async def elimina_bando(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not _ha_ruolo_bandi(interaction):
            return await interaction.response.send_message(
                "❌ Non hai il permesso per eliminare bandi.", ephemeral=True
            )
        if not bandi_personalizzati:
            return await interaction.response.send_message(
                "ℹ️ Non ci sono bandi personalizzati da eliminare.", ephemeral=True
            )
        # Mostra un select per scegliere quale bando eliminare
        view = ViewEliminaBando()
        await interaction.response.send_message(
            "🗑️ **Seleziona il bando da eliminare:**",
            view=view,
            ephemeral=True
        )


class SelectEliminaBando(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=b["titolo"][:50], value=key, emoji="🗑️")
            for key, b in list(bandi_personalizzati.items())[:25]
        ]
        super().__init__(
            placeholder="Scegli il bando da eliminare...",
            min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not _ha_ruolo_bandi(interaction):
            return await interaction.response.send_message("❌ Permesso negato.", ephemeral=True)
        key = self.values[0]
        nome = bandi_personalizzati.pop(key, {}).get("titolo", key)
        await interaction.response.send_message(
            f"✅ **Bando `{nome}` eliminato con successo.**", ephemeral=True
        )


class ViewEliminaBando(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(SelectEliminaBando())


# ─── SISTEMA CANDIDATURE DAL FORUM BANDI ──────────────────────────────────────
# Quando un player scrive in un thread del canale forum Bandi-Lavorativi,
# il bot: 1) manda la candidatura nel log con bottoni Accetta/Rifiuta
#          2) cancella il thread dal forum

class ViewEsitoForumBando(discord.ui.View):
    """Bottoni Accetta/Rifiuta che appaiono nel log bandi per le candidature da forum."""

    def __init__(self, candidato_id: int, titolo_bando: str, thread_nome: str):
        super().__init__(timeout=None)
        self.candidato_id = candidato_id
        self.titolo_bando = titolo_bando
        self.thread_nome  = thread_nome

    def _ha_permesso(self, interaction: discord.Interaction) -> bool:
        return any(r.id == RUOLO_STAFF_BANDI for r in interaction.user.roles)

    async def _chiudi(self, interaction: discord.Interaction):
        """Disabilita i bottoni dopo la decisione."""
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="✅ Accetta", style=discord.ButtonStyle.success, custom_id="forum_bando_accetta")
    async def accetta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._ha_permesso(interaction):
            return await interaction.response.send_message("❌ Non hai il ruolo per gestire le candidature.", ephemeral=True)

        candidato = interaction.guild.get_member(self.candidato_id)
        canale_esiti = interaction.guild.get_channel(CH_BANDI_ESITI)

        embed = discord.Embed(
            title=f"✅ CANDIDATURA ACCETTATA — {self.titolo_bando.upper()}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="👤 Candidato",    value=candidato.mention if candidato else f"ID: {self.candidato_id}", inline=True)
        embed.add_field(name="📋 Bando",        value=self.titolo_bando, inline=True)
        embed.add_field(name="✅ Approvato da", value=interaction.user.mention, inline=True)

        if canale_esiti:
            await canale_esiti.send(embed=embed)

        if candidato:
            try:
                dm = discord.Embed(
                    title=f"✅ Candidatura Accettata — {self.titolo_bando}",
                    description=f"Congratulazioni! La tua candidatura per **{self.titolo_bando}** è stata **accettata**.\nContatta lo staff per ulteriori informazioni.",
                    color=discord.Color.green()
                )
                dm.set_thumbnail(url=LOGO_SERVER)
                await candidato.send(embed=dm)
            except Exception:
                pass

        await self._chiudi(interaction)
        await interaction.response.send_message(
            f"✅ Candidatura di {candidato.mention if candidato else self.candidato_id} **accettata**.", ephemeral=True
        )

    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.danger, custom_id="forum_bando_rifiuta")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self._ha_permesso(interaction):
            return await interaction.response.send_message("❌ Non hai il ruolo per gestire le candidature.", ephemeral=True)

        candidato = interaction.guild.get_member(self.candidato_id)
        canale_esiti = interaction.guild.get_channel(CH_BANDI_ESITI)

        embed = discord.Embed(
            title=f"❌ CANDIDATURA RIFIUTATA — {self.titolo_bando.upper()}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="👤 Candidato",    value=candidato.mention if candidato else f"ID: {self.candidato_id}", inline=True)
        embed.add_field(name="📋 Bando",        value=self.titolo_bando, inline=True)
        embed.add_field(name="❌ Rifiutato da", value=interaction.user.mention, inline=True)

        if canale_esiti:
            await canale_esiti.send(embed=embed)

        if candidato:
            try:
                dm = discord.Embed(
                    title=f"❌ Candidatura Rifiutata — {self.titolo_bando}",
                    description=f"Purtroppo la tua candidatura per **{self.titolo_bando}** è stata **rifiutata**.\nPuoi riprovare in futuro!",
                    color=discord.Color.red()
                )
                dm.set_thumbnail(url=LOGO_SERVER)
                await candidato.send(embed=dm)
            except Exception:
                pass

        await self._chiudi(interaction)
        await interaction.response.send_message(
            f"❌ Candidatura di {candidato.mention if candidato else self.candidato_id} **rifiutata**.", ephemeral=True
        )


@bot.event
async def on_message(message: discord.Message):
    """Intercetta i messaggi nei thread del forum Bandi-Lavorativi.
    
    Struttura del forum:
    - Ogni thread/post è un bando con il modulo già scritto dal bot/staff
    - Il cittadino copia il modello, lo compila e lo invia come messaggio nel thread
    - Il bot salva la candidatura nel log, cancella SOLO il messaggio del cittadino
      (il thread/post originale rimane intatto)
    """
    # Ignora i messaggi del bot stesso
    if message.author.bot:
        await bot.process_commands(message)
        return

    # Controlla se il messaggio è in un thread figlio del forum bandi
    if (
        isinstance(message.channel, discord.Thread)
        and message.channel.parent_id == CH_FORUM_BANDI
    ):
        thread       = message.channel
        titolo_bando = thread.name  # nome del post del forum = nome del bando

        # Costruisce l'embed della candidatura per il log
        log_canale = message.guild.get_channel(CH_BANDI_CANDIDATURE)
        if log_canale:
            embed = discord.Embed(
                title=f"📋 NUOVA CANDIDATURA — {titolo_bando.upper()}",
                color=discord.Color.from_rgb(255, 107, 53),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=LOGO_SERVER)
            embed.set_author(
                name=f"{message.author.display_name} ({message.author})",
                icon_url=message.author.display_avatar.url
            )

            # Il testo compilato dal cittadino — lo mettiamo in un campo dedicato
            testo = message.content[:1020] if message.content else "_Nessun testo._"
            embed.add_field(
                name="📝 Modulo compilato",
                value=testo,
                inline=False
            )

            # Allegati (screenshot, documenti, ecc.)
            if message.attachments:
                allegati = "\n".join(a.url for a in message.attachments[:5])
                embed.add_field(name="📎 Allegati", value=allegati, inline=False)

            embed.add_field(name="📌 Bando",    value=titolo_bando,           inline=True)
            embed.add_field(name="👤 Candidato", value=message.author.mention, inline=True)
            embed.set_footer(text=f"ID candidato: {message.author.id}")

            view = ViewEsitoForumBando(message.author.id, titolo_bando, thread.name)
            await log_canale.send(embed=embed, view=view)

        # Cancella SOLO il messaggio del cittadino, il thread/post rimane intatto
        try:
            await message.delete()
        except Exception:
            pass

        return  # non processare come comando

    await bot.process_commands(message)




# --- COMANDI PREFIX FALLBACK (funzionano subito senza sync) ---

@bot.command(name="dormi")
async def dormi_prefix(ctx):
    uid = ctx.author.id
    if uid in personaggi_addormentati:
        return await ctx.send("😴 Stai già dormendo! Usa `!sveglia` per alzarti.", delete_after=10)
    personaggi_addormentati.add(uid)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name=f"😴  {ctx.author.display_name} si è addormentato/a", icon_url=ctx.author.display_avatar.url)
    embed.description = (
        "🛏️ | **PERSONAGGIO ADDORMENTATO**\n\n"
        "➢ Il tuo personaggio sta dormendo.\n"
        "➢ Durante il sonno **non puoi usare comandi**.\n"
        "➢ **Fame e sete non scendono** mentre dormi.\n\n"
        "*Usa `!sveglia` quando vuoi alzarti.*"
    )
    embed.set_footer(text=f"Addormentato alle {datetime.now().strftime('%H:%M')} del {datetime.now().strftime('%d/%m/%Y')}")
    await ctx.send(embed=embed)

@bot.command(name="sveglia")
async def sveglia_prefix(ctx):
    uid = ctx.author.id
    if uid not in personaggi_addormentati:
        return await ctx.send("☀️ Il tuo personaggio è già sveglio!", delete_after=10)
    personaggi_addormentati.discard(uid)
    b = _init_bisogni(uid)
    barra_f = _barra_fame(b["fame"], FAME_MAX)
    barra_s = _barra_sete(b["sete"], SETE_MAX)
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
    embed.set_author(name=f"☀️  {ctx.author.display_name} si è svegliato/a", icon_url=ctx.author.display_avatar.url)
    embed.description = (
        "🌅 | **BUONGIORNO!**\n\n"
        "➢ Il tuo personaggio si è svegliato.\n"
        "➢ Puoi di nuovo usare tutti i comandi.\n\n"
        f"🍽️ **FAME**\n{barra_f}  `{b['fame']}/{FAME_MAX}` — {_stato_testo(b['fame'])}\n\n"
        f"💧 **SETE**\n{barra_s}  `{b['sete']}/{SETE_MAX}` — {_stato_testo(b['sete'])}"
    )
    embed.set_footer(text=f"Svegliato alle {datetime.now().strftime('%H:%M')} del {datetime.now().strftime('%d/%m/%Y')}")
    await ctx.send(embed=embed)


# ══════════════════════════════════════════════════════════════
# 🔫  SISTEMA ARMERIA
# ══════════════════════════════════════════════════════════════

# Stock armeria: {nome_arma: {"prezzo": int, "quantita": int}}

def _is_direttore_armeria(member: discord.Member) -> bool:
    nomi = [r.name.lower() for r in member.roles]
    return (
        member.guild_permissions.administrator
        or any("direttore armeria" in n or "armeria" in n for n in nomi)
        or _ha_ruolo(member, _KW_STAFF)
    )

def _armi_disponibili() -> list:
    return [nome for nome, dati in oggetti_creati.items() if dati.get("categoria") in CATEGORIE_ARMI]


class ArmeriaPrezzoModal(discord.ui.Modal, title="💰 Modifica Prezzo"):
    prezzo = discord.ui.TextInput(label="Nuovo prezzo ($)", placeholder="es. 5000", min_length=1, max_length=10)
    def __init__(self, nome_arma: str):
        super().__init__()
        self.nome_arma = nome_arma
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.prezzo.value.strip())
            if val < 0: raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Prezzo non valido.", ephemeral=True)
        if self.nome_arma not in stock_armeria:
            stock_armeria[self.nome_arma] = {"prezzo": val, "quantita": 0}
        else:
            stock_armeria[self.nome_arma]["prezzo"] = val
        _salva_dati()
        await interaction.response.send_message(f"✅ Prezzo di **{self.nome_arma}** → **{val}$**.", ephemeral=True)


class ArmeriaQtyModal(discord.ui.Modal, title="📦 Modifica Quantità"):
    qty = discord.ui.TextInput(label="Nuova quantità", placeholder="es. 10", min_length=1, max_length=6)
    def __init__(self, nome_arma: str):
        super().__init__()
        self.nome_arma = nome_arma
    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.qty.value.strip())
            if val < 0: raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Quantità non valida.", ephemeral=True)
        if self.nome_arma not in stock_armeria:
            stock_armeria[self.nome_arma] = {"prezzo": 0, "quantita": val}
        else:
            stock_armeria[self.nome_arma]["quantita"] = val
        _salva_dati()
        await interaction.response.send_message(f"✅ Quantità di **{self.nome_arma}** → **{val}**.", ephemeral=True)


class ArmeriaAggiungiModal(discord.ui.Modal, title="➕ Aggiungi Arma allo Stock"):
    prezzo = discord.ui.TextInput(label="Prezzo ($)", placeholder="es. 5000", min_length=1, max_length=10)
    qty    = discord.ui.TextInput(label="Quantità", placeholder="es. 10", min_length=1, max_length=6)
    def __init__(self, nome_arma: str):
        super().__init__()
        self.nome_arma = nome_arma
    async def on_submit(self, interaction: discord.Interaction):
        try:
            p = int(self.prezzo.value.strip())
            q = int(self.qty.value.strip())
            if p < 0 or q < 0: raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Valori non validi.", ephemeral=True)
        stock_armeria[self.nome_arma] = {"prezzo": p, "quantita": q}
        _salva_dati()
        await interaction.response.send_message(
            f"✅ **{self.nome_arma}** aggiunta allo stock!\n💰 {p}$ | 📦 x{q}", ephemeral=True
        )


class ArmeriaSottoView(discord.ui.View):
    def __init__(self, nome_arma: str, direttore: discord.Member):
        super().__init__(timeout=120)
        self.nome_arma = nome_arma
        self.direttore = direttore

    @discord.ui.button(label="💰 Cambia Prezzo", style=discord.ButtonStyle.primary)
    async def cambia_prezzo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        await interaction.response.send_modal(ArmeriaPrezzoModal(self.nome_arma))

    @discord.ui.button(label="📦 Cambia Quantità", style=discord.ButtonStyle.secondary)
    async def cambia_qty(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        await interaction.response.send_modal(ArmeriaQtyModal(self.nome_arma))

    @discord.ui.button(label="🗑️ Rimuovi dallo Stock", style=discord.ButtonStyle.danger)
    async def rimuovi(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        stock_armeria.pop(self.nome_arma, None)
        _salva_dati()
        await interaction.response.send_message(f"🗑️ **{self.nome_arma}** rimossa dallo stock.", ephemeral=True)


def _make_arma_select_view(direttore, armi, modifica_stock):
    class ArmaSelectView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            opzioni = [discord.SelectOption(label=a[:100], value=a, emoji="🔫") for a in armi[:25]]
            self.add_item(self._make_select(opzioni))

        def _make_select(self, opzioni):
            _dir = direttore
            _mod = modifica_stock

            class ArmaSelect(discord.ui.Select):
                def __init__(self_inner):
                    super().__init__(placeholder="🔫 Seleziona un'arma...", options=opzioni)
                async def callback(self_inner, inter: discord.Interaction):
                    if inter.user.id != _dir.id:
                        return await inter.response.send_message("❌ Non sei il direttore!", ephemeral=True)
                    nome = self_inner.values[0]
                    if _mod:
                        info = stock_armeria.get(nome, {"prezzo": 0, "quantita": 0})
                        embed = discord.Embed(title=f"🔫 {nome}", color=discord.Color.red())
                        embed.add_field(name="💰 Prezzo", value=f"**{info['prezzo']}$**", inline=True)
                        embed.add_field(name="📦 Quantità", value=f"**{info['quantita']}**", inline=True)
                        embed.set_author(name="🏪 Gestione Armeria", icon_url=LOGO_SERVER)
                        await inter.response.send_message(embed=embed, view=ArmeriaSottoView(nome, _dir), ephemeral=True)
                    else:
                        await inter.response.send_modal(ArmeriaAggiungiModal(nome))
            return ArmaSelect()
    return ArmaSelectView()


class ArmeriaGestioneView(discord.ui.View):
    def __init__(self, direttore: discord.Member):
        super().__init__(timeout=120)
        self.direttore = direttore

    @discord.ui.button(label="➕ Aggiungi Arma", style=discord.ButtonStyle.success, emoji="➕")
    async def aggiungi(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        non_in_stock = [a for a in _armi_disponibili() if a not in stock_armeria]
        if not non_in_stock:
            return await interaction.response.send_message("✅ Tutte le armi sono già in stock!", ephemeral=True)
        await interaction.response.send_message("➕ **Scegli quale arma aggiungere:**",
            view=_make_arma_select_view(self.direttore, non_in_stock, False), ephemeral=True)

    @discord.ui.button(label="✏️ Modifica Stock", style=discord.ButtonStyle.primary, emoji="✏️")
    async def modifica(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        if not stock_armeria:
            return await interaction.response.send_message("❌ Stock vuoto!", ephemeral=True)
        await interaction.response.send_message("✏️ **Scegli quale arma modificare:**",
            view=_make_arma_select_view(self.direttore, list(stock_armeria.keys()), True), ephemeral=True)

    @discord.ui.button(label="📋 Visualizza Stock", style=discord.ButtonStyle.secondary, emoji="📋")
    async def visualizza(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.direttore.id:
            return await interaction.response.send_message("❌ Non sei il direttore!", ephemeral=True)
        if not stock_armeria:
            return await interaction.response.send_message("❌ Stock vuoto.", ephemeral=True)
        embed = discord.Embed(title="🏪 Stock Armeria", color=discord.Color.red())
        embed.set_author(name="Gestione Armeria — Vista Direttore", icon_url=LOGO_SERVER)
        righe = "\n".join(f"🔫 **{n}** — 💰 {d['prezzo']}$ | 📦 x{d['quantita']}" for n, d in stock_armeria.items())
        embed.description = righe
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="armeria-gestione", description="🔫 Gestisci lo stock dell'armeria (Solo Direttore Armeria)")
async def armeria_gestione(interaction: discord.Interaction):
    membro = await _get_member(interaction)
    if not _is_direttore_armeria(membro):
        return await interaction.response.send_message("❌ Accesso negato. Riservato al Direttore dell'Armeria.", ephemeral=True)
    embed = discord.Embed(title="🏪 | GESTIONE ARMERIA", color=discord.Color.red(), timestamp=datetime.now())
    embed.set_author(name="Eclipse City RP® — Armeria", icon_url=LOGO_SERVER)
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "➢ **Aggiungi** nuove armi allo stock con prezzo e quantità\n"
        "➢ **Modifica** prezzo o quantità di armi già presenti\n"
        "➢ **Rimuovi** armi dallo stock\n"
        "➢ **Visualizza** lo stock attuale\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await interaction.response.send_message(embed=embed, view=ArmeriaGestioneView(membro), ephemeral=True)


def _make_vendita_select_view(direttore, cliente):
    armi_stock = [n for n, d in stock_armeria.items() if d.get("quantita", 0) > 0]

    class VenditaView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            opzioni = [
                discord.SelectOption(
                    label=n[:100], value=n,
                    description=f"💰 {stock_armeria[n]['prezzo']}$ | 📦 x{stock_armeria[n]['quantita']}",
                    emoji="🔫"
                ) for n in armi_stock[:25]
            ]
            self.add_item(self._make_select(opzioni))

        def _make_select(self, opzioni):
            _dir = direttore
            _cli = cliente

            class VenditaSelect(discord.ui.Select):
                def __init__(self_inner):
                    super().__init__(placeholder="🔫 Seleziona arma da vendere...", options=opzioni)
                async def callback(self_inner, inter: discord.Interaction):
                    if inter.user.id != _dir.id:
                        return await inter.response.send_message("❌ Non sei il direttore!", ephemeral=True)
                    nome = self_inner.values[0]
                    info = stock_armeria.get(nome)
                    if not info or info["quantita"] <= 0:
                        return await inter.response.send_message("❌ Arma esaurita!", ephemeral=True)
                    prezzo = info["prezzo"]
                    saldo = portafogli.get(_cli.id, 0)
                    if saldo < prezzo:
                        return await inter.response.send_message(
                            f"❌ **{_cli.display_name}** non ha abbastanza soldi!\n💰 Serve: **{prezzo}$** | Ha: **{saldo}$**",
                            ephemeral=True
                        )
                    portafogli[_cli.id] = saldo - prezzo
                    _paga_direttore("armeria", prezzo)
                    stock_armeria[nome]["quantita"] -= 1
                    if inventari.get(_cli.id) is None:
                        inventari[_cli.id] = []
                    inventari[_cli.id].append(nome)
                    _salva_dati()

                    embed = discord.Embed(title="🔫 | ACQUISTO ARMERIA", color=discord.Color.red(), timestamp=datetime.now())
                    embed.set_author(name="Eclipse City RP® — Armeria", icon_url=LOGO_SERVER)
                    embed.set_thumbnail(url=LOGO_SERVER)
                    embed.description = (
                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🔫 **Arma** ➢ {nome}\n"
                        f"👤 **Cliente** ➢ {_cli.mention}\n"
                        f"💰 **Pagato** ➢ **{prezzo}$**\n"
                        f"📦 **Stock rimasto** ➢ {stock_armeria[nome]['quantita']}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━"
                    )
                    embed.set_footer(text=f"Vendita effettuata da {inter.user.display_name}")
                    await inter.response.send_message(embed=embed)
                    await log_azione(inter.guild, inter.user, "🔫 Vendita Armeria", f"**{nome}** → {_cli.mention} | {prezzo}$", discord.Color.red())
            return VenditaSelect()
    return VenditaView()


@bot.tree.command(name="armeria-vendi", description="🔫 Vendi un'arma a un cliente (Solo Direttore Armeria)")
@app_commands.describe(cliente="Il cliente a cui vendere l'arma")
async def armeria_vendi(interaction: discord.Interaction, cliente: discord.Member):
    membro = await _get_member(interaction)
    if not _is_direttore_armeria(membro):
        return await interaction.response.send_message("❌ Accesso negato. Riservato al Direttore dell'Armeria.", ephemeral=True)
    if not stock_armeria or all(d.get("quantita", 0) == 0 for d in stock_armeria.values()):
        return await interaction.response.send_message("❌ Stock vuoto! Usa `/armeria-gestione` prima.", ephemeral=True)

    embed = discord.Embed(title="🔫 | VENDITA ARMERIA", color=discord.Color.red(), timestamp=datetime.now())
    embed.set_author(name="Eclipse City RP® — Armeria", icon_url=LOGO_SERVER)
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **Cliente** ➢ {cliente.mention}\n"
        f"💰 **Saldo cliente** ➢ **{portafogli.get(cliente.id, 0)}$**\n\n"
        f"➢ Seleziona l'arma da vendere qui sotto.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await interaction.response.send_message(embed=embed, view=_make_vendita_select_view(membro, cliente), ephemeral=True)

# ══════════════════════════════════════════════
# 🚔 ARMADETTO PD — Gestione kit polizia
# ══════════════════════════════════════════════
# ══════════════════════════════════════════════
# 🗃️ ARMADIETTO FDO — Kit per MSPD / FBI
# ══════════════════════════════════════════════
# armadietto_fdo = { "nome_kit": {"categoria": str, "contenuto": str, "peso": float, "creato_da": str} }
armadietto_fdo: dict = {
    "🚔 Kit Pattuglia Standard": {
        "categoria": "MSPD",
        "contenuto": (
            "Radio MOTOROLA APX 8000 CRIPTATA (650g)\n"
            "Pistola pesante COLT 1911 con torcia e caricatore pieno (1.5kg)\n"
            "Axon Bodycam con GPS (200g)\n"
            "Cinturone in pelle vuoto con fondina taser, pistola, 2 porta-caricatori (1.3kg)\n"
            "2 Caricatori aggiuntivi (500g)\n"
            "Taser 7 a dardo e corpo a corpo (400g)\n"
            "1 Paio di manette con 2 chiavi (300g)\n"
            "Bastone telescopico in acciaio / manganello (500g)\n"
            "10 Fascette (50g)\n"
            "Penna e taccuino (200g)\n"
            "Coltellino svizzero (150g)\n"
            "Torcia (300g)\n"
            "Giubbotto antiproiettile standard IIA (2.2kg)\n"
            "Kit primo soccorso (300g)\n"
            "Guanti tattici anti-taglio (100g)\n"
            "Distintivo di polizia (100g)\n"
            "Fondina da caviglia (125g)\n"
            "Glock 43 con caricatore carico (600g)"
        ),
        "peso": 9.475,
        "creato_da": "Sistema"
    }
}

CATEGORIE_FDO = ["MSPD", "FBI"]

def _kit_per_categoria(cat: str) -> dict:
    return {k: v for k, v in armadietto_fdo.items() if v.get("categoria") == cat}


class KitFdoModal(discord.ui.Modal, title="🗃️ Crea Kit Armadietto"):
    nome_kit   = discord.ui.TextInput(label="Nome del kit", placeholder="Es: Kit Pattuglia Standard", max_length=60)
    categoria  = discord.ui.TextInput(label="Categoria (MSPD / FBI)", placeholder="MSPD", max_length=10)
    contenuto1 = discord.ui.TextInput(label="Contenuto — parte 1", style=discord.TextStyle.paragraph, placeholder="Es: Glock 17, Manette, Radio...", max_length=1000)
    contenuto2 = discord.ui.TextInput(label="Contenuto — parte 2 (opzionale)", style=discord.TextStyle.paragraph, required=False, max_length=1000)
    peso       = discord.ui.TextInput(label="Peso totale (kg)", placeholder="Es: 4.5", max_length=6)

    async def on_submit(self, interaction: discord.Interaction):
        cat = self.categoria.value.strip().upper()
        if cat not in CATEGORIE_FDO:
            return await interaction.response.send_message(f"❌ Categoria non valida. Usa: {', '.join(CATEGORIE_FDO)}", ephemeral=True)
        try:
            p = float(self.peso.value.replace(",", "."))
            if p <= 0: raise ValueError
        except ValueError:
            return await interaction.response.send_message("❌ Peso non valido.", ephemeral=True)
        nome = self.nome_kit.value.strip()
        contenuto = self.contenuto1.value.strip()
        if self.contenuto2.value.strip():
            contenuto += "\n" + self.contenuto2.value.strip()
        armadietto_fdo[nome] = {"categoria": cat, "contenuto": contenuto, "peso": p, "creato_da": interaction.user.display_name}
        _salva_dati()
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title="✅ Kit creato")
        embed.add_field(name="📦 Nome", value=nome, inline=True)
        embed.add_field(name="🏷️ Categoria", value=cat, inline=True)
        embed.add_field(name="⚖️ Peso", value=f"{p} kg", inline=True)
        embed.add_field(name="📋 Contenuto", value=contenuto[:1024], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await log_staff(interaction.guild, f"🗃️ {interaction.user.mention} ha creato il kit **{nome}** [{cat}] ({p}kg)", discord.Color.from_rgb(255, 107, 53))


class ArmadiettoFdoCatView(discord.ui.View):
    """Scelta categoria — mostra poi la view della categoria."""
    def __init__(self, uid: int, azione: str):
        super().__init__(timeout=60)
        self.uid = uid
        self.azione = azione  # "lista" | "assegna" | "elimina"

    async def _mostra_cat(self, interaction: discord.Interaction, cat: str):
        if interaction.user.id != self.uid: return await interaction.response.send_message("❌", ephemeral=True)
        kit_cat = _kit_per_categoria(cat)
        if not kit_cat and self.azione != "crea":
            return await interaction.response.send_message(f"❌ Nessun kit in {cat}.", ephemeral=True)
        if self.azione == "lista":
            desc = ""
            for nome, dati in kit_cat.items():
                desc += f"**{nome}**\n📋 {dati['contenuto'][:500]}\n⚖️ {dati['peso']} kg | 👤 {dati['creato_da']}\n\n"
            embed = discord.Embed(title=f"🗃️ Kit {cat}", description=desc[:4000] or "Nessun kit.", color=discord.Color.from_rgb(255, 107, 53))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif self.azione == "elimina":
            opzioni = [discord.SelectOption(label=n[:100], value=n) for n in list(kit_cat.keys())[:25]]
            class ElSel(discord.ui.Select):
                def __init__(s): super().__init__(placeholder="Scegli kit...", options=opzioni)
                async def callback(s, inter):
                    armadietto_fdo.pop(s.values[0], None); _salva_dati()
                    await inter.response.send_message(f"🗑️ Kit **{s.values[0]}** eliminato.", ephemeral=True)
            v = discord.ui.View(timeout=60); v.add_item(ElSel())
            await interaction.response.send_message("Scegli il kit da eliminare:", view=v, ephemeral=True)
        elif self.azione == "assegna":
            opzioni = [discord.SelectOption(label=n[:100], value=n) for n in list(kit_cat.keys())[:25]]
            uid = self.uid
            class AsSel(discord.ui.Select):
                def __init__(s): super().__init__(placeholder="Scegli kit...", options=opzioni)
                async def callback(s, inter):
                    nome_kit = s.values[0]
                    class AgenteModal(discord.ui.Modal, title="👤 A chi assegnare il kit?"):
                        agente_nome = discord.ui.TextInput(label="Nome Discord dell'agente", placeholder="Es: Mario123 o ID", max_length=100)
                        async def on_submit(sm, inter2):
                            valore = sm.agente_nome.value.strip()
                            membro = None
                            if valore.isdigit():
                                membro = inter2.guild.get_member(int(valore))
                                if not membro:
                                    try: membro = await inter2.guild.fetch_member(int(valore))
                                    except: pass
                            if not membro:
                                vl = valore.lower()
                                membro = discord.utils.find(lambda m: m.name.lower() == vl or m.display_name.lower() == vl, inter2.guild.members)
                            if not membro:
                                return await inter2.response.send_message(f"❌ **{valore}** non trovato.", ephemeral=True)
                            dati = armadietto_fdo[nome_kit]
                            item_kit = f"🗃️ {nome_kit}"
                            if membro.id not in inventari: inventari[membro.id] = []
                            inventari[membro.id].append(item_kit)
                            PESI_OGGETTI[item_kit] = 0.0
                            _salva_dati()
                            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title="📤 Kit Assegnato")
                            embed.add_field(name="👤 Agente", value=membro.mention, inline=True)
                            embed.add_field(name="🏷️ Categoria", value=dati["categoria"], inline=True)
                            embed.add_field(name="📦 Kit", value=nome_kit, inline=False)
                            embed.add_field(name="📋 Contenuto", value=dati["contenuto"][:1024], inline=False)
                            embed.add_field(name="⚖️ Peso dotazione", value=f"{dati['peso']} kg (non pesa nell'inventario)", inline=False)
                            await inter2.response.send_message(embed=embed)
                            await log_staff(inter2.guild, f"📤 {inter2.user.mention} → kit **{nome_kit}** [{dati['categoria']}] a {membro.mention}", discord.Color.from_rgb(255, 107, 53))
                    await inter.response.send_modal(AgenteModal())
            v = discord.ui.View(timeout=60); v.add_item(AsSel())
            await interaction.response.send_message("Scegli il kit:", view=v, ephemeral=True)

    @discord.ui.button(label="🚔 MSPD", style=discord.ButtonStyle.primary)
    async def cat_mspd(self, inter, btn): await self._mostra_cat(inter, "MSPD")

    @discord.ui.button(label="🕵️ FBI", style=discord.ButtonStyle.danger)
    async def cat_fbi(self, inter, btn): await self._mostra_cat(inter, "FBI")


class ArmadiettoFdoView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=120)
        self.uid = uid

    @discord.ui.button(label="➕ Crea Kit", style=discord.ButtonStyle.primary)
    async def crea_kit(self, inter, btn):
        if inter.user.id != self.uid: return await inter.response.send_message("❌", ephemeral=True)
        await inter.response.send_modal(KitFdoModal())

    @discord.ui.button(label="📋 Lista Kit", style=discord.ButtonStyle.secondary)
    async def lista_kit(self, inter, btn):
        if inter.user.id != self.uid: return await inter.response.send_message("❌", ephemeral=True)
        await inter.response.send_message("Scegli la categoria:", view=ArmadiettoFdoCatView(self.uid, "lista"), ephemeral=True)

    @discord.ui.button(label="🗑️ Elimina Kit", style=discord.ButtonStyle.danger)
    async def elimina_kit(self, inter, btn):
        if inter.user.id != self.uid: return await inter.response.send_message("❌", ephemeral=True)
        await inter.response.send_message("Scegli la categoria:", view=ArmadiettoFdoCatView(self.uid, "elimina"), ephemeral=True)

    @discord.ui.button(label="📤 Assegna Kit", style=discord.ButtonStyle.success, row=1)
    async def assegna_kit(self, inter, btn):
        if inter.user.id != self.uid: return await inter.response.send_message("❌", ephemeral=True)
        await inter.response.send_message("Scegli la categoria:", view=ArmadiettoFdoCatView(self.uid, "assegna"), ephemeral=True)

    @discord.ui.button(label="🗑️ Togli Kit", style=discord.ButtonStyle.danger, row=1)
    async def togli_kit(self, inter, btn):
        if inter.user.id != self.uid: return await inter.response.send_message("❌", ephemeral=True)
        uid = self.uid
        kit_in_inv = [item for item in inventari.get(inter.user.id, []) if item.startswith("🗃️")]
        if not kit_in_inv:
            return await inter.response.send_message("❌ Non hai kit nell'inventario.", ephemeral=True)
        opzioni = [discord.SelectOption(label=n[:100], value=n) for n in kit_in_inv[:25]]
        class TogliSel(discord.ui.Select):
            def __init__(s): super().__init__(placeholder="Scegli kit da riconsegnare...", options=opzioni)
            async def callback(s, inter2):
                if inter2.user.id != uid: return await inter2.response.send_message("❌", ephemeral=True)
                item_kit = s.values[0]
                if item_kit in inventari.get(inter2.user.id, []):
                    inventari[inter2.user.id].remove(item_kit)
                _salva_dati()
                nome = item_kit.replace("🗃️ ", "")
                await inter2.response.send_message(f"✅ Kit **{nome}** riconsegnato.", ephemeral=True)
                await log_staff(inter2.guild, f"🗑️ {inter2.user.mention} ha riconsegnato il kit **{nome}**.", discord.Color.from_rgb(255, 107, 53))
        v = discord.ui.View(timeout=60); v.add_item(TogliSel())
        await inter.response.send_message("Scegli il kit:", view=v, ephemeral=True)


@bot.tree.command(name="armadietto-fdo", description="🗃️ Armadietto Forze dell'Ordine — kit MSPD e FBI")
@has_police_permission()
async def armadietto_fdo_cmd(interaction: discord.Interaction):
    tot = len(armadietto_fdo)
    mspd = len(_kit_per_categoria("MSPD"))
    fbi  = len(_kit_per_categoria("FBI"))
    embed = discord.Embed(title="🗃️ ARMADIETTO FDO", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_author(name="Eclipse City RP — Forze dell'Ordine", icon_url=LOGO_SERVER)
    embed.description = (
        f"**Kit totali:** {tot}\n"
        f"🚔 MSPD: {mspd} kit\n"
        f"🕵️ FBI: {fbi} kit\n\n"
        "Usa i bottoni per gestire i kit dotazione."
    )
    await interaction.response.send_message(embed=embed, view=ArmadiettoFdoView(interaction.user.id), ephemeral=True)


# ══════════════════════════════════════════════
# 🌿 RACCOLTA — Farm marijuana / cocaina
# ══════════════════════════════════════════════
raccolte_attive: dict = {}  # {uid: {"tipo": str, "inizio": datetime, "foto_url": str}}

TIPI_RACCOLTA = {
    "marijuana":  {"emoji": "🌿", "piante": 5,  "ore": 12, "item": "🌿 Marijuana",  "nome": "Marijuana"},
    "cocaina":    {"emoji": "💮", "piante": 2,  "ore": 12, "item": "💮 Cocaina",    "nome": "Cocaina"},
}


@bot.tree.command(name="inizia-raccolta", description="🌿 Inizia la raccolta di marijuana o cocaina (richiede foto)")
async def inizia_raccolta(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid in raccolte_attive:
        r = raccolte_attive[uid]
        minuti = int((datetime.now() - r["inizio"]).total_seconds() // 60)
        return await interaction.response.send_message(
            f"❌ Hai già una raccolta di **{r['tipo'].capitalize()}** attiva da {minuti} min. Usa `/fine-raccolta` per raccogliere.", ephemeral=True
        )

    class RaccoltaModal(discord.ui.Modal, title="🌿 Inizia Raccolta"):
        tipo_pianta = discord.ui.TextInput(label="Tipo (marijuana / cocaina)", placeholder="marijuana", max_length=20)
        foto_url    = discord.ui.TextInput(label="URL foto della pianta", placeholder="https://...", max_length=500)

        async def on_submit(self_m, inter: discord.Interaction):
            tipo = self_m.tipo_pianta.value.strip().lower()
            if tipo not in TIPI_RACCOLTA:
                return await inter.response.send_message("❌ Tipo non valido. Usa: marijuana / cocaina", ephemeral=True)
            foto = self_m.foto_url.value.strip()
            dati = TIPI_RACCOLTA[tipo]
            raccolte_attive[uid] = {"tipo": tipo, "inizio": datetime.now(), "foto_url": foto}
            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title=f"{dati['emoji']} Raccolta Avviata", timestamp=datetime.now())
            embed.set_author(name=inter.user.display_name, icon_url=inter.user.display_avatar.url)
            embed.description = (
                f"**Pianta:** {dati['nome']}\n"
                f"**Produzione:** {dati['piante']} piante ogni **{dati['ore']} ore**\n\n"
                f"Usa `/fine-raccolta` per raccogliere le piante prodotte."
            )
            if foto.startswith("http"):
                embed.set_image(url=foto)
            await inter.response.send_message(embed=embed)
            await log_azione(inter.guild, inter.user, f"{dati['emoji']} Raccolta avviata", f"Tipo: {dati['nome']}", discord.Color.from_rgb(255, 107, 53))

    await interaction.response.send_modal(RaccoltaModal())


@bot.tree.command(name="fine-raccolta", description="🌿 Termina la raccolta e ritira le piante prodotte")
async def fine_raccolta(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid not in raccolte_attive:
        return await interaction.response.send_message("❌ Nessuna raccolta attiva. Usa `/inizia-raccolta`.", ephemeral=True)
    r = raccolte_attive.pop(uid)
    dati = TIPI_RACCOLTA[r["tipo"]]
    ore_lavorate = (datetime.now() - r["inizio"]).total_seconds() / 3600
    piante = max(1, int((ore_lavorate / dati["ore"]) * dati["piante"]))
    if uid not in inventari: inventari[uid] = []
    for _ in range(piante):
        inventari[uid].append(dati["item"])
    _salva_dati()
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title=f"{dati['emoji']} Raccolta Completata", timestamp=datetime.now())
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.description = (
        f"**Pianta:** {dati['nome']}\n"
        f"**Tempo:** {ore_lavorate:.1f} ore\n"
        f"**Raccolte:** {piante}x {dati['item']} → aggiunte all'inventario"
    )
    await interaction.response.send_message(embed=embed)
    await log_azione(interaction.guild, interaction.user, f"{dati['emoji']} Raccolta completata", f"{dati['nome']} x{piante} in {ore_lavorate:.1f}h", discord.Color.from_rgb(255, 107, 53))


# ══════════════════════════════════════════════
# 📦 NASCONDI / PRENDI OGGETTO  (foto come allegato)
# ══════════════════════════════════════════════
oggetti_nascosti: dict = {}  # {id_str: {"oggetto": str, "nascosto_da": str, "uid": int, "luogo": str, "foto_url": str, "ts": str}}
_nascondi_counter: list = [0]

# Step 1 — selezione oggetto via select menu
@bot.tree.command(name="nascondi-oggetto", description="📦 Nascondi un oggetto dal tuo inventario (allega foto del posto)")
async def nascondi_oggetto(interaction: discord.Interaction):
    uid = interaction.user.id
    items = inventari.get(uid, [])
    if not items:
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ **Inventario vuoto.** Non hai oggetti da nascondere."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    from collections import Counter
    conteggio = Counter(items)
    opzioni = [discord.SelectOption(label=f"{n} (x{q})"[:100], value=n) for n, q in list(conteggio.items())[:25]]

    embed_sel = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed_sel.set_author(name="📦 NASCONDI OGGETTO", icon_url=LOGO_SERVER)
    embed_sel.description = (
        "Seleziona l'oggetto che vuoi nascondere dal menu qui sotto.\n"
        "Dopo aver scelto ti verrà chiesto **dove** lo nascondi e di **allegare una foto** del posto."
    )
    embed_sel.set_footer(text=f"{interaction.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    class OggettoSelect(discord.ui.Select):
        def __init__(s):
            super().__init__(placeholder="🔍 Scegli l'oggetto da nascondere...", options=opzioni, min_values=1, max_values=1)
        async def callback(s, inter: discord.Interaction):
            if inter.user.id != uid:
                return await inter.response.send_message("❌ Non sei autorizzato.", ephemeral=True)
            oggetto = s.values[0]

            class NascondiStep2Modal(discord.ui.Modal, title="📦 Dove lo nascondi?"):
                luogo = discord.ui.TextInput(
                    label="Descrizione del posto",
                    style=discord.TextStyle.paragraph,
                    placeholder="Es: Dietro la roccia grande vicino al porto nord, lato sinistro...",
                    max_length=300,
                    required=True
                )
                async def on_submit(sm, inter2: discord.Interaction):
                    if oggetto not in inventari.get(uid, []):
                        return await inter2.response.send_message("❌ Non possiedi più questo oggetto.", ephemeral=True)

                    luogo_desc = sm.luogo.value.strip()

                    # Chiedi la foto come attachment nello step successivo
                    embed_foto = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
                    embed_foto.set_author(name="📸 INVIA LA FOTO DEL POSTO", icon_url=LOGO_SERVER)
                    embed_foto.description = (
                        f"✅ Posto registrato: **{luogo_desc}**\n\n"
                        "📸 **Ora allega la foto** usando il comando:\n"
                        f"```/nascondi-foto oggetto:{oggetto} luogo:{luogo_desc[:80]}```\n"
                        "oppure usa il comando `/nascondi-foto` con i parametri richiesti."
                    )
                    # Salviamo temporaneamente in attesa della foto
                    if not hasattr(bot, '_nascondi_pending'):
                        bot._nascondi_pending = {}
                    bot._nascondi_pending[uid] = {"oggetto": oggetto, "luogo": luogo_desc}
                    await inter2.response.send_message(embed=embed_foto, ephemeral=True)

            await inter.response.send_modal(NascondiStep2Modal())

    view = discord.ui.View(timeout=120)
    view.add_item(OggettoSelect())
    await interaction.response.send_message(embed=embed_sel, view=view, ephemeral=True)


@bot.tree.command(name="nascondi-foto", description="📸 Step 2: Allega la foto del posto dove hai nascosto l'oggetto")
@app_commands.describe(foto="📸 Scatta/allega la foto del posto")
async def nascondi_foto(interaction: discord.Interaction, foto: discord.Attachment):
    uid = interaction.user.id
    pending = getattr(bot, '_nascondi_pending', {})
    if uid not in pending:
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Nessuna operazione in corso. Usa prima `/nascondi-oggetto`."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if not foto.content_type or not foto.content_type.startswith("image/"):
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Il file allegato non è un'immagine valida. Riprova con una foto."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    dati_pending = pending.pop(uid)
    oggetto = dati_pending["oggetto"]
    luogo_desc = dati_pending["luogo"]

    if oggetto not in inventari.get(uid, []):
        embed = discord.Embed(color=discord.Color.red())
        embed.description = f"❌ Non possiedi più **{oggetto}** nell'inventario."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    inventari[uid].remove(oggetto)
    _nascondi_counter[0] += 1
    id_obj = str(_nascondi_counter[0])

    oggetti_nascosti[id_obj] = {
        "oggetto": oggetto,
        "nascosto_da": interaction.user.display_name,
        "uid": uid,
        "luogo": luogo_desc,
        "foto_url": foto.url,
        "ts": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    _salva_dati()

    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title="📦 OGGETTO NASCOSTO",
        timestamp=datetime.now()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.description = (
        f"**Oggetto ➢** {oggetto}\n\n"
        f"**Posto ➢** {luogo_desc}\n\n"
        f"**🔑 ID Recupero ➢** `{id_obj}`\n"
        f"*Conserva questo ID — ti servirà per recuperare l'oggetto!*"
    )
    embed.set_image(url=foto.url)
    embed.set_footer(text=f"Nascosto il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}")

    await interaction.response.send_message(embed=embed, ephemeral=True)
    await log_azione(
        interaction.guild, interaction.user,
        "📦 Oggetto nascosto",
        f"{oggetto} | Posto: {luogo_desc} | ID: {id_obj}",
        discord.Color.from_rgb(255, 107, 53)
    )


@bot.tree.command(name="prendi-oggetto", description="📦 Recupera un oggetto nascosto — allega la foto del posto e inserisci l'ID")
@app_commands.describe(
    id_oggetto="ID dell'oggetto da recuperare (es: 5)",
    foto="📸 Foto che dimostra che sei sul posto"
)
async def prendi_oggetto(interaction: discord.Interaction, id_oggetto: str, foto: discord.Attachment):
    uid = interaction.user.id
    id_str = id_oggetto.strip()

    if not foto.content_type or not foto.content_type.startswith("image/"):
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Il file allegato non è un'immagine valida. Allega una foto reale del posto."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if id_str not in oggetti_nascosti:
        embed = discord.Embed(color=discord.Color.red())
        embed.description = f"❌ Nessun oggetto trovato con ID `{id_str}`. Controlla l'ID e riprova."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    dati = oggetti_nascosti.pop(id_str)
    if uid not in inventari:
        inventari[uid] = []
    inventari[uid].append(dati["oggetto"])
    _salva_dati()

    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title="📦 OGGETTO RECUPERATO",
        timestamp=datetime.now()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.description = (
        f"**Oggetto ➢** {dati['oggetto']}\n\n"
        f"**Nascosto da ➢** {dati['nascosto_da']}\n\n"
        f"**Posto ➢** {dati['luogo']}\n\n"
        f"**Nascosto il ➢** {dati['ts']}\n\n"
        f"✅ L'oggetto è stato aggiunto al tuo inventario."
    )
    embed.set_image(url=foto.url)
    embed.set_footer(text=f"Recuperato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}")

    await interaction.response.send_message(embed=embed)
    await log_azione(
        interaction.guild, interaction.user,
        "📦 Oggetto recuperato",
        f"{dati['oggetto']} | ID: {id_str} | Nascosto da: {dati['nascosto_da']}",
        discord.Color.from_rgb(255, 107, 53)
    )


# ══════════════════════════════════════════════════════════════════
# 💜 REVOLUT — Interfaccia conto pubblica
# ══════════════════════════════════════════════════════════════════

def _registra_transazione(uid: int, segno: str, importo: int, tipo: str, controparte: str = ""):
    """Registra una transazione nello storico dell'utente (max 20 per utente)."""
    if uid not in storico_transazioni:
        storico_transazioni[uid] = []
    storico_transazioni[uid].insert(0, {
        "segno": segno,
        "importo": importo,
        "tipo": tipo,
        "controparte": controparte,
        "ts": datetime.now().strftime("%d/%m/%Y, %H:%M")
    })
    storico_transazioni[uid] = storico_transazioni[uid][:20]



def _build_revolut_embed(uid: int, member: discord.Member) -> discord.Embed:
    """Costruisce l'embed stile Revolut."""
    saldo = conti_bancari.get(uid, 0)
    transazioni = storico_transazioni.get(uid, [])

    saldo_abs = abs(saldo)
    saldo_fmt = f"{saldo_abs:,}".replace(",", ".")
    segno = "-" if saldo < 0 else ""
    colore = discord.Color.from_rgb(255, 107, 53) if saldo >= 0 else discord.Color.from_rgb(220, 50, 50)

    embed = discord.Embed(color=colore, timestamp=datetime.now())
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)

    stato = "⚠️  SALDO NEGATIVO" if saldo < 0 else "✅  Conto attivo"
    embed.description = (
        f"```\n"
        f"  Personale  ·  $ Eclipse Dollar\n"
        f"```\n"
        f"# {segno}{saldo_fmt},00 $\n"
        f"-# {stato}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"-# ➕ Aggiungi fondi　　🔀 Sposta fondi　　🏛️ Coordinate　　👜 Preleva"
    )

    if not transazioni:
        mov = "*Nessun movimento registrato ancora.*"
    else:
        mov = ""
        for t in transazioni[:6]:
            emoji = "🟢" if t["segno"] == "+" else "🔴"
            segno_v = "+" if t["segno"] == "+" else "−"
            imp_fmt = f"{t['importo']:,}".replace(",", ".")
            cp = f"  ·  {t['controparte']}" if t.get("controparte") else ""
            mov += f"{emoji}  **{t['tipo']}**{cp}\n> `{t['ts']}`　　`{segno_v}{imp_fmt} $`\n"

    embed.add_field(name="📋  Movimenti recenti", value=mov, inline=False)
    embed.set_footer(text="Eclipse City RP  ·  Pacific Bank  ·  Banca Privata", icon_url=LOGO_SERVER)
    return embed


class RevolutView(discord.ui.View):
    """Bottoni interattivi stile Revolut."""

    def __init__(self, owner_uid: int):
        super().__init__(timeout=300)
        self.owner_uid = owner_uid

    def _check(self, inter: discord.Interaction) -> bool:
        return inter.user.id == self.owner_uid

    # ── Riga 1: Aggiungi fondi / Sposta fondi ──
    @discord.ui.button(label="➕  Aggiungi fondi", style=discord.ButtonStyle.secondary, row=0)
    async def aggiungi_fondi(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self._check(inter):
            return await inter.response.send_message("❌ Questo conto non è tuo.", ephemeral=True)

        class DepositaModal(discord.ui.Modal, title="➕ Aggiungi fondi"):
            importo = discord.ui.TextInput(
                label="Importo da depositare ($)",
                placeholder="Es: 5000",
                required=True, max_length=12
            )
            async def on_submit(sm, i: discord.Interaction):
                try:
                    val = int(sm.importo.value.strip().replace("$","").replace(".","").replace(",",""))
                    if val <= 0: raise ValueError
                except ValueError:
                    return await i.response.send_message("❌ Importo non valido.", ephemeral=True)
                uid2 = i.user.id
                portaf = portafogli.get(uid2, 0)
                if portaf < val:
                    return await i.response.send_message(
                        f"❌ Portafoglio insufficiente. Hai **{portaf:,} $** in contanti.", ephemeral=True
                    )
                portafogli[uid2] = portaf - val
                if uid2 not in conti_bancari: conti_bancari[uid2] = 0
                conti_bancari[uid2] += val
                _registra_transazione(uid2, "+", val, "🏠 Deposito contanti", "Portafoglio")
                _salva_dati()
                await i.response.edit_message(embed=_build_revolut_embed(uid2, i.user), view=RevolutView(uid2))

        await inter.response.send_modal(DepositaModal())

    @discord.ui.button(label="🔀  Sposta fondi", style=discord.ButtonStyle.secondary, row=0)
    async def sposta_fondi(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self._check(inter):
            return await inter.response.send_message("❌ Questo conto non è tuo.", ephemeral=True)

        class SpostaModal(discord.ui.Modal, title="🔀 Trasferisci fondi"):
            destinatario = discord.ui.TextInput(
                label="ID Discord o @menzione del destinatario",
                placeholder="Es: 123456789012345678",
                required=True, max_length=30
            )
            importo = discord.ui.TextInput(
                label="Importo ($)",
                placeholder="Es: 10000",
                required=True, max_length=12
            )
            causale = discord.ui.TextInput(
                label="Causale (opzionale)",
                placeholder="Es: Pagamento affitto",
                required=False, max_length=80
            )
            async def on_submit(sm, i: discord.Interaction):
                try:
                    val = int(sm.importo.value.strip().replace("$","").replace(".","").replace(",",""))
                    if val <= 0: raise ValueError
                except ValueError:
                    return await i.response.send_message("❌ Importo non valido.", ephemeral=True)
                uid2 = i.user.id
                saldo2 = conti_bancari.get(uid2, 0)
                if saldo2 < val:
                    return await i.response.send_message(
                        f"❌ Fondi insufficienti. Saldo: **{saldo2:,} $**", ephemeral=True
                    )
                # Cerca destinatario
                dest_raw = sm.destinatario.value.strip().replace("<@","").replace(">","").replace("!","")
                try:
                    dest_uid = int(dest_raw)
                except ValueError:
                    return await i.response.send_message("❌ ID destinatario non valido.", ephemeral=True)
                if dest_uid == uid2:
                    return await i.response.send_message("❌ Non puoi inviare fondi a te stesso.", ephemeral=True)
                if dest_uid not in conti_bancari:
                    return await i.response.send_message("❌ Il destinatario non ha un conto bancario.", ephemeral=True)
                causale_txt = sm.causale.value.strip() if sm.causale.value.strip() else "Trasferimento"
                conti_bancari[uid2] -= val
                conti_bancari[dest_uid] += val
                _registra_transazione(uid2, "−", val, f"🔀 {causale_txt}", f"<@{dest_uid}>")
                _registra_transazione(dest_uid, "+", val, f"🔀 {causale_txt}", f"<@{uid2}>")
                _salva_dati()
                await i.response.edit_message(embed=_build_revolut_embed(uid2, i.user), view=RevolutView(uid2))
                # Notifica DM al destinatario
                try:
                    dest_member = i.guild.get_member(dest_uid)
                    if dest_member:
                        em_notif = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title="💜 Hai ricevuto un bonifico!", timestamp=datetime.now())
                        em_notif.description = f"**Da:** {i.user.mention}\n**Importo:** `+{val:,} $`\n**Causale:** {causale_txt}"
                        em_notif.set_footer(text="Pacific Bank · Eclipse City RP RP")
                        await dest_member.send(embed=em_notif)
                except Exception:
                    pass

        await inter.response.send_modal(SpostaModal())

    # ── Riga 2: Coordinate / Preleva / Aggiorna ──
    @discord.ui.button(label="🏛️  Coordinate", style=discord.ButtonStyle.secondary, row=1)
    async def coordinate(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self._check(inter):
            return await inter.response.send_message("❌ Questo conto non è tuo.", ephemeral=True)
        uid2 = inter.user.id
        saldo2 = conti_bancari.get(uid2, 0)
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title="🏛️ Coordinate conto", timestamp=datetime.now())
        embed.set_author(name="Pacific Bank · Eclipse City RP", icon_url=LOGO_SERVER)
        embed.description = (
            f"**Titolare ➢** {inter.user.mention}\n"
            f"**Banca ➢** Pacific Bank\n"
            f"**Tipo ➢** Conto corrente RP\n"
            f"**Valuta ➢** $ Eclipse Dollar\n"
            f"**Saldo attuale ➢** `{saldo2:,} $`\n"
            f"**ID Conto ➢** `MS-{uid2}`"
        )
        embed.set_footer(text="Eclipse City RP · Banca Privata")
        await inter.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="👜  Preleva", style=discord.ButtonStyle.secondary, row=1)
    async def preleva(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self._check(inter):
            return await inter.response.send_message("❌ Questo conto non è tuo.", ephemeral=True)

        class PrelevaModal(discord.ui.Modal, title="👜 Preleva contanti"):
            importo = discord.ui.TextInput(
                label="Importo da prelevare ($)",
                placeholder="Es: 2000",
                required=True, max_length=12
            )
            async def on_submit(sm, i: discord.Interaction):
                try:
                    val = int(sm.importo.value.strip().replace("$","").replace(".","").replace(",",""))
                    if val <= 0: raise ValueError
                except ValueError:
                    return await i.response.send_message("❌ Importo non valido.", ephemeral=True)
                uid2 = i.user.id
                saldo2 = conti_bancari.get(uid2, 0)
                if saldo2 < val:
                    return await i.response.send_message(
                        f"❌ Fondi insufficienti. Saldo: **{saldo2:,} $**", ephemeral=True
                    )
                conti_bancari[uid2] -= val
                if uid2 not in portafogli: portafogli[uid2] = 0
                portafogli[uid2] += val
                _registra_transazione(uid2, "−", val, "👜 Prelievo contanti", "Portafoglio")
                _salva_dati()
                await i.response.edit_message(embed=_build_revolut_embed(uid2, i.user), view=RevolutView(uid2))

        await inter.response.send_modal(PrelevaModal())

    @discord.ui.button(label="🔄  Aggiorna", style=discord.ButtonStyle.primary, row=1)
    async def aggiorna(self, inter: discord.Interaction, button: discord.ui.Button):
        if not self._check(inter):
            return await inter.response.send_message("❌ Questo conto non è tuo.", ephemeral=True)
        embed_upd = _build_revolut_embed(inter.user.id, inter.user)
        await inter.response.edit_message(embed=embed_upd, view=RevolutView(inter.user.id))


@bot.tree.command(name="revolut", description="💜 Apri la tua interfaccia conto Revolut")
async def revolut_cmd(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid not in conti_bancari:
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Non hai un conto bancario attivo. Recati alla **Pacific Bank** per aprirlo."
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = _build_revolut_embed(uid, interaction.user)
    await interaction.response.send_message(embed=embed, view=RevolutView(uid))


# ══════════════════════════════════════════════════════════════════
# 🚗 FINANZIAMENTO CONCESSIONARIO
# ══════════════════════════════════════════════════════════════════
# Solo il Direttore Concessionario può creare finanziamenti.
# I pagamenti sono settimanali e scalati automaticamente dal conto
# del cliente (anche se va in negativo).
# I soldi accreditati vanno al conto del Direttore Concessionario.
# ══════════════════════════════════════════════════════════════════

DIRETTORE_CONCESSIONARIO_USER_ID = 904037679115694162  # Conto destinazione rate

finanziamenti_attivi: dict = {}
# Struttura: {uid_cliente: [
#   {"id": str, "nome_ic": str, "veicolo": str, "rata": int,
#    "rate_totali": int, "rate_pagate": int, "prossimo_pagamento": str,
#    "direttore_uid": int, "direttore_nome": str, "ts_inizio": str},
#   ...
# ]}

_finanziamento_counter: list = [0]

# Aggiungi "finanziamenti_attivi" al salvataggio
_DIZIONARI_CHIAVE_INT.append("finanziamenti_attivi")


def _is_direttore_concessionario(member: discord.Member) -> bool:
    """Ritorna True se il membro ha il ruolo Direttore Concessionario o è admin."""
    if member.guild_permissions.administrator:
        return True
    nomi_puliti = [_pulisci_ruolo(r.name) for r in member.roles]
    for nome in nomi_puliti:
        if "direttore" in nome and "concess" in nome:
            return True
    return False


@bot.tree.command(name="finanziamento", description="🚗 Crea un piano di finanziamento per un cliente [Solo Dir. Concessionario]")
@app_commands.describe(cliente="Il membro Discord del cliente")
async def finanziamento_cmd(interaction: discord.Interaction, cliente: discord.Member):
    membro = await _get_member(interaction)

    if not _is_direttore_concessionario(membro):
        embed = discord.Embed(color=discord.Color.red())
        embed.set_author(name="❌ ACCESSO NEGATO", icon_url=LOGO_SERVER)
        embed.description = "Questo comando è riservato esclusivamente al **Direttore del Concessionario**."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if cliente.id == interaction.user.id:
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Non puoi creare un finanziamento per te stesso."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    direttore_uid = interaction.user.id
    direttore_nome = interaction.user.display_name
    cliente_uid = cliente.id

    class FinanziamentoModal(discord.ui.Modal, title="🚗 Nuovo Finanziamento"):
        nome_ic = discord.ui.TextInput(
            label="Nome e Cognome IC del cliente",
            style=discord.TextStyle.short,
            placeholder="Es: Marco Rossi",
            required=True,
            max_length=60
        )
        veicolo = discord.ui.TextInput(
            label="Veicolo / Oggetto finanziato",
            style=discord.TextStyle.short,
            placeholder="Es: Grotti X80 Proto Nera",
            required=True,
            max_length=80
        )
        costo_totale = discord.ui.TextInput(
            label="Costo totale ($)",
            style=discord.TextStyle.short,
            placeholder="Es: 150000",
            required=True,
            max_length=12
        )
        numero_rate = discord.ui.TextInput(
            label="Numero di rate settimanali",
            style=discord.TextStyle.short,
            placeholder="Es: 4  (pagamento ogni 7 giorni)",
            required=True,
            max_length=3
        )

        async def on_submit(sm, inter: discord.Interaction):
            try:
                costo = int(sm.costo_totale.value.strip().replace("$", "").replace(".", "").replace(",", ""))
                n_rate = int(sm.numero_rate.value.strip())
                if costo <= 0 or n_rate <= 0:
                    raise ValueError
            except ValueError:
                embed = discord.Embed(color=discord.Color.red())
                embed.description = "❌ Costo totale e numero rate devono essere numeri interi positivi."
                return await inter.response.send_message(embed=embed, ephemeral=True)

            rata = costo // n_rate
            resto = costo - (rata * n_rate)
            # L'ultima rata assorbe il centesimo di resto
            _finanziamento_counter[0] += 1
            fid = str(_finanziamento_counter[0])

            record = {
                "id": fid,
                "nome_ic": sm.nome_ic.value.strip(),
                "veicolo": sm.veicolo.value.strip(),
                "rata": rata,
                "resto": resto,
                "rate_totali": n_rate,
                "rate_pagate": 0,
                "direttore_uid": direttore_uid,
                "direttore_nome": direttore_nome,
                "ts_inizio": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }

            if cliente_uid not in finanziamenti_attivi:
                finanziamenti_attivi[cliente_uid] = []
            finanziamenti_attivi[cliente_uid].append(record)
            _salva_dati()

            # ── Embed riepilogo al direttore ──
            embed = discord.Embed(
                color=discord.Color.from_rgb(255, 107, 53),
                title="🚗 FINANZIAMENTO CREATO",
                timestamp=datetime.now()
            )
            embed.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
            embed.set_thumbnail(url=cliente.display_avatar.url)
            embed.description = (
                f"**📋 ID Finanziamento ➢** `{fid}`\n\n"
                f"**👤 Cliente ➢** {cliente.mention}\n"
                f"**🪪 Nome IC ➢** {sm.nome_ic.value.strip()}\n\n"
                f"**🚗 Veicolo ➢** {sm.veicolo.value.strip()}\n\n"
                f"**💰 Costo Totale ➢** `${costo:,}`\n"
                f"**📅 Rate ➢** `{n_rate}` rate da `${rata:,}` a settimana\n"
                f"**💳 Prima rata ➢** tra **7 giorni** (automatica)\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ *I pagamenti verranno scalati automaticamente ogni 7 giorni.*\n"
                f"*Se il saldo è insufficiente il conto andrà in negativo.*"
            )
            embed.set_footer(text=f"Creato da {direttore_nome} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            await inter.response.send_message(embed=embed)

            # ── Notifica DM al cliente ──
            try:
                embed_dm = discord.Embed(
                    color=discord.Color.from_rgb(255, 107, 53),
                    title="🚗 HAI UN NUOVO FINANZIAMENTO",
                    timestamp=datetime.now()
                )
                embed_dm.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
                embed_dm.description = (
                    f"**Ciao {sm.nome_ic.value.strip()}!**\n\n"
                    f"Il **Direttore del Concessionario** ha attivato un piano di finanziamento per te.\n\n"
                    f"**🚗 Veicolo ➢** {sm.veicolo.value.strip()}\n"
                    f"**💰 Costo Totale ➢** `${costo:,}`\n"
                    f"**📅 Rate ➢** `{n_rate}` rate settimanali da `${rata:,}`\n\n"
                    f"I pagamenti verranno **scalati automaticamente** dal tuo conto bancario ogni 7 giorni.\n"
                    f"⚠️ Assicurati di avere fondi sufficienti per evitare saldo negativo!"
                )
                embed_dm.set_footer(text=f"ID Finanziamento: {fid}")
                await cliente.send(embed=embed_dm)
            except Exception:
                pass

            await log_azione(
                inter.guild, inter.user,
                "🚗 Finanziamento creato",
                f"Cliente: {cliente.mention} | IC: {sm.nome_ic.value.strip()} | Veicolo: {sm.veicolo.value.strip()} | ${costo:,} in {n_rate} rate | ID: {fid}",
                discord.Color.from_rgb(255, 107, 53)
            )

    await interaction.response.send_modal(FinanziamentoModal())


@bot.tree.command(name="finanziamenti", description="📋 Visualizza i tuoi finanziamenti attivi")
async def finanziamenti_lista(interaction: discord.Interaction):
    uid = interaction.user.id
    lista = finanziamenti_attivi.get(uid, [])
    lista_attivi = [f for f in lista if f["rate_pagate"] < f["rate_totali"]]

    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title="📋 I TUOI FINANZIAMENTI",
        timestamp=datetime.now()
    )
    embed.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    if not lista_attivi:
        embed.description = "✅ Non hai finanziamenti attivi al momento."
    else:
        desc = ""
        for f in lista_attivi:
            rate_rimanenti = f["rate_totali"] - f["rate_pagate"]
            totale_residuo = rate_rimanenti * f["rata"] + f.get("resto", 0) if rate_rimanenti == 1 else rate_rimanenti * f["rata"]
            desc += (
                f"**🔑 ID `{f['id']}` — {f['veicolo']}**\n"
                f"┣ 🪪 Nome IC: {f['nome_ic']}\n"
                f"┣ 💰 Rata: `${f['rata']:,}` /settimana\n"
                f"┣ 📅 Rate pagate: `{f['rate_pagate']}/{f['rate_totali']}`\n"
                f"┗ 💳 Residuo: `${totale_residuo:,}`\n\n"
            )
        embed.description = desc
    embed.set_footer(text=f"{interaction.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="paga-rata", description="💳 Paga subito una rata del tuo finanziamento manualmente")
@app_commands.describe(id_finanziamento="ID del finanziamento da pagare (lascia vuoto per vedere i tuoi)")
async def paga_rata(interaction: discord.Interaction, id_finanziamento: str = None):
    uid = interaction.user.id
    lista = finanziamenti_attivi.get(uid, [])
    lista_attivi = [f for f in lista if f["rate_pagate"] < f["rate_totali"]]

    if not lista_attivi:
        embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53))
        embed.set_author(name="💳 PAGA RATA", icon_url=LOGO_SERVER)
        embed.description = "✅ Non hai finanziamenti attivi da pagare."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Se non è stato specificato un ID, e ne ha solo uno, lo seleziona automaticamente
    if id_finanziamento is None:
        if len(lista_attivi) == 1:
            finanziamento = lista_attivi[0]
        else:
            # Mostra la lista dei finanziamenti con bottoni
            desc = "Hai più finanziamenti attivi. Usa `/paga-rata id_finanziamento:[ID]`:\n\n"
            for f in lista_attivi:
                rate_rimanenti = f["rate_totali"] - f["rate_pagate"]
                desc += (
                    f"**🔑 ID `{f['id']}`** — {f['veicolo']}\n"
                    f"┣ 💰 Rata: `${f['rata']:,}` | Rimanenti: `{rate_rimanenti}`\n\n"
                )
            embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title="📋 I TUOI FINANZIAMENTI", timestamp=datetime.now())
            embed.set_author(name="💳 PAGA RATA", icon_url=LOGO_SERVER)
            embed.description = desc
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        fid = id_finanziamento.strip()
        finanziamento = next((f for f in lista_attivi if f["id"] == fid), None)
        if finanziamento is None:
            embed = discord.Embed(color=discord.Color.red())
            embed.description = f"❌ Finanziamento `{fid}` non trovato o già saldato."
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Calcola importo rata
    e_ultima = (finanziamento["rate_pagate"] + 1 == finanziamento["rate_totali"])
    importo = finanziamento["rata"] + (finanziamento.get("resto", 0) if e_ultima else 0)
    saldo_conto = conti_bancari.get(uid, 0)

    # Embed conferma con bottoni
    embed_conf = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title="💳 CONFERMA PAGAMENTO RATA",
        timestamp=datetime.now()
    )
    embed_conf.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
    saldo_str = f"`${saldo_conto:,}`" if saldo_conto >= 0 else f"⚠️ **`-${abs(saldo_conto):,}` (NEGATIVO)**"
    saldo_dopo = saldo_conto - importo
    saldo_dopo_str = f"`${saldo_dopo:,}`" if saldo_dopo >= 0 else f"⚠️ **`-${abs(saldo_dopo):,}` (andrà in negativo)**"
    embed_conf.description = (
        f"**🚗 Veicolo ➢** {finanziamento['veicolo']}\n"
        f"**🔑 ID ➢** `{finanziamento['id']}`\n\n"
        f"**💰 Importo rata ➢** `${importo:,}`\n"
        f"**📅 Rata ➢** `{finanziamento['rate_pagate'] + 1}/{finanziamento['rate_totali']}`"
        + (" *(ultima rata — finanziamento completato!)*" if e_ultima else "") + "\n\n"
        f"**🏦 Saldo attuale ➢** {saldo_str}\n"
        f"**🏦 Saldo dopo il pagamento ➢** {saldo_dopo_str}\n\n"
        f"Vuoi pagare questa rata adesso?"
    )
    embed_conf.set_footer(text=interaction.user.display_name)

    class ConfermaView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.fid = finanziamento["id"]
            self.uid = uid
            self.importo = importo
            self.e_ultima = e_ultima

        @discord.ui.button(label="✅ PAGA ORA", style=discord.ButtonStyle.green)
        async def paga(self, inter: discord.Interaction, button: discord.ui.Button):
            if inter.user.id != self.uid:
                return await inter.response.send_message("❌ Non sei tu il titolare.", ephemeral=True)

            # Ritrova il finanziamento (potrebbe essere cambiato)
            lista_now = finanziamenti_attivi.get(self.uid, [])
            fin = next((f for f in lista_now if f["id"] == self.fid and f["rate_pagate"] < f["rate_totali"]), None)
            if fin is None:
                for child in self.children: child.disabled = True
                embed_err = discord.Embed(color=discord.Color.red())
                embed_err.description = "❌ Finanziamento non trovato o già completato."
                return await inter.response.edit_message(embed=embed_err, view=self)

            # Scala dal conto cliente (anche negativo)
            if self.uid not in conti_bancari:
                conti_bancari[self.uid] = 0
            conti_bancari[self.uid] -= self.importo
            _registra_transazione(self.uid, "−", self.importo, "🚗 Rata finanziamento", fin['veicolo'])

            # Accredita al direttore concessionario
            if DIRETTORE_CONCESSIONARIO_USER_ID not in conti_bancari:
                conti_bancari[DIRETTORE_CONCESSIONARIO_USER_ID] = 0
            conti_bancari[DIRETTORE_CONCESSIONARIO_USER_ID] += self.importo
            _registra_transazione(DIRETTORE_CONCESSIONARIO_USER_ID, "+", self.importo, "🚗 Rata incassata", fin['veicolo'])

            fin["rate_pagate"] += 1
            completato = (fin["rate_pagate"] >= fin["rate_totali"])
            _salva_dati()

            saldo_finale = conti_bancari.get(self.uid, 0)
            saldo_finale_str = f"`${saldo_finale:,}`" if saldo_finale >= 0 else f"⚠️ **`-${abs(saldo_finale):,}` (NEGATIVO)**"

            for child in self.children: child.disabled = True

            embed_ok = discord.Embed(
                color=discord.Color.from_rgb(255, 107, 53) if saldo_finale >= 0 else discord.Color.from_rgb(255, 107, 53),
                title="✅ RATA PAGATA" if not completato else "🎉 FINANZIAMENTO SALDATO!",
                timestamp=datetime.now()
            )
            embed_ok.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
            embed_ok.description = (
                f"**🚗 Veicolo ➢** {fin['veicolo']}\n"
                f"**💰 Importo pagato ➢** `${self.importo:,}`\n"
                f"**📅 Rata ➢** `{fin['rate_pagate']}/{fin['rate_totali']}`\n"
                f"**🏦 Saldo conto ➢** {saldo_finale_str}\n\n"
                + ("🎉 **Complimenti! Hai saldato completamente il finanziamento!**" if completato
                   else f"📅 Prossima rata automatica tra **7 giorni** — oppure usa `/paga-rata` per anticiparla.")
            )
            embed_ok.set_footer(text=interaction.user.display_name)
            await inter.response.edit_message(embed=embed_ok, view=self)
            await log_azione(
                inter.guild, inter.user,
                "💳 Rata pagata manualmente",
                f"Veicolo: {fin['veicolo']} | ID: {self.fid} | Importo: ${self.importo:,} | Rata {fin['rate_pagate']}/{fin['rate_totali']}",
                discord.Color.from_rgb(255, 107, 53)
            )

        @discord.ui.button(label="❌ ANNULLA", style=discord.ButtonStyle.red)
        async def annulla(self, inter: discord.Interaction, button: discord.ui.Button):
            if inter.user.id != self.uid:
                return await inter.response.send_message("❌", ephemeral=True)
            for child in self.children: child.disabled = True
            embed_ann = discord.Embed(color=discord.Color.red())
            embed_ann.description = "❌ Pagamento annullato."
            await inter.response.edit_message(embed=embed_ann, view=self)

    await interaction.response.send_message(embed=embed_conf, view=ConfermaView(), ephemeral=True)


@bot.tree.command(name="finanziamenti-tutti", description="📊 Vedi tutti i finanziamenti attivi del concessionario [Solo Dir.]")
async def finanziamenti_tutti(interaction: discord.Interaction):
    membro = await _get_member(interaction)
    if not _is_direttore_concessionario(membro):
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Comando riservato al **Direttore del Concessionario**."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title="📊 TUTTI I FINANZIAMENTI ATTIVI",
        timestamp=datetime.now()
    )
    embed.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
    totale_crediti = 0
    righe = []
    for uid_str, lista in finanziamenti_attivi.items():
        try:
            uid_int = int(uid_str)
        except Exception:
            uid_int = uid_str
        for f in lista:
            if f["rate_pagate"] >= f["rate_totali"]:
                continue
            rate_rimanenti = f["rate_totali"] - f["rate_pagate"]
            residuo = rate_rimanenti * f["rata"]
            totale_crediti += residuo
            righe.append(
                f"**ID `{f['id']}`** — <@{uid_int}>\n"
                f"┣ 🪪 {f['nome_ic']} | 🚗 {f['veicolo']}\n"
                f"┣ 📅 {f['rate_pagate']}/{f['rate_totali']} rate | Rata: `${f['rata']:,}`\n"
                f"┗ 💳 Residuo: `${residuo:,}`\n"
            )
    if not righe:
        embed.description = "✅ Nessun finanziamento attivo al momento."
    else:
        embed.description = "\n".join(righe[:20])
        embed.add_field(name="💰 Totale Crediti", value=f"`${totale_crediti:,}`", inline=False)
    embed.set_footer(text=f"Richiesto da {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="annulla-finanziamento", description="❌ Annulla un finanziamento attivo [Solo Dir. Concessionario]")
@app_commands.describe(id_finanziamento="ID del finanziamento da annullare")
async def annulla_finanziamento(interaction: discord.Interaction, id_finanziamento: str):
    membro = await _get_member(interaction)
    if not _is_direttore_concessionario(membro):
        embed = discord.Embed(color=discord.Color.red())
        embed.description = "❌ Comando riservato al **Direttore del Concessionario**."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    fid = id_finanziamento.strip()
    trovato = False
    for uid_k, lista in finanziamenti_attivi.items():
        for i, f in enumerate(lista):
            if f["id"] == fid:
                lista.pop(i)
                trovato = True
                _salva_dati()
                break
        if trovato:
            break

    if not trovato:
        embed = discord.Embed(color=discord.Color.red())
        embed.description = f"❌ Finanziamento `{fid}` non trovato."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.set_author(name="❌ FINANZIAMENTO ANNULLATO", icon_url=LOGO_SERVER)
    embed.description = f"Il finanziamento **ID `{fid}`** è stato annullato con successo."
    await interaction.response.send_message(embed=embed, ephemeral=True)
    await log_azione(interaction.guild, interaction.user, "❌ Finanziamento annullato", f"ID: {fid}", discord.Color.from_rgb(255, 107, 53))


# ── Task settimanale: ogni 7 giorni scala le rate automaticamente ──
@tasks.loop(hours=168)  # 168 ore = 7 giorni
async def pagamento_rate_task():
    """Ogni 7 giorni scala automaticamente le rate dai conti dei clienti e accredita al direttore."""
    guild = None
    for g in bot.guilds:
        guild = g
        break

    for uid_k in list(finanziamenti_attivi.keys()):
        lista = finanziamenti_attivi[uid_k]
        try:
            uid_int = int(uid_k)
        except Exception:
            uid_int = uid_k

        for f in lista:
            if f["rate_pagate"] >= f["rate_totali"]:
                continue

            f["rate_pagate"] += 1
            e_ultima = (f["rate_pagate"] == f["rate_totali"])
            importo = f["rata"] + (f.get("resto", 0) if e_ultima else 0)

            # Scala dal conto cliente (va in negativo se non ci sono fondi)
            if uid_int not in conti_bancari:
                conti_bancari[uid_int] = 0
            conti_bancari[uid_int] -= importo
            _registra_transazione(uid_int, "−", importo, "🚗 Rata automatica", f['veicolo'])

            # Accredita al conto del Direttore Concessionario
            if DIRETTORE_CONCESSIONARIO_USER_ID not in conti_bancari:
                conti_bancari[DIRETTORE_CONCESSIONARIO_USER_ID] = 0
            conti_bancari[DIRETTORE_CONCESSIONARIO_USER_ID] += importo
            _registra_transazione(DIRETTORE_CONCESSIONARIO_USER_ID, "+", importo, "🚗 Rata incassata (auto)", f['veicolo'])

            # Notifica DM al cliente
            stato_pagamento = "completato ✅" if e_ultima else f"({f['rate_pagate']}/{f['rate_totali']})"
            saldo_dopo = conti_bancari.get(uid_int, 0)
            saldo_str = f"`${saldo_dopo:,}`" if saldo_dopo >= 0 else f"⚠️ **`-${abs(saldo_dopo):,}` (NEGATIVO)**"

            try:
                membro_discord = None
                if guild:
                    membro_discord = guild.get_member(uid_int)
                if membro_discord:
                    embed_notifica = discord.Embed(
                        color=discord.Color.from_rgb(255, 107, 53) if saldo_dopo >= 0 else discord.Color.red(),
                        title="💳 RATA FINANZIAMENTO SCALATA",
                        timestamp=datetime.now()
                    )
                    embed_notifica.set_author(name="Concessionario Eclipse City", icon_url=LOGO_SERVER)
                    embed_notifica.description = (
                        f"**🚗 Veicolo ➢** {f['veicolo']}\n"
                        f"**💰 Importo scalato ➢** `${importo:,}`\n"
                        f"**📅 Rata ➢** {stato_pagamento}\n"
                        f"**🏦 Saldo conto dopo ➢** {saldo_str}\n\n"
                        + ("✅ **Finanziamento completamente saldato!**" if e_ultima else
                           f"📅 Prossima rata tra **7 giorni** — `${f['rata']:,}`")
                    )
                    embed_notifica.set_footer(text=f"ID Finanziamento: {f['id']}")
                    await membro_discord.send(embed=embed_notifica)
            except Exception:
                pass

        # Rimuovi finanziamenti completati
        finanziamenti_attivi[uid_k] = [f for f in lista if f["rate_pagate"] < f["rate_totali"]]

    _salva_dati()
    print(f"💳 [RATE] Pagamento settimanale rate eseguito — {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ══════════════════════════════════════════════════════════════════
# 🏝️ ISLA DE ORO — Sistema Ordini Ristorante
# ══════════════════════════════════════════════════════════════════

ISLA_CANALE_ORDINI_ID = 1530635315268817126
ISLA_RUOLO_CAMERIERE  = 1520768829838327899
ISLA_CASSA_UID        = 1510391381867233351

ISLA_MENU = {
    "🦐 Carpaccio de Carabinero Real":        {"prezzo": 650,   "cat": "🌊 Menú de Mar — Antipasti"},
    "🐟 Tartar de Atún Rojo y Oro":           {"prezzo": 550,   "cat": "🌊 Menú de Mar — Antipasti"},
    "🦪 Ostras Perla del Sur":                {"prezzo": 750,   "cat": "🌊 Menú de Mar — Antipasti"},
    "🦞 Ceviche de Bogavante Galiziano":      {"prezzo": 600,   "cat": "🌊 Menú de Mar — Antipasti"},
    "🔥 Pulpo a la Brasa Crujiente":          {"prezzo": 450,   "cat": "🌊 Menú de Mar — Antipasti"},
    "🥂 Risotto al Champagne y Bogavante":    {"prezzo": 1200,  "cat": "🌊 Menú de Mar — Primi"},
    "🖤 Tagliolini Negros con Erizo de Mar":  {"prezzo": 950,   "cat": "🌊 Menú de Mar — Primi"},
    "🥟 Raviolis de Centollo con Trufa":      {"prezzo": 1100,  "cat": "🌊 Menú de Mar — Primi"},
    "🍝 Spaghetti alla Chitarra con Caviar":  {"prezzo": 1300,  "cat": "🌊 Menú de Mar — Primi"},
    "🦞 Caldereta de Marisco Premium":        {"prezzo": 1450,  "cat": "🌊 Menú de Mar — Primi"},
    "🔥 Rodaballo Salvaje a la Donostiarra":  {"prezzo": 200,   "cat": "🌊 Menú de Mar — Secondi"},
    "🧂 Lubina en Costra de Sal Marina":      {"prezzo": 500,   "cat": "🌊 Menú de Mar — Secondi"},
    "🦐 Cigalas Reales a la Plancha":         {"prezzo": 300,   "cat": "🌊 Menú de Mar — Secondi"},
    "🦀 Turbante de Lenguado con King Crab":  {"prezzo": 800,   "cat": "🌊 Menú de Mar — Secondi"},
    "🥜 Tataki de Atún en Costra de Pistacho":{"prezzo": 600,   "cat": "🌊 Menú de Mar — Secondi"},
    "🐖 Jamón Ibérico 100% Bellota":          {"prezzo": 100,   "cat": "🥩 Menú de Tierra — Antipasti"},
    "👑 Tartar de Wagyu A5 con Huevo":        {"prezzo": 500,   "cat": "🥩 Menú de Tierra — Antipasti"},
    "🍄 Carpaccio de Solomillo con Trufa":    {"prezzo": 100,   "cat": "🥩 Menú de Tierra — Antipasti"},
    "💜 Gnocchi de Patata Violeta con Foie":  {"prezzo": 50,    "cat": "🥩 Menú de Tierra — Primi"},
    "🌲 Pappardelle con Ragú de Jabalí":      {"prezzo": 20,    "cat": "🥩 Menú de Tierra — Primi"},
    "👑 Risotto al Tartufo Blanco y Oro":     {"prezzo": 100,   "cat": "🥩 Menú de Tierra — Primi"},
    "🥩 Filet Mignon con Salsa de Colmenillas":{"prezzo": 140,  "cat": "🥩 Menú de Tierra — Secondi"},
    "🪓 Tomahawk de Ternera Black Angus":     {"prezzo": 1000,  "cat": "🥩 Menú de Tierra — Secondi"},
    "👑 Chuletón de Wagyu Kagoshima":         {"prezzo": 5000,  "cat": "👑 Carnes Premium"},
    "🔥 Paletilla de Cordero Lechal":         {"prezzo": 67,    "cat": "👑 Carnes Premium"},
    "🌴 Marbella Mule":                       {"prezzo": 40,    "cat": "🍸 Coctelería de Autor"},
    "🌅 Ibiza Sunset":                        {"prezzo": 100,   "cat": "🍸 Coctelería de Autor"},
    "🥂 Isla de Oro Spritz":                  {"prezzo": 30,    "cat": "🍸 Coctelería de Autor"},
    "🍷 Tinto de Verano Luxury":              {"prezzo": 60,    "cat": "🍸 Coctelería de Autor"},
    "🔥 Smoked Old Fashioned":                {"prezzo": 130,   "cat": "🍸 Coctelería de Autor"},
    "💧 Acqua Minerale Voss":                 {"prezzo": 20,    "cat": "🥤 Bevande & Refrescos"},
    "🥤 Coca-Cola (Bottiglia in vetro)":      {"prezzo": 40,    "cat": "🥤 Bevande & Refrescos"},
    "⚡ Red Bull Premium Edition":            {"prezzo": 70,    "cat": "🥤 Bevande & Refrescos"},
    "🍊 Fanta Arancia / Limone":              {"prezzo": 40,    "cat": "🥤 Bevande & Refrescos"},
    "🟢 Sprite":                              {"prezzo": 40,    "cat": "🥤 Bevande & Refrescos"},
    "🍋 Tonica Premium Fever-Tree":           {"prezzo": 50,    "cat": "🥤 Bevande & Refrescos"},
    "🇪🇸 Vega Sicilia Único":                {"prezzo": 1500,  "cat": "🍾 La Bodega Real — Vini"},
    "🇪🇸 Pingus":                            {"prezzo": 1400,  "cat": "🍾 La Bodega Real — Vini"},
    "🇫🇷 Château Margaux":                   {"prezzo": 5000,  "cat": "🍾 La Bodega Real — Vini"},
    "🇪🇸 Pazo de Señorans Selección":        {"prezzo": 600,   "cat": "🍾 La Bodega Real — Vini"},
    "🇮🇹 Gaja Gaia & Rey":                   {"prezzo": 800,   "cat": "🍾 La Bodega Real — Vini"},
    "✨ Dom Pérignon Vintage Luminous":        {"prezzo": 3500,  "cat": "🥂 Les Champagnes"},
    "👑 Louis Roederer Cristal":              {"prezzo": 5000,  "cat": "🥂 Les Champagnes"},
    "🥂 Krug Grande Cuvée":                   {"prezzo": 500,   "cat": "🥂 Les Champagnes"},
    "🃏 Armand de Brignac Ace of Spades":     {"prezzo": 10000, "cat": "🥂 Les Champagnes"},
    "🌹 Perrier-Jouët Belle Époque Rosé":     {"prezzo": 3000,  "cat": "🥂 Les Champagnes"},
}

_ISLA_CATEGORIE: dict = {}
for _in, _id in ISLA_MENU.items():
    _ISLA_CATEGORIE.setdefault(_id["cat"], []).append(_in)


def _isla_embed_home(user: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title="⚓ 👑 ISLA DE ORO | EL MENÚ DE GALA 👑 ⚓",
        timestamp=datetime.now()
    )
    embed.set_author(name="Isla de Oro — Dove l'oceano diventa lusso assoluto", icon_url=LOGO_SERVER)
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.description = (
        "🌊 **Menú de Mar** — Antipasti, Primi, Secondi di mare\n"
        "🥩 **Menú de Tierra** — Antipasti, Primi, Secondi di terra\n"
        "👑 **Carnes Premium** — Le carni più pregiate al mondo\n"
        "🍸 **Coctelería de Autor** — Cocktail signature della casa\n"
        "🥤 **Bevande & Refrescos** — Acqua, bibite, energy drink\n"
        "🍾 **La Bodega Real** — Vini selezionati\n"
        "🥂 **Les Champagnes** — Champagne d'élite\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 Il tuo portafoglio ➢ **`${portafogli.get(user.id, 0):,}`**\n\n"
        "*Seleziona una sezione dal menu qui sotto per ordinare.* 🥂"
    )
    embed.set_footer(
        text=f"{user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        icon_url=user.display_avatar.url
    )
    return embed


def _isla_embed_categoria(cat: str, piatti: list, user: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 107, 53),
        title=f"⚓ {cat}",
        timestamp=datetime.now()
    )
    embed.set_author(name="Isla de Oro — El Menú de Gala", icon_url=LOGO_SERVER)
    righe = [f"➢ **{p}** — `${ISLA_MENU[p]['prezzo']:,}`" for p in piatti]
    embed.description = "\n".join(righe)
    embed.set_footer(
        text=f"Seleziona il piatto • Portafoglio: ${portafogli.get(user.id, 0):,}",
        icon_url=user.display_avatar.url
    )
    return embed


def _isla_applica_effetto(uid: int, piatto: str) -> str:
    """Applica automaticamente fame/sete se il piatto ha un effetto. Ritorna stringa descrittiva."""
    b = _init_bisogni(uid)
    righe = []
    # Cerca nel piatto esatto prima, poi per parole chiave
    effetto = EFFETTI_ITEM.get(piatto)
    if effetto is None:
        nome_lower = piatto.lower()
        for k, v in EFFETTI_ITEM.items():
            if k.lower() in nome_lower or nome_lower in k.lower():
                effetto = v
                break
    # Fallback per categorie note dal menu
    if effetto is None:
        nome_lower = piatto.lower()
        # Bevande (cocktail, vini, champagne, bibite)
        keywords_bev = ["mule", "sunset", "spritz", "tinto", "smoked", "voss", "coca", "red bull",
                        "fanta", "sprite", "tonica", "vega", "pingus", "château", "pazo", "gaja",
                        "dom pérignon", "roederer", "krug", "armand", "perrier", "champagne", "vino",
                        "bodega", "acqua"]
        keywords_cibo = ["carpaccio", "tartar", "ostras", "ceviche", "pulpo", "risotto", "tagliolini",
                         "ravioli", "spaghetti", "caldereta", "rodaballo", "lubina", "cigalas",
                         "turbante", "tataki", "jamón", "wagyu", "gnocchi", "pappardelle", "filet",
                         "tomahawk", "chuletón", "paletilla"]
        if any(k in nome_lower for k in keywords_bev):
            effetto = {"sete": 40}
        elif any(k in nome_lower for k in keywords_cibo):
            effetto = {"fame": 45}
        else:
            effetto = {"fame": 30}  # default generico

    if "fame" in effetto:
        vecchia = b["fame"]
        b["fame"] = min(FAME_MAX, b["fame"] + effetto["fame"])
        guadagnato = b["fame"] - vecchia
        barra = _barra_fame(b["fame"], FAME_MAX)
        righe.append(f"🍽️ **+{guadagnato} fame** {barra} `{b['fame']}/{FAME_MAX}`")
    if "sete" in effetto:
        vecchia = b["sete"]
        b["sete"] = min(SETE_MAX, b["sete"] + effetto["sete"])
        guadagnato = b["sete"] - vecchia
        barra = _barra_sete(b["sete"], SETE_MAX)
        righe.append(f"💧 **+{guadagnato} sete** {barra} `{b['sete']}/{SETE_MAX}`")
    return "\n".join(righe) if righe else ""


class IslaAccettaView(discord.ui.View):
    """View inviata al cliente via DM per accettare la consegna."""

    def __init__(self, cliente_uid: int, piatto: str, cameriere_uid: int,
                 cameriere_nome: str, msg_canale, guild):
        super().__init__(timeout=300)  # 5 minuti per accettare
        self.cliente_uid = cliente_uid
        self.piatto = piatto
        self.cameriere_uid = cameriere_uid
        self.cameriere_nome = cameriere_nome
        self.msg_canale = msg_canale   # messaggio nel canale ordini da aggiornare
        self.guild = guild
        self.accettato = False

    @discord.ui.button(label="✅ ACCETTO IL PIATTO", style=discord.ButtonStyle.success, emoji="🍽️")
    async def accetta_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if inter.user.id != self.cliente_uid:
            return await inter.response.send_message("❌ Non sei tu il cliente.", ephemeral=True)
        if self.accettato:
            return await inter.response.send_message("❌ Hai già accettato questo ordine.", ephemeral=True)
        self.accettato = True

        # Aggiunge piatto all'inventario cliente
        if self.cliente_uid not in inventari:
            inventari[self.cliente_uid] = []
        inventari[self.cliente_uid].append(f"🍽️ {self.piatto}")

        # Applica effetto fame/sete automaticamente
        effetto_str = _isla_applica_effetto(self.cliente_uid, self.piatto)
        _salva_dati()

        for child in self.children:
            child.disabled = True

        embed_ok = discord.Embed(
            color=discord.Color.from_rgb(255, 107, 53),
            title="🍽️ PIATTO RICEVUTO!",
            timestamp=datetime.now()
        )
        embed_ok.set_author(name="Isla de Oro", icon_url=LOGO_SERVER)
        embed_ok.description = (
            f"✅ Hai ricevuto **{self.piatto}**!\n"
            f"**👨‍🍳 Servito da ➢** {self.cameriere_nome}\n\n"
            + (f"**Effetti:**\n{effetto_str}\n\n" if effetto_str else "")
            + "*Buon appetito! Buen provecho! 🥂*"
        )
        await inter.response.edit_message(embed=embed_ok, view=self)

        # Aggiorna il messaggio nel canale ordini
        try:
            embed_can = discord.Embed(
                color=discord.Color.from_rgb(255, 107, 53),
                title="✅ ORDINE ACCETTATO DAL CLIENTE",
                timestamp=datetime.now()
            )
            embed_can.set_author(name="Isla de Oro", icon_url=LOGO_SERVER)
            embed_can.description = (
                f"**🍽️ Piatto ➢** {self.piatto}\n"
                f"**👤 Cliente ➢** <@{self.cliente_uid}>\n"
                f"**👨‍🍳 Servito da ➢** {self.cameriere_nome}\n\n"
                f"✅ *Cliente ha accettato e consumato il piatto.*\n"
                + (f"{effetto_str}" if effetto_str else "")
            )
            await self.msg_canale.edit(embed=embed_can, view=None)
        except Exception:
            pass

    @discord.ui.button(label="❌ RIFIUTO", style=discord.ButtonStyle.danger, emoji="❌")
    async def rifiuta_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        if inter.user.id != self.cliente_uid:
            return await inter.response.send_message("❌ Non sei tu il cliente.", ephemeral=True)
        if self.accettato:
            return await inter.response.send_message("❌ Hai già risposto a questo ordine.", ephemeral=True)
        self.accettato = True
        for child in self.children:
            child.disabled = True
        embed_no = discord.Embed(color=discord.Color.red(), title="❌ Piatto Rifiutato", timestamp=datetime.now())
        embed_no.set_author(name="Isla de Oro", icon_url=LOGO_SERVER)
        embed_no.description = f"Hai rifiutato **{self.piatto}**.\nContatta il cameriere o lo staff per assistenza."
        await inter.response.edit_message(embed=embed_no, view=self)
        try:
            embed_can = discord.Embed(color=discord.Color.red(), title="❌ ORDINE RIFIUTATO DAL CLIENTE", timestamp=datetime.now())
            embed_can.set_author(name="Isla de Oro", icon_url=LOGO_SERVER)
            embed_can.description = (
                f"**🍽️ Piatto ➢** {self.piatto}\n"
                f"**👤 Cliente ➢** <@{self.cliente_uid}>\n\n"
                f"❌ *Il cliente ha rifiutato il piatto. Contattarlo per chiarimenti.*"
            )
            await self.msg_canale.edit(embed=embed_can, view=None)
        except Exception:
            pass

    async def on_timeout(self):
        if not self.accettato:
            for child in self.children:
                child.disabled = True
            try:
                embed_to = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), title="⏰ Tempo scaduto")
                embed_to.description = f"Non hai risposto in tempo per **{self.piatto}**.\nContatta il cameriere."
                await self.message.edit(embed=embed_to, view=self)
            except Exception:
                pass


class IslaConsegnaView(discord.ui.View):
    def __init__(self, cliente_uid: int, cliente_nome: str, piatto: str, cameriere):
        super().__init__(timeout=None)
        self.cliente_uid = cliente_uid
        self.cliente_nome = cliente_nome
        self.piatto = piatto
        self.cameriere = cameriere
        self.consegnato = False

    @discord.ui.button(label="✅ CONSEGNATO AL TAVOLO", style=discord.ButtonStyle.success, emoji="🍽️")
    async def consegnato_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        membro = await _get_member(inter)
        ha_ruolo_cam = any(r.id == ISLA_RUOLO_CAMERIERE for r in membro.roles)
        if not (ha_ruolo_cam or membro.guild_permissions.administrator):
            return await inter.response.send_message("❌ Solo i camerieri possono segnare l'ordine come consegnato.", ephemeral=True)
        if self.consegnato:
            return await inter.response.send_message("❌ Ordine già consegnato.", ephemeral=True)
        self.consegnato = True

        # Rimuove l'item dall'inventario del cameriere
        cam_uid = inter.user.id
        item_cam = f"🍽️ {self.piatto} [per {self.cliente_nome}]"
        if cam_uid in inventari and item_cam in inventari[cam_uid]:
            inventari[cam_uid].remove(item_cam)
        _salva_dati()

        # Aggiorna il messaggio nel canale ordini — in attesa del cliente
        for child in self.children:
            child.disabled = True
        embed_attesa = discord.Embed(
            color=discord.Color.from_rgb(255, 107, 53),
            title="⏳ IN ATTESA CONFERMA CLIENTE",
            timestamp=datetime.now()
        )
        embed_attesa.set_author(name="Isla de Oro", icon_url=LOGO_SERVER)
        embed_attesa.description = (
            f"**🍽️ Piatto ➢** {self.piatto}\n"
            f"**👤 Cliente ➢** <@{self.cliente_uid}>\n"
            f"**👨‍🍳 Cameriere ➢** {inter.user.mention}\n\n"
            f"⏳ *Notifica inviata al cliente in DM. In attesa che accetti il piatto...*"
        )
        msg_canale = await inter.response.edit_message(embed=embed_attesa, view=self)

        # Recupera il messaggio aggiornato per passarlo alla IslaAccettaView
        try:
            msg_obj = await inter.original_response()
        except Exception:
            msg_obj = None

        # Invia DM al cliente con bottoni accetta/rifiuta
        cliente_member = inter.guild.get_member(self.cliente_uid)
        if cliente_member:
            embed_dm = discord.Embed(
                color=discord.Color.from_rgb(255, 107, 53),
                title="🍽️ IL TUO ORDINE È ARRIVATO!",
                timestamp=datetime.now()
            )
            embed_dm.set_author(name="Isla de Oro", icon_url=LOGO_SERVER)
            embed_dm.set_thumbnail(url=LOGO_SERVER)
            embed_dm.description = (
                f"**Il cameriere {inter.user.display_name}** ti sta portando il piatto al tavolo!\n\n"
                f"**🍽️ Piatto ➢** {self.piatto}\n\n"
                f"➢ Clicca **✅ ACCETTO** per riceverlo nel tuo inventario.\n"
                f"➢ Clicca **❌ RIFIUTO** se c'è un problema.\n\n"
                f"*Hai 5 minuti per rispondere.*"
            )
            embed_dm.set_footer(text=f"Isla de Oro • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            accetta_view = IslaAccettaView(
                cliente_uid=self.cliente_uid,
                piatto=self.piatto,
                cameriere_uid=cam_uid,
                cameriere_nome=inter.user.display_name,
                msg_canale=msg_obj,
                guild=inter.guild
            )
            try:
                dm_msg = await cliente_member.send(embed=embed_dm, view=accetta_view)
                accetta_view.message = dm_msg
            except discord.Forbidden:
                # Se il cliente ha i DM chiusi, consegna direttamente senza conferma
                if self.cliente_uid not in inventari:
                    inventari[self.cliente_uid] = []
                inventari[self.cliente_uid].append(f"🍽️ {self.piatto}")
                _isla_applica_effetto(self.cliente_uid, self.piatto)
                _salva_dati()
                await inter.followup.send(
                    f"⚠️ <@{self.cliente_uid}> ha i DM chiusi. Piatto consegnato direttamente all'inventario.",
                    ephemeral=True
                )

    @discord.ui.button(label="🔄 Riassegna", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def riassegna_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        membro = await _get_member(inter)
        if not (membro.guild_permissions.administrator or membro.guild_permissions.manage_messages):
            return await inter.response.send_message("❌ Solo lo staff può riassegnare.", ephemeral=True)
        ruolo_cam = inter.guild.get_role(ISLA_RUOLO_CAMERIERE)
        if not ruolo_cam or not ruolo_cam.members:
            return await inter.response.send_message("❌ Nessun cameriere disponibile.", ephemeral=True)
        if self.cameriere:
            old_item = f"🍽️ {self.piatto} [per {self.cliente_nome}]"
            if self.cameriere.id in inventari and old_item in inventari[self.cameriere.id]:
                inventari[self.cameriere.id].remove(old_item)
        nuovo_cam = next(
            (m for m in ruolo_cam.members if not m.bot and m != self.cameriere),
            ruolo_cam.members[0] if ruolo_cam.members else None
        )
        if not nuovo_cam:
            return await inter.response.send_message("❌ Nessun altro cameriere disponibile.", ephemeral=True)
        self.cameriere = nuovo_cam
        item_cam = f"🍽️ {self.piatto} [per {self.cliente_nome}]"
        if nuovo_cam.id not in inventari:
            inventari[nuovo_cam.id] = []
        inventari[nuovo_cam.id].append(item_cam)
        _salva_dati()
        await inter.response.send_message(f"🔄 Ordine riassegnato a {nuovo_cam.mention}.", ephemeral=True)


class IslaConfermaModal(discord.ui.Modal, title="🍽️ Conferma Ordine"):
    note = discord.ui.TextInput(
        label="Note per la cucina (opzionale)",
        style=discord.TextStyle.paragraph,
        placeholder="Es: senza cipolla, cottura al sangue, allergie...",
        required=False,
        max_length=200
    )

    def __init__(self, uid: int, piatto: str, prezzo: int):
        super().__init__()
        self.uid = uid
        self.piatto = piatto
        self.prezzo = prezzo

    async def on_submit(self, inter: discord.Interaction):
        uid = inter.user.id
        piatto = self.piatto
        prezzo = self.prezzo
        note_txt = self.note.value.strip() if self.note.value.strip() else "Nessuna"

        saldo = portafogli.get(uid, 0)
        if saldo < prezzo:
            embed = discord.Embed(color=discord.Color.red())
            embed.set_author(name="⚓ Isla de Oro", icon_url=LOGO_SERVER)
            embed.description = (
                f"❌ **Fondi insufficienti!**\n\n"
                f"**Piatto ➢** {piatto}\n"
                f"**Prezzo ➢** `${prezzo:,}`\n"
                f"**Il tuo portafoglio ➢** `${saldo:,}`\n\n"
                f"*Non hai abbastanza contanti in portafoglio.*"
            )
            return await inter.response.send_message(embed=embed, ephemeral=True)

        portafogli[uid] -= prezzo
        portafogli[ISLA_CASSA_UID] = portafogli.get(ISLA_CASSA_UID, 0) + prezzo
        _registra_transazione(uid, "−", prezzo, f"⚓ Ordine Isla de Oro", piatto)
        _salva_dati()

        guild = inter.guild
        # Log nel canale economia
        if guild:
            log_eco = guild.get_channel(CH_LOG_ECONOMIA)
            if log_eco:
                log_embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
                log_embed.set_author(name="⚓ Acquisto Isla de Oro", icon_url=LOGO_SERVER)
                log_embed.description = (
                    f"**👤 Utente :** <@{uid}>\n"
                    f"**🍽️ Piatto :** {piatto}\n"
                    f"**💸 Importo :** `−{prezzo:,} $`\n"
                    f"**👜 Portafoglio residuo :** `{portafogli.get(uid, 0):,} $`"
                )
                log_embed.set_footer(text=f"UserID: {uid}")
                try:
                    await log_eco.send(embed=log_embed)
                except Exception:
                    pass
        cameriere_trovato = None
        if guild:
            ruolo_cam = guild.get_role(ISLA_RUOLO_CAMERIERE)
            if ruolo_cam:
                for membro_cam in ruolo_cam.members:
                    if not membro_cam.bot:
                        cameriere_trovato = membro_cam
                        break

        if cameriere_trovato:
            if cameriere_trovato.id not in inventari:
                inventari[cameriere_trovato.id] = []
            inventari[cameriere_trovato.id].append(f"🍽️ {piatto} [per {inter.user.display_name}]")
            _salva_dati()

        embed_ok = discord.Embed(
            color=discord.Color.from_rgb(255, 107, 53),
            title="⚓ ORDINE CONFERMATO — ISLA DE ORO",
            timestamp=datetime.now()
        )
        embed_ok.set_author(name="Isla de Oro | El Menú de Gala", icon_url=LOGO_SERVER)
        embed_ok.set_thumbnail(url=LOGO_SERVER)
        embed_ok.description = (
            f"✅ Il tuo ordine è stato ricevuto!\n\n"
            f"**🍽️ Piatto ➢** {piatto}\n"
            f"**💰 Pagato ➢** `${prezzo:,}`\n"
            f"**📝 Note ➢** {note_txt}\n\n"
            + (f"**👨‍🍳 Cameriere ➢** {cameriere_trovato.mention}\n\n" if cameriere_trovato else "")
            + "*Il cameriere ti porterà il piatto al tavolo a breve. Gracias!* 🥂"
        )
        embed_ok.set_footer(
            text=f"{inter.user.display_name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            icon_url=inter.user.display_avatar.url
        )
        await inter.response.send_message(embed=embed_ok, ephemeral=True)

        canale_ordini = guild.get_channel(ISLA_CANALE_ORDINI_ID) if guild else None
        if canale_ordini:
            embed_ord = discord.Embed(
                color=discord.Color.from_rgb(255, 107, 53),
                title="🔔 NUOVO ORDINE — ISLA DE ORO",
                timestamp=datetime.now()
            )
            embed_ord.set_author(name="Sistema Ordini", icon_url=LOGO_SERVER)
            embed_ord.set_thumbnail(url=inter.user.display_avatar.url)
            embed_ord.description = (
                f"**👤 Cliente ➢** {inter.user.mention}\n"
                f"**🍽️ Piatto ➢** {piatto}\n"
                f"**💰 Pagato ➢** `${prezzo:,}`\n"
                f"**📝 Note ➢** {note_txt}\n"
                + (f"\n**👨‍🍳 Cameriere ➢** {cameriere_trovato.mention}\n*Item aggiunto al suo inventario.*"
                   if cameriere_trovato
                   else "\n⚠️ **Nessun cameriere disponibile** — assegna manualmente.")
            )
            embed_ord.set_footer(text=f"Ordine del {datetime.now().strftime('%d/%m/%Y alle %H:%M')}")
            view_consegna = IslaConsegnaView(
                cliente_uid=uid,
                cliente_nome=inter.user.display_name,
                piatto=piatto,
                cameriere=cameriere_trovato
            )
            await canale_ordini.send(
                content=cameriere_trovato.mention if cameriere_trovato else "@here Ordine senza cameriere!",
                embed=embed_ord,
                view=view_consegna
            )

        await log_azione(
            guild, inter.user,
            "⚓ Ordine Isla de Oro",
            f"Piatto: **{piatto}** | ${prezzo:,} | Note: {note_txt}",
            discord.Color.from_rgb(255, 107, 53)
        )


class IslaPiattiView(discord.ui.View):
    def __init__(self, uid: int, cat: str, piatti: list):
        super().__init__(timeout=120)
        self.uid = uid

        opzioni = [
            discord.SelectOption(label=p[:100], value=p, description=f"${ISLA_MENU[p]['prezzo']:,}")
            for p in piatti[:25]
        ]
        sel = discord.ui.Select(placeholder="🍽️ Scegli il piatto...", options=opzioni)

        async def sel_callback(inter: discord.Interaction):
            if inter.user.id != self.uid:
                return await inter.response.send_message("❌ Non è il tuo ordine.", ephemeral=True)
            piatto = sel.values[0]
            await inter.response.send_modal(IslaConfermaModal(self.uid, piatto, ISLA_MENU[piatto]["prezzo"]))

        sel.callback = sel_callback
        self.add_item(sel)

        btn_back = discord.ui.Button(label="🔙 Torna al menú", style=discord.ButtonStyle.secondary, row=1)

        async def back_callback(inter: discord.Interaction):
            if inter.user.id != self.uid:
                return await inter.response.send_message("❌", ephemeral=True)
            await inter.response.edit_message(
                embed=_isla_embed_home(inter.user),
                view=IslaMenuCategoriaView(self.uid)
            )

        btn_back.callback = back_callback
        self.add_item(btn_back)


class IslaMenuCategoriaView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=120)
        self.uid = uid

        opzioni = [
            discord.SelectOption(label=cat[:100], value=cat, emoji="🍽️")
            for cat in _ISLA_CATEGORIE
        ]
        sel = discord.ui.Select(placeholder="⚓ Scegli una sezione del menú...", options=opzioni[:25])

        async def sel_callback(inter: discord.Interaction):
            if inter.user.id != self.uid:
                return await inter.response.send_message("❌ Non è il tuo ordine.", ephemeral=True)
            cat = sel.values[0]
            piatti = _ISLA_CATEGORIE[cat]
            await inter.response.edit_message(
                embed=_isla_embed_categoria(cat, piatti, inter.user),
                view=IslaPiattiView(self.uid, cat, piatti)
            )

        sel.callback = sel_callback
        self.add_item(sel)


@bot.tree.command(name="isla-de-oro", description="⚓ Apri il menú del ristorante Isla de Oro")
@_blocca_se_dorme()
async def isla_de_oro(interaction: discord.Interaction):
    embed = _isla_embed_home(interaction.user)
    await interaction.response.send_message(
        embed=embed,
        view=IslaMenuCategoriaView(interaction.user.id),
        ephemeral=True
    )


# ══════════════════════════════════════════════════════════════════
# 💾 BACKUP SERVER — solo Developer
# ══════════════════════════════════════════════════════════════════

BACKUP_OUTPUT_FILE         = "backup_completo.json"
BACKUP_MESSAGGI_PER_CANALE = None   # None = TUTTI i messaggi senza limite

def _bk_permessi_to_dict(permissions: discord.Permissions) -> dict:
    return {nome: valore for nome, valore in permissions}

def _bk_overwrite_to_dict(overwrite: discord.PermissionOverwrite) -> dict:
    allow, deny = overwrite.pair()
    return {"allow": _bk_permessi_to_dict(allow), "deny": _bk_permessi_to_dict(deny)}

def _bk_overwrites_list(obj) -> list:
    result = []
    for target, overwrite in obj.overwrites.items():
        result.append({
            "id":       str(target.id),
            "nome":     target.name,
            "tipo":     "ruolo" if isinstance(target, discord.Role) else "membro",
            "permessi": _bk_overwrite_to_dict(overwrite),
        })
    return result

async def _bk_leggi_messaggi(canale) -> list:
    """Legge TUTTI i messaggi del canale in ordine cronologico (dal più vecchio al più recente)."""
    messaggi = []
    try:
        async for msg in canale.history(limit=BACKUP_MESSAGGI_PER_CANALE, oldest_first=True):
            messaggi.append({
                "id":          str(msg.id),
                "autore":      str(msg.author),
                "autore_id":   str(msg.author.id),
                "autore_avatar": str(msg.author.display_avatar.url) if msg.author.display_avatar else None,
                "contenuto":   msg.content,
                "timestamp":   msg.created_at.isoformat(),
                "pinned":      msg.pinned,
                "tipo":        msg.type.name,
                "attachments": [{"nome": a.filename, "url": a.url} for a in msg.attachments],
                "embeds":      [{"titolo": e.title or "", "desc": e.description or "", "url": e.url or ""} for e in msg.embeds],
                "reactions":   [{"emoji": str(r.emoji), "count": r.count} for r in msg.reactions],
            })
    except discord.Forbidden:
        messaggi = [{"errore": "Accesso negato"}]
    except discord.HTTPException as e:
        messaggi = [{"errore": str(e)}]
    return messaggi

async def _bk_server_info(guild: discord.Guild) -> dict:
    return {
        "id":                str(guild.id),
        "nome":              guild.name,
        "descrizione":       guild.description,
        "icona_url":         str(guild.icon.url) if guild.icon else None,
        "banner_url":        str(guild.banner.url) if guild.banner else None,
        "splash_url":        str(guild.splash.url) if guild.splash else None,
        "owner_id":          str(guild.owner_id),
        "boost_level":       guild.premium_tier,
        "boost_count":       guild.premium_subscription_count,
        "verifica":          guild.verification_level.name,
        "filtro_contenuti":  guild.explicit_content_filter.name,
        "mfa_level":         guild.mfa_level.name if hasattr(guild.mfa_level, "name") else str(guild.mfa_level),
        "notifiche_default": guild.default_notifications.name,
        "creato_il":         guild.created_at.isoformat(),
        "vanity_url":        guild.vanity_url_code,
        "canale_regole_id":  str(guild.rules_channel.id) if guild.rules_channel else None,
        "canale_sistema_id": str(guild.system_channel.id) if guild.system_channel else None,
        "canale_afk_id":     str(guild.afk_channel.id) if guild.afk_channel else None,
        "afk_timeout_sec":   guild.afk_timeout,
        "funzionalita":      list(guild.features),
        "member_count":      guild.member_count,
    }

async def _bk_ruoli(guild: discord.Guild) -> list:
    ruoli = []
    for ruolo in sorted(guild.roles, key=lambda r: r.position, reverse=True):
        ruoli.append({
            "id":              str(ruolo.id),
            "nome":            ruolo.name,
            "colore":          ruolo.color.value,
            "colore_hex":      str(ruolo.color),
            "hoist":           ruolo.hoist,
            "mentionable":     ruolo.mentionable,
            "posizione":       ruolo.position,
            "managed":         ruolo.managed,
            "icona_url":       str(ruolo.icon.url) if getattr(ruolo, "icon", None) else None,
            "permessi_valore": ruolo.permissions.value,
            "permessi":        _bk_permessi_to_dict(ruolo.permissions),
        })
    return ruoli

async def _bk_emoji(guild: discord.Guild) -> list:
    return [{
        "id": str(e.id), "nome": e.name, "animata": e.animated,
        "managed": e.managed, "url": str(e.url),
        "ruoli_ids": [str(r.id) for r in e.roles],
    } for e in guild.emojis]

async def _bk_sticker(guild: discord.Guild) -> list:
    return [{
        "id": str(s.id), "nome": s.name, "descrizione": s.description,
        "formato": s.format.name, "url": str(s.url),
    } for s in guild.stickers]

async def _bk_webhook(guild: discord.Guild) -> list:
    try:
        return [{
            "id": str(wh.id), "nome": wh.name, "url": wh.url,
            "canale_id": str(wh.channel_id) if wh.channel_id else None,
            "tipo": wh.type.name,
            "creato_il": wh.created_at.isoformat() if wh.created_at else None,
        } for wh in await guild.webhooks()]
    except discord.Forbidden:
        return [{"errore": "Accesso negato"}]

async def _bk_inviti(guild: discord.Guild) -> list:
    try:
        return [{
            "codice": inv.code, "url": inv.url,
            "canale_id": str(inv.channel.id) if inv.channel else None,
            "canale": inv.channel.name if inv.channel else None,
            "creato_da": str(inv.inviter) if inv.inviter else None,
            "usi": inv.uses, "max_usi": inv.max_uses,
            "scadenza": inv.expires_at.isoformat() if inv.expires_at else None,
            "temporaneo": inv.temporary,
            "creato_il": inv.created_at.isoformat() if inv.created_at else None,
        } for inv in await guild.invites()]
    except discord.Forbidden:
        return [{"errore": "Accesso negato"}]

async def _bk_eventi(guild: discord.Guild) -> list:
    try:
        return [{
            "id": str(ev.id), "nome": ev.name, "descrizione": ev.description,
            "stato": ev.status.name, "tipo_luogo": ev.entity_type.name,
            "luogo": ev.location if ev.entity_type == discord.EntityType.external else None,
            "canale_id": str(ev.channel_id) if ev.channel_id else None,
            "inizio": ev.start_time.isoformat() if ev.start_time else None,
            "fine": ev.end_time.isoformat() if ev.end_time else None,
            "creatore_id": str(ev.creator_id) if ev.creator_id else None,
        } for ev in await guild.fetch_scheduled_events()]
    except discord.Forbidden:
        return [{"errore": "Accesso negato"}]

async def _bk_thread(canale) -> list:
    thread_list = []
    try:
        threads_visti = {t.id: t for t in canale.threads}
        try:
            async for t in canale.guild.active_threads():
                if t.parent_id == canale.id and t.id not in threads_visti:
                    threads_visti[t.id] = t
        except (discord.Forbidden, AttributeError):
            pass
        for t in threads_visti.values():
            messaggi_thread = await _bk_leggi_messaggi(t)
            thread_list.append({
                "id": str(t.id), "nome": t.name,
                "archiviato": t.archived, "bloccato": t.locked,
                "slowmode_sec": t.slowmode_delay,
                "creato_il": t.created_at.isoformat() if t.created_at else None,
                "messaggi": messaggi_thread,
            })
    except Exception:
        pass
    return thread_list

async def _bk_canali(guild: discord.Guild) -> list:
    canali_data = []
    tutti_canali = (
        list(guild.categories) +
        list(guild.text_channels) +
        list(guild.voice_channels) +
        list(guild.stage_channels) +
        list(guild.forums) +
        [c for c in guild.channels if isinstance(c, discord.ForumChannel) or getattr(c, "type", None) == discord.ChannelType.news]
    )
    visti = set()
    unici = []
    for c in tutti_canali:
        if c.id not in visti:
            visti.add(c.id)
            unici.append(c)

    for canale in unici:
        tipo = type(canale).__name__
        messaggi_data = []
        thread_data   = []
        if isinstance(canale, discord.TextChannel):
            messaggi_data = await _bk_leggi_messaggi(canale)
            thread_data   = await _bk_thread(canale)
        elif isinstance(canale, discord.ForumChannel):
            thread_data   = await _bk_thread(canale)

        canali_data.append({
            "id":               str(canale.id),
            "nome":             canale.name,
            "tipo":             tipo,
            "posizione":        getattr(canale, "position", None),
            "categoria_id":     str(canale.category_id) if getattr(canale, "category_id", None) else None,
            "categoria":        canale.category.name if getattr(canale, "category", None) else None,
            "nsfw":             getattr(canale, "nsfw", False),
            "slowmode_sec":     getattr(canale, "slowmode_delay", 0),
            "topic":            getattr(canale, "topic", None),
            "bitrate":          getattr(canale, "bitrate", None),
            "user_limit":       getattr(canale, "user_limit", None),
            "permessi_canale":  _bk_overwrites_list(canale),
            "messaggi":         messaggi_data,
            "thread":           thread_data,
        })
    return canali_data

def _bk_barra(perc: int) -> str:
    """Genera una barra di avanzamento testuale."""
    filled = int(perc / 10)
    return "█" * filled + "░" * (10 - filled)

async def _esegui_backup_completo(guild: discord.Guild, output_file: str = None, dm_user: discord.User = None) -> str:
    """Esegue il backup completo con aggiornamenti in DM sulla percentuale."""
    if output_file is None:
        output_file = f"backup_{guild.id}.json"

    # Fasi: (nome_fase, peso_percentuale)
    FASI = [
        ("🖥️ Info server",        5),
        ("👑 Ruoli",              10),
        ("😀 Emoji",              10),
        ("🎨 Sticker",            10),
        ("🔗 Webhook",            10),
        ("✉️ Inviti",             10),
        ("📅 Eventi programmati", 10),
        ("📁 Canali + messaggi",  35),
    ]
    totale_peso = sum(p for _, p in FASI)
    perc_corrente = 0

    async def aggiorna_dm(messaggio_dm, fase_nome, perc):
        if messaggio_dm is None:
            return
        barra = _bk_barra(perc)
        try:
            await messaggio_dm.edit(content=(
                f"⚙️ **Backup in corso — {guild.name}**\n"
                f"`{barra}` **{perc}%**\n"
                f"➤ {fase_nome}"
            ))
        except Exception:
            pass

    # Manda il primo messaggio DM
    messaggio_dm = None
    if dm_user:
        try:
            messaggio_dm = await dm_user.send(
                f"⚙️ **Backup in corso — {guild.name}**\n"
                f"`{'░' * 10}` **0%**\n"
                f"➤ Avvio..."
            )
        except discord.Forbidden:
            pass

    # ── Fase 1: Info server ──
    await aggiorna_dm(messaggio_dm, FASI[0][0], perc_corrente)
    server_info = await _bk_server_info(guild)
    perc_corrente += FASI[0][1]

    # ── Fase 2: Ruoli ──
    await aggiorna_dm(messaggio_dm, FASI[1][0], perc_corrente)
    ruoli = await _bk_ruoli(guild)
    perc_corrente += FASI[1][1]

    # ── Fase 3: Emoji ──
    await aggiorna_dm(messaggio_dm, FASI[2][0], perc_corrente)
    emoji = await _bk_emoji(guild)
    perc_corrente += FASI[2][1]

    # ── Fase 4: Sticker ──
    await aggiorna_dm(messaggio_dm, FASI[3][0], perc_corrente)
    sticker = await _bk_sticker(guild)
    perc_corrente += FASI[3][1]

    # ── Fase 5: Webhook ──
    await aggiorna_dm(messaggio_dm, FASI[4][0], perc_corrente)
    webhook = await _bk_webhook(guild)
    perc_corrente += FASI[4][1]

    # ── Fase 6: Inviti ──
    await aggiorna_dm(messaggio_dm, FASI[5][0], perc_corrente)
    inviti = await _bk_inviti(guild)
    perc_corrente += FASI[5][1]

    # ── Fase 7: Eventi ──
    await aggiorna_dm(messaggio_dm, FASI[6][0], perc_corrente)
    eventi = await _bk_eventi(guild)
    perc_corrente += FASI[6][1]

    # ── Fase 8: Canali (con aggiornamento per ogni canale) ──
    await aggiorna_dm(messaggio_dm, FASI[7][0], perc_corrente)
    canali_data = []
    tutti_canali_raw = (
        list(guild.categories) +
        list(guild.text_channels) +
        list(guild.voice_channels) +
        list(guild.stage_channels) +
        list(guild.forums) +
        [c for c in guild.channels if isinstance(c, discord.ForumChannel) or getattr(c, "type", None) == discord.ChannelType.news]
    )
    visti = set()
    unici = []
    for c in tutti_canali_raw:
        if c.id not in visti:
            visti.add(c.id)
            unici.append(c)

    n_canali = len(unici)
    for i, canale in enumerate(unici):
        tipo = type(canale).__name__
        messaggi_data = []
        thread_data   = []
        if isinstance(canale, discord.TextChannel):
            messaggi_data = await _bk_leggi_messaggi(canale)
            thread_data   = await _bk_thread(canale)
        elif isinstance(canale, discord.ForumChannel):
            thread_data   = await _bk_thread(canale)

        canali_data.append({
            "id":              str(canale.id),
            "nome":            canale.name,
            "tipo":            tipo,
            "posizione":       getattr(canale, "position", None),
            "categoria_id":    str(canale.category_id) if getattr(canale, "category_id", None) else None,
            "categoria":       canale.category.name if getattr(canale, "category", None) else None,
            "nsfw":            getattr(canale, "nsfw", False),
            "slowmode_sec":    getattr(canale, "slowmode_delay", 0),
            "topic":           getattr(canale, "topic", None),
            "bitrate":         getattr(canale, "bitrate", None),
            "user_limit":      getattr(canale, "user_limit", None),
            "permessi_canale": _bk_overwrites_list(canale),
            "messaggi":        messaggi_data,
            "thread":          thread_data,
        })

        # Aggiorna percentuale progressivamente durante i canali
        perc_canali = perc_corrente + int((i + 1) / n_canali * FASI[7][1])
        if messaggio_dm and (i % 5 == 0 or i == n_canali - 1):
            barra = _bk_barra(min(perc_canali, 99))
            try:
                await messaggio_dm.edit(content=(
                    f"⚙️ **Backup in corso — {guild.name}**\n"
                    f"`{barra}` **{min(perc_canali, 99)}%**\n"
                    f"➤ {FASI[7][0]}: #{canale.name} ({i+1}/{n_canali})"
                ))
            except Exception:
                pass

    # ── Salvataggio ──
    backup = {
        "meta": {
            "versione": "3.1",
            "data":     datetime.now(timezone.utc).isoformat(),
            "tipo":     "backup_completo_no_membri",
        },
        "server":             server_info,
        "ruoli":              ruoli,
        "emoji":              emoji,
        "sticker":            sticker,
        "webhook":            webhook,
        "inviti":             inviti,
        "eventi_programmati": eventi,
        "canali":             canali_data,
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)

    tot_msg    = sum(len(c.get("messaggi", [])) for c in canali_data)
    tot_thread = sum(len(c.get("thread",   [])) for c in canali_data)
    tot_msg_th = sum(len(t.get("messaggi", [])) for c in canali_data for t in c.get("thread", []))
    riepilogo  = (
        f"Ruoli: **{len(ruoli)}** | Canali: **{len(canali_data)}** | Emoji: **{len(emoji)}**\n"
        f"Sticker: **{len(sticker)}** | Webhook: **{len(webhook)}** | Inviti: **{len(inviti)}** | "
        f"Eventi: **{len(eventi)}**\n"
        f"Messaggi canali: **{tot_msg}** | Thread: **{tot_thread}** | Messaggi thread: **{tot_msg_th}**"
    )

    # ── DM finale con codice ripristino ──
    codice_ripristino = f"RESTORE:{guild.id}:{output_file}"
    if messaggio_dm:
        try:
            await messaggio_dm.edit(content=(
                f"✅ **Backup completato — {guild.name}**\n"
                f"`{'█' * 10}` **100%**\n\n"
                f"{riepilogo}\n"
                f"📁 File: `{output_file}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔑 **Codice ripristino** (copialo e usalo con `/ripristina`):\n"
                f"```\n{codice_ripristino}\n```"
            ))
        except Exception:
            pass

    return riepilogo, codice_ripristino


# ── Helpers ripristino ──────────────────────────────────────────

def _bk_build_overwrites(permessi_canale: list, guild: discord.Guild) -> dict:
    """Converte la lista permessi_canale del JSON in overwrites discord.py."""
    overwrites = {}
    for p in permessi_canale:
        # Cerca il target (ruolo o membro) per nome
        if p["tipo"] == "ruolo":
            target = discord.utils.get(guild.roles, name=p["nome"])
        else:
            target = guild.get_member_named(p["nome"])
        if target is None:
            continue
        allow_val = sum(v for v in p["permessi"]["allow"].values() if v is True and isinstance(v, bool))
        deny_val  = sum(v for v in p["permessi"]["deny"].values()  if v is True and isinstance(v, bool))
        allow = discord.Permissions(**{k: v for k, v in p["permessi"]["allow"].items() if isinstance(v, bool)})
        deny  = discord.Permissions(**{k: v for k, v in p["permessi"]["deny"].items()  if isinstance(v, bool)})
        ow = discord.PermissionOverwrite.from_pair(allow, deny)
        overwrites[target] = ow
    return overwrites

async def _ripristina_ruoli(guild: discord.Guild, ruoli: list, msg_dm, n_tot: int):
    """Ricrea i ruoli nel server di destinazione (dal basso verso l'alto)."""
    creati = 0
    mappa_ruoli = {}  # nome -> role object
    for i, r in enumerate(reversed(ruoli)):
        if r["nome"] == "@everyone":
            # Aggiorna i permessi di @everyone
            try:
                everyone = guild.default_role
                await everyone.edit(permissions=discord.Permissions(r["permessi_valore"]), reason="Ripristino backup")
            except Exception:
                pass
            mappa_ruoli["@everyone"] = guild.default_role
            continue
        esistente = discord.utils.get(guild.roles, name=r["nome"])
        if esistente:
            # Aggiorna permessi anche se già esiste
            try:
                await esistente.edit(
                    color=discord.Color(r["colore"]),
                    hoist=r["hoist"],
                    mentionable=r["mentionable"],
                    permissions=discord.Permissions(r["permessi_valore"]),
                    reason="Ripristino backup"
                )
            except Exception:
                pass
            mappa_ruoli[r["nome"]] = esistente
            continue
        try:
            nuovo = await guild.create_role(
                name=r["nome"],
                color=discord.Color(r["colore"]),
                hoist=r["hoist"],
                mentionable=r["mentionable"],
                permissions=discord.Permissions(r["permessi_valore"]),
                reason="Ripristino backup"
            )
            mappa_ruoli[r["nome"]] = nuovo
            creati += 1
        except Exception:
            pass
        if msg_dm and i % 5 == 0:
            perc = int((i + 1) / max(n_tot, 1) * 100)
            try:
                await msg_dm.edit(content=(
                    f"🔄 **Ripristino in corso...**\n"
                    f"`{_bk_barra(min(perc // 10, 10))}` **{perc}%**\n"
                    f"➤ 👑 Ruoli: {i+1}/{n_tot}"
                ))
            except Exception:
                pass
    return creati

async def _ripristina_canali(guild: discord.Guild, canali: list, msg_dm):
    """Ricrea categorie e canali con tutti i permessi nel server di destinazione."""
    mappa_cat = {}

    # Prima passa: crea/aggiorna categorie con permessi
    for c in canali:
        if c["tipo"] != "CategoryChannel":
            continue
        overwrites = _bk_build_overwrites(c.get("permessi_canale", []), guild)
        esistente = discord.utils.get(guild.categories, name=c["nome"])
        if esistente:
            try:
                await esistente.edit(overwrites=overwrites, reason="Ripristino backup")
            except Exception:
                pass
            mappa_cat[c["nome"]] = esistente
            continue
        try:
            nuova = await guild.create_category(
                name=c["nome"], overwrites=overwrites, reason="Ripristino backup"
            )
            mappa_cat[c["nome"]] = nuova
        except Exception:
            pass

    # Seconda passa: crea/aggiorna canali con permessi
    n_tot = len([c for c in canali if c["tipo"] != "CategoryChannel"])
    creati = 0
    for i, c in enumerate([c for c in canali if c["tipo"] != "CategoryChannel"]):
        categoria  = mappa_cat.get(c.get("categoria")) if c.get("categoria") else None
        overwrites = _bk_build_overwrites(c.get("permessi_canale", []), guild)
        esistente  = discord.utils.get(guild.channels, name=c["nome"])
        try:
            tipo = c["tipo"]
            if esistente:
                # Aggiorna solo i permessi se esiste già
                try:
                    await esistente.edit(overwrites=overwrites, reason="Ripristino backup")
                except Exception:
                    pass
            else:
                if tipo == "TextChannel":
                    await guild.create_text_channel(
                        name=c["nome"], category=categoria,
                        topic=c.get("topic"), nsfw=c.get("nsfw", False),
                        slowmode_delay=c.get("slowmode_sec", 0),
                        overwrites=overwrites,
                        reason="Ripristino backup"
                    )
                elif tipo == "VoiceChannel":
                    await guild.create_voice_channel(
                        name=c["nome"], category=categoria,
                        bitrate=min(c.get("bitrate") or 64000, guild.bitrate_limit),
                        user_limit=c.get("user_limit") or 0,
                        overwrites=overwrites,
                        reason="Ripristino backup"
                    )
                elif tipo == "ForumChannel":
                    await guild.create_forum(
                        name=c["nome"], category=categoria,
                        overwrites=overwrites,
                        reason="Ripristino backup"
                    )
                elif tipo == "StageChannel":
                    await guild.create_stage_channel(
                        name=c["nome"], category=categoria,
                        overwrites=overwrites,
                        reason="Ripristino backup"
                    )
                creati += 1
        except Exception:
            pass

        if msg_dm and i % 5 == 0:
            perc = int((i + 1) / max(n_tot, 1) * 100)
            try:
                await msg_dm.edit(content=(
                    f"🔄 **Ripristino in corso...**\n"
                    f"`{_bk_barra(min(perc // 10, 10))}` **{perc}%**\n"
                    f"➤ 📁 Canali: {i+1}/{n_tot}"
                ))
            except Exception:
                pass
    return creati


@bot.tree.command(name="backup", description="💾 Esegui il backup completo del server (solo Developer)")
@is_dev_or_owner()
async def backup_server(interaction: discord.Interaction):
    """Backup COMPLETO: ruoli, canali, permessi, TUTTI i messaggi. Risultato via DM silenzioso."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild = interaction.guild
    if guild is None:
        return await interaction.followup.send("❌ Devi usare questo comando in un server.", ephemeral=True)

    output_file = f"backup_{guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        riepilogo, codice_ripristino = await _esegui_backup_completo(
            guild, output_file=output_file, dm_user=interaction.user
        )
    except Exception as e:
        return await interaction.followup.send(f"❌ Errore durante il backup: `{e}`", ephemeral=True)

    embed = discord.Embed(
        title="✅ Backup completato",
        description=(
            f"**Server:** {guild.name} (`{guild.id}`)\n"
            f"**File:** `{output_file}`\n\n"
            f"{riepilogo}\n\n"
            f"📩 **Codice ripristino inviato in DM** — usalo con `/ripristina`."
        ),
        color=discord.Color.from_rgb(255, 107, 53),
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Richiesto da {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed, ephemeral=True)


# ─── Backup messaggi singolo utente ──────────────────────────────────────────

@bot.tree.command(name="backup-utente", description="👤 Copia tutti i messaggi di un utente dal server (solo Developer)")
@is_dev_or_owner()
@app_commands.describe(utente="L'utente di cui copiare i messaggi")
async def backup_utente(interaction: discord.Interaction, utente: discord.Member):
    """Scansiona TUTTI i canali e salva solo i messaggi dell'utente scelto in un JSON."""
    await interaction.response.defer(ephemeral=True, thinking=True)
    guild = interaction.guild
    if guild is None:
        return await interaction.followup.send("❌ Usa questo comando in un server.", ephemeral=True)

    output_file = f"backup_utente_{utente.id}_{guild.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # DM di avvio
    msg_dm = None
    try:
        msg_dm = await interaction.user.send(
            f"🔍 **Backup messaggi di {utente} avviato**\n"
            f"`{'░' * 10}` **0%**\n➤ Scansione canali in corso..."
        )
    except discord.Forbidden:
        pass

    async def aggiorna_dm(testo: str):
        if msg_dm:
            try:
                await msg_dm.edit(content=testo)
            except Exception:
                pass

    # Raccogli tutti i canali testo (inclusi thread)
    canali_testo = list(guild.text_channels)
    n_tot = len(canali_testo)
    risultati = []   # lista di {canale, messaggi}
    tot_msg = 0

    for i, canale in enumerate(canali_testo):
        perc = int((i + 1) / max(n_tot, 1) * 90)
        if i % 5 == 0 or i == n_tot - 1:
            await aggiorna_dm(
                f"🔍 **Backup messaggi di {utente}**\n"
                f"`{_bk_barra(perc // 10)}` **{perc}%**\n"
                f"➤ #{canale.name} ({i+1}/{n_tot})"
            )

        messaggi_canale = []
        try:
            async for msg in canale.history(limit=None, oldest_first=True):
                if msg.author.id == utente.id:
                    messaggi_canale.append({
                        "id":          str(msg.id),
                        "canale":      canale.name,
                        "canale_id":   str(canale.id),
                        "contenuto":   msg.content,
                        "timestamp":   msg.created_at.isoformat(),
                        "attachments": [{"nome": a.filename, "url": a.url} for a in msg.attachments],
                        "embeds":      [{"titolo": e.title or "", "desc": e.description or ""} for e in msg.embeds],
                        "reactions":   [{"emoji": str(r.emoji), "count": r.count} for r in msg.reactions],
                        "pinned":      msg.pinned,
                    })
        except discord.Forbidden:
            pass
        except Exception as e:
            print(f"[BACKUP-UTENTE] Errore #{canale.name}: {e}")

        # Scansiona anche i thread del canale
        messaggi_thread = []
        try:
            threads_visti = {t.id: t for t in canale.threads}
            try:
                async for t in guild.active_threads():
                    if t.parent_id == canale.id and t.id not in threads_visti:
                        threads_visti[t.id] = t
            except Exception:
                pass
            for thread in threads_visti.values():
                try:
                    async for msg in thread.history(limit=None, oldest_first=True):
                        if msg.author.id == utente.id:
                            messaggi_thread.append({
                                "id":          str(msg.id),
                                "canale":      f"{canale.name} > {thread.name}",
                                "canale_id":   str(canale.id),
                                "thread":      thread.name,
                                "thread_id":   str(thread.id),
                                "contenuto":   msg.content,
                                "timestamp":   msg.created_at.isoformat(),
                                "attachments": [{"nome": a.filename, "url": a.url} for a in msg.attachments],
                                "embeds":      [{"titolo": e.title or "", "desc": e.description or ""} for e in msg.embeds],
                                "reactions":   [{"emoji": str(r.emoji), "count": r.count} for r in msg.reactions],
                                "pinned":      msg.pinned,
                            })
                except Exception:
                    pass
        except Exception:
            pass

        tutti = messaggi_canale + messaggi_thread
        if tutti:
            risultati.append({
                "canale":    canale.name,
                "canale_id": str(canale.id),
                "messaggi":  tutti,
            })
            tot_msg += len(tutti)

    # Salva JSON
    dati_finali = {
        "meta": {
            "versione":   "1.0",
            "tipo":       "backup_utente",
            "data":       datetime.now(timezone.utc).isoformat(),
            "server":     guild.name,
            "server_id":  str(guild.id),
            "utente":     str(utente),
            "utente_id":  str(utente.id),
            "avatar_url": str(utente.display_avatar.url) if utente.display_avatar else None,
        },
        "canali": risultati,
        "totale_messaggi": tot_msg,
    }
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dati_finali, f, ensure_ascii=False, indent=2)
    except Exception as e:
        await aggiorna_dm(f"❌ Errore salvataggio file: `{e}`")
        return await interaction.followup.send(f"❌ Errore salvataggio: `{e}`", ephemeral=True)

    # DM finale
    await aggiorna_dm(
        f"✅ **Backup messaggi di {utente} completato!**\n"
        f"`{'█' * 10}` **100%**\n\n"
        f"💬 Messaggi trovati: **{tot_msg}**\n"
        f"📁 Canali scansionati: **{n_tot}**\n"
        f"📄 File: `{output_file}`"
    )

    embed = discord.Embed(
        title=f"✅ Backup utente completato",
        description=(
            f"**Utente:** {utente.mention} (`{utente.id}`)\n"
            f"**Server:** {guild.name}\n"
            f"**File:** `{output_file}`\n\n"
            f"💬 Messaggi totali: **{tot_msg}**\n"
            f"📁 Canali con messaggi: **{len(risultati)}** su {n_tot}"
        ),
        color=discord.Color.from_rgb(255, 107, 53),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=utente.display_avatar.url if utente.display_avatar else None)
    embed.set_footer(text=f"Richiesto da {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed, ephemeral=True)


# ─── Helper: ripristina messaggi via webhook ──────────────────────────────────

async def _ripristina_messaggi_canale(canale, messaggi: list):
    """Reinvia i messaggi salvati nel canale usando un webhook temporaneo (simula l'autore originale)."""
    if not messaggi:
        return 0

    # Crea webhook temporaneo — gestisce TextChannel e Thread
    wh = None
    try:
        # I thread non supportano create_webhook, bisogna crearlo sul canale padre
        if isinstance(canale, discord.Thread):
            canale_wh = canale.parent
        else:
            canale_wh = canale
        wh = await canale_wh.create_webhook(name="Ripristino Backup")
    except Exception as e:
        print(f"[BACKUP] Impossibile creare webhook su #{getattr(canale, 'name', '?')}: {e}")
        return 0

    inviati = 0
    errori  = 0
    try:
        for msg in messaggi:
            if msg.get("errore"):
                continue

            contenuto = msg.get("contenuto", "").strip()

            # Allegati: aggiungi URL come testo
            allegati_str = ""
            for att in msg.get("attachments", []):
                allegati_str += f"\n📎 [{att['nome']}]({att['url']})"

            testo_finale = (contenuto + allegati_str).strip()
            if not testo_finale:
                continue  # messaggio vuoto (solo embed di sistema ecc.)

            # Aggiunge timestamp originale come nota finale
            ts = msg.get("timestamp", "")
            footer_ts = f"\n-# 🕐 {ts[:19].replace('T', ' ')} UTC" if ts else ""
            testo_finale = (testo_finale + footer_ts)[:2000]

            # Avatar: usa stringa vuota se None (discord.py v2 non accetta None/Embed.Empty)
            avatar_url = msg.get("autore_avatar") or ""

            try:
                kwargs = dict(
                    content=testo_finale,
                    username=msg.get("autore", "Utente")[:80],
                )
                if avatar_url:
                    kwargs["avatar_url"] = avatar_url
                # Se il canale di destinazione è un thread, passa thread=canale
                if isinstance(canale, discord.Thread):
                    kwargs["thread"] = canale

                await wh.send(**kwargs)
                inviati += 1
                await asyncio.sleep(1.1)  # Discord webhook: max ~50 msg/min per webhook

            except discord.HTTPException as e:
                errori += 1
                print(f"[BACKUP] Errore invio messaggio in #{getattr(canale, 'name', '?')}: {e}")
                if e.status == 429:  # rate limited
                    await asyncio.sleep(5)
            except Exception as e:
                errori += 1
                print(f"[BACKUP] Errore generico messaggio: {e}")

    finally:
        try:
            await wh.delete()
        except Exception:
            pass

    print(f"[BACKUP] #{getattr(canale, 'name', '?')}: {inviati} messaggi inviati, {errori} errori")
    return inviati


@bot.tree.command(name="ripristina", description="♻️ Ripristina un backup su un server (solo Developer)")
@is_dev_or_owner()
@app_commands.describe(
    codice="Codice ripristino ricevuto in DM dopo il backup",
    guild_id="ID del server destinazione"
)
async def ripristina_server(interaction: discord.Interaction, codice: str, guild_id: str):
    await interaction.response.defer(ephemeral=True, thinking=True)

    # Valida codice
    try:
        parti = codice.strip().split(":")
        if len(parti) != 3 or parti[0] != "RESTORE":
            raise ValueError
        _guild_id_src = parti[1]
        output_file   = parti[2]
    except Exception:
        return await interaction.followup.send(
            "❌ Codice ripristino non valido. Usa quello fornito dal bot al termine del backup.",
            ephemeral=True
        )

    # Controlla file
    if not os.path.exists(output_file):
        return await interaction.followup.send(
            f"❌ File `{output_file}` non trovato sul server dove gira il bot.",
            ephemeral=True
        )

    # Controlla guild destinazione
    guild_dest = bot.get_guild(int(guild_id))
    if guild_dest is None:
        return await interaction.followup.send(
            f"❌ Server destinazione `{guild_id}` non trovato. Il bot è presente lì?",
            ephemeral=True
        )

    # Carica JSON
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            dati = json.load(f)
    except Exception as e:
        return await interaction.followup.send(f"❌ Errore lettura file backup: `{e}`", ephemeral=True)

    # Manda DM di avvio
    msg_dm = None
    try:
        msg_dm = await interaction.user.send(
            f"🔄 **Ripristino avviato su {guild_dest.name}**\n"
            f"`{'░' * 10}` **0%**\n➤ Avvio..."
        )
    except discord.Forbidden:
        pass

    ruoli_creati   = 0
    canali_creati  = 0
    messaggi_inviati = 0

    async def _aggiorna_dm_ripristino(testo: str):
        if msg_dm:
            try:
                await msg_dm.edit(content=testo)
            except Exception:
                pass

    try:
        # ── Fase 1: Ripristina ruoli ──
        await _aggiorna_dm_ripristino(
            f"🔄 **Ripristino in corso — {guild_dest.name}**\n"
            f"`{'░' * 10}` **0%**\n➤ 👑 Creazione ruoli..."
        )
        ruoli_creati = await _ripristina_ruoli(guild_dest, dati.get("ruoli", []), msg_dm, len(dati.get("ruoli", [])))

        # ── Fase 2: Ripristina canali ──
        await _aggiorna_dm_ripristino(
            f"🔄 **Ripristino in corso — {guild_dest.name}**\n"
            f"`{'███░░░░░░░'}` **30%**\n➤ 📁 Creazione canali e permessi..."
        )
        canali_creati = await _ripristina_canali(guild_dest, dati.get("canali", []), msg_dm)



    except Exception as e:
        await _aggiorna_dm_ripristino(f"❌ Errore durante il ripristino: `{e}`")
        return await interaction.followup.send(f"❌ Errore ripristino: `{e}`", ephemeral=True)

    # DM finale
    await _aggiorna_dm_ripristino(
        f"✅ **Ripristino completato — {guild_dest.name}**\n"
        f"`{'█' * 10}` **100%**\n\n"
        f"👑 Ruoli creati: **{ruoli_creati}**\n"
        f"📁 Canali creati: **{canali_creati}**\n"
        f"💬 Messaggi ripristinati: **{messaggi_inviati}**"
    )

    embed = discord.Embed(
        title="✅ Ripristino completato",
        description=(
            f"**Server destinazione:** {guild_dest.name} (`{guild_dest.id}`)\n"
            f"**Sorgente backup:** `{output_file}`\n\n"
            f"👑 Ruoli creati: **{ruoli_creati}**\n"
            f"📁 Canali creati: **{canali_creati}**\n"
            f"💬 Messaggi ripristinati: **{messaggi_inviati}**"
        ),
        color=discord.Color.from_rgb(255, 107, 53),
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Richiesto da {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="ripristina-messaggiutente", description="👤 Ripristina i messaggi di un utente da un backup-utente (solo Developer)")
@is_dev_or_owner()
@app_commands.describe(
    file_backup="Nome del file generato da /backup-utente (es: backup_utente_123_456_20260822.json)",
    guild_id="ID del server destinazione dove inviare i messaggi"
)
async def ripristina_messaggi_utente(interaction: discord.Interaction, file_backup: str, guild_id: str):
    """Ripristina i messaggi di una persona specifica da un file backup-utente."""
    await interaction.response.defer(ephemeral=True, thinking=True)

    # Controlla file
    if not os.path.exists(file_backup):
        return await interaction.followup.send(
            f"❌ File `{file_backup}` non trovato. Controlla il nome esatto ricevuto in DM dopo `/backup-utente`.",
            ephemeral=True
        )

    # Carica JSON
    try:
        with open(file_backup, "r", encoding="utf-8") as f:
            dati = json.load(f)
    except Exception as e:
        return await interaction.followup.send(f"❌ Errore lettura file: `{e}`", ephemeral=True)

    # Verifica che sia un backup-utente
    if dati.get("meta", {}).get("tipo") != "backup_utente":
        return await interaction.followup.send(
            "❌ Il file non è un backup-utente valido. Usa il file generato da `/backup-utente`.",
            ephemeral=True
        )

    # Controlla guild destinazione
    guild_dest = bot.get_guild(int(guild_id))
    if guild_dest is None:
        return await interaction.followup.send(
            f"❌ Server `{guild_id}` non trovato. Il bot è presente lì?",
            ephemeral=True
        )

    nome_utente    = dati.get("meta", {}).get("utente", "Utente")
    avatar_utente  = dati.get("meta", {}).get("avatar_url")
    tot_msg_totali = dati.get("totale_messaggi", 0)
    canali_utente  = dati.get("canali", [])
    n_canali       = len(canali_utente)

    # DM di avvio
    msg_dm = None
    try:
        msg_dm = await interaction.user.send(
            f"🔄 **Ripristino messaggi di {nome_utente}**\n"
            f"`{'░' * 10}` **0%**\n"
            f"➤ {tot_msg_totali} messaggi in {n_canali} canali..."
        )
    except discord.Forbidden:
        pass

    async def aggiorna_dm(testo: str):
        if msg_dm:
            try:
                await msg_dm.edit(content=testo)
            except Exception:
                pass

    # Ri-fetch canali aggiornati
    try:
        await guild_dest.fetch_channels()
    except Exception:
        pass

    messaggi_inviati = 0

    for idx, c_data in enumerate(canali_utente):
        nome_canale = c_data.get("canale", "?")
        messaggi_u  = [
            m for m in c_data.get("messaggi", [])
            if not m.get("errore") and (m.get("contenuto") or m.get("attachments"))
        ]
        if not messaggi_u:
            continue

        perc = int((idx + 1) / max(n_canali, 1) * 95)
        await aggiorna_dm(
            f"🔄 **Ripristino messaggi di {nome_utente}**\n"
            f"`{_bk_barra(perc // 10)}` **{perc}%**\n"
            f"➤ #{nome_canale} — {len(messaggi_u)} msg ({idx+1}/{n_canali})"
        )

        # Cerca il canale per nome (case-insensitive)
        canale_dest = discord.utils.find(
            lambda c, n=nome_canale: c.name.lower() == n.lower(),
            guild_dest.text_channels
        )
        if canale_dest is None:
            try:
                await guild_dest.fetch_channels()
                canale_dest = discord.utils.find(
                    lambda c, n=nome_canale: c.name.lower() == n.lower(),
                    guild_dest.text_channels
                )
            except Exception:
                pass

        if canale_dest:
            inviati = await _ripristina_messaggi_canale(canale_dest, messaggi_u)
            messaggi_inviati += inviati
        else:
            print(f"[RIPRISTINA-UTENTE] Canale #{nome_canale} non trovato nel server destinazione — salto")

    # DM finale
    await aggiorna_dm(
        f"✅ **Ripristino messaggi completato!**\n"
        f"`{'█' * 10}` **100%**\n\n"
        f"👤 Utente: **{nome_utente}**\n"
        f"💬 Messaggi ripristinati: **{messaggi_inviati}** / {tot_msg_totali}\n"
        f"📁 Server: **{guild_dest.name}**"
    )

    embed = discord.Embed(
        title="✅ Ripristino messaggi utente completato",
        description=(
            f"**Utente:** {nome_utente}\n"
            f"**Server destinazione:** {guild_dest.name} (`{guild_dest.id}`)\n"
            f"**File usato:** `{file_backup}`\n\n"
            f"💬 Messaggi ripristinati: **{messaggi_inviati}** / {tot_msg_totali}"
        ),
        color=discord.Color.from_rgb(255, 107, 53),
        timestamp=datetime.now()
    )
    if avatar_utente:
        embed.set_thumbnail(url=avatar_utente)
    embed.set_footer(text=f"Richiesto da {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=embed, ephemeral=True)


# --- AVVIO DEL BOT ---


@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    ch = message.guild.get_channel(CH_LOG_MESSAGGI) if message.guild else None
    if not ch:
        return
    embed = discord.Embed(title="🗑️ Messaggio eliminato", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Utente", value=message.author.mention, inline=True)
    embed.add_field(name="Canale", value=message.channel.mention, inline=True)
    embed.add_field(name="Contenuto", value=message.content[:1024] if message.content else "*[allegato/embed]*", inline=False)
    embed.set_footer(text=f"ID: {message.author.id}")
    await ch.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    ch = before.guild.get_channel(CH_LOG_MESSAGGI) if before.guild else None
    if not ch:
        return
    embed = discord.Embed(title="✏️ Messaggio modificato", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Utente", value=before.author.mention, inline=True)
    embed.add_field(name="Canale", value=before.channel.mention, inline=True)
    embed.add_field(name="Prima", value=before.content[:512] if before.content else "*vuoto*", inline=False)
    embed.add_field(name="Dopo", value=after.content[:512] if after.content else "*vuoto*", inline=False)
    embed.set_footer(text=f"ID: {before.author.id}")
    await ch.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    ch = channel.guild.get_channel(CH_LOG_CANALI)
    if not ch:
        return
    embed = discord.Embed(title="✅ Canale creato", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Nome", value=channel.mention, inline=True)
    embed.add_field(name="Tipo", value=str(channel.type), inline=True)
    await ch.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel):
    ch = channel.guild.get_channel(CH_LOG_CANALI)
    if not ch:
        return
    embed = discord.Embed(title="❌ Canale eliminato", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Nome", value=f"#{channel.name}", inline=True)
    embed.add_field(name="Tipo", value=str(channel.type), inline=True)
    await ch.send(embed=embed)

@bot.event
async def on_guild_role_create(role):
    ch = role.guild.get_channel(CH_LOG_RUOLI)
    if not ch:
        return
    embed = discord.Embed(title="✅ Ruolo creato", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Ruolo", value=role.mention, inline=True)
    await ch.send(embed=embed)

@bot.event
async def on_guild_role_delete(role):
    ch = role.guild.get_channel(CH_LOG_RUOLI)
    if not ch:
        return
    embed = discord.Embed(title="❌ Ruolo eliminato", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Nome", value=role.name, inline=True)
    await ch.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return
    ch = after.guild.get_channel(CH_LOG_RUOLI)
    if not ch:
        return
    aggiunti = [r for r in after.roles if r not in before.roles]
    rimossi  = [r for r in before.roles if r not in after.roles]
    if not aggiunti and not rimossi:
        return
    embed = discord.Embed(title="🔄 Ruoli aggiornati", color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    embed.add_field(name="Membro", value=after.mention, inline=False)
    if aggiunti:
        embed.add_field(name="✅ Aggiunti", value=" ".join(r.mention for r in aggiunti), inline=True)
    if rimossi:
        embed.add_field(name="❌ Rimossi", value=" ".join(r.mention for r in rimossi), inline=True)
    await ch.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    ch = member.guild.get_channel(CH_LOG_VOCALI)
    if not ch:
        return
    if before.channel == after.channel:
        return
    embed = discord.Embed(color=discord.Color.from_rgb(255, 107, 53), timestamp=datetime.now())
    if before.channel is None:
        embed.title = "🔊 Entrato in vocale"
        embed.add_field(name="Membro", value=member.mention, inline=True)
        embed.add_field(name="Canale", value=after.channel.name, inline=True)
    elif after.channel is None:
        embed.title = "🔇 Uscito da vocale"
        embed.add_field(name="Membro", value=member.mention, inline=True)
        embed.add_field(name="Canale", value=before.channel.name, inline=True)
    else:
        embed.title = "🔀 Cambiato canale vocale"
        embed.add_field(name="Membro", value=member.mention, inline=True)
        embed.add_field(name="Da", value=before.channel.name, inline=True)
        embed.add_field(name="A", value=after.channel.name, inline=True)
    await ch.send(embed=embed)

@bot.event
async def on_ready():
    print(f"🔥 MASTER BOT RP ONLINE — Caricamento completato! 🚀")
    try:
        sincronizzati = await bot.tree.sync()
        print(f"⚡ Sincronizzati {len(sincronizzati)} comandi slash con successo!")
    except Exception as e:
        print(f"❌ Errore di sincronizzazione: {e}")
    if not autosave_task.is_running():
        autosave_task.start()
        print("💾 Autosave attivo: i dati vengono salvati ogni 20 secondi.")
    if not decremento_bisogni_task.is_running():
        decremento_bisogni_task.start()
        print("🍽️ Decremento fame/sete attivo: ogni 10 minuti.")
    if not pagamento_rate_task.is_running():
        pagamento_rate_task.start()
        print("💳 Pagamento rate finanziamenti attivo: ogni 7 giorni.")

    bot.add_view(ViewSondaggioPulsanti())
    bot.add_view(ViewPannelloBg())
    bot.add_view(TicketPanelView())
    bot.add_view(ViewBandi())
    bot.add_view(ViewEsitoBandoCustom(0, "__placeholder__"))
    bot.add_view(ViewFirmaContratto())
    bot.add_view(ViewEsitoForumBando(0, "__placeholder__", "__placeholder__"))


# ══════════════════════════════════════════════════════════════════
# 🏠  SISTEMA CONTRATTO D'AFFITTO — DYNASTY 8
# ══════════════════════════════════════════════════════════════════

RUOLO_DIRETTORE_DYNASTY8 = 1532126796877660343   # direttore dynasty8
RUOLO_FIRMA_DYNASTY8     = 1532126909939318926   # ruolo che può firmare (direttore firma)

# Stato firme per ogni contratto attivo: { message_id: { "cittadino": bool, "direttore": bool, "cittadino_id": int } }
contratti_affitto_firme: dict = {}


class ModalContrattoAffitto(discord.ui.Modal, title="🏠 Contratto d'Affitto — Dynasty 8"):
    nome_cognome = discord.ui.TextInput(
        label="Nome e Cognome IC dell'intestatario",
        placeholder="Es: Marco Rossi",
        required=True, max_length=80
    )
    posizione_casa = discord.ui.TextInput(
        label="Posizione / Indirizzo della casa",
        placeholder="Es: 1561 San Vitas St, Apt. 3",
        required=True, max_length=150
    )
    affitto_settimanale = discord.ui.TextInput(
        label="Affitto settimanale ($)",
        placeholder="Es: 5000",
        required=True, max_length=20
    )
    responsabilita = discord.ui.TextInput(
        label="Responsabilità dell'inquilino",
        style=discord.TextStyle.paragraph,
        placeholder="Es: Mantenere la proprietà in buono stato, non subaffittare...",
        required=True, max_length=500
    )
    occupazione_reddito = discord.ui.TextInput(
        label="Occupazione e reddito IC",
        placeholder="Es: Meccanico, reddito settimanale ~8.000$",
        required=True, max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Cerca il membro per nome (intestatario) — il direttore lo compila
        embed = discord.Embed(
            title="🏠 CONTRATTO D'AFFITTO — DYNASTY 8",
            color=discord.Color.from_rgb(255, 107, 53),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=LOGO_SERVER)
        embed.add_field(name="📋 Intestatario", value=self.nome_cognome.value, inline=True)
        embed.add_field(name="📍 Indirizzo", value=self.posizione_casa.value, inline=True)
        embed.add_field(name="💰 Affitto Settimanale", value=f"**${self.affitto_settimanale.value}**", inline=True)
        embed.add_field(name="📌 Responsabilità", value=self.responsabilita.value, inline=False)
        embed.add_field(name="💼 Occupazione e Reddito IC", value=self.occupazione_reddito.value, inline=False)
        embed.add_field(
            name="✍️ Firme",
            value=(
                "🔴 Cittadino — **In attesa di firma**\n"
                "🔴 Direttore Dynasty 8 — **In attesa di firma**"
            ),
            inline=False
        )
        embed.set_footer(text=f"Contratto emesso da {interaction.user.display_name} | Dynasty 8 Real Estate")

        view = ViewFirmaContratto()
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()

        # Salva stato firme
        contratti_affitto_firme[msg.id] = {
            "cittadino":    False,
            "direttore":    False,
            "cittadino_id": None,
            "direttore_id": None,
            "embed_data": {
                "intestatario":  self.nome_cognome.value,
                "indirizzo":     self.posizione_casa.value,
                "affitto":       self.affitto_settimanale.value,
                "responsabilita": self.responsabilita.value,
                "occupazione":   self.occupazione_reddito.value,
            }
        }


class ViewFirmaContratto(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✍️ Firma (Cittadino)", style=discord.ButtonStyle.primary, custom_id="contratto_firma_cittadino")
    async def firma_cittadino(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg_id = interaction.message.id
        stato  = contratti_affitto_firme.get(msg_id)
        if not stato:
            return await interaction.response.send_message("❌ Contratto non trovato.", ephemeral=True)

        # Chiunque può firmare come cittadino (è l'intestatario che preme)
        if stato["cittadino"]:
            return await interaction.response.send_message("❌ Il cittadino ha già firmato.", ephemeral=True)

        # Non permettere al direttore di firmare come cittadino
        if any(r.id == RUOLO_DIRETTORE_DYNASTY8 for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Il direttore deve usare il bottone apposito.", ephemeral=True)

        stato["cittadino"]    = True
        stato["cittadino_id"] = interaction.user.id

        await _aggiorna_embed_contratto(interaction, msg_id, stato)
        await interaction.response.send_message("✅ Hai firmato il contratto come cittadino.", ephemeral=True)

    @discord.ui.button(label="✍️ Firma (Direttore)", style=discord.ButtonStyle.success, custom_id="contratto_firma_direttore")
    async def firma_direttore(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg_id = interaction.message.id
        stato  = contratti_affitto_firme.get(msg_id)
        if not stato:
            return await interaction.response.send_message("❌ Contratto non trovato.", ephemeral=True)

        # Solo chi ha il ruolo giusto può firmare come direttore
        if not any(r.id in (RUOLO_DIRETTORE_DYNASTY8, RUOLO_FIRMA_DYNASTY8) for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Non hai il ruolo per firmare come Direttore Dynasty 8.", ephemeral=True)

        if stato["direttore"]:
            return await interaction.response.send_message("❌ Il direttore ha già firmato.", ephemeral=True)

        stato["direttore"]    = True
        stato["direttore_id"] = interaction.user.id

        await _aggiorna_embed_contratto(interaction, msg_id, stato)
        await interaction.response.send_message("✅ Hai firmato il contratto come Direttore.", ephemeral=True)


async def _aggiorna_embed_contratto(interaction: discord.Interaction, msg_id: int, stato: dict):
    dati = stato["embed_data"]

    citt_firma = f"✅ <@{stato['cittadino_id']}> — **Firmato**" if stato["cittadino"] else "🔴 Cittadino — **In attesa di firma**"
    dir_firma  = f"✅ <@{stato['direttore_id']}> — **Firmato**" if stato["direttore"] else "🔴 Direttore Dynasty 8 — **In attesa di firma**"

    embed = discord.Embed(
        title="🏠 CONTRATTO D'AFFITTO — DYNASTY 8",
        color=discord.Color.green() if (stato["cittadino"] and stato["direttore"]) else discord.Color.from_rgb(255, 107, 53),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.add_field(name="📋 Intestatario",        value=dati["intestatario"],  inline=True)
    embed.add_field(name="📍 Indirizzo",           value=dati["indirizzo"],     inline=True)
    embed.add_field(name="💰 Affitto Settimanale", value=f"**${dati['affitto']}**", inline=True)
    embed.add_field(name="📌 Responsabilità",      value=dati["responsabilita"], inline=False)
    embed.add_field(name="💼 Occupazione e Reddito IC", value=dati["occupazione"], inline=False)
    embed.add_field(name="✍️ Firme", value=f"{citt_firma}\n{dir_firma}", inline=False)

    if stato["cittadino"] and stato["direttore"]:
        embed.add_field(
            name="✅ CONTRATTO UFFICIALE",
            value="Il contratto è stato **firmato da entrambe le parti** ed è ora ufficialmente valido.",
            inline=False
        )
        embed.set_footer(text="Dynasty 8 Real Estate — Contratto Ufficiale ✅")
        # Disabilita i bottoni
        view = discord.ui.View()
        await interaction.message.edit(embed=embed, view=view)
    else:
        embed.set_footer(text="Dynasty 8 Real Estate — In attesa di firme")
        await interaction.message.edit(embed=embed)


dynasty8_group = app_commands.Group(name="dynasty8", description="🏠 Comandi Agenzia Immobiliare Dynasty 8")

@dynasty8_group.command(name="contratto", description="🏠 Crea un contratto d'affitto [Solo Direttore Dynasty 8]")
async def contratto_affitto_cmd(interaction: discord.Interaction):
    if not any(r.id in (RUOLO_DIRETTORE_DYNASTY8, RUOLO_FIRMA_DYNASTY8) for r in interaction.user.roles):
        return await interaction.response.send_message(
            "❌ Solo il Direttore Dynasty 8 può emettere contratti d'affitto.", ephemeral=True
        )
    await interaction.response.send_modal(ModalContrattoAffitto())

@dynasty8_group.command(name="revoca", description="🚫 Revoca un contratto d'affitto [Solo Direttore Dynasty 8]")
@app_commands.describe(intestatario="Nome e Cognome IC dell'intestatario", motivo="Motivo della revoca")
async def revoca_contratto_cmd(interaction: discord.Interaction, intestatario: str, motivo: str):
    if not any(r.id == RUOLO_DIRETTORE_DYNASTY8 for r in interaction.user.roles):
        return await interaction.response.send_message(
            "❌ Solo il Direttore Dynasty 8 può revocare un contratto.", ephemeral=True
        )
    embed = discord.Embed(
        title="🚫 REVOCA CONTRATTO D'AFFITTO — DYNASTY 8",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=LOGO_SERVER)
    embed.add_field(name="📋 Intestatario", value=intestatario, inline=True)
    embed.add_field(name="❌ Motivo Revoca", value=motivo, inline=False)
    embed.add_field(name="👤 Revocato da", value=interaction.user.mention, inline=True)
    embed.set_footer(text="Dynasty 8 Real Estate — Contratto Revocato")
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Contratto revocato e pubblicato nel canale.", ephemeral=True)

bot.tree.add_command(dynasty8_group)


# --- AVVIO DEL BOT ---
if not TOKEN:
    raise RuntimeError(
        "❌ Token Discord non trovato. Imposta la variabile d'ambiente DISCORD_TOKEN "
        "(o creane una in un file .env) prima di avviare il bot."
    )

bot.run(TOKEN)
