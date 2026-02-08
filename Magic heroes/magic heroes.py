import tkinter as tk
from tkinter import messagebox
import random

# --- KONFIGURACE A DATA ---

# Definice typů efektů podle pravidel
EF_UTOK_HRDINA = "Červená kapka"  # Útok na životy hrdiny
EF_UTOK_ZBRAN = "Černý meč"       # Útok na životy zbraně
EF_MANA = "Růžová hvězda"         # Zisk many
EF_STIT = "Modrý štít"            # Obrana
EF_LECENI = "Zelený kříž"         # Léčení (zjednodušené)
EF_NIC = "Nic"

class Hero:
    def __init__(self, name, life, description, bonuses):
        self.name = name
        self.max_life = life
        self.current_life = life
        self.mana = 0
        self.shield = 0
        self.description = description
        # Bonusy: klíč je tuple (min_hod, max_hod), hodnota je (typ_efektu, bonus_hodnota)
        # Např: {(1, 2): (EF_UTOK_HRDINA, 2)} znamená: Pokud padne 1 nebo 2 na kostce hrdiny
        # a zbraň má efekt Červená kapka, přičti k síle +2.
        self.bonuses = bonuses

    def reset(self):
        self.current_life = self.max_life
        self.mana = 0
        self.shield = 0

class Weapon:
    def __init__(self, name, life, repair_cost, effects):
        self.name = name
        self.max_life = life
        self.current_life = life
        self.repair_cost = repair_cost
        # Efekty: klíč je číslo na kostce (1-6), hodnota je (nazev_efektu, sila)
        self.effects = effects

    def reset(self):
        self.current_life = self.max_life

# --- DATABÁZE HRDINŮ A ZBRANÍ ---

HEROES_DATA = {
    "Červená Karkulka": Hero(
        "Červená Karkulka", 20, "Mstitelka z lesa.",
        {
            (1, 2): (EF_UTOK_HRDINA, 2),  # Bonus +2 k útoku na hrdinu při hodu 1-2
            (5, 6): (EF_MANA, 1)          # Bonus +1 k maně při hodu 5-6
        }
    ),
    "Zlý Vlk": Hero(
        "Zlý Vlk", 22, "Predátor Noxveilu.",
        {
            (1, 2): (EF_UTOK_ZBRAN, 2),   # Bonus +2 k ničení zbraně
            (3, 4): (EF_STIT, 2)          # Bonus +2 ke štítu
        }
    ),
    "Temný Rytíř": Hero(
        "Temný Rytíř", 25, "Obrněný válečník.",
        {
            (5, 6): (EF_UTOK_HRDINA, 1),
            (3, 4): (EF_UTOK_ZBRAN, 1)
        }
    )
}

WEAPONS_DATA = {
    "Červený šáteček": Weapon(
        "Červený šáteček", 8, 3,
        {
            1: (EF_UTOK_HRDINA, 3), 2: (EF_UTOK_HRDINA, 4),
            3: (EF_MANA, 2), 4: (EF_STIT, 3),
            5: (EF_UTOK_HRDINA, 2), 6: (EF_LECENI, 2)
        }
    ),
    "Zub vlka": Weapon(
        "Zub vlka", 10, 4,
        {
            1: (EF_UTOK_ZBRAN, 3), 2: (EF_UTOK_ZBRAN, 4),
            3: (EF_UTOK_HRDINA, 3), 4: (EF_STIT, 2),
            5: (EF_MANA, 1), 6: (EF_UTOK_HRDINA, 5)
        }
    ),
    "Černá hůl": Weapon(
        "Černá hůl", 6, 2,
        {
            1: (EF_MANA, 3), 2: (EF_MANA, 4),
            3: (EF_UTOK_HRDINA, 2), 4: (EF_STIT, 4),
            5: (EF_UTOK_ZBRAN, 2), 6: (EF_MANA, 5)
        }
    ),
    "Dýka smrti": Weapon(
        "Dýka smrti", 7, 3,
        {
            1: (EF_UTOK_HRDINA, 5), 2: (EF_UTOK_HRDINA, 1),
            3: (EF_UTOK_ZBRAN, 3), 4: (EF_NIC, 0),
            5: (EF_UTOK_HRDINA, 4), 6: (EF_UTOK_ZBRAN, 4)
        }
    )
}

# --- GUI APLIKACE ---

class MagicHeroesGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Magic Heroes - Dark Fantasy")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a1a")
        
        # Styly
        self.bg_color = "#1a1a1a"
        self.fg_color = "#e0e0e0"
        self.accent_color = "#b30000" # Krvavě červená
        self.font_main = ("Helvetica", 12)
        self.font_title = ("Georgia", 24, "bold")
        
        self.player_hero = None
        self.player_weapon = None
        self.ai_hero = None
        self.ai_weapon = None
        
        self.turn_active = False # Zámek proti klikání během tahu AI

        self.create_selection_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- OBRAZOVKA VÝBĚRU ---
    def create_selection_screen(self):
        self.clear_screen()
        
        tk.Label(self.root, text="MAGIC HEROES", font=self.font_title, bg=self.bg_color, fg=self.accent_color).pack(pady=20)
        
        # Kontejnery pro výběr
        selection_frame = tk.Frame(self.root, bg=self.bg_color)
        selection_frame.pack(fill="both", expand=True, padx=20)
        
        # Levý sloupec - Hrdinové
        hero_frame = tk.Frame(selection_frame, bg=self.bg_color)
        hero_frame.pack(side="left", fill="both", expand=True)
        tk.Label(hero_frame, text="Vyber Hrdinu:", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        
        self.selected_hero_var = tk.StringVar(value=list(HEROES_DATA.keys())[0])
        for h_name in HEROES_DATA:
            tk.Radiobutton(hero_frame, text=h_name, variable=self.selected_hero_var, value=h_name,
                           bg=self.bg_color, fg=self.fg_color, selectcolor="#333", activebackground=self.bg_color, activeforeground="white",
                           command=self.update_info_labels).pack(anchor="w", pady=2)

        # Pravý sloupec - Zbraně
        weapon_frame = tk.Frame(selection_frame, bg=self.bg_color)
        weapon_frame.pack(side="right", fill="both", expand=True)
        tk.Label(weapon_frame, text="Vyber Zbraň:", font=("Helvetica", 16, "bold"), bg=self.bg_color, fg=self.fg_color).pack(anchor="w")
        
        self.selected_weapon_var = tk.StringVar(value=list(WEAPONS_DATA.keys())[0])
        for w_name in WEAPONS_DATA:
            tk.Radiobutton(weapon_frame, text=w_name, variable=self.selected_weapon_var, value=w_name,
                           bg=self.bg_color, fg=self.fg_color, selectcolor="#333", activebackground=self.bg_color, activeforeground="white",
                           command=self.update_info_labels).pack(anchor="w", pady=2)

        # Informační panel (Popis schopností)
        self.info_label = tk.Label(self.root, text="", bg="#252525", fg="white", font=("Courier", 10), justify="left", relief="sunken", bd=2, padx=10, pady=10)
        self.info_label.pack(fill="x", padx=20, pady=20)
        
        start_btn = tk.Button(self.root, text="VSTOUPIT DO ARÉNY", font=("Helvetica", 14, "bold"), bg=self.accent_color, fg="white", command=self.start_game)
        start_btn.pack(pady=20)

        self.update_info_labels()

    def update_info_labels(self):
        h_name = self.selected_hero_var.get()
        w_name = self.selected_weapon_var.get()
        
        h_data = HEROES_DATA[h_name]
        w_data = WEAPONS_DATA[w_name]
        
        info_text = f"--- HRDINA: {h_name} ---\n"
        info_text += f"Životy: {h_data.max_life} | Popis: {h_data.description}\n"
        info_text += "Bonusy:\n"
        for rng, bonus in h_data.bonuses.items():
            info_text += f"  Hod {rng[0]}-{rng[1]}: +{bonus[1]} k síle efektu '{bonus[0]}'\n"
            
        info_text += f"\n--- ZBRAŇ: {w_name} ---\n"
        info_text += f"Výdrž: {w_data.max_life} | Cena opravy: {w_data.repair_cost} HP\n"
        info_text += "Efekty kostky (1-6):\n"
        for roll, eff in w_data.effects.items():
            info_text += f"  [{roll}] {eff[0]} (Síla {eff[1]})\n"
            
        self.info_label.config(text=info_text)

    # --- HERNÍ LOGIKA A OBRAZOVKA ---

    def start_game(self):
        # Inicializace hráče
        p_hero_key = self.selected_hero_var.get()
        p_weapon_key = self.selected_weapon_var.get()
        
        # Vytvoření instancí (kopií) pro hru
        import copy
        self.player_hero = copy.deepcopy(HEROES_DATA[p_hero_key])
        self.player_hero.reset()
        self.player_weapon = copy.deepcopy(WEAPONS_DATA[p_weapon_key])
        self.player_weapon.reset()
        
        # Inicializace AI (vybere zbývajícího hrdinu nebo náhodného, zbraň náhodně)
        ai_hero_key = random.choice([k for k in HEROES_DATA.keys() if k != p_hero_key])
        ai_weapon_key = random.choice(list(WEAPONS_DATA.keys()))
        
        self.ai_hero = copy.deepcopy(HEROES_DATA[ai_hero_key])
        self.ai_hero.reset()
        self.ai_weapon = copy.deepcopy(WEAPONS_DATA[ai_weapon_key])
        self.ai_weapon.reset()

        self.create_game_screen()
        self.log("Hra začíná!", "neutral")
        self.log(f"{self.player_hero.name} (Ty) vs {self.ai_hero.name} (AI)", "neutral")
        self.update_status_display()

    def create_game_screen(self):
        self.clear_screen()
        
        # Horní panel - AI
        self.ai_frame = tk.Frame(self.root, bg="#330000", bd=2, relief="ridge")
        self.ai_frame.pack(fill="x", padx=10, pady=5)
        self.ai_label = tk.Label(self.ai_frame, text="AI STATUS", bg="#330000", fg="white", font=("Helvetica", 12, "bold"))
        self.ai_label.pack(pady=5)
        
        # Střední panel - Log a Kostky
        center_frame = tk.Frame(self.root, bg=self.bg_color)
        center_frame.pack(fill="both", expand=True, padx=10)
        
        self.log_box = tk.Text(center_frame, height=15, bg="#111", fg="#ddd", font=("Consolas", 10), state="disabled")
        self.log_box.pack(fill="both", expand=True, pady=10)
        
        # Spodní panel - Hráč a ovládání
        self.player_frame = tk.Frame(self.root, bg="#001a33", bd=2, relief="ridge")
        self.player_frame.pack(fill="x", padx=10, pady=5)
        self.player_label = tk.Label(self.player_frame, text="PLAYER STATUS", bg="#001a33", fg="white", font=("Helvetica", 12, "bold"))
        self.player_label.pack(pady=5)
        
        controls_frame = tk.Frame(self.root, bg=self.bg_color)
        controls_frame.pack(pady=10)
        
        self.btn_roll = tk.Button(controls_frame, text="HODIT KOSTKAMI (Útok)", font=("Helvetica", 12, "bold"), bg=self.accent_color, fg="white", width=25, command=self.player_turn_roll)
        self.btn_roll.grid(row=0, column=0, padx=5)
        
        self.btn_repair = tk.Button(controls_frame, text="OPRAVIT ZBRAŇ", font=("Helvetica", 12, "bold"), bg="#555", fg="white", width=25, command=self.player_turn_repair)
        self.btn_repair.grid(row=0, column=1, padx=5)

    def log(self, message, mtype="neutral"):
        self.log_box.config(state="normal")
        color = "white"
        if mtype == "player": color = "#66ccff" # Modrá
        elif mtype == "ai": color = "#ff6666"   # Červená
        elif mtype == "system": color = "#ffff99" # Žlutá
        
        self.log_box.tag_config(mtype, foreground=color)
        self.log_box.insert("end", f"> {message}\n", mtype)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def update_status_display(self):
        # AI Status Text
        ai_w_status = f"{self.ai_weapon.current_life}/{self.ai_weapon.max_life}"
        if self.ai_weapon.current_life <= 0: ai_w_status = "ROZBITÁ!"
        
        ai_text = f"{self.ai_hero.name}\nŽivoty: {self.ai_hero.current_life}/{self.ai_hero.max_life} | Mana: {self.ai_hero.mana} | Štít: {self.ai_hero.shield}\n"
        ai_text += f"Zbraň: {self.ai_weapon.name} ({ai_w_status})"
        self.ai_label.config(text=ai_text)
        
        # Player Status Text
        p_w_status = f"{self.player_weapon.current_life}/{self.player_weapon.max_life}"
        if self.player_weapon.current_life <= 0: p_w_status = "ROZBITÁ! (Musíš opravit)"
        
        p_text = f"{self.player_hero.name} (Ty)\nŽivoty: {self.player_hero.current_life}/{self.player_hero.max_life} | Mana: {self.player_hero.mana} | Štít: {self.player_hero.shield}\n"
        p_text += f"Zbraň: {self.player_weapon.name} ({p_w_status})"
        self.player_label.config(text=p_text)

        # Ovládání tlačítek podle stavu zbraně
        if self.player_weapon.current_life <= 0:
            self.btn_roll.config(state="disabled", bg="#333")
            self.btn_repair.config(state="normal", bg="#4CAF50") # Zelená pro opravu
        else:
            self.btn_roll.config(state="normal", bg=self.accent_color)
            self.btn_repair.config(state="disabled", bg="#333")

    def check_game_over(self):
        if self.player_hero.current_life <= 0:
            messagebox.showinfo("Konec hry", f"Prohrál jsi! {self.ai_hero.name} zvítězil.")
            self.root.quit()
            return True
        if self.ai_hero.current_life <= 0:
            messagebox.showinfo("Konec hry", f"Vyhrál jsi! {self.player_hero.name} padl.")
            self.root.quit()
            return True
        return False

    # --- MECHANIKA TAHŮ ---

    def resolve_action(self, attacker_hero, attacker_weapon, defender_hero, defender_weapon, is_player):
        source = "Hráč" if is_player else "AI"
        log_type = "player" if is_player else "ai"
        
        # 1. Kontrola zbraně
        if attacker_weapon.current_life <= 0:
            self.log(f"{source} má rozbitou zbraň a nemohl útočit!", log_type)
            # Pokud je to AI, automaticky si opraví zbraň v dalším kroku logiky, 
            # ale zde jen ukončíme akci útoku.
            return

        # 2. Hody kostkami
        hero_roll = random.randint(1, 6)
        weapon_roll = random.randint(1, 6)
        
        self.log(f"{source} hází: Hrdina[{hero_roll}], Zbraň[{weapon_roll}]", log_type)

        # 3. Zjištění základního efektu ze zbraně
        effect_type, base_value = attacker_weapon.effects.get(weapon_roll, (EF_NIC, 0))
        
        # 4. Aplikace bonusu z hrdiny
        final_value = base_value
        bonus_applied = False
        
        for rng, bonus in attacker_hero.bonuses.items():
            # rng je (min, max), bonus je (typ, hodnota)
            if rng[0] <= hero_roll <= rng[1]:
                # Bonus se aplikuje jen pokud se shoduje typ efektu zbraně s bonusem hrdiny
                if bonus[0] == effect_type:
                    final_value += bonus[1]
                    bonus_applied = True
                    self.log(f"  -> Pasivní bonus hrdiny aktivován! (+{bonus[1]} síla)", log_type)

        # 5. Vyhodnocení efektu
        msg = f"  -> Efekt: {effect_type} (Síla {final_value})"
        
        if effect_type == EF_UTOK_HRDINA:
            damage = final_value
            # Štít absorbuje poškození
            if defender_hero.shield > 0:
                blocked = min(defender_hero.shield, damage)
                defender_hero.shield -= blocked
                damage -= blocked
                msg += f". Štít pohltil {blocked} zranění."
            
            defender_hero.current_life -= damage
            msg += f". Soupeř ztrácí {damage} životů!"
            
        elif effect_type == EF_UTOK_ZBRAN:
            defender_weapon.current_life -= final_value
            msg += f". Soupeřova zbraň ztrácí {final_value} výdrže!"
            
        elif effect_type == EF_MANA:
            attacker_hero.mana += final_value
            msg += f". Zisk {final_value} many."
            
        elif effect_type == EF_STIT:
            attacker_hero.shield += final_value
            msg += f". Přidán štít o síle {final_value}."
            
        elif effect_type == EF_LECENI:
            attacker_hero.current_life = min(attacker_hero.current_life + final_value, attacker_hero.max_life)
            msg += f". Léčení o {final_value}."
            
        self.log(msg, log_type)
        self.update_status_display()

    # --- TAH HRÁČE ---

    def player_turn_roll(self):
        if self.turn_active: return
        self.turn_active = True
        
        # Vyhodnocení útoku hráče
        self.resolve_action(self.player_hero, self.player_weapon, self.ai_hero, self.ai_weapon, is_player=True)
        
        if not self.check_game_over():
            # Spuštění tahu AI se zpožděním
            self.root.after(1500, self.ai_turn)

    def player_turn_repair(self):
        if self.turn_active: return
        self.turn_active = True
        
        cost = self.player_weapon.repair_cost
        if self.player_hero.current_life > cost:
            self.player_hero.current_life -= cost
            self.player_weapon.current_life = self.player_weapon.max_life
            self.log(f"Hráč obětoval {cost} životů a opravil zbraň!", "system")
            self.update_status_display()
            self.root.after(1500, self.ai_turn)
        else:
            self.log("Nemáš dost životů na opravu! (Prohraješ příští kolo?)", "system")
            # Hráč nemůže opravit, musí přeskočit tah nebo prohrát.
            # Pro zjednodušení pustíme AI.
            self.root.after(1500, self.ai_turn)

    # --- TAH AI ---

    def ai_turn(self):
        self.log("--- Tah AI ---", "system")
        
        # Logika AI: Pokud má rozbitou zbraň, musí opravit
        if self.ai_weapon.current_life <= 0:
            cost = self.ai_weapon.repair_cost
            if self.ai_hero.current_life > cost:
                self.ai_hero.current_life -= cost
                self.ai_weapon.current_life = self.ai_weapon.max_life
                self.log(f"AI ({self.ai_hero.name}) opravuje zbraň za {cost} životů.", "ai")
            else:
                self.log("AI nemá na opravu a je bezbranné!", "ai")
        else:
            # Jinak útočí
            self.resolve_action(self.ai_hero, self.ai_weapon, self.player_hero, self.player_weapon, is_player=False)
        
        self.update_status_display()
        self.check_game_over()
        self.turn_active = False # Uvolnění tahu pro hráče
        self.log("--- Tvůj tah ---", "system")

# Spuštění aplikace
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicHeroesGame(root)
    root.mainloop()