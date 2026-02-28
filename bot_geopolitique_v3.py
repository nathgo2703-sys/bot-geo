import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
import re
from datetime import datetime
import urllib.request

# ============================================================
# CONFIGURATION
# ============================================================
TOKEN = os.environ.get("TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ============================================================
# RÉGIONS DU MONDE (population réelle, ressources, bonus)
# ============================================================
REGIONS = {
    # ═══ EUROPE ═══
    "france": {
        "nom": "🇫🇷 France", "continent": "Europe",
        "population": 68_000_000, "pib_base": 2_800_000_000_000,
        "tresor_base": 500_000_000,
        "ressources": {"blé": 800, "acier": 400, "vin": 600, "pétrole": 50},
        "bonus": "Agriculture & Luxe : +20% revenus fermes",
        "bonus_id": "agriculture",
        "chomage_base": 7.1, "inflation_base": 2.5
    },
    "allemagne": {
        "nom": "🇩🇪 Allemagne", "continent": "Europe",
        "population": 84_000_000, "pib_base": 4_100_000_000_000,
        "tresor_base": 700_000_000,
        "ressources": {"acier": 900, "charbon": 600, "machines": 800},
        "bonus": "Industrie : +25% revenus usines",
        "bonus_id": "industrie",
        "chomage_base": 3.0, "inflation_base": 2.1
    },
    "royaume_uni": {
        "nom": "🇬🇧 Royaume-Uni", "continent": "Europe",
        "population": 67_000_000, "pib_base": 3_100_000_000_000,
        "tresor_base": 600_000_000,
        "ressources": {"pétrole": 300, "acier": 300, "finance": 900},
        "bonus": "Finance & Commerce : +20% revenus ports",
        "bonus_id": "commerce",
        "chomage_base": 4.2, "inflation_base": 2.8
    },
    "russie": {
        "nom": "🇷🇺 Russie", "continent": "Europe/Asie",
        "population": 144_000_000, "pib_base": 1_800_000_000_000,
        "tresor_base": 400_000_000,
        "ressources": {"pétrole": 2000, "gaz": 2000, "acier": 800, "blé": 600},
        "bonus": "Ressources naturelles : +30% revenus mines/raffineries",
        "bonus_id": "ressources",
        "chomage_base": 3.9, "inflation_base": 5.0
    },
    "italie": {
        "nom": "🇮🇹 Italie", "continent": "Europe",
        "population": 60_000_000, "pib_base": 2_100_000_000_000,
        "tresor_base": 350_000_000,
        "ressources": {"vin": 800, "marbre": 500, "tourisme": 700},
        "bonus": "Tourisme & Culture : +25% revenus stades/aéroports",
        "bonus_id": "tourisme",
        "chomage_base": 7.8, "inflation_base": 2.9
    },
    "espagne": {
        "nom": "🇪🇸 Espagne", "continent": "Europe",
        "population": 47_000_000, "pib_base": 1_400_000_000_000,
        "tresor_base": 280_000_000,
        "ressources": {"blé": 500, "tourisme": 800, "vin": 600},
        "bonus": "Tourisme : +20% revenus aéroports et stades",
        "bonus_id": "tourisme",
        "chomage_base": 12.9, "inflation_base": 3.1
    },
    "pologne": {
        "nom": "🇵🇱 Pologne", "continent": "Europe",
        "population": 38_000_000, "pib_base": 688_000_000_000,
        "tresor_base": 150_000_000,
        "ressources": {"charbon": 800, "acier": 400, "blé": 500},
        "bonus": "Industrie lourde : +15% revenus usines",
        "bonus_id": "industrie",
        "chomage_base": 5.1, "inflation_base": 4.2
    },
    "normandie": {
        "nom": "⚜️ Normandie", "continent": "Europe",
        "population": 3_300_000, "pib_base": 95_000_000_000,
        "tresor_base": 50_000_000,
        "ressources": {"blé": 400, "pommes": 300, "fromage": 200, "pêche": 300},
        "bonus": "Agriculture régionale : +15% revenus fermes",
        "bonus_id": "agriculture",
        "chomage_base": 8.5, "inflation_base": 2.3
    },
    "scandinavie": {
        "nom": "🏔️ Scandinavie", "continent": "Europe",
        "population": 21_000_000, "pib_base": 1_500_000_000_000,
        "tresor_base": 400_000_000,
        "ressources": {"pétrole": 800, "poisson": 600, "bois": 700},
        "bonus": "Énergie verte : +30% revenus centrales solaires",
        "bonus_id": "energie",
        "chomage_base": 4.0, "inflation_base": 2.0
    },
    # ═══ ASIE ═══
    "chine": {
        "nom": "🇨🇳 Chine", "continent": "Asie",
        "population": 1_400_000_000, "pib_base": 17_700_000_000_000,
        "tresor_base": 2_000_000_000,
        "ressources": {"acier": 2000, "charbon": 1800, "terres_rares": 1500},
        "bonus": "Industrie massive : +30% revenus usines",
        "bonus_id": "industrie",
        "chomage_base": 5.5, "inflation_base": 2.0
    },
    "japon": {
        "nom": "🇯🇵 Japon", "continent": "Asie",
        "population": 125_000_000, "pib_base": 4_200_000_000_000,
        "tresor_base": 800_000_000,
        "ressources": {"technologie": 1200, "acier": 500, "poisson": 400},
        "bonus": "Technologie : +30% revenus centres de recherche",
        "bonus_id": "technologie",
        "chomage_base": 2.6, "inflation_base": 1.0
    },
    "inde": {
        "nom": "🇮🇳 Inde", "continent": "Asie",
        "population": 1_430_000_000, "pib_base": 3_500_000_000_000,
        "tresor_base": 600_000_000,
        "ressources": {"blé": 1000, "acier": 600, "charbon": 700, "technologie": 500},
        "bonus": "Main d'oeuvre : +20% emplois toutes infrastructures",
        "bonus_id": "population",
        "chomage_base": 7.6, "inflation_base": 5.5
    },
    "arabie_saoudite": {
        "nom": "🇸🇦 Arabie Saoudite", "continent": "Asie",
        "population": 35_000_000, "pib_base": 1_100_000_000_000,
        "tresor_base": 1_500_000_000,
        "ressources": {"pétrole": 5000, "gaz": 2000, "or": 300},
        "bonus": "Pétrole : +50% revenus raffineries",
        "bonus_id": "ressources",
        "chomage_base": 5.6, "inflation_base": 2.5
    },
    "coree_sud": {
        "nom": "🇰🇷 Corée du Sud", "continent": "Asie",
        "population": 51_000_000, "pib_base": 1_700_000_000_000,
        "tresor_base": 400_000_000,
        "ressources": {"technologie": 1000, "acier": 600, "navires": 700},
        "bonus": "High-Tech : +25% revenus centres de recherche",
        "bonus_id": "technologie",
        "chomage_base": 2.9, "inflation_base": 3.6
    },
    "siberie": {
        "nom": "🏔️ Sibérie", "continent": "Asie",
        "population": 38_000_000, "pib_base": 400_000_000_000,
        "tresor_base": 120_000_000,
        "ressources": {"pétrole": 1500, "gaz": 1800, "bois": 1000, "or": 500},
        "bonus": "Ressources : +40% revenus mines",
        "bonus_id": "ressources",
        "chomage_base": 6.0, "inflation_base": 4.5
    },
    # ═══ AMÉRIQUE ═══
    "usa_est": {
        "nom": "🗽 USA - Côte Est", "continent": "Amérique",
        "population": 120_000_000, "pib_base": 7_000_000_000_000,
        "tresor_base": 1_200_000_000,
        "ressources": {"finance": 1500, "technologie": 800, "acier": 400},
        "bonus": "Finance mondiale : +30% revenus zones franches",
        "bonus_id": "commerce",
        "chomage_base": 3.8, "inflation_base": 3.2
    },
    "usa_ouest": {
        "nom": "🌉 USA - Côte Ouest", "continent": "Amérique",
        "population": 80_000_000, "pib_base": 5_000_000_000_000,
        "tresor_base": 900_000_000,
        "ressources": {"technologie": 2000, "pétrole": 400, "finance": 800},
        "bonus": "Silicon Valley : +40% revenus centres de recherche",
        "bonus_id": "technologie",
        "chomage_base": 4.2, "inflation_base": 3.5
    },
    "texas": {
        "nom": "🤠 Texas", "continent": "Amérique",
        "population": 30_000_000, "pib_base": 2_000_000_000_000,
        "tresor_base": 500_000_000,
        "ressources": {"pétrole": 2500, "gaz": 1500, "blé": 600, "acier": 300},
        "bonus": "Pétrole & Gaz : +35% revenus raffineries",
        "bonus_id": "ressources",
        "chomage_base": 4.1, "inflation_base": 3.0
    },
    "bresil": {
        "nom": "🇧🇷 Brésil", "continent": "Amérique",
        "population": 215_000_000, "pib_base": 2_100_000_000_000,
        "tresor_base": 300_000_000,
        "ressources": {"blé": 1200, "fer": 1500, "pétrole": 600, "bois": 1000},
        "bonus": "Agriculture tropicale : +25% revenus fermes",
        "bonus_id": "agriculture",
        "chomage_base": 8.1, "inflation_base": 4.6
    },
    "canada": {
        "nom": "🇨🇦 Canada", "continent": "Amérique",
        "population": 38_000_000, "pib_base": 2_100_000_000_000,
        "tresor_base": 450_000_000,
        "ressources": {"pétrole": 1200, "bois": 1500, "or": 400, "blé": 700},
        "bonus": "Ressources naturelles : +20% revenus mines",
        "bonus_id": "ressources",
        "chomage_base": 5.2, "inflation_base": 2.8
    },
    # ═══ AFRIQUE ═══
    "afrique_du_sud": {
        "nom": "🇿🇦 Afrique du Sud", "continent": "Afrique",
        "population": 60_000_000, "pib_base": 400_000_000_000,
        "tresor_base": 100_000_000,
        "ressources": {"or": 1500, "diamants": 800, "platine": 600, "charbon": 500},
        "bonus": "Minerais précieux : +40% revenus mines",
        "bonus_id": "ressources",
        "chomage_base": 32.9, "inflation_base": 5.9
    },
    "nigeria": {
        "nom": "🇳🇬 Nigeria", "continent": "Afrique",
        "population": 220_000_000, "pib_base": 477_000_000_000,
        "tresor_base": 80_000_000,
        "ressources": {"pétrole": 1800, "gaz": 800, "blé": 400},
        "bonus": "Pétrole africain : +30% revenus raffineries",
        "bonus_id": "ressources",
        "chomage_base": 33.3, "inflation_base": 18.0
    },
    "egypte": {
        "nom": "🇪🇬 Égypte", "continent": "Afrique",
        "population": 104_000_000, "pib_base": 476_000_000_000,
        "tresor_base": 90_000_000,
        "ressources": {"pétrole": 400, "blé": 500, "tourisme": 700, "canal": 900},
        "bonus": "Commerce maritime : +30% revenus ports",
        "bonus_id": "commerce",
        "chomage_base": 7.4, "inflation_base": 8.5
    },
    # ═══ OCÉANIE ═══
    "australie": {
        "nom": "🇦🇺 Australie", "continent": "Océanie",
        "population": 26_000_000, "pib_base": 1_700_000_000_000,
        "tresor_base": 400_000_000,
        "ressources": {"fer": 2000, "charbon": 1500, "or": 600, "blé": 800},
        "bonus": "Minerais : +30% revenus mines",
        "bonus_id": "ressources",
        "chomage_base": 3.7, "inflation_base": 3.5
    },
}

# ============================================================
# UNITÉS MILITAIRES (arbre technologique)
# ============================================================
# Niveau 1 = débloqué par défaut
# Niveau 2 = nécessite caserne niveau 2
# Niveau 3 = nécessite base aérienne ou navale
UNITES_MILITAIRES = {
    # ══ INFANTERIE ══
    "infanterie_legere": {
        "nom": "👥 Infanterie Légère", "categorie": "Infanterie",
        "niveau_tech": 1,
        "cout": 10_000, "maintenance": 500,
        "puissance": 1, "defense": 1,
        "contre": [],  # Pas de bonus contre
        "faible_contre": ["tank_lourd", "artillerie"],
        "quantite_min": 100,
        "desc": "Soldats de base. Bon marché, faible puissance.",
        "emoji": "👥"
    },
    "infanterie_lourde": {
        "nom": "🪖 Infanterie Lourde", "categorie": "Infanterie",
        "niveau_tech": 1,
        "cout": 25_000, "maintenance": 1_200,
        "puissance": 2, "defense": 3,
        "contre": ["infanterie_legere"],
        "faible_contre": ["tank_moyen", "artillerie"],
        "quantite_min": 50,
        "desc": "Soldats blindés. Forte défense contre infanterie.",
        "emoji": "🪖"
    },
    "sniper": {
        "nom": "🎯 Unité Sniper", "categorie": "Infanterie",
        "niveau_tech": 2,
        "cout": 80_000, "maintenance": 3_000,
        "puissance": 5, "defense": 1,
        "contre": ["infanterie_legere", "infanterie_lourde", "officiers"],
        "faible_contre": ["tank_leger", "helicoptere"],
        "quantite_min": 10,
        "desc": "Élite. Très efficace contre l'infanterie ennemie.",
        "emoji": "🎯"
    },
    "forces_speciales": {
        "nom": "⚡ Forces Spéciales", "categorie": "Infanterie",
        "niveau_tech": 3,
        "cout": 500_000, "maintenance": 20_000,
        "puissance": 10, "defense": 8,
        "contre": ["infanterie_legere", "infanterie_lourde", "sniper", "artillerie"],
        "faible_contre": ["avion_chasse", "drone"],
        "quantite_min": 5,
        "desc": "Unité d'élite absolue. Coûteuse mais dévastatrice.",
        "emoji": "⚡"
    },
    # ══ BLINDÉS ══
    "tank_leger": {
        "nom": "🚗 Tank Léger", "categorie": "Blindés",
        "niveau_tech": 2,
        "cout": 500_000, "maintenance": 15_000,
        "puissance": 8, "defense": 5,
        "contre": ["infanterie_legere", "infanterie_lourde", "sniper"],
        "faible_contre": ["tank_lourd", "helicoptere", "avion_attaque"],
        "quantite_min": 5,
        "desc": "Rapide et mobile. Écrase l'infanterie.",
        "emoji": "🚗"
    },
    "tank_moyen": {
        "nom": "🚙 Tank Moyen", "categorie": "Blindés",
        "niveau_tech": 2,
        "cout": 2_000_000, "maintenance": 50_000,
        "puissance": 15, "defense": 12,
        "contre": ["tank_leger", "infanterie_legere", "infanterie_lourde"],
        "faible_contre": ["tank_lourd", "helicoptere"],
        "quantite_min": 3,
        "desc": "Polyvalent. Bon équilibre attaque/défense.",
        "emoji": "🚙"
    },
    "tank_lourd": {
        "nom": "🛡️ Tank Lourd (MBT)", "categorie": "Blindés",
        "niveau_tech": 3,
        "cout": 8_000_000, "maintenance": 200_000,
        "puissance": 30, "defense": 35,
        "contre": ["tank_leger", "tank_moyen", "infanterie_legere", "infanterie_lourde"],
        "faible_contre": ["helicoptere", "avion_attaque", "drone"],
        "quantite_min": 1,
        "desc": "Char de bataille principal. Presque invincible au sol.",
        "emoji": "🛡️"
    },
    "artillerie": {
        "nom": "💥 Artillerie", "categorie": "Blindés",
        "niveau_tech": 2,
        "cout": 3_000_000, "maintenance": 80_000,
        "puissance": 25, "defense": 3,
        "contre": ["infanterie_legere", "infanterie_lourde", "artillerie", "base_fixe"],
        "faible_contre": ["avion_chasse", "drone", "forces_speciales"],
        "quantite_min": 2,
        "desc": "Puissance de feu à distance. Faible en défense.",
        "emoji": "💥"
    },
    # ══ AVIATION ══
    "helicoptere": {
        "nom": "🚁 Hélicoptère d'Attaque", "categorie": "Aviation",
        "niveau_tech": 3,
        "cout": 15_000_000, "maintenance": 400_000,
        "puissance": 40, "defense": 15,
        "contre": ["tank_leger", "tank_moyen", "tank_lourd", "infanterie_lourde"],
        "faible_contre": ["avion_chasse", "systeme_anti_aerien"],
        "quantite_min": 1,
        "desc": "Prédateur des chars. Vulnérable aux chasseurs.",
        "emoji": "🚁"
    },
    "avion_chasse": {
        "nom": "✈️ Avion de Chasse", "categorie": "Aviation",
        "niveau_tech": 3,
        "cout": 50_000_000, "maintenance": 1_500_000,
        "puissance": 60, "defense": 20,
        "contre": ["helicoptere", "avion_attaque", "drone", "avion_chasse"],
        "faible_contre": ["systeme_anti_aerien", "avion_furtif"],
        "quantite_min": 1,
        "desc": "Maître des airs. Domine tous les autres aéronefs.",
        "emoji": "✈️"
    },
    "avion_attaque": {
        "nom": "🛩️ Avion d'Attaque", "categorie": "Aviation",
        "niveau_tech": 3,
        "cout": 30_000_000, "maintenance": 900_000,
        "puissance": 45, "defense": 10,
        "contre": ["tank_lourd", "tank_moyen", "artillerie", "infanterie_lourde"],
        "faible_contre": ["avion_chasse", "systeme_anti_aerien"],
        "quantite_min": 1,
        "desc": "Spécialisé contre les blindés ennemis.",
        "emoji": "🛩️"
    },
    "drone": {
        "nom": "🤖 Drone de Combat", "categorie": "Aviation",
        "niveau_tech": 3,
        "cout": 5_000_000, "maintenance": 150_000,
        "puissance": 20, "defense": 5,
        "contre": ["infanterie_legere", "sniper", "artillerie", "forces_speciales"],
        "faible_contre": ["avion_chasse", "systeme_anti_aerien"],
        "quantite_min": 2,
        "desc": "Pas de pilote à risque. Bon contre l'infanterie.",
        "emoji": "🤖"
    },
    # ══ MARINE ══
    "corvette": {
        "nom": "⛵ Corvette", "categorie": "Marine",
        "niveau_tech": 2,
        "cout": 10_000_000, "maintenance": 300_000,
        "puissance": 15, "defense": 10,
        "contre": ["sous_marin"],
        "faible_contre": ["destroyer", "avion_attaque"],
        "quantite_min": 1,
        "desc": "Patrouilleur rapide. Anti-sous-marin.",
        "emoji": "⛵"
    },
    "destroyer": {
        "nom": "🚢 Destroyer", "categorie": "Marine",
        "niveau_tech": 3,
        "cout": 80_000_000, "maintenance": 2_000_000,
        "puissance": 50, "defense": 40,
        "contre": ["corvette", "sous_marin", "helicoptere"],
        "faible_contre": ["porte_avions", "missile_balistique"],
        "quantite_min": 1,
        "desc": "Navire de guerre polyvalent. Domine les mers.",
        "emoji": "🚢"
    },
    "sous_marin": {
        "nom": "🌊 Sous-Marin", "categorie": "Marine",
        "niveau_tech": 3,
        "cout": 100_000_000, "maintenance": 3_000_000,
        "puissance": 70, "defense": 60,
        "contre": ["destroyer", "corvette", "porte_avions"],
        "faible_contre": ["corvette"],  # Détecté par corvette
        "quantite_min": 1,
        "desc": "Arme secrète. Très difficile à détecter.",
        "emoji": "🌊"
    },
    # ══ DÉFENSE ══
    "systeme_anti_aerien": {
        "nom": "🎯 Système Anti-Aérien", "categorie": "Défense",
        "niveau_tech": 2,
        "cout": 20_000_000, "maintenance": 500_000,
        "puissance": 30, "defense": 20,
        "contre": ["helicoptere", "avion_chasse", "avion_attaque", "drone"],
        "faible_contre": ["forces_speciales", "artillerie"],
        "quantite_min": 1,
        "desc": "Protège contre toutes menaces aériennes.",
        "emoji": "🎯"
    },
    "missile_balistique": {
        "nom": "🚀 Missile Balistique", "categorie": "Défense",
        "niveau_tech": 3,
        "cout": 500_000_000, "maintenance": 10_000_000,
        "puissance": 200, "defense": 0,
        "contre": ["base_fixe", "destroyer", "porte_avions"],
        "faible_contre": ["systeme_anti_aerien"],
        "quantite_min": 1,
        "desc": "Arme de destruction massive. Frappe n'importe où.",
        "emoji": "🚀"
    },
}

# Niveaux technologiques requis par catégorie
TECH_REQUIS = {
    1: "Aucun prérequis",
    2: "Nécessite : Caserne niveau 2 (construire 3 casernes)",
    3: "Nécessite : Base Aérienne ou Navale"
}

# ============================================================
# INFRASTRUCTURES CIVILES
# ============================================================
INFRA_CIVILES = {
    "ferme_petite": {
        "nom": "🌾 Petite Ferme", "categorie": "Économie",
        "cout": 500_000, "maintenance": 10_000,
        "revenu": 50_000, "emplois": 200,
        "effet_chomage": -0.1, "effet_pib": 50_000,
        "desc": "Ferme agricole locale.", "max": 20
    },
    "ferme_grande": {
        "nom": "🚜 Grande Ferme", "categorie": "Économie",
        "cout": 5_000_000, "maintenance": 80_000,
        "revenu": 600_000, "emplois": 800,
        "effet_chomage": -0.3, "effet_pib": 600_000,
        "desc": "Exploitation agricole industrielle.", "max": 10
    },
    "usine_petite": {
        "nom": "🏭 Petite Usine", "categorie": "Économie",
        "cout": 2_000_000, "maintenance": 40_000,
        "revenu": 200_000, "emplois": 500,
        "effet_chomage": -0.2, "effet_pib": 200_000,
        "desc": "Usine de production légère.", "max": 30
    },
    "usine_grande": {
        "nom": "🏗️ Grande Usine", "categorie": "Économie",
        "cout": 20_000_000, "maintenance": 300_000,
        "revenu": 2_500_000, "emplois": 3000,
        "effet_chomage": -0.8, "effet_pib": 2_500_000,
        "desc": "Complexe industriel lourd.", "max": 10
    },
    "raffinerie": {
        "nom": "⛽ Raffinerie", "categorie": "Économie",
        "cout": 50_000_000, "maintenance": 1_000_000,
        "revenu": 8_000_000, "emplois": 2000,
        "effet_chomage": -0.5, "effet_pib": 8_000_000,
        "desc": "Raffine le pétrole.", "max": 5
    },
    "mine": {
        "nom": "⛏️ Mine", "categorie": "Économie",
        "cout": 10_000_000, "maintenance": 200_000,
        "revenu": 1_500_000, "emplois": 1500,
        "effet_chomage": -0.4, "effet_pib": 1_500_000,
        "desc": "Extraction de minerais.", "max": 10
    },
    "port_commercial": {
        "nom": "🚢 Port Commercial", "categorie": "Économie",
        "cout": 30_000_000, "maintenance": 500_000,
        "revenu": 4_000_000, "emplois": 2500,
        "effet_chomage": -0.6, "effet_pib": 4_000_000,
        "desc": "Port d'import/export.", "max": 5
    },
    "zone_franche": {
        "nom": "🏢 Zone Franche", "categorie": "Économie",
        "cout": 100_000_000, "maintenance": 1_500_000,
        "revenu": 15_000_000, "emplois": 10000,
        "effet_chomage": -1.5, "effet_pib": 15_000_000,
        "desc": "Zone économique spéciale.", "max": 3
    },
    "hopital": {
        "nom": "🏥 Hôpital", "categorie": "Services",
        "cout": 10_000_000, "maintenance": 400_000,
        "revenu": 200_000, "emplois": 1000,
        "effet_chomage": -0.2, "effet_stabilite": 2, "effet_population": 15000,
        "effet_pib": 200_000,
        "desc": "Centre de soins.", "max": 15
    },
    "ecole": {
        "nom": "🏫 École", "categorie": "Services",
        "cout": 1_000_000, "maintenance": 80_000,
        "revenu": 0, "emplois": 150,
        "effet_chomage": -0.05, "effet_stabilite": 1,
        "effet_pib": 100_000,
        "desc": "Éducation primaire.", "max": 50
    },
    "universite": {
        "nom": "🎓 Université", "categorie": "Services",
        "cout": 15_000_000, "maintenance": 500_000,
        "revenu": 200_000, "emplois": 1000,
        "effet_chomage": -0.5, "effet_stabilite": 2,
        "effet_pib": 2_000_000,
        "desc": "Forme des cadres qualifiés.", "max": 5
    },
    "centrale_electrique": {
        "nom": "⚡ Centrale Électrique", "categorie": "Services",
        "cout": 40_000_000, "maintenance": 800_000,
        "revenu": 3_000_000, "emplois": 500,
        "effet_pib": 5_000_000,
        "desc": "Fournit l'énergie.", "max": 5
    },
    "centrale_solaire": {
        "nom": "☀️ Parc Solaire", "categorie": "Services",
        "cout": 20_000_000, "maintenance": 200_000,
        "revenu": 1_500_000, "emplois": 200,
        "effet_pib": 2_000_000, "effet_stabilite": 1,
        "desc": "Énergie renouvelable.", "max": 10
    },
    "aeroport": {
        "nom": "✈️ Aéroport", "categorie": "Services",
        "cout": 80_000_000, "maintenance": 2_000_000,
        "revenu": 10_000_000, "emplois": 5000,
        "effet_chomage": -0.8, "effet_pib": 12_000_000,
        "desc": "Hub aérien international.", "max": 3
    },
    "centre_recherche": {
        "nom": "🔬 Centre de Recherche", "categorie": "Services",
        "cout": 30_000_000, "maintenance": 1_000_000,
        "revenu": 500_000, "emplois": 800,
        "effet_chomage": -0.3, "effet_pib": 3_000_000, "effet_stabilite": 2,
        "desc": "R&D nationale.", "max": 5
    },
    "stade": {
        "nom": "🏟️ Stade", "categorie": "Services",
        "cout": 10_000_000, "maintenance": 300_000,
        "revenu": 1_200_000, "emplois": 500,
        "effet_stabilite": 3, "effet_pib": 1_200_000,
        "desc": "Boost le moral.", "max": 3
    },
    "logements_sociaux": {
        "nom": "🏘️ Logements Sociaux", "categorie": "Services",
        "cout": 5_000_000, "maintenance": 200_000,
        "revenu": 0, "emplois": 300,
        "effet_stabilite": 4, "effet_population": 10000,
        "desc": "Loge la population.", "max": 20
    },
}

# ============================================================
# INFRASTRUCTURES MILITAIRES
# ============================================================
INFRA_MILITAIRES = {
    "caserne": {
        "nom": "🏕️ Caserne", "categorie": "Militaire",
        "cout": 5_000_000, "maintenance": 200_000,
        "emplois": 500, "effet_chomage": -0.2,
        "desc": "Débloque tech niveau 2 à partir de 3 casernes. +500 soldats.",
        "soldats_bonus": 500, "max": 20
    },
    "base_aerienne": {
        "nom": "✈️ Base Aérienne", "categorie": "Militaire",
        "cout": 80_000_000, "maintenance": 3_000_000,
        "emplois": 2000, "effet_chomage": -0.5,
        "desc": "Débloque tech niveau 3 (aviation).",
        "soldats_bonus": 0, "max": 3
    },
    "base_navale": {
        "nom": "⚓ Base Navale", "categorie": "Militaire",
        "cout": 60_000_000, "maintenance": 2_000_000,
        "emplois": 1500, "effet_chomage": -0.3,
        "desc": "Débloque tech niveau 3 (marine).",
        "soldats_bonus": 0, "max": 3
    },
    "usine_armes": {
        "nom": "🔫 Usine d'Armement", "categorie": "Militaire",
        "cout": 40_000_000, "maintenance": 1_000_000,
        "revenu": 2_000_000, "emplois": 2000, "effet_chomage": -0.5,
        "desc": "Produit des armes. Réduit coût unités de 10%.",
        "max": 5
    },
    "centre_renseignement": {
        "nom": "🕵️ Centre de Renseignement", "categorie": "Militaire",
        "cout": 20_000_000, "maintenance": 800_000,
        "emplois": 500, "effet_stabilite": 2,
        "desc": "Services secrets. Boost défense.",
        "max": 2
    },
    "bunker": {
        "nom": "🏔️ Bunker", "categorie": "Militaire",
        "cout": 15_000_000, "maintenance": 300_000,
        "emplois": 100, "effet_stabilite": 1,
        "desc": "Protection contre les attaques.",
        "max": 5
    },
    "radar": {
        "nom": "📡 Réseau Radar", "categorie": "Militaire",
        "cout": 10_000_000, "maintenance": 400_000,
        "emplois": 200, "effet_stabilite": 1,
        "desc": "Détecte les attaques ennemies.",
        "max": 5
    },
}

ALL_INFRA = {**INFRA_CIVILES, **INFRA_MILITAIRES}

# ============================================================
# ÉVÉNEMENTS (avec effets réels précis)
# ============================================================
EVENEMENTS = [
    {
        "nom": "💰 Boom Économique",
        "desc": "Une vague d'investissements étrangers massifs propulse l'économie !",
        "effets": {"tresor": 200_000_000, "pib": 500_000_000, "chomage": -2.0, "stabilite": 5},
        "couleur": "green"
    },
    {
        "nom": "🛢️ Découverte de Pétrole",
        "desc": "Un immense gisement pétrolier est découvert sur votre territoire !",
        "effets": {"tresor": 500_000_000, "pib": 300_000_000, "stabilite": 3},
        "ressources": {"pétrole": 1000},
        "couleur": "green"
    },
    {
        "nom": "⚡ Crise Énergétique",
        "desc": "Une pénurie d'énergie frappe le pays, paralysant l'industrie.",
        "effets": {"tresor": -100_000_000, "pib": -200_000_000, "chomage": 3.0, "stabilite": -8},
        "couleur": "red"
    },
    {
        "nom": "🌾 Récolte Exceptionnelle",
        "desc": "Les conditions météo parfaites donnent une récolte record !",
        "effets": {"tresor": 80_000_000, "pib": 150_000_000, "stabilite": 2},
        "ressources": {"blé": 500},
        "couleur": "green"
    },
    {
        "nom": "🦠 Épidémie",
        "desc": "Une épidémie se propage, affectant la main-d'œuvre et l'économie.",
        "effets": {"population": -50000, "chomage": 2.0, "tresor": -150_000_000, "stabilite": -10},
        "couleur": "red"
    },
    {
        "nom": "🌊 Catastrophe Naturelle",
        "desc": "Un séisme/inondation dévaste une région entière du pays.",
        "effets": {"tresor": -300_000_000, "pib": -400_000_000, "stabilite": -15, "population": -20000},
        "couleur": "red"
    },
    {
        "nom": "🤝 Accord Commercial",
        "desc": "Un accord commercial majeur est signé avec plusieurs nations.",
        "effets": {"tresor": 150_000_000, "pib": 250_000_000, "chomage": -1.0, "stabilite": 3},
        "couleur": "green"
    },
    {
        "nom": "✊ Grève Générale",
        "desc": "Les travailleurs se mettent en grève, paralysant l'économie.",
        "effets": {"pib": -200_000_000, "chomage": 4.0, "tresor": -50_000_000, "stabilite": -12},
        "couleur": "red"
    },
    {
        "nom": "🔬 Avancée Technologique",
        "desc": "Une découverte scientifique majeure révolutionne l'industrie nationale.",
        "effets": {"pib": 400_000_000, "tresor": 100_000_000, "chomage": -1.5, "stabilite": 5},
        "couleur": "green"
    },
    {
        "nom": "🏦 Crise Bancaire",
        "desc": "Le système bancaire s'effondre partiellement, ruinant des milliers de citoyens.",
        "effets": {"tresor": -500_000_000, "pib": -600_000_000, "chomage": 5.0, "stabilite": -20, "inflation": 4.0},
        "couleur": "red"
    },
    {
        "nom": "👑 Popularité du Dirigeant",
        "desc": "Le chef d'État est plébiscité par la population. Stabilité renforcée.",
        "effets": {"stabilite": 15, "tresor": 30_000_000},
        "couleur": "green"
    },
    {
        "nom": "🌍 Flux Migratoire",
        "desc": "Une vague d'immigration qualifiée booste la main-d'œuvre.",
        "effets": {"population": 200000, "chomage": -1.0, "pib": 100_000_000},
        "couleur": "green"
    },
    {
        "nom": "💣 Attentat Terroriste",
        "desc": "Un attentat majeur frappe la capitale, déstabilisant le gouvernement.",
        "effets": {"stabilite": -25, "tresor": -100_000_000, "pib": -150_000_000},
        "couleur": "red"
    },
    {
        "nom": "🥇 Jeux Olympiques",
        "desc": "Votre pays accueille les JO ! Boom touristique et économique.",
        "effets": {"tresor": 300_000_000, "pib": 200_000_000, "stabilite": 10},
        "couleur": "green"
    },
    {
        "nom": "⛏️ Filon d'Or",
        "desc": "Un immense filon d'or est découvert dans les montagnes.",
        "effets": {"tresor": 800_000_000, "stabilite": 8},
        "ressources": {"or": 500},
        "couleur": "green"
    },
]

# ============================================================
# BASE DE DONNÉES
# ============================================================
DATA_FILE = "geopolitique_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pays": {}, "guerres": [], "alliances": [], "log_actions": [], "regions_prises": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_pays_du_joueur(data, user_id):
    for nom, pays in data["pays"].items():
        if str(user_id) in pays.get("membres", []):
            return nom, pays
    return None, None

def get_pays_du_chef(data, user_id):
    for nom, pays in data["pays"].items():
        if pays.get("chef") == str(user_id):
            return nom, pays
    return None, None

def get_niveau_tech(pays):
    """Retourne le niveau technologique débloqué."""
    infras = pays.get("infrastructures", {})
    nb_casernes = infras.get("caserne", 0)
    has_base_aerienne = infras.get("base_aerienne", 0) > 0
    has_base_navale = infras.get("base_navale", 0) > 0
    if has_base_aerienne or has_base_navale:
        return 3
    elif nb_casernes >= 3:
        return 2
    return 1

def calculer_puissance_militaire(pays):
    """Calcule la puissance militaire totale d'un pays."""
    total = 0
    for unite_id, quantite in pays.get("armee_unites", {}).items():
        if unite_id in UNITES_MILITAIRES:
            unite = UNITES_MILITAIRES[unite_id]
            total += unite["puissance"] * quantite
    return total

def calculer_finances(pays):
    revenu = 0
    depenses = 0
    region_id = pays.get("region_id", "")
    region = REGIONS.get(region_id, {})
    bonus_id = region.get("bonus_id", "")

    for infra_id, quantite in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA:
            infra = ALL_INFRA[infra_id]
            rev_base = infra.get("revenu", 0) * quantite
            # Appliquer bonus régional
            if bonus_id == "agriculture" and infra_id in ["ferme_petite", "ferme_grande"]:
                rev_base = int(rev_base * 1.2)
            elif bonus_id == "industrie" and infra_id in ["usine_petite", "usine_grande"]:
                rev_base = int(rev_base * 1.25)
            elif bonus_id == "commerce" and infra_id in ["port_commercial", "zone_franche"]:
                rev_base = int(rev_base * 1.2)
            elif bonus_id == "ressources" and infra_id in ["mine", "raffinerie"]:
                rev_base = int(rev_base * 1.3)
            elif bonus_id == "tourisme" and infra_id in ["aeroport", "stade"]:
                rev_base = int(rev_base * 1.25)
            elif bonus_id == "technologie" and infra_id == "centre_recherche":
                rev_base = int(rev_base * 1.3)
            elif bonus_id == "energie" and infra_id == "centrale_solaire":
                rev_base = int(rev_base * 1.3)
            revenu += rev_base
            depenses += infra.get("maintenance", 0) * quantite

    # Impôts
    taux_imposition = 0.15
    revenu_impots = int(pays["pib"] * taux_imposition * (1 - pays["chomage"] / 100))
    revenu += revenu_impots

    # Maintenance unités militaires
    for unite_id, quantite in pays.get("armee_unites", {}).items():
        if unite_id in UNITES_MILITAIRES:
            depenses += UNITES_MILITAIRES[unite_id]["maintenance"] * quantite

    benefice = revenu - depenses
    pays["revenu_total"] = revenu
    pays["depenses_total"] = depenses
    pays["benefice_net"] = benefice
    return revenu, depenses, benefice

def appliquer_cycle_economique(data):
    for nom, pays in data["pays"].items():
        revenu, depenses, benefice = calculer_finances(pays)
        pays["tresor"] = max(0, pays["tresor"] + benefice)
        if pays["tresor"] < depenses:
            pays["inflation"] = min(50, pays["inflation"] + 0.5)
            pays["stabilite"] = max(0, pays["stabilite"] - 1)
    save_data(data)

# ============================================================
# IA GROQ
# ============================================================
def analyser_action_ia(action, pays_nom, pays_data, contexte_mondial):
    infra_list = ", ".join([f"{k}×{v}" for k, v in pays_data.get("infrastructures", {}).items()])
    armee_list = ", ".join([f"{k}×{v}" for k, v in pays_data.get("armee_unites", {}).items()])
    region_nom = REGIONS.get(pays_data.get("region_id", ""), {}).get("nom", "Inconnue")

    prompt = f"""Tu es le moteur économique d'un jeu de rôle géopolitique Discord.

=== PAYS : {pays_nom} (Région: {region_nom}) ===
Population: {pays_data.get('population', 0):,}
PIB: {pays_data.get('pib', 0):,} $
Trésor: {pays_data.get('tresor', 0):,} $
Armée: {armee_list or 'Aucune unité'}
Puissance militaire: {calculer_puissance_militaire(pays_data)}
Chômage: {pays_data.get('chomage', 0)}%
Inflation: {pays_data.get('inflation', 0)}%
Stabilité: {pays_data.get('stabilite', 100)}/100
Ressources: {pays_data.get('ressources', {})}
Infrastructures: {infra_list or 'Aucune'}
Bénéfice net: {pays_data.get('benefice_net', 0):,} $/cycle

=== ACTION ===
{action}

=== CONTEXTE MONDIAL ===
Pays: {len(contexte_mondial.get('pays', {}))} | Guerres: {len(contexte_mondial.get('guerres', []))}

Réponds UNIQUEMENT avec un JSON valide sans texte avant ou après:
{{
  "resume": "2-3 phrases narratives",
  "modifications": {{
    "pib": 0,
    "population": 0,
    "chomage": 0.0,
    "inflation": 0.0,
    "stabilite": 0,
    "tresor": 0
  }},
  "ressources_gagnees": {{}},
  "alerte": null
}}"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    body = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 600
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]

def appliquer_consequences(data, pays_nom, action_description):
    pays = data["pays"][pays_nom]
    try:
        reponse_ia = analyser_action_ia(action_description, pays_nom, pays, data)
        json_match = re.search(r'\{.*\}', reponse_ia, re.DOTALL)
        if not json_match:
            return None, "Erreur IA: format invalide"
        consequences = json.loads(json_match.group())
        mods = consequences.get("modifications", {})
        for stat, valeur in mods.items():
            if stat in pays:
                pays[stat] = max(0, pays[stat] + valeur)
        for res, qte in consequences.get("ressources_gagnees", {}).items():
            pays["ressources"][res] = pays["ressources"].get(res, 0) + qte
        save_data(data)
        return consequences, None
    except Exception as e:
        return None, f"Erreur: {str(e)}"

# ============================================================
# TÂCHE PÉRIODIQUE
# ============================================================
@tasks.loop(hours=6)
async def cycle_economique():
    data = load_data()
    appliquer_cycle_economique(data)
    print(f"[{datetime.now()}] Cycle économique appliqué.")

# ============================================================
# BUILDERS D'EMBEDS
# ============================================================
def build_embed_stats(pays_nom, pays):
    calculer_finances(pays)
    stab = pays['stabilite']
    stab_bar = "🟩" * (stab // 20) + "⬛" * (5 - stab // 20)
    stab_emoji = "🟢" if stab > 70 else "🟡" if stab > 40 else "🔴"
    region = REGIONS.get(pays.get("region_id", ""), {})
    puissance = calculer_puissance_militaire(pays)

    embed = discord.Embed(
        title=f"🌍 {pays_nom}",
        description=f"**Région :** {region.get('nom', 'Inconnue')} | **{region.get('bonus', '')}**",
        color=discord.Color.blue()
    )
    embed.add_field(name="🏛️ Capitale", value=pays['capitale'], inline=True)
    embed.add_field(name="⚖️ Idéologie", value=pays['ideologie'], inline=True)
    embed.add_field(name="👑 Chef", value=pays['chef_nom'], inline=True)
    embed.add_field(name="👥 Population", value=f"{pays['population']:,}", inline=True)
    embed.add_field(name="💰 PIB", value=f"{pays['pib']:,} $", inline=True)
    embed.add_field(name="🏦 Trésor", value=f"{pays['tresor']:,} $", inline=True)
    embed.add_field(name="📈 Bénéfice/cycle", value=f"{pays['benefice_net']:+,} $", inline=True)
    embed.add_field(name="📉 Chômage", value=f"{pays['chomage']}%", inline=True)
    embed.add_field(name="💹 Inflation", value=f"{pays['inflation']}%", inline=True)
    embed.add_field(name=f"{stab_emoji} Stabilité", value=f"{stab_bar} {stab}/100", inline=False)
    embed.add_field(name="⚔️ Puissance Militaire", value=f"{puissance:,} pts", inline=True)
    nb_unites = sum(pays.get("armee_unites", {}).values())
    embed.add_field(name="🪖 Unités", value=f"{nb_unites:,} unités", inline=True)
    nb_infra = sum(pays.get("infrastructures", {}).values())
    embed.add_field(name="🏗️ Infrastructures", value=f"{nb_infra} bâtiments", inline=True)
    res_text = " | ".join([f"{k}: {v}" for k, v in pays['ressources'].items() if v > 0])
    if res_text:
        embed.add_field(name="🏭 Ressources", value=res_text, inline=False)
    if pays.get('alliances'):
        embed.add_field(name="🤝 Alliances", value=", ".join(pays['alliances']), inline=True)
    if pays.get('en_guerre_contre'):
        embed.add_field(name="⚔️ En guerre", value=", ".join(pays['en_guerre_contre']), inline=True)
    return embed

def build_embed_militaire(pays_nom, pays):
    tech_level = get_niveau_tech(pays)
    puissance = calculer_puissance_militaire(pays)
    embed = discord.Embed(
        title=f"⚔️ Armée de {pays_nom}",
        description=f"**Niveau technologique :** {tech_level}/3 | **Puissance totale :** {puissance:,} pts",
        color=discord.Color.red()
    )
    embed.add_field(name="🏦 Trésor", value=f"{pays['tresor']:,} $", inline=True)
    embed.add_field(name="🔓 Tech débloquée", value=TECH_REQUIS[tech_level], inline=False)

    # Unités par catégorie
    categories = {}
    for unite_id, qte in pays.get("armee_unites", {}).items():
        if unite_id in UNITES_MILITAIRES and qte > 0:
            unite = UNITES_MILITAIRES[unite_id]
            cat = unite["categorie"]
            if cat not in categories:
                categories[cat] = []
            puiss_total = unite["puissance"] * qte
            categories[cat].append(f"{unite['emoji']} **{unite['nom']}** ×{qte} → {puiss_total} pts")
    for cat, lines in categories.items():
        embed.add_field(name=f"━━ {cat} ━━", value="\n".join(lines), inline=False)
    if not categories:
        embed.add_field(name="🪖 Unités", value="Aucune unité recrutée.", inline=False)
    if pays.get("en_guerre_contre"):
        embed.add_field(name="⚔️ En guerre contre", value=", ".join(pays["en_guerre_contre"]), inline=False)
    embed.set_footer(text="Utilisez le menu pour recruter des unités ou construire des installations.")
    return embed

def build_embed_finances(pays_nom, pays):
    calculer_finances(pays)
    benefice = pays["benefice_net"]
    couleur = discord.Color.green() if benefice >= 0 else discord.Color.red()
    embed = discord.Embed(title=f"💰 Finances de {pays_nom}", color=couleur)
    embed.add_field(name="🏦 Trésor actuel", value=f"{pays['tresor']:,} $", inline=False)
    embed.add_field(name="📥 Revenus/cycle", value=f"+{pays['revenu_total']:,} $", inline=True)
    embed.add_field(name="📤 Dépenses/cycle", value=f"-{pays['depenses_total']:,} $", inline=True)
    embed.add_field(name="💹 Bénéfice net", value=f"{benefice:+,} $", inline=True)
    revenus_detail = []
    for infra_id, qte in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA:
            infra = ALL_INFRA[infra_id]
            if infra.get("revenu", 0) > 0:
                revenus_detail.append(f"{infra['nom']} ×{qte}: +{infra['revenu']*qte:,} $")
    if revenus_detail:
        embed.add_field(name="📊 Revenus par infra", value="\n".join(revenus_detail[:8]), inline=False)
    depenses_detail = []
    for infra_id, qte in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA and ALL_INFRA[infra_id].get("maintenance", 0) > 0:
            infra = ALL_INFRA[infra_id]
            depenses_detail.append(f"{infra['nom']} ×{qte}: -{infra['maintenance']*qte:,} $")
    for unite_id, qte in pays.get("armee_unites", {}).items():
        if unite_id in UNITES_MILITAIRES:
            u = UNITES_MILITAIRES[unite_id]
            depenses_detail.append(f"{u['emoji']} {u['nom']} ×{qte}: -{u['maintenance']*qte:,} $")
    if depenses_detail:
        embed.add_field(name="📋 Dépenses détaillées", value="\n".join(depenses_detail[:8]), inline=False)
    embed.set_footer(text="Cycle économique toutes les 6h.")
    return embed

def build_embed_infra(pays_nom, pays):
    calculer_finances(pays)
    embed = discord.Embed(title=f"🏗️ Infrastructures de {pays_nom}", color=discord.Color.teal())
    embed.add_field(name="🏦 Trésor", value=f"{pays['tresor']:,} $", inline=True)
    embed.add_field(name="💹 Bénéfice/cycle", value=f"{pays['benefice_net']:+,} $", inline=True)
    civ_lines, mil_lines = [], []
    for infra_id, qte in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA:
            infra = ALL_INFRA[infra_id]
            rev = infra.get("revenu", 0) * qte
            dep = infra.get("maintenance", 0) * qte
            line = f"{infra['nom']} ×**{qte}** | +{rev:,}$ / -{dep:,}$"
            if infra_id in INFRA_MILITAIRES:
                mil_lines.append(line)
            else:
                civ_lines.append(line)
    if civ_lines:
        embed.add_field(name="🏛️ Civiles", value="\n".join(civ_lines), inline=False)
    if mil_lines:
        embed.add_field(name="⚔️ Militaires", value="\n".join(mil_lines), inline=False)
    if not civ_lines and not mil_lines:
        embed.description = "Aucune infrastructure. Utilisez le menu pour construire !"
    return embed

# ============================================================
# VUES INTERACTIVES
# ============================================================
class MenuPrincipalView(discord.ui.View):
    def __init__(self, pays_nom, user_id):
        super().__init__(timeout=180)
        self.pays_nom = pays_nom
        self.user_id = user_id

    def check(self, interaction):
        return str(interaction.user.id) == str(self.user_id)

    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.primary, row=0)
    async def btn_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check(interaction):
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True); return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        await interaction.response.edit_message(embed=build_embed_stats(self.pays_nom, pays), view=self)

    @discord.ui.button(label="💰 Finances", style=discord.ButtonStyle.success, row=0)
    async def btn_finances(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        await interaction.response.edit_message(embed=build_embed_finances(self.pays_nom, pays), view=self)

    @discord.ui.button(label="🏗️ Infrastructures", style=discord.ButtonStyle.secondary, row=0)
    async def btn_infra(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        view = InfraMenuView(self.pays_nom, self.user_id)
        await interaction.response.edit_message(embed=build_embed_infra(self.pays_nom, pays), view=view)

    @discord.ui.button(label="⚔️ Armée", style=discord.ButtonStyle.danger, row=0)
    async def btn_militaire(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check(interaction):
            await interaction.response.send_message("❌", ephemeral=True); return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        view = ArmeePrincipalView(self.pays_nom, self.user_id)
        await interaction.response.edit_message(embed=build_embed_militaire(self.pays_nom, pays), view=view)


class InfraMenuView(discord.ui.View):
    def __init__(self, pays_nom, user_id):
        super().__init__(timeout=180)
        self.pays_nom = pays_nom
        self.user_id = user_id
        self.add_item(SelectCategorieInfra(pays_nom, user_id))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        await interaction.response.edit_message(embed=build_embed_stats(self.pays_nom, pays), view=MenuPrincipalView(self.pays_nom, self.user_id))


class SelectCategorieInfra(discord.ui.Select):
    def __init__(self, pays_nom, user_id):
        self.pays_nom = pays_nom
        self.user_id = user_id
        options = [
            discord.SelectOption(label="💼 Économie (Fermes, Usines, Ports...)", value="Économie"),
            discord.SelectOption(label="🏛️ Services (Hôpitaux, Écoles, Énergie...)", value="Services"),
            discord.SelectOption(label="⚔️ Militaire (Casernes, Bases, Radar...)", value="Militaire"),
        ]
        super().__init__(placeholder="📋 Choisir une catégorie...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True); return
        categorie = self.values[0]
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = self.build_catalogue(pays, categorie)
        view = AcheterInfraView(self.pays_nom, self.user_id, categorie)
        await interaction.response.edit_message(embed=embed, view=view)

    def build_catalogue(self, pays, categorie):
        embed = discord.Embed(
            title=f"📋 Catalogue — {categorie}",
            description=f"💰 Trésor: **{pays['tresor']:,} $**",
            color=discord.Color.gold()
        )
        if categorie == "Militaire":
            infras = INFRA_MILITAIRES
        else:
            infras = {k: v for k, v in INFRA_CIVILES.items() if v["categorie"] == categorie}
        for k, infra in infras.items():
            qte = pays.get("infrastructures", {}).get(k, 0)
            ok = "✅" if pays["tresor"] >= infra["cout"] else "❌"
            ben = infra.get("revenu", 0) - infra.get("maintenance", 0)
            val = (f"💸 Coût: **{infra['cout']:,} $** {ok}\n"
                   f"🔧 Maintenance: {infra.get('maintenance',0):,} $/cycle\n"
                   f"💹 Revenu: +{infra.get('revenu',0):,} $/cycle\n"
                   f"📊 Bénéfice: **{ben:+,} $/cycle**\n"
                   f"📦 Construit: {qte}/{infra['max']}\n"
                   f"📝 {infra['desc']}")
            embed.add_field(name=infra["nom"], value=val, inline=True)
        return embed


class AcheterInfraView(discord.ui.View):
    def __init__(self, pays_nom, user_id, categorie):
        super().__init__(timeout=180)
        self.pays_nom = pays_nom
        self.user_id = user_id
        if categorie == "Militaire":
            infras = INFRA_MILITAIRES
        else:
            infras = {k: v for k, v in INFRA_CIVILES.items() if v["categorie"] == categorie}
        self.add_item(SelectAcheterInfra(pays_nom, user_id, infras))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        await interaction.response.edit_message(embed=build_embed_infra(self.pays_nom, pays), view=InfraMenuView(self.pays_nom, self.user_id))


class SelectAcheterInfra(discord.ui.Select):
    def __init__(self, pays_nom, user_id, infras):
        self.pays_nom = pays_nom
        self.user_id = user_id
        options = [
            discord.SelectOption(label=f"{v['nom']} — {v['cout']:,}$", description=v['desc'][:50], value=k)
            for k, v in list(infras.items())[:25]
        ]
        super().__init__(placeholder="🛒 Construire une infrastructure...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True); return
        infra_id = self.values[0]
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        if pays.get("chef") != str(interaction.user.id):
            await interaction.response.send_message("❌ Seul le chef peut construire !", ephemeral=True); return
        infra = ALL_INFRA[infra_id]
        qte_actuelle = pays["infrastructures"].get(infra_id, 0)
        if qte_actuelle >= infra["max"]:
            await interaction.response.send_message(f"❌ Maximum atteint ({infra['max']}) !", ephemeral=True); return
        if pays["tresor"] < infra["cout"]:
            await interaction.response.send_message(f"❌ Trésor insuffisant ! Besoin: {infra['cout']:,} $ | Disponible: {pays['tresor']:,} $", ephemeral=True); return
        pays["tresor"] -= infra["cout"]
        pays["infrastructures"][infra_id] = qte_actuelle + 1
        if "effet_pib" in infra: pays["pib"] += infra["effet_pib"]
        if "effet_chomage" in infra: pays["chomage"] = max(0, round(pays["chomage"] + infra["effet_chomage"], 2))
        if "effet_stabilite" in infra: pays["stabilite"] = min(100, pays["stabilite"] + infra["effet_stabilite"])
        if "effet_population" in infra: pays["population"] += infra["effet_population"]
        if "soldats_bonus" in infra and infra["soldats_bonus"] > 0:
            pays["armee_unites"]["infanterie_legere"] = pays["armee_unites"].get("infanterie_legere", 0) + infra["soldats_bonus"]
        calculer_finances(pays)
        save_data(data)
        embed = discord.Embed(title=f"✅ {infra['nom']} construite !", color=discord.Color.green())
        embed.add_field(name="💸 Coût payé", value=f"{infra['cout']:,} $", inline=True)
        embed.add_field(name="💰 Trésor restant", value=f"{pays['tresor']:,} $", inline=True)
        embed.add_field(name="📦 Total", value=f"{qte_actuelle+1}/{infra['max']}", inline=True)
        embed.add_field(name="💹 Revenu/cycle", value=f"+{infra.get('revenu',0):,} $", inline=True)
        embed.add_field(name="📊 Bénéfice net/cycle", value=f"{pays['benefice_net']:+,} $", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ══════════════════════════════════════════════════
# VUE ARMÉE PRINCIPALE
# ══════════════════════════════════════════════════
class ArmeePrincipalView(discord.ui.View):
    def __init__(self, pays_nom, user_id):
        super().__init__(timeout=180)
        self.pays_nom = pays_nom
        self.user_id = user_id
        self.add_item(SelectCategorieArmee(pays_nom, user_id))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        await interaction.response.edit_message(embed=build_embed_stats(self.pays_nom, pays), view=MenuPrincipalView(self.pays_nom, self.user_id))


class SelectCategorieArmee(discord.ui.Select):
    def __init__(self, pays_nom, user_id):
        self.pays_nom = pays_nom
        self.user_id = user_id
        options = [
            discord.SelectOption(label="👥 Infanterie", value="Infanterie", emoji="👥"),
            discord.SelectOption(label="🛡️ Blindés", value="Blindés", emoji="🛡️"),
            discord.SelectOption(label="✈️ Aviation", value="Aviation", emoji="✈️"),
            discord.SelectOption(label="⛵ Marine", value="Marine", emoji="⛵"),
            discord.SelectOption(label="🎯 Défense", value="Défense", emoji="🎯"),
        ]
        super().__init__(placeholder="🪖 Choisir une catégorie d'unités...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True); return
        categorie = self.values[0]
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        tech_level = get_niveau_tech(pays)
        unites_cat = {k: v for k, v in UNITES_MILITAIRES.items() if v["categorie"] == categorie}
        embed = self.build_catalogue_unites(pays, unites_cat, tech_level)
        view = AcheterUniteView(self.pays_nom, self.user_id, unites_cat, tech_level)
        await interaction.response.edit_message(embed=embed, view=view)

    def build_catalogue_unites(self, pays, unites, tech_level):
        embed = discord.Embed(
            title="🪖 Catalogue des Unités Militaires",
            description=f"🔓 **Tech niveau {tech_level}/3** | 🏦 Trésor: **{pays['tresor']:,} $**",
            color=discord.Color.dark_red()
        )
        for k, unite in unites.items():
            tech_ok = tech_level >= unite["niveau_tech"]
            lock = "🔓" if tech_ok else f"🔒 (Tech {unite['niveau_tech']} requise)"
            abordable = "✅" if pays["tresor"] >= unite["cout"] and tech_ok else "❌"
            qte = pays.get("armee_unites", {}).get(k, 0)
            contre_text = ", ".join([UNITES_MILITAIRES[u]["nom"] for u in unite["contre"] if u in UNITES_MILITAIRES]) or "Aucun bonus"
            faible_text = ", ".join([UNITES_MILITAIRES[u]["nom"] for u in unite["faible_contre"] if u in UNITES_MILITAIRES]) or "Aucun"
            val = (f"{lock} {abordable}\n"
                   f"💸 Coût: **{unite['cout']:,} $** | 🔧 Maint: {unite['maintenance']:,} $/u\n"
                   f"⚔️ Puissance: **{unite['puissance']} pts** | 🛡️ Défense: {unite['defense']} pts\n"
                   f"✅ Fort contre: {contre_text}\n"
                   f"❌ Faible contre: {faible_text}\n"
                   f"📦 En service: {qte}\n"
                   f"📝 {unite['desc']}")
            embed.add_field(name=f"{unite['emoji']} {unite['nom']}", value=val, inline=False)
        return embed


class AcheterUniteView(discord.ui.View):
    def __init__(self, pays_nom, user_id, unites, tech_level):
        super().__init__(timeout=180)
        self.pays_nom = pays_nom
        self.user_id = user_id
        self.add_item(SelectAcheterUnite(pays_nom, user_id, unites, tech_level))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        await interaction.response.edit_message(embed=build_embed_militaire(self.pays_nom, pays), view=ArmeePrincipalView(self.pays_nom, self.user_id))


class SelectAcheterUnite(discord.ui.Select):
    def __init__(self, pays_nom, user_id, unites, tech_level):
        self.pays_nom = pays_nom
        self.user_id = user_id
        self.tech_level = tech_level
        options = []
        for k, v in list(unites.items())[:25]:
            locked = tech_level < v["niveau_tech"]
            label = f"{'🔒' if locked else '🔓'} {v['nom']} — {v['cout']:,}$/unité"
            options.append(discord.SelectOption(label=label[:100], description=v['desc'][:50], value=k))
        super().__init__(placeholder="🛒 Recruter/Acheter des unités...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True); return
        unite_id = self.values[0]
        unite = UNITES_MILITAIRES[unite_id]
        if self.tech_level < unite["niveau_tech"]:
            await interaction.response.send_message(
                f"🔒 **Unité verrouillée !**\n{TECH_REQUIS[unite['niveau_tech']]}", ephemeral=True); return
        await interaction.response.send_modal(RecruterUniteModal(self.pays_nom, unite_id, unite))


class RecruterUniteModal(discord.ui.Modal, title="Recruter des unités"):
    quantite = discord.ui.TextInput(
        label="Quantité à recruter", placeholder="Ex: 10", required=True, max_length=6)

    def __init__(self, pays_nom, unite_id, unite):
        super().__init__()
        self.pays_nom = pays_nom
        self.unite_id = unite_id
        self.unite = unite
        self.quantite.label = f"Combien de {unite['nom']} ? (min: {unite['quantite_min']})"

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nb = int(self.quantite.value.replace(" ", "").replace(",", ""))
        except ValueError:
            await interaction.response.send_message("❌ Nombre invalide !", ephemeral=True); return
        if nb < self.unite["quantite_min"]:
            await interaction.response.send_message(f"❌ Minimum {self.unite['quantite_min']} unités !", ephemeral=True); return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        if pays.get("chef") != str(interaction.user.id):
            await interaction.response.send_message("❌ Seul le chef peut recruter !", ephemeral=True); return
        cout_total = self.unite["cout"] * nb
        # Réduction si usine d'armes
        nb_usines_armes = pays.get("infrastructures", {}).get("usine_armes", 0)
        if nb_usines_armes > 0:
            cout_total = int(cout_total * (1 - 0.10 * nb_usines_armes))
        if pays["tresor"] < cout_total:
            await interaction.response.send_message(
                f"❌ Trésor insuffisant !\n💸 Coût: {cout_total:,} $ | 💰 Disponible: {pays['tresor']:,} $", ephemeral=True); return
        pays["tresor"] -= cout_total
        pays["armee_unites"][self.unite_id] = pays["armee_unites"].get(self.unite_id, 0) + nb
        puissance_ajoutee = self.unite["puissance"] * nb
        calculer_finances(pays)
        save_data(data)
        embed = discord.Embed(title=f"✅ {self.unite['emoji']} {nb} × {self.unite['nom']} recrutés !", color=discord.Color.red())
        embed.add_field(name="💸 Coût total", value=f"{cout_total:,} $", inline=True)
        embed.add_field(name="💰 Trésor restant", value=f"{pays['tresor']:,} $", inline=True)
        embed.add_field(name="⚔️ Puissance ajoutée", value=f"+{puissance_ajoutee} pts", inline=True)
        embed.add_field(name="📊 Total en service", value=f"{pays['armee_unites'][self.unite_id]}", inline=True)
        if nb_usines_armes > 0:
            embed.add_field(name="🏭 Réduction usine d'armes", value=f"-{nb_usines_armes*10}%", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================================
# COMMANDES SLASH
# ============================================================
@tree.command(name="creer_pays", description="Créer votre pays — 1 seul pays par joueur !")
@app_commands.describe(nom="Nom de votre pays", capitale="Votre capitale", ideologie="Idéologie politique")
async def creer_pays(interaction: discord.Interaction, nom: str, capitale: str, ideologie: str):
    await interaction.response.defer(ephemeral=False)
    data = load_data()

    # Vérification : 1 pays par joueur
    pays_existant, _ = get_pays_du_joueur(data, interaction.user.id)
    if pays_existant:
        await interaction.followup.send(f"❌ Vous avez déjà un pays : **{pays_existant}** ! Un seul pays par joueur.")
        return
    if nom in data["pays"]:
        await interaction.followup.send(f"❌ Le pays **{nom}** existe déjà !")
        return

    # Menu de sélection de région
    view = SelectRegionView(nom, capitale, ideologie, interaction.user)
    embed = discord.Embed(
        title="🌍 Choisissez votre Région",
        description="Chaque région a sa propre **population réelle**, ses **ressources** et un **bonus économique** unique !",
        color=discord.Color.blue()
    )
    embed.add_field(name="ℹ️ Note", value="La région est **permanente** — choisissez bien !", inline=False)
    await interaction.followup.send(embed=embed, view=view)


class SelectRegionView(discord.ui.View):
    def __init__(self, pays_nom, capitale, ideologie, user):
        super().__init__(timeout=120)
        self.pays_nom = pays_nom
        self.capitale = capitale
        self.ideologie = ideologie
        self.user = user
        self.add_item(SelectContinent(pays_nom, capitale, ideologie, user))


class SelectContinent(discord.ui.Select):
    def __init__(self, pays_nom, capitale, ideologie, user):
        self.pays_nom = pays_nom
        self.capitale = capitale
        self.ideologie = ideologie
        self.user = user
        continents = list(set(r["continent"] for r in REGIONS.values()))
        options = [discord.SelectOption(label=c, value=c) for c in sorted(continents)]
        super().__init__(placeholder="1️⃣ Choisir un continent...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user.id):
            await interaction.response.send_message("❌", ephemeral=True); return
        continent = self.values[0]
        view = SelectRegionFinaleView(self.pays_nom, self.capitale, self.ideologie, self.user, continent)
        embed = discord.Embed(title=f"🌍 Régions — {continent}", description="Choisissez votre région :", color=discord.Color.blue())
        regions_cont = {k: v for k, v in REGIONS.items() if v["continent"] == continent}
        for k, r in regions_cont.items():
            data = load_data()
            prise = k in data.get("regions_prises", [])
            statut = "❌ Déjà prise" if prise else "✅ Disponible"
            embed.add_field(
                name=f"{r['nom']} {statut}",
                value=(f"👥 Pop: {r['population']:,}\n"
                       f"💰 PIB: {r['pib_base']:,} $\n"
                       f"🏦 Trésor: {r['tresor_base']:,} $\n"
                       f"🎁 Bonus: {r['bonus']}\n"
                       f"📦 Ressources: {', '.join(r['ressources'].keys())}"),
                inline=True
            )
        await interaction.response.edit_message(embed=embed, view=view)


class SelectRegionFinaleView(discord.ui.View):
    def __init__(self, pays_nom, capitale, ideologie, user, continent):
        super().__init__(timeout=120)
        self.pays_nom = pays_nom
        self.capitale = capitale
        self.ideologie = ideologie
        self.user = user
        self.continent = continent
        regions_cont = {k: v for k, v in REGIONS.items() if v["continent"] == continent}
        self.add_item(SelectRegionFinale(pays_nom, capitale, ideologie, user, regions_cont))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user.id): return
        view = SelectRegionView(self.pays_nom, self.capitale, self.ideologie, self.user)
        embed = discord.Embed(title="🌍 Choisissez votre Région", color=discord.Color.blue())
        await interaction.response.edit_message(embed=embed, view=view)


class SelectRegionFinale(discord.ui.Select):
    def __init__(self, pays_nom, capitale, ideologie, user, regions):
        self.pays_nom = pays_nom
        self.capitale = capitale
        self.ideologie = ideologie
        self.user = user
        options = [
            discord.SelectOption(
                label=f"{v['nom']}",
                description=f"Pop: {v['population']:,} | {v['bonus'][:40]}",
                value=k
            ) for k, v in list(regions.items())[:25]
        ]
        super().__init__(placeholder="2️⃣ Choisir votre région...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user.id):
            await interaction.response.send_message("❌", ephemeral=True); return
        region_id = self.values[0]
        data = load_data()

        if region_id in data.get("regions_prises", []):
            await interaction.response.send_message("❌ Cette région est déjà prise par un autre pays !", ephemeral=True); return

        region = REGIONS[region_id]
        # Créer le pays avec les vraies données de la région
        data["pays"][self.pays_nom] = {
            "chef": str(self.user.id),
            "chef_nom": self.user.display_name,
            "capitale": self.capitale,
            "ideologie": self.ideologie,
            "membres": [str(self.user.id)],
            "region_id": region_id,
            "population": region["population"],
            "pib": region["pib_base"],
            "tresor": region["tresor_base"],
            "chomage": region["chomage_base"],
            "inflation": region["inflation_base"],
            "stabilite": random.randint(60, 90),
            "ressources": dict(region["ressources"]),
            "infrastructures": {},
            "armee_unites": {},
            "alliances": [],
            "en_guerre_contre": [],
            "revenu_total": 0,
            "depenses_total": 0,
            "benefice_net": 0,
            "creation": datetime.now().isoformat()
        }
        if "regions_prises" not in data:
            data["regions_prises"] = []
        data["regions_prises"].append(region_id)
        calculer_finances(data["pays"][self.pays_nom])
        save_data(data)

        embed = discord.Embed(
            title=f"🎉 {self.pays_nom} est fondé !",
            description=f"**Région :** {region['nom']}\n**Bonus :** {region['bonus']}",
            color=discord.Color.green()
        )
        embed.add_field(name="👥 Population", value=f"{region['population']:,}", inline=True)
        embed.add_field(name="💰 PIB", value=f"{region['pib_base']:,} $", inline=True)
        embed.add_field(name="🏦 Trésor de départ", value=f"{region['tresor_base']:,} $", inline=True)
        embed.add_field(name="📦 Ressources", value=", ".join(f"{k}: {v}" for k, v in region["ressources"].items()), inline=False)
        embed.set_footer(text="Utilisez /tableau_bord pour gérer votre pays !")
        await interaction.response.edit_message(embed=embed, view=None)


@tree.command(name="tableau_bord", description="Ouvrir le tableau de bord de votre pays")
async def tableau_bord(interaction: discord.Interaction):
    data = load_data()
    pays_nom, pays = get_pays_du_joueur(data, interaction.user.id)
    if not pays_nom:
        await interaction.response.send_message("❌ Vous n'avez pas de pays. Utilisez `/creer_pays` !", ephemeral=True); return
    calculer_finances(pays)
    save_data(data)
    embed = build_embed_stats(pays_nom, pays)
    view = MenuPrincipalView(pays_nom, interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="action", description="Effectuer une action géopolitique (analysée par l'IA)")
@app_commands.describe(description="Décrivez votre action")
async def action(interaction: discord.Interaction, description: str):
    await interaction.response.defer()
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom:
        await interaction.followup.send("❌ Seul le chef d'État peut effectuer des actions !")
        return
    msg = await interaction.followup.send("⏳ L'IA analyse les conséquences de votre action...")
    consequences, erreur = appliquer_consequences(data, pays_nom, description)
    if erreur:
        await msg.edit(content=f"❌ {erreur}")
        return
    embed = discord.Embed(title=f"🎯 Action de {pays_nom}", description=f"**{description}**", color=discord.Color.orange())
    embed.add_field(name="📜 Conséquences", value=consequences.get("resume", ""), inline=False)
    mods = consequences.get("modifications", {})
    if mods:
        lines = [f"{'📈' if v > 0 else '📉'} **{k}**: {'+' if v > 0 else ''}{v:,}" for k, v in mods.items() if v != 0]
        if lines:
            embed.add_field(name="📊 Modifications", value="\n".join(lines), inline=False)
    if consequences.get("alerte"):
        embed.add_field(name="🚨 ALERTE", value=consequences["alerte"], inline=False)
    await msg.edit(content=None, embed=embed)


@tree.command(name="evenement", description="Déclencher un événement aléatoire dans votre pays")
async def evenement(interaction: discord.Interaction):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom:
        await interaction.response.send_message("❌ Seul le chef d'État peut déclencher un événement !")
        return
    ev = random.choice(EVENEMENTS)
    # Appliquer les effets RÉELS
    effets_appliques = {}
    for stat, valeur in ev["effets"].items():
        if stat in pays:
            ancien = pays[stat]
            pays[stat] = max(0, pays[stat] + valeur)
            effets_appliques[stat] = valeur
    for res, qte in ev.get("ressources", {}).items():
        pays["ressources"][res] = pays["ressources"].get(res, 0) + qte
    calculer_finances(pays)
    save_data(data)

    couleur = discord.Color.green() if ev["couleur"] == "green" else discord.Color.red()
    embed = discord.Embed(title=f"⚡ {ev['nom']}", description=ev["desc"], color=couleur)
    effets_text = []
    for stat, val in effets_appliques.items():
        emoji = "📈" if val > 0 else "📉"
        unite = "$" if stat in ["tresor", "pib"] else ("%" if stat in ["chomage", "inflation"] else "")
        effets_text.append(f"{emoji} **{stat}**: {'+' if val > 0 else ''}{val:,}{unite}")
    if ev.get("ressources"):
        for res, qte in ev["ressources"].items():
            effets_text.append(f"📦 **{res}**: +{qte}")
    embed.add_field(name="📊 Effets sur votre pays", value="\n".join(effets_text), inline=False)
    embed.add_field(name="🏦 Trésor actuel", value=f"{pays['tresor']:,} $", inline=True)
    embed.add_field(name="🛡️ Stabilité", value=f"{pays['stabilite']}/100", inline=True)
    embed.set_footer(text=f"Pays : {pays_nom}")
    await interaction.response.send_message(embed=embed)


@tree.command(name="declarer_guerre", description="Déclarer la guerre à un pays")
@app_commands.describe(cible="Nom du pays à attaquer")
async def declarer_guerre(interaction: discord.Interaction, cible: str):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom:
        await interaction.response.send_message("❌ Vous n'êtes pas chef d'État !"); return
    if cible not in data["pays"] or cible in pays["en_guerre_contre"] or cible == pays_nom:
        await interaction.response.send_message("❌ Action impossible."); return
    pays["en_guerre_contre"].append(cible)
    data["pays"][cible]["en_guerre_contre"].append(pays_nom)
    data["guerres"].append({"attaquant": pays_nom, "defenseur": cible, "debut": datetime.now().isoformat()})
    pays["stabilite"] = max(0, pays["stabilite"] - 10)
    data["pays"][cible]["stabilite"] = max(0, data["pays"][cible]["stabilite"] - 15)
    save_data(data)
    pays_cible = data["pays"][cible]
    puiss_att = calculer_puissance_militaire(pays)
    puiss_def = calculer_puissance_militaire(pays_cible)
    embed = discord.Embed(title="⚔️ DÉCLARATION DE GUERRE !", description=f"**{pays_nom}** → **{cible}**", color=discord.Color.red())
    embed.add_field(name="🏴 Attaquant", value=f"{pays_nom}\n⚔️ Puissance: {puiss_att:,} pts", inline=True)
    embed.add_field(name="🛡️ Défenseur", value=f"{cible}\n⚔️ Puissance: {puiss_def:,} pts", inline=True)
    await interaction.response.send_message(embed=embed)


@tree.command(name="bataille", description="Lancer une bataille contre un pays ennemi")
@app_commands.describe(cible="Pays ennemi")
async def bataille(interaction: discord.Interaction, cible: str):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom or cible not in pays["en_guerre_contre"]:
        await interaction.response.send_message("❌ Vous n'êtes pas en guerre contre ce pays !"); return
    pays_cible = data["pays"][cible]

    # Calcul avec contre-unités
    def calc_force(attaquant, defenseur):
        force = 0
        for unite_id, qte in attaquant.get("armee_unites", {}).items():
            if unite_id in UNITES_MILITAIRES:
                unite = UNITES_MILITAIRES[unite_id]
                pts = unite["puissance"] * qte
                # Bonus si l'unité est forte contre une unité ennemie
                for contre_id in unite["contre"]:
                    if defenseur.get("armee_unites", {}).get(contre_id, 0) > 0:
                        pts = int(pts * 1.5)  # +50% contre l'unité faible
                force += pts
        return int(force * random.uniform(0.85, 1.15))

    force_att = calc_force(pays, pays_cible)
    force_def = calc_force(pays_cible, pays)
    victoire = force_att > force_def

    # Pertes (% des unités)
    taux_perte = random.uniform(0.05, 0.20)
    for unite_id in list(pays.get("armee_unites", {}).keys()):
        pertes = int(pays["armee_unites"][unite_id] * taux_perte)
        pays["armee_unites"][unite_id] = max(0, pays["armee_unites"][unite_id] - pertes)

    taux_perte_def = random.uniform(0.10, 0.30) if victoire else random.uniform(0.03, 0.10)
    for unite_id in list(pays_cible.get("armee_unites", {}).keys()):
        pertes = int(pays_cible["armee_unites"][unite_id] * taux_perte_def)
        pays_cible["armee_unites"][unite_id] = max(0, pays_cible["armee_unites"][unite_id] - pertes)

    if victoire:
        butin = int(pays_cible["tresor"] * random.uniform(0.02, 0.08))
        pays["tresor"] += butin
        pays_cible["tresor"] = max(0, pays_cible["tresor"] - butin)
        pays_cible["stabilite"] = max(0, pays_cible["stabilite"] - random.randint(5, 20))
        couleur, resultat = discord.Color.green(), "🏆 VICTOIRE !"
    else:
        butin = 0
        pays["stabilite"] = max(0, pays["stabilite"] - random.randint(5, 15))
        couleur, resultat = discord.Color.red(), "💀 DÉFAITE !"

    save_data(data)
    embed = discord.Embed(title=f"⚔️ BATAILLE : {resultat}", description=f"**{pays_nom}** vs **{cible}**", color=couleur)
    embed.add_field(name="🏴 Votre force", value=f"{force_att:,} pts", inline=True)
    embed.add_field(name="🛡️ Force ennemie", value=f"{force_def:,} pts", inline=True)
    if victoire:
        embed.add_field(name="💰 Butin", value=f"+{butin:,} $", inline=False)
    embed.add_field(name="⚠️ Pertes", value=f"Vos unités ont subi ~{int(taux_perte*100)}% de pertes", inline=False)
    await interaction.response.send_message(embed=embed)


@tree.command(name="paix", description="Signer la paix")
@app_commands.describe(cible="Pays ennemi")
async def paix(interaction: discord.Interaction, cible: str):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom or cible not in pays.get("en_guerre_contre", []):
        await interaction.response.send_message("❌ Vous n'êtes pas en guerre contre ce pays !"); return
    pays["en_guerre_contre"].remove(cible)
    data["pays"][cible]["en_guerre_contre"].remove(pays_nom)
    pays["stabilite"] = min(100, pays["stabilite"] + 5)
    data["pays"][cible]["stabilite"] = min(100, data["pays"][cible]["stabilite"] + 5)
    data["guerres"] = [g for g in data["guerres"] if not (
        (g["attaquant"] == pays_nom and g["defenseur"] == cible) or
        (g["attaquant"] == cible and g["defenseur"] == pays_nom))]
    save_data(data)
    await interaction.response.send_message(f"🕊️ **Paix signée !** La guerre entre **{pays_nom}** et **{cible}** est terminée.")


@tree.command(name="alliance", description="Former une alliance")
@app_commands.describe(cible="Pays allié")
async def alliance(interaction: discord.Interaction, cible: str):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom or cible not in data["pays"] or cible in pays.get("alliances", []):
        await interaction.response.send_message("❌ Impossible."); return
    pays["alliances"].append(cible)
    data["pays"][cible]["alliances"].append(pays_nom)
    save_data(data)
    await interaction.response.send_message(f"🤝 **{pays_nom}** et **{cible}** sont désormais alliés !")


@tree.command(name="classement", description="Classement mondial")
@app_commands.choices(critere=[
    app_commands.Choice(name="💰 PIB", value="pib"),
    app_commands.Choice(name="🏦 Trésor", value="tresor"),
    app_commands.Choice(name="⚔️ Puissance Militaire", value="puissance"),
    app_commands.Choice(name="👥 Population", value="population"),
    app_commands.Choice(name="🛡️ Stabilité", value="stabilite"),
    app_commands.Choice(name="💹 Bénéfice Net", value="benefice_net"),
])
async def classement(interaction: discord.Interaction, critere: str = "pib"):
    data = load_data()
    if not data["pays"]:
        await interaction.response.send_message("❌ Aucun pays !"); return
    for pays in data["pays"].values():
        calculer_finances(pays)
    if critere == "puissance":
        pays_tries = sorted(data["pays"].items(), key=lambda x: calculer_puissance_militaire(x[1]), reverse=True)
    else:
        pays_tries = sorted(data["pays"].items(), key=lambda x: x[1].get(critere, 0), reverse=True)
    labels = {"pib": "💰 PIB", "tresor": "🏦 Trésor", "puissance": "⚔️ Puissance Militaire",
              "population": "👥 Population", "stabilite": "🛡️ Stabilité", "benefice_net": "💹 Bénéfice Net"}
    embed = discord.Embed(title=f"🌍 Classement — {labels.get(critere, critere)}", color=discord.Color.gold())
    medailles = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (nom, pays) in enumerate(pays_tries[:10]):
        m = medailles[i] if i < 3 else f"`{i+1}.`"
        region = REGIONS.get(pays.get("region_id", ""), {})
        if critere == "puissance":
            v = calculer_puissance_militaire(pays)
        else:
            v = pays.get(critere, 0)
        lines.append(f"{m} **{nom}** {region.get('nom','')} — {v:+,}" if critere == "benefice_net" else f"{m} **{nom}** {region.get('nom','')} — {v:,}")
    embed.description = "\n".join(lines)
    save_data(data)
    await interaction.response.send_message(embed=embed)


@tree.command(name="liste_pays", description="Voir tous les pays du monde")
async def liste_pays(interaction: discord.Interaction):
    data = load_data()
    if not data["pays"]:
        await interaction.response.send_message("❌ Aucun pays !"); return
    embed = discord.Embed(title="🌍 Nations du Monde", color=discord.Color.blue())
    for nom, pays in data["pays"].items():
        calculer_finances(pays)
        region = REGIONS.get(pays.get("region_id", ""), {})
        statut = "⚔️ En guerre" if pays.get("en_guerre_contre") else ("🤝 Allié" if pays.get("alliances") else "🕊️ Neutre")
        puissance = calculer_puissance_militaire(pays)
        embed.add_field(
            name=f"🏳️ {nom} — {region.get('nom', '?')}",
            value=(f"👑 {pays['chef_nom']} | {statut}\n"
                   f"👥 {pays['population']:,} | 🏦 {pays['tresor']:,} $\n"
                   f"💹 {pays['benefice_net']:+,} $/cycle | ⚔️ {puissance:,} pts"),
            inline=False
        )
    save_data(data)
    await interaction.response.send_message(embed=embed)


# ============================================================
# DÉMARRAGE
# ============================================================
@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    try:
        synced = await tree.sync()
        print(f"✅ {len(synced)} commandes synchronisées")
    except Exception as e:
        print(f"❌ Erreur sync: {e}")
    cycle_economique.start()

bot.run(TOKEN)
