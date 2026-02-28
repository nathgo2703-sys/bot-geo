import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
import re
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
import os
import urllib.request
import urllib.parse
TOKEN = os.environ.get("TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ============================================================
# CATALOGUE DES INFRASTRUCTURES
# ============================================================
INFRA_CIVILES = {
    # --- ÉCONOMIE ---
    "ferme_petite": {
        "nom": "🌾 Petite Ferme", "categorie": "Économie",
        "cout": 500_000, "maintenance": 10_000,
        "revenu": 50_000, "emplois": 200,
        "effet_chomage": -0.1, "effet_pib": 50_000,
        "desc": "Ferme agricole locale. Produit blé et légumes.",
        "max": 20
    },
    "ferme_grande": {
        "nom": "🚜 Grande Ferme Industrielle", "categorie": "Économie",
        "cout": 5_000_000, "maintenance": 80_000,
        "revenu": 600_000, "emplois": 800,
        "effet_chomage": -0.3, "effet_pib": 600_000,
        "desc": "Exploitation agricole industrielle. Fort rendement.",
        "max": 10
    },
    "usine_petite": {
        "nom": "🏭 Petite Usine", "categorie": "Économie",
        "cout": 2_000_000, "maintenance": 40_000,
        "revenu": 200_000, "emplois": 500,
        "effet_chomage": -0.2, "effet_pib": 200_000,
        "desc": "Usine de production légère.",
        "max": 30
    },
    "usine_grande": {
        "nom": "🏗️ Grande Usine", "categorie": "Économie",
        "cout": 20_000_000, "maintenance": 300_000,
        "revenu": 2_500_000, "emplois": 3000,
        "effet_chomage": -0.8, "effet_pib": 2_500_000,
        "desc": "Complexe industriel lourd. Produit acier et machines.",
        "max": 10
    },
    "raffinerie": {
        "nom": "⛽ Raffinerie de Pétrole", "categorie": "Économie",
        "cout": 50_000_000, "maintenance": 1_000_000,
        "revenu": 8_000_000, "emplois": 2000,
        "effet_chomage": -0.5, "effet_pib": 8_000_000,
        "desc": "Raffine le pétrole brut. Nécessite ressource pétrole.",
        "max": 5
    },
    "mine": {
        "nom": "⛏️ Mine", "categorie": "Économie",
        "cout": 10_000_000, "maintenance": 200_000,
        "revenu": 1_500_000, "emplois": 1500,
        "effet_chomage": -0.4, "effet_pib": 1_500_000,
        "desc": "Extraction de minerais. Génère or et acier.",
        "max": 10
    },
    "port_commercial": {
        "nom": "🚢 Port Commercial", "categorie": "Économie",
        "cout": 30_000_000, "maintenance": 500_000,
        "revenu": 4_000_000, "emplois": 2500,
        "effet_chomage": -0.6, "effet_pib": 4_000_000,
        "desc": "Port d'import/export. Booste le commerce.",
        "max": 5
    },
    "zone_franche": {
        "nom": "🏢 Zone Franche Économique", "categorie": "Économie",
        "cout": 100_000_000, "maintenance": 1_500_000,
        "revenu": 15_000_000, "emplois": 10000,
        "effet_chomage": -1.5, "effet_pib": 15_000_000,
        "desc": "Zone économique spéciale. Attire les investissements.",
        "max": 3
    },
    # --- SERVICES ---
    "hopital_petit": {
        "nom": "🏥 Clinique", "categorie": "Services",
        "cout": 3_000_000, "maintenance": 150_000,
        "revenu": 80_000, "emplois": 300,
        "effet_chomage": -0.1, "effet_stabilite": 1, "effet_population": 5000,
        "effet_pib": 80_000,
        "desc": "Soins de santé de base pour la population.",
        "max": 20
    },
    "hopital_grand": {
        "nom": "🏨 Grand Hôpital", "categorie": "Services",
        "cout": 25_000_000, "maintenance": 800_000,
        "revenu": 500_000, "emplois": 2000,
        "effet_chomage": -0.4, "effet_stabilite": 3, "effet_population": 30000,
        "effet_pib": 500_000,
        "desc": "Centre hospitalier universitaire. Améliore l'espérance de vie.",
        "max": 5
    },
    "ecole": {
        "nom": "🏫 École", "categorie": "Services",
        "cout": 1_000_000, "maintenance": 80_000,
        "revenu": 0, "emplois": 150,
        "effet_chomage": -0.05, "effet_stabilite": 1,
        "effet_pib": 100_000,
        "desc": "Éducation primaire. Réduit le chômage sur le long terme.",
        "max": 50
    },
    "universite": {
        "nom": "🎓 Université", "categorie": "Services",
        "cout": 15_000_000, "maintenance": 500_000,
        "revenu": 200_000, "emplois": 1000,
        "effet_chomage": -0.5, "effet_stabilite": 2,
        "effet_pib": 2_000_000,
        "desc": "Université nationale. Forme des cadres qualifiés.",
        "max": 5
    },
    "centrale_electrique": {
        "nom": "⚡ Centrale Électrique", "categorie": "Services",
        "cout": 40_000_000, "maintenance": 800_000,
        "revenu": 3_000_000, "emplois": 500,
        "effet_chomage": -0.1, "effet_pib": 5_000_000,
        "desc": "Fournit l'énergie au pays. Booste toute l'économie.",
        "max": 5
    },
    "centrale_solaire": {
        "nom": "☀️ Parc Solaire", "categorie": "Services",
        "cout": 20_000_000, "maintenance": 200_000,
        "revenu": 1_500_000, "emplois": 200,
        "effet_chomage": -0.05, "effet_pib": 2_000_000, "effet_stabilite": 1,
        "desc": "Énergie renouvelable propre. Faible maintenance.",
        "max": 10
    },
    "aeroport": {
        "nom": "✈️ Aéroport", "categorie": "Services",
        "cout": 80_000_000, "maintenance": 2_000_000,
        "revenu": 10_000_000, "emplois": 5000,
        "effet_chomage": -0.8, "effet_pib": 12_000_000,
        "desc": "Hub aérien international. Booste le tourisme et commerce.",
        "max": 3
    },
    "centre_recherche": {
        "nom": "🔬 Centre de Recherche", "categorie": "Services",
        "cout": 30_000_000, "maintenance": 1_000_000,
        "revenu": 500_000, "emplois": 800,
        "effet_chomage": -0.3, "effet_pib": 3_000_000, "effet_stabilite": 2,
        "desc": "R&D. Améliore la technologie nationale à long terme.",
        "max": 5
    },
    "stade": {
        "nom": "🏟️ Stade National", "categorie": "Services",
        "cout": 10_000_000, "maintenance": 300_000,
        "revenu": 1_200_000, "emplois": 500,
        "effet_stabilite": 3, "effet_pib": 1_200_000,
        "desc": "Améliore le moral et le tourisme sportif.",
        "max": 3
    },
    "logements_sociaux": {
        "nom": "🏘️ Logements Sociaux", "categorie": "Services",
        "cout": 5_000_000, "maintenance": 200_000,
        "revenu": 0, "emplois": 300,
        "effet_stabilite": 4, "effet_population": 10000, "effet_pib": 500_000,
        "desc": "Loge la population défavorisée. Améliore la stabilité.",
        "max": 20
    },
}

INFRA_MILITAIRES = {
    "caserne": {
        "nom": "🏕️ Caserne Militaire", "categorie": "Militaire",
        "cout": 5_000_000, "maintenance": 200_000,
        "revenu": 0, "emplois": 500,
        "soldats_bonus": 2000,
        "effet_chomage": -0.2,
        "desc": "Entraîne et loge des soldats. +2000 soldats.",
        "max": 20
    },
    "base_aerienne": {
        "nom": "✈️ Base Aérienne", "categorie": "Militaire",
        "cout": 80_000_000, "maintenance": 3_000_000,
        "revenu": 0, "emplois": 2000,
        "soldats_bonus": 500, "force_bonus": 15,
        "effet_chomage": -0.5,
        "desc": "Base pour l'armée de l'air. Booste la force de combat.",
        "max": 3
    },
    "base_navale": {
        "nom": "⚓ Base Navale", "categorie": "Militaire",
        "cout": 60_000_000, "maintenance": 2_000_000,
        "revenu": 0, "emplois": 1500,
        "soldats_bonus": 300, "force_bonus": 10,
        "effet_chomage": -0.3,
        "desc": "Port militaire. Permet des opérations navales.",
        "max": 3
    },
    "usine_armes": {
        "nom": "🔫 Usine d'Armement", "categorie": "Militaire",
        "cout": 40_000_000, "maintenance": 1_000_000,
        "revenu": 2_000_000, "emplois": 2000,
        "force_bonus": 8, "effet_chomage": -0.5,
        "desc": "Produit des armes. Revend à l'étranger. +force armée.",
        "max": 5
    },
    "centre_renseignement": {
        "nom": "🕵️ Centre de Renseignement", "categorie": "Militaire",
        "cout": 20_000_000, "maintenance": 800_000,
        "revenu": 0, "emplois": 500,
        "force_bonus": 5, "effet_stabilite": 2,
        "desc": "Services secrets. Améliore la sécurité nationale.",
        "max": 2
    },
    "bunker": {
        "nom": "🏔️ Bunker Souterrain", "categorie": "Militaire",
        "cout": 15_000_000, "maintenance": 300_000,
        "revenu": 0, "emplois": 100,
        "force_bonus": 3, "effet_stabilite": 1,
        "desc": "Protection en cas d'attaque. Résistance aux bombes.",
        "max": 5
    },
    "systeme_missiles": {
        "nom": "🚀 Système de Missiles", "categorie": "Militaire",
        "cout": 150_000_000, "maintenance": 5_000_000,
        "revenu": 0, "emplois": 1000,
        "force_bonus": 30,
        "desc": "Missiles balistiques. Puissance de frappe massive.",
        "max": 2
    },
    "radar": {
        "nom": "📡 Réseau Radar", "categorie": "Militaire",
        "cout": 10_000_000, "maintenance": 400_000,
        "revenu": 0, "emplois": 200,
        "force_bonus": 4, "effet_stabilite": 1,
        "desc": "Système de surveillance. Détecte les attaques ennemies.",
        "max": 5
    },
}

ALL_INFRA = {**INFRA_CIVILES, **INFRA_MILITAIRES}

# ============================================================
# BASE DE DONNÉES
# ============================================================
DATA_FILE = "geopolitique_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pays": {}, "guerres": [], "alliances": [], "log_actions": []}

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

def nouveau_pays_data(chef_id, chef_nom, capitale, ideologie):
    return {
        "chef": str(chef_id),
        "chef_nom": chef_nom,
        "capitale": capitale,
        "ideologie": ideologie,
        "membres": [str(chef_id)],
        # Stats de base
        "population": random.randint(5_000_000, 50_000_000),
        "pib": random.randint(500_000_000, 5_000_000_000),
        "armee": random.randint(10_000, 200_000),
        "chomage": round(random.uniform(3.0, 15.0), 1),
        "inflation": round(random.uniform(1.0, 8.0), 1),
        "stabilite": random.randint(60, 95),
        # ARGENT (trésor de l'État)
        "tresor": random.randint(100_000_000, 1_000_000_000),
        "revenu_total": 0,       # recalculé
        "depenses_total": 0,     # recalculé
        "benefice_net": 0,       # recalculé
        # Force militaire (0-100)
        "force_militaire": random.randint(10, 40),
        # Ressources
        "ressources": {
            "pétrole": random.randint(0, 500),
            "blé": random.randint(100, 1000),
            "acier": random.randint(50, 500),
            "or": random.randint(0, 200)
        },
        # Infrastructures {id_infra: nombre}
        "infrastructures": {},
        # Relations
        "alliances": [],
        "en_guerre_contre": [],
        "creation": datetime.now().isoformat()
    }

# ============================================================
# CALCUL ÉCONOMIQUE
# ============================================================
def calculer_finances(pays):
    """Recalcule revenus, dépenses, bénéfice d'un pays."""
    revenu = 0
    depenses = 0
    emplois_total = 0
    force_bonus = 0
    stabilite_bonus = 0

    for infra_id, quantite in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA:
            infra = ALL_INFRA[infra_id]
            revenu += infra.get("revenu", 0) * quantite
            depenses += infra.get("maintenance", 0) * quantite
            emplois_total += infra.get("emplois", 0) * quantite
            force_bonus += infra.get("force_bonus", 0) * quantite
            stabilite_bonus += infra.get("effet_stabilite", 0) * quantite

    # Revenus de base : impôts (% du PIB selon pop et chômage)
    taux_imposition = 0.15
    revenu_impots = int(pays["pib"] * taux_imposition * (1 - pays["chomage"] / 100))
    revenu += revenu_impots

    # Dépenses militaires de base
    depenses_armee = pays["armee"] * 100  # 100$ par soldat par cycle
    depenses += depenses_armee

    benefice = revenu - depenses

    pays["revenu_total"] = revenu
    pays["depenses_total"] = depenses
    pays["benefice_net"] = benefice
    pays["force_militaire"] = min(100, max(0, pays.get("force_militaire", 20) + force_bonus // 10))

    return revenu, depenses, benefice

def appliquer_cycle_economique(data):
    """Applique le cycle économique à tous les pays (appelé périodiquement)."""
    for nom, pays in data["pays"].items():
        revenu, depenses, benefice = calculer_finances(pays)
        pays["tresor"] = max(0, pays["tresor"] + benefice)
        # Inflation si trésor trop bas
        if pays["tresor"] < depenses:
            pays["inflation"] = min(50, pays["inflation"] + 0.5)
            pays["stabilite"] = max(0, pays["stabilite"] - 1)
    save_data(data)

# ============================================================
# IA GEMINI (Google - 100% Gratuit)
# ============================================================
def analyser_action_ia(action, pays_nom, pays_data, contexte_mondial):
    infra_list = ", ".join([f"{k}x{v}" for k, v in pays_data.get("infrastructures", {}).items()])
    prompt = f"""Tu es le moteur économique d'un jeu de rôle géopolitique Discord.

=== PAYS : {pays_nom} ===
Population: {pays_data.get('population', 0):,}
PIB: {pays_data.get('pib', 0):,} $
Trésor: {pays_data.get('tresor', 0):,} $
Armée: {pays_data.get('armee', 0):,} soldats
Force militaire: {pays_data.get('force_militaire', 0)}/100
Chômage: {pays_data.get('chomage', 0)}%
Inflation: {pays_data.get('inflation', 0)}%
Stabilité: {pays_data.get('stabilite', 100)}/100
Ressources: {pays_data.get('ressources', {})}
Infrastructures: {infra_list or 'Aucune'}
Bénéfice net actuel: {pays_data.get('benefice_net', 0):,} $/cycle

=== ACTION EFFECTUÉE ===
{action}

=== CONTEXTE MONDIAL ===
Pays dans le jeu: {len(contexte_mondial.get('pays', {}))}
Guerres en cours: {len(contexte_mondial.get('guerres', []))}

Réponds UNIQUEMENT avec un JSON valide (sans texte avant ou après):
{{
  "resume": "2-3 phrases narratives décrivant les conséquences",
  "modifications": {{
    "pib": variation numerique,
    "population": variation numerique,
    "armee": variation numerique,
    "chomage": variation en pourcentage ex -1.5,
    "inflation": variation en pourcentage ex 0.5,
    "stabilite": variation entre -20 et 20,
    "tresor": variation numerique
  }},
  "ressources_gagnees": {{}},
  "alerte": null
}}"""

    import time
    # gemini-1.5-flash-8b = limites gratuites très élevées (1500 req/jour)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
    }).encode("utf-8")
    # Retry automatique si 429
    for tentative in range(3):
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            if "429" in str(e) and tentative < 2:
                time.sleep(5)  # attend 5 secondes et réessaie
                continue
            raise e

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
        ressources = consequences.get("ressources_gagnees", {})
        for res, qte in ressources.items():
            pays["ressources"][res] = pays["ressources"].get(res, 0) + qte
        data["log_actions"].append({
            "date": datetime.now().isoformat(),
            "pays": pays_nom,
            "action": action_description,
            "resume": consequences.get("resume", "")
        })
        save_data(data)
        return consequences, None
    except Exception as e:
        return None, f"Erreur: {str(e)}"

# ============================================================
# TÂCHE PÉRIODIQUE : CYCLE ÉCONOMIQUE
# ============================================================
@tasks.loop(hours=6)
async def cycle_economique():
    data = load_data()
    appliquer_cycle_economique(data)
    print(f"[{datetime.now()}] Cycle économique appliqué.")

# ============================================================
# VUES INTERACTIVES
# ============================================================

# ---------- VUE MENU PRINCIPAL ----------
class MenuPrincipalView(discord.ui.View):
    def __init__(self, pays_nom, user_id):
        super().__init__(timeout=120)
        self.pays_nom = pays_nom
        self.user_id = user_id

    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.primary)
    async def btn_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True)
            return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_stats(self.pays_nom, pays)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="💰 Finances", style=discord.ButtonStyle.success)
    async def btn_finances(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True)
            return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        calculer_finances(pays)
        embed = build_embed_finances(self.pays_nom, pays)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🏗️ Infrastructures", style=discord.ButtonStyle.secondary)
    async def btn_infra(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True)
            return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_infra(self.pays_nom, pays)
        view = InfraMenuView(self.pays_nom, self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="⚔️ Militaire", style=discord.ButtonStyle.danger)
    async def btn_militaire(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ Ce menu ne vous appartient pas.", ephemeral=True)
            return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_militaire(self.pays_nom, pays)
        view = MilitaireMenuView(self.pays_nom, self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)


# ---------- VUE MENU INFRASTRUCTURE ----------
class InfraMenuView(discord.ui.View):
    def __init__(self, pays_nom, user_id):
        super().__init__(timeout=120)
        self.pays_nom = pays_nom
        self.user_id = user_id
        # Dropdown catégorie
        self.add_item(SelectCategorieCivile(pays_nom, user_id))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True)
            return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_stats(self.pays_nom, pays)
        await interaction.response.edit_message(embed=embed, view=MenuPrincipalView(self.pays_nom, self.user_id))


class SelectCategorieCivile(discord.ui.Select):
    def __init__(self, pays_nom, user_id):
        self.pays_nom = pays_nom
        self.user_id = user_id
        options = [
            discord.SelectOption(label="🌾 Économie (Farms, Usines, Ports...)", value="Économie", emoji="💼"),
            discord.SelectOption(label="🏥 Services (Hôpitaux, Écoles, Énergie...)", value="Services", emoji="🏛️"),
        ]
        super().__init__(placeholder="📋 Sélectionner une catégorie d'infrastructure...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True)
            return
        categorie = self.values[0]
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_catalogue(self.pays_nom, pays, categorie)
        view = AcheterInfraView(self.pays_nom, self.user_id, categorie)
        await interaction.response.edit_message(embed=embed, view=view)


class AcheterInfraView(discord.ui.View):
    def __init__(self, pays_nom, user_id, categorie):
        super().__init__(timeout=120)
        self.pays_nom = pays_nom
        self.user_id = user_id
        self.categorie = categorie
        # Remplir le select avec les infras de la catégorie
        infras_cat = {k: v for k, v in INFRA_CIVILES.items() if v["categorie"] == categorie}
        self.add_item(SelectAcheterInfra(pays_nom, user_id, infras_cat))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_infra(self.pays_nom, pays)
        await interaction.response.edit_message(embed=embed, view=InfraMenuView(self.pays_nom, self.user_id))


class SelectAcheterInfra(discord.ui.Select):
    def __init__(self, pays_nom, user_id, infras):
        self.pays_nom = pays_nom
        self.user_id = user_id
        options = []
        for k, v in list(infras.items())[:25]:
            options.append(discord.SelectOption(
                label=f"{v['nom']} — {v['cout']:,}$",
                description=v['desc'][:50],
                value=k
            ))
        super().__init__(placeholder="🛒 Choisir une infrastructure à construire...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True)
            return
        infra_id = self.values[0]
        data = load_data()
        pays = data["pays"].get(self.pays_nom)

        if pays.get("chef") != str(interaction.user.id):
            await interaction.response.send_message("❌ Seul le chef d'État peut construire !", ephemeral=True)
            return

        infra = ALL_INFRA[infra_id]
        quantite_actuelle = pays["infrastructures"].get(infra_id, 0)
        if quantite_actuelle >= infra["max"]:
            await interaction.response.send_message(f"❌ Maximum atteint ({infra['max']}) pour {infra['nom']} !", ephemeral=True)
            return

        if pays["tresor"] < infra["cout"]:
            manque = infra["cout"] - pays["tresor"]
            await interaction.response.send_message(
                f"❌ Trésor insuffisant ! Il vous manque **{manque:,} $**\n"
                f"💰 Votre trésor: {pays['tresor']:,} $\n"
                f"💸 Coût: {infra['cout']:,} $", ephemeral=True)
            return

        # ACHAT
        pays["tresor"] -= infra["cout"]
        pays["infrastructures"][infra_id] = quantite_actuelle + 1

        # Appliquer effets immédiats
        if "effet_pib" in infra:
            pays["pib"] += infra["effet_pib"]
        if "effet_chomage" in infra:
            pays["chomage"] = max(0, round(pays["chomage"] + infra["effet_chomage"], 2))
        if "effet_stabilite" in infra:
            pays["stabilite"] = min(100, pays["stabilite"] + infra["effet_stabilite"])
        if "effet_population" in infra:
            pays["population"] += infra["effet_population"]

        calculer_finances(pays)
        save_data(data)

        embed = discord.Embed(
            title=f"✅ Construction réussie !",
            description=f"**{infra['nom']}** construite en **{self.pays_nom}** !",
            color=discord.Color.green()
        )
        embed.add_field(name="💸 Coût payé", value=f"{infra['cout']:,} $", inline=True)
        embed.add_field(name="💰 Trésor restant", value=f"{pays['tresor']:,} $", inline=True)
        embed.add_field(name="📦 Total construit", value=f"{quantite_actuelle + 1}/{infra['max']}", inline=True)
        embed.add_field(name="💹 Revenu/cycle", value=f"+{infra['revenu']:,} $", inline=True)
        embed.add_field(name="🔧 Maintenance/cycle", value=f"-{infra['maintenance']:,} $", inline=True)
        embed.add_field(name="👷 Emplois créés", value=f"+{infra['emplois']:,}", inline=True)
        embed.add_field(name="📊 Bénéfice net/cycle", value=f"{pays['benefice_net']:,} $", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


# ---------- VUE MILITAIRE ----------
class MilitaireMenuView(discord.ui.View):
    def __init__(self, pays_nom, user_id):
        super().__init__(timeout=120)
        self.pays_nom = pays_nom
        self.user_id = user_id
        self.add_item(SelectAcheterMilitaire(pays_nom, user_id))

    @discord.ui.button(label="🔙 Retour", style=discord.ButtonStyle.secondary, row=2)
    async def btn_retour(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        embed = build_embed_stats(self.pays_nom, pays)
        await interaction.response.edit_message(embed=embed, view=MenuPrincipalView(self.pays_nom, self.user_id))

    @discord.ui.button(label="👥 Recruter des soldats", style=discord.ButtonStyle.danger, row=1)
    async def btn_recruter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id): return
        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        if pays.get("chef") != str(interaction.user.id):
            await interaction.response.send_message("❌ Seul le chef peut recruter !", ephemeral=True)
            return
        await interaction.response.send_modal(RecrutementModal(self.pays_nom))


class SelectAcheterMilitaire(discord.ui.Select):
    def __init__(self, pays_nom, user_id):
        self.pays_nom = pays_nom
        self.user_id = user_id
        options = []
        for k, v in list(INFRA_MILITAIRES.items())[:25]:
            options.append(discord.SelectOption(
                label=f"{v['nom']} — {v['cout']:,}$",
                description=v['desc'][:50],
                value=k
            ))
        super().__init__(placeholder="🏗️ Construire une infrastructure militaire...", options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌", ephemeral=True)
            return
        infra_id = self.values[0]
        data = load_data()
        pays = data["pays"].get(self.pays_nom)

        if pays.get("chef") != str(interaction.user.id):
            await interaction.response.send_message("❌ Seul le chef d'État peut construire !", ephemeral=True)
            return

        infra = INFRA_MILITAIRES[infra_id]
        quantite_actuelle = pays["infrastructures"].get(infra_id, 0)

        if quantite_actuelle >= infra["max"]:
            await interaction.response.send_message(f"❌ Maximum atteint ({infra['max']}) !", ephemeral=True)
            return

        if pays["tresor"] < infra["cout"]:
            await interaction.response.send_message(
                f"❌ Trésor insuffisant ! Besoin: {infra['cout']:,} $ | Disponible: {pays['tresor']:,} $", ephemeral=True)
            return

        pays["tresor"] -= infra["cout"]
        pays["infrastructures"][infra_id] = quantite_actuelle + 1

        if "soldats_bonus" in infra:
            pays["armee"] += infra["soldats_bonus"]
        if "force_bonus" in infra:
            pays["force_militaire"] = min(100, pays["force_militaire"] + infra["force_bonus"])
        if "effet_stabilite" in infra:
            pays["stabilite"] = min(100, pays["stabilite"] + infra["effet_stabilite"])
        if "effet_chomage" in infra:
            pays["chomage"] = max(0, round(pays["chomage"] + infra["effet_chomage"], 2))

        calculer_finances(pays)
        save_data(data)

        embed = discord.Embed(
            title=f"✅ Infrastructure militaire construite !",
            description=f"**{infra['nom']}** opérationnelle en **{self.pays_nom}** !",
            color=discord.Color.red()
        )
        embed.add_field(name="💸 Coût", value=f"{infra['cout']:,} $", inline=True)
        embed.add_field(name="💰 Trésor restant", value=f"{pays['tresor']:,} $", inline=True)
        embed.add_field(name="📦 Quantité", value=f"{quantite_actuelle + 1}/{infra['max']}", inline=True)
        if "soldats_bonus" in infra:
            embed.add_field(name="👥 Soldats ajoutés", value=f"+{infra['soldats_bonus']:,}", inline=True)
        if "force_bonus" in infra:
            embed.add_field(name="⚔️ Force +", value=f"+{infra['force_bonus']}", inline=True)
        embed.add_field(name="🔧 Maintenance/cycle", value=f"-{infra['maintenance']:,} $", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class RecrutementModal(discord.ui.Modal, title="Recrutement militaire"):
    nombre = discord.ui.TextInput(
        label="Nombre de soldats à recruter",
        placeholder="Ex: 5000",
        required=True, max_length=10
    )

    def __init__(self, pays_nom):
        super().__init__()
        self.pays_nom = pays_nom

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nb = int(self.nombre.value.replace(" ", "").replace(",", ""))
        except ValueError:
            await interaction.response.send_message("❌ Nombre invalide !", ephemeral=True)
            return

        data = load_data()
        pays = data["pays"].get(self.pays_nom)
        cout_par_soldat = 5_000
        cout_total = nb * cout_par_soldat

        if pays["tresor"] < cout_total:
            await interaction.response.send_message(
                f"❌ Trésor insuffisant !\n💰 Disponible: {pays['tresor']:,} $\n💸 Coût: {cout_total:,} $ ({nb:,} × {cout_par_soldat:,} $)",
                ephemeral=True)
            return

        pays["tresor"] -= cout_total
        pays["armee"] += nb
        pays["chomage"] = max(0, round(pays["chomage"] - (nb / pays["population"]) * 100, 2))
        calculer_finances(pays)
        save_data(data)

        await interaction.response.send_message(
            f"✅ **{nb:,} soldats recrutés !**\n"
            f"⚔️ Armée totale: **{pays['armee']:,}**\n"
            f"💸 Coût total: **{cout_total:,} $**\n"
            f"💰 Trésor restant: **{pays['tresor']:,} $**",
            ephemeral=True)

# ============================================================
# BUILDERS D'EMBEDS
# ============================================================
def build_embed_stats(pays_nom, pays):
    calculer_finances(pays)
    stab = pays['stabilite']
    stab_bar = "🟩" * (stab // 20) + "⬛" * (5 - stab // 20)
    stab_emoji = "🟢" if stab > 70 else "🟡" if stab > 40 else "🔴"

    embed = discord.Embed(
        title=f"🌍 {pays_nom} — Tableau de bord",
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
    embed.add_field(name="⚔️ Armée", value=f"{pays['armee']:,} soldats", inline=True)
    embed.add_field(name="🎖️ Force militaire", value=f"{pays['force_militaire']}/100", inline=True)
    nb_infra = sum(pays.get("infrastructures", {}).values())
    embed.add_field(name="🏗️ Infrastructures", value=f"{nb_infra} bâtiments", inline=True)
    res_text = " | ".join([f"{k}: {v}" for k, v in pays['ressources'].items()])
    embed.add_field(name="🏭 Ressources", value=res_text or "Aucune", inline=False)
    if pays.get('alliances'):
        embed.add_field(name="🤝 Alliances", value=", ".join(pays['alliances']), inline=True)
    if pays.get('en_guerre_contre'):
        embed.add_field(name="⚔️ En guerre", value=", ".join(pays['en_guerre_contre']), inline=True)
    return embed

def build_embed_finances(pays_nom, pays):
    benefice = pays["benefice_net"]
    couleur = discord.Color.green() if benefice >= 0 else discord.Color.red()
    embed = discord.Embed(title=f"💰 Finances de {pays_nom}", color=couleur)
    embed.add_field(name="🏦 Trésor actuel", value=f"{pays['tresor']:,} $", inline=False)
    embed.add_field(name="📥 Revenus/cycle", value=f"+{pays['revenu_total']:,} $", inline=True)
    embed.add_field(name="📤 Dépenses/cycle", value=f"-{pays['depenses_total']:,} $", inline=True)
    embed.add_field(name="💹 Bénéfice net", value=f"{benefice:+,} $", inline=True)

    # Détail des revenus par infrastructure
    revenus_detail = []
    for infra_id, qte in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA:
            infra = ALL_INFRA[infra_id]
            if infra.get("revenu", 0) > 0:
                total_rev = infra["revenu"] * qte
                revenus_detail.append(f"{infra['nom']} ×{qte}: +{total_rev:,} $")
    if revenus_detail:
        embed.add_field(name="📊 Revenus par infrastructure", value="\n".join(revenus_detail[:10]), inline=False)

    # Détail des dépenses
    depenses_detail = []
    for infra_id, qte in pays.get("infrastructures", {}).items():
        if infra_id in ALL_INFRA:
            infra = ALL_INFRA[infra_id]
            if infra.get("maintenance", 0) > 0:
                total_dep = infra["maintenance"] * qte
                depenses_detail.append(f"{infra['nom']} ×{qte}: -{total_dep:,} $")
    dep_armee = pays['armee'] * 100
    depenses_detail.append(f"⚔️ Armée ({pays['armee']:,} soldats): -{dep_armee:,} $")
    if depenses_detail:
        embed.add_field(name="📋 Dépenses détaillées", value="\n".join(depenses_detail[:10]), inline=False)

    embed.add_field(name="📉 Chômage", value=f"{pays['chomage']}%", inline=True)
    embed.add_field(name="📈 Inflation", value=f"{pays['inflation']}%", inline=True)
    embed.set_footer(text="Le cycle économique se déclenche toutes les 6h.")
    return embed

def build_embed_infra(pays_nom, pays):
    embed = discord.Embed(title=f"🏗️ Infrastructures de {pays_nom}", color=discord.Color.teal())
    infras_pays = pays.get("infrastructures", {})
    if not infras_pays:
        embed.description = "Aucune infrastructure construite.\nUtilisez le menu ci-dessous pour construire !"
    else:
        civ_lines = []
        mil_lines = []
        for infra_id, qte in infras_pays.items():
            if infra_id in ALL_INFRA:
                infra = ALL_INFRA[infra_id]
                rev = infra.get("revenu", 0) * qte
                dep = infra.get("maintenance", 0) * qte
                line = f"{infra['nom']} ×**{qte}** | Rev: +{rev:,}$ | Maint: -{dep:,}$"
                if infra_id in INFRA_MILITAIRES:
                    mil_lines.append(line)
                else:
                    civ_lines.append(line)
        if civ_lines:
            embed.add_field(name="🏛️ Civiles", value="\n".join(civ_lines), inline=False)
        if mil_lines:
            embed.add_field(name="⚔️ Militaires", value="\n".join(mil_lines), inline=False)

    calculer_finances(pays)
    embed.add_field(name="💹 Bénéfice net/cycle", value=f"{pays['benefice_net']:+,} $", inline=True)
    embed.add_field(name="🏦 Trésor", value=f"{pays['tresor']:,} $", inline=True)
    embed.set_footer(text="Sélectionnez une catégorie pour construire.")
    return embed

def build_embed_militaire(pays_nom, pays):
    embed = discord.Embed(title=f"⚔️ Armée de {pays_nom}", color=discord.Color.red())
    embed.add_field(name="👥 Soldats", value=f"{pays['armee']:,}", inline=True)
    embed.add_field(name="🎖️ Force", value=f"{pays['force_militaire']}/100", inline=True)
    embed.add_field(name="💰 Trésor", value=f"{pays['tresor']:,} $", inline=True)
    embed.add_field(name="💸 Coût recrutement", value="5 000 $ / soldat", inline=True)
    embed.add_field(name="🔧 Maintenance armée", value=f"{pays['armee'] * 100:,} $/cycle", inline=True)
    # Infras militaires
    mil_lines = []
    for infra_id, qte in pays.get("infrastructures", {}).items():
        if infra_id in INFRA_MILITAIRES:
            infra = INFRA_MILITAIRES[infra_id]
            mil_lines.append(f"{infra['nom']} ×{qte}")
    if mil_lines:
        embed.add_field(name="🏗️ Installations", value="\n".join(mil_lines), inline=False)
    else:
        embed.add_field(name="🏗️ Installations", value="Aucune installation militaire.", inline=False)

    if pays.get("en_guerre_contre"):
        embed.add_field(name="⚔️ En guerre contre", value=", ".join(pays["en_guerre_contre"]), inline=False)
    embed.set_footer(text="Recrutez des soldats ou construisez des installations militaires.")
    return embed

def build_embed_catalogue(pays_nom, pays, categorie):
    embed = discord.Embed(
        title=f"📋 Catalogue — {categorie}",
        description=f"💰 Trésor disponible : **{pays['tresor']:,} $**",
        color=discord.Color.gold()
    )
    infras_cat = {k: v for k, v in INFRA_CIVILES.items() if v["categorie"] == categorie}
    for k, infra in infras_cat.items():
        qte_actuelle = pays.get("infrastructures", {}).get(k, 0)
        benefice_infra = infra.get("revenu", 0) - infra.get("maintenance", 0)
        abordable = "✅" if pays["tresor"] >= infra["cout"] else "❌"
        val = (
            f"💸 Coût: **{infra['cout']:,} $** {abordable}\n"
            f"🔧 Maintenance: {infra['maintenance']:,} $/cycle\n"
            f"💹 Revenu: +{infra.get('revenu', 0):,} $/cycle\n"
            f"📊 Bénéfice net: **{benefice_infra:+,} $/cycle**\n"
            f"👷 Emplois: +{infra.get('emplois', 0):,}\n"
            f"📦 Construit: {qte_actuelle}/{infra['max']}"
        )
        embed.add_field(name=infra["nom"], value=val, inline=True)
    return embed

# ============================================================
# COMMANDES SLASH
# ============================================================

@tree.command(name="creer_pays", description="Créer votre pays dans le RP géopolitique")
@app_commands.describe(nom="Nom du pays", capitale="Capitale", ideologie="Idéologie politique")
async def creer_pays(interaction: discord.Interaction, nom: str, capitale: str, ideologie: str):
    await interaction.response.defer()
    data = load_data()

    if any(p.get("chef") == str(interaction.user.id) for p in data["pays"].values()):
        await interaction.followup.send("❌ Vous dirigez déjà un pays !")
        return
    if nom in data["pays"]:
        await interaction.followup.send(f"❌ Le pays **{nom}** existe déjà !")
        return
    pays_nom_existant, _ = get_pays_du_joueur(data, interaction.user.id)
    if pays_nom_existant:
        await interaction.followup.send("❌ Vous faites déjà partie d'un pays !")
        return

    data["pays"][nom] = nouveau_pays_data(interaction.user.id, interaction.user.display_name, capitale, ideologie)
    calculer_finances(data["pays"][nom])
    save_data(data)

    embed = build_embed_stats(nom, data["pays"][nom])
    embed.title = f"🎉 Nouveau pays créé : {nom}"
    embed.color = discord.Color.green()
    embed.set_footer(text="Utilisez /tableau_bord pour gérer votre pays !")
    await interaction.followup.send(embed=embed)

@tree.command(name="tableau_bord", description="Ouvrir le tableau de bord de votre pays")
async def tableau_bord(interaction: discord.Interaction):
    data = load_data()
    pays_nom, pays = get_pays_du_joueur(data, interaction.user.id)
    if not pays_nom:
        await interaction.response.send_message("❌ Vous n'avez pas de pays. Utilisez `/creer_pays` !", ephemeral=True)
        return
    calculer_finances(pays)
    save_data(data)
    embed = build_embed_stats(pays_nom, pays)
    view = MenuPrincipalView(pays_nom, interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="rejoindre_pays", description="Rejoindre un pays existant")
@app_commands.describe(nom="Nom du pays")
async def rejoindre_pays(interaction: discord.Interaction, nom: str):
    data = load_data()
    pays_actuel, _ = get_pays_du_joueur(data, interaction.user.id)
    if pays_actuel:
        await interaction.response.send_message(f"❌ Vous faites déjà partie de **{pays_actuel}** !")
        return
    if nom not in data["pays"]:
        await interaction.response.send_message(f"❌ Le pays **{nom}** n'existe pas !")
        return
    data["pays"][nom]["membres"].append(str(interaction.user.id))
    save_data(data)
    await interaction.response.send_message(f"✅ Vous avez rejoint **{nom}** ! Bienvenue, {interaction.user.mention} !")

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

    embed = discord.Embed(
        title=f"🎯 Action de {pays_nom}",
        description=f"**Action :** {description}",
        color=discord.Color.orange()
    )
    embed.add_field(name="📜 Conséquences", value=consequences.get("resume", "Aucune info"), inline=False)
    mods = consequences.get("modifications", {})
    if mods:
        mods_text = [f"{'📈' if v > 0 else '📉'} **{k}**: {'+' if v > 0 else ''}{v:,}" for k, v in mods.items()]
        embed.add_field(name="📊 Modifications", value="\n".join(mods_text), inline=False)
    if consequences.get("alerte"):
        embed.add_field(name="🚨 ALERTE", value=consequences["alerte"], inline=False)
    await msg.edit(content=None, embed=embed)

@tree.command(name="declarer_guerre", description="Déclarer la guerre à un pays")
@app_commands.describe(cible="Nom du pays à attaquer")
async def declarer_guerre(interaction: discord.Interaction, cible: str):
    await interaction.response.defer()
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom:
        await interaction.followup.send("❌ Vous n'êtes pas chef d'État !")
        return
    if cible not in data["pays"]:
        await interaction.followup.send(f"❌ Le pays **{cible}** n'existe pas !")
        return
    if cible in pays["en_guerre_contre"] or cible == pays_nom:
        await interaction.followup.send("❌ Action impossible.")
        return
    pays["en_guerre_contre"].append(cible)
    data["pays"][cible]["en_guerre_contre"].append(pays_nom)
    data["guerres"].append({"attaquant": pays_nom, "defenseur": cible, "debut": datetime.now().isoformat()})
    pays["stabilite"] = max(0, pays["stabilite"] - 10)
    data["pays"][cible]["stabilite"] = max(0, data["pays"][cible]["stabilite"] - 15)
    save_data(data)
    pays_cible = data["pays"][cible]
    embed = discord.Embed(title="⚔️ DÉCLARATION DE GUERRE !", description=f"**{pays_nom}** → **{cible}**", color=discord.Color.red())
    embed.add_field(name="🏴 Attaquant", value=f"{pays_nom}\n{pays['armee']:,} soldats\nForce: {pays['force_militaire']}/100", inline=True)
    embed.add_field(name="🛡️ Défenseur", value=f"{cible}\n{pays_cible['armee']:,} soldats\nForce: {pays_cible['force_militaire']}/100", inline=True)
    await interaction.followup.send(embed=embed)

@tree.command(name="bataille", description="Lancer une bataille")
@app_commands.describe(cible="Pays ennemi", soldats="Soldats à engager")
async def bataille(interaction: discord.Interaction, cible: str, soldats: int):
    await interaction.response.defer()
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom or cible not in pays["en_guerre_contre"]:
        await interaction.followup.send("❌ Vous n'êtes pas en guerre contre ce pays !")
        return
    if soldats > pays["armee"]:
        await interaction.followup.send(f"❌ Vous n'avez que {pays['armee']:,} soldats !")
        return
    pays_cible = data["pays"][cible]
    soldats_cible = min(int(pays_cible["armee"] * random.uniform(0.3, 0.8)), pays_cible["armee"])
    force_att = soldats * (pays["force_militaire"] / 50) * random.uniform(0.8, 1.2)
    force_def = soldats_cible * (pays_cible["force_militaire"] / 50) * random.uniform(0.9, 1.3)
    victoire = force_att > force_def
    pertes_att = int(soldats * random.uniform(0.05, 0.20))
    pertes_def = int(soldats_cible * random.uniform(0.05, 0.20))
    pays["armee"] -= pertes_att
    pays_cible["armee"] -= pertes_def
    if victoire:
        butin = int(pays_cible["tresor"] * random.uniform(0.01, 0.05))
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
    embed.add_field(name="🏴 Soldats engagés", value=f"{soldats:,}", inline=True)
    embed.add_field(name="🛡️ Soldats ennemis", value=f"{soldats_cible:,}", inline=True)
    embed.add_field(name="💀 Vos pertes", value=f"{pertes_att:,}", inline=True)
    embed.add_field(name="☠️ Pertes ennemies", value=f"{pertes_def:,}", inline=True)
    if victoire:
        embed.add_field(name="💰 Butin pillé", value=f"{butin:,} $", inline=False)
    await interaction.followup.send(embed=embed)

@tree.command(name="paix", description="Signer la paix")
@app_commands.describe(cible="Pays ennemi")
async def paix(interaction: discord.Interaction, cible: str):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom or cible not in pays["en_guerre_contre"]:
        await interaction.response.send_message("❌ Vous n'êtes pas en guerre contre ce pays !")
        return
    pays["en_guerre_contre"].remove(cible)
    data["pays"][cible]["en_guerre_contre"].remove(pays_nom)
    pays["stabilite"] = min(100, pays["stabilite"] + 5)
    data["pays"][cible]["stabilite"] = min(100, data["pays"][cible]["stabilite"] + 5)
    data["guerres"] = [g for g in data["guerres"] if not (
        (g["attaquant"] == pays_nom and g["defenseur"] == cible) or
        (g["attaquant"] == cible and g["defenseur"] == pays_nom)
    )]
    save_data(data)
    await interaction.response.send_message(f"🕊️ **Paix signée !** La guerre entre **{pays_nom}** et **{cible}** est terminée.")

@tree.command(name="alliance", description="Former une alliance")
@app_commands.describe(cible="Pays allié")
async def alliance(interaction: discord.Interaction, cible: str):
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom:
        await interaction.response.send_message("❌ Vous n'êtes pas chef d'État !")
        return
    if cible not in data["pays"] or cible in pays["alliances"]:
        await interaction.response.send_message("❌ Impossible de former cette alliance.")
        return
    pays["alliances"].append(cible)
    data["pays"][cible]["alliances"].append(pays_nom)
    save_data(data)
    await interaction.response.send_message(f"🤝 **{pays_nom}** et **{cible}** sont désormais alliés !")

@tree.command(name="classement", description="Classement mondial")
@app_commands.describe(critere="Critère")
@app_commands.choices(critere=[
    app_commands.Choice(name="💰 PIB", value="pib"),
    app_commands.Choice(name="🏦 Trésor", value="tresor"),
    app_commands.Choice(name="⚔️ Armée", value="armee"),
    app_commands.Choice(name="👥 Population", value="population"),
    app_commands.Choice(name="🛡️ Stabilité", value="stabilite"),
    app_commands.Choice(name="🎖️ Force militaire", value="force_militaire"),
    app_commands.Choice(name="💹 Bénéfice net", value="benefice_net"),
])
async def classement(interaction: discord.Interaction, critere: str = "pib"):
    data = load_data()
    if not data["pays"]:
        await interaction.response.send_message("❌ Aucun pays n'existe encore !")
        return
    for pays in data["pays"].values():
        calculer_finances(pays)
    pays_tries = sorted(data["pays"].items(), key=lambda x: x[1].get(critere, 0), reverse=True)
    labels = {"pib": "💰 PIB", "tresor": "🏦 Trésor", "armee": "⚔️ Armée", "population": "👥 Population",
              "stabilite": "🛡️ Stabilité", "force_militaire": "🎖️ Force Militaire", "benefice_net": "💹 Bénéfice Net"}
    unites = {"pib": "$", "tresor": "$", "armee": "soldats", "population": "", "stabilite": "/100", "force_militaire": "/100", "benefice_net": "$/cycle"}
    embed = discord.Embed(title=f"🌍 Classement — {labels.get(critere, critere)}", color=discord.Color.gold())
    medailles = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (nom, pays) in enumerate(pays_tries[:10]):
        m = medailles[i] if i < 3 else f"`{i+1}.`"
        v = pays.get(critere, 0)
        u = unites.get(critere, "")
        lines.append(f"{m} **{nom}** — {v:+,} {u}" if critere == "benefice_net" else f"{m} **{nom}** — {v:,} {u}")
    embed.description = "\n".join(lines)
    await interaction.response.send_message(embed=embed)

@tree.command(name="liste_pays", description="Voir tous les pays")
async def liste_pays(interaction: discord.Interaction):
    data = load_data()
    if not data["pays"]:
        await interaction.response.send_message("❌ Aucun pays n'existe encore !")
        return
    embed = discord.Embed(title="🌍 Nations du monde", color=discord.Color.blue())
    for nom, pays in data["pays"].items():
        calculer_finances(pays)
        statut = "⚔️ En guerre" if pays["en_guerre_contre"] else ("🤝 Allié" if pays["alliances"] else "🕊️ Neutre")
        embed.add_field(
            name=f"🏳️ {nom}",
            value=(f"Chef: {pays['chef_nom']} | {statut}\n"
                   f"Pop: {pays['population']:,} | Trésor: {pays['tresor']:,} $\n"
                   f"Bénéfice: {pays['benefice_net']:+,} $/cycle"),
            inline=False
        )
    save_data(data)
    await interaction.response.send_message(embed=embed)

@tree.command(name="evenement", description="Déclencher un événement aléatoire")
async def evenement(interaction: discord.Interaction):
    await interaction.response.defer()
    data = load_data()
    pays_nom, pays = get_pays_du_chef(data, interaction.user.id)
    if not pays_nom:
        await interaction.followup.send("❌ Vous n'êtes pas chef d'État !")
        return
    ev = random.choice([
        "Découverte d'un gisement de pétrole dans le nord",
        "Grève générale paralyse l'économie nationale",
        "Tremblement de terre frappe la capitale",
        "Vague d'immigration massive arrive aux frontières",
        "Scandale de corruption éclate au gouvernement",
        "Récolte exceptionnelle booste l'agriculture",
        "Épidémie se propage dans les grandes villes",
        "Accord commercial proposé par un pays voisin",
        "Manifestations populaires éclatent dans plusieurs villes",
        "Avancée technologique révolutionne l'industrie",
        "Crise financière mondiale frappe les exportations",
        "Boom touristique suite à un événement sportif international"
    ])
    consequences, erreur = appliquer_consequences(data, pays_nom, f"Événement aléatoire: {ev}")
    embed = discord.Embed(title=f"⚡ ÉVÉNEMENT EN {pays_nom.upper()} !", description=f"**{ev}**", color=discord.Color.purple())
    if consequences:
        embed.add_field(name="📜 Impact", value=consequences.get("resume", ""), inline=False)
        mods = consequences.get("modifications", {})
        if mods:
            embed.add_field(name="📊 Modifications", value="\n".join([f"{'📈' if v > 0 else '📉'} **{k}**: {'+' if v > 0 else ''}{v:,}" for k, v in mods.items()]), inline=False)
    await interaction.followup.send(embed=embed)

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
