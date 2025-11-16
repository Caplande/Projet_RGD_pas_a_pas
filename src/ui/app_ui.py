import yaml
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from tkinter import TclError
import parametres as config
from .theme_global import definir_theme_global, zones, fonts
from src.core.context import context as ctxt
from colorama import Fore, Style


print("Module app_ui chargé avec succès.")

ecran = None


class AppUi(tk.Tk):
    nb_instances = 0

    def __init__(self):
        # *******************
        AppUi.nb_instances += 1
        if AppUi.nb_instances > 1:
            print(
                Fore.RED + f"Nb instances AppUi = {AppUi.nb_instances}" + Style.RESET_ALL)
        # *******************
        super().__init__()

        self.geometry("1200x800")
        self.title(
            f"{ctxt.nom_application} (version:{ctxt.version})")

        # Les palettes, les styles
        # Appliquer le thème global
        # Affecte le thème global TFrame à tous les frames, TLabel à tous les labels etc...
        # Inventaire des palettes et polices disponibles
        self.d_palettes_polices = self.lister_palettes_polices()

        self.theme = definir_theme_global(self)

        # Instanciation du manager de widgets (self.wtm_xxx).
        ctxt.wtm = WidgetTreeManager(self)

        # Création de la racine du menu principal
        self.menubar = tk.Menu(self)
        self.configure(menu=self.menubar)
        ctxt.set_widget_names(self.menubar, "menubar")
        # breakpoint()

        # Création d'un Frame central pour accueillir les pages
        self.fr_centre = ttk.Frame(self)
        self.fr_centre.pack(side="top", fill="both", expand=True)
        ctxt.set_widget_names(self.fr_centre, "fr_centre")

        # Affichage initial: frame de statut: fr_statut et page d'accueil: AccueilPage
        # Affichage de la barre de statut fr_statut
        self.fr_statut = ttk.Frame(
            self, height=25, style="FondBarreEtat.TFrame")
        # Empêcher le redimensionnement automatique calculé par rapport à la taille des enfants
        self.fr_statut.pack_propagate(False)
        self.fr_statut.pack(side="bottom", fill="x")
        ctxt.set_widget_names(self.fr_statut, "fr_statut")
        self.label_statut_1 = ttk.Label(
            self.fr_statut,
            anchor="w", style="LabelBarreEtat.TLabel"
        )
        self.label_statut_2 = ttk.Label(
            self.fr_statut,
            anchor="w", style="LabelBarreEtat.TLabel"
        )

        self.label_statut_1.pack(side="left", padx=10)
        self.label_statut_2.pack(side="left", padx=10)
        ctxt.set_widget_names(self.label_statut_1, "label_statut_1")
        ctxt.set_widget_names(self.label_statut_2, "label_statut_2")

        # Dictionnaire des pages initialisé depuis AppUi mais rempli depuis activation_ecran.py (pour éviter référence circulaires)
        self.pages = {}

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def afficher_page(self, nom_page):
        # Voir ci-dessus: self.pages est rempli depuis activation_ecran.py
        for p in self.pages.values():
            p.pack_forget()
        page = self.pages[nom_page]
        # page.pack(fill="both", expand=True)

    def on_close(self):
        """Ferme proprement l'application."""
        print("Fermeture de la connexion à la base…")
        ctxt.db.close()
        self.destroy()

    def lister_palettes_polices(self):
        with open("parametres.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Accéder au niveau "application" -> "themes"
        palettes = data["PALETTES"]
        polices = data["POLICES"]

        return [list(palettes.keys()), list(polices.keys())]

    def maj_barre_etat(self, contenu_1=f"Base connectée : {Path(ctxt.path_bdd).name}", contenu_2=""):
        self.label_statut_1.config(text=contenu_1)
        self.label_statut_2.config(text=contenu_2)

    def changer_theme(self, event=None):
        def get_theme_selection(event=None):
            d_palette = config.PALETTES[bx_palette.get()]
            d_police = config.POLICES[bx_police.get()]
            print(f"Palette: {d_palette}, Police: {d_police}")
            return d_palette, d_police

        def modifier_theme():
            d_palette, d_police = get_theme_selection()
            ctxt.set_palette(d_palette)
            ctxt.set_police(d_police)
            self.theme = definir_theme_global(self)

            # --- Frame theme ---
        fr_theme = ttk.Frame(ctxt.ecran.pages['page_affichage'], borderwidth=2,  # type: ignore
                             relief="groove", padding=5)
        # fr_theme.pack(side="top", anchor="nw", padx=5, pady=5)
        # placement avec grid
        fr_theme.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        page_affichage = ctxt.ecran.pages['page_affichage']  # type: ignore
        page_affichage.grid_rowconfigure(
            0, weight=0)   # la barre reste en haut
        page_affichage.grid_columnconfigure(0, weight=1)

        # --- Combobox Palette ---
        ttk.Label(fr_theme, text="Palette:").grid(
            row=0, column=0, sticky="nw", padx=5, pady=2)
        bx_palette = ttk.Combobox(
            fr_theme, values=self.d_palettes_polices[0])
        bx_palette.current(0)
        bx_palette.grid(row=0, column=1, padx=5, pady=2)

        # --- Combobox Police ---
        ttk.Label(fr_theme, text="Police:").grid(
            row=1, column=0, sticky="nw", padx=5, pady=2)
        bx_police = ttk.Combobox(
            fr_theme, values=self.d_palettes_polices[1])
        bx_police.current(0)
        bx_police.grid(row=1, column=1, padx=5, pady=2)

        # --- Lier les changements à la fonction ---
        bx_palette.bind("<<ComboboxSelected>>", get_theme_selection)
        bx_police.bind("<<ComboboxSelected>>", get_theme_selection)

        # --- Bouton d'application du thème ---
        btn_appliquer = ttk.Button(
            fr_theme, text="Appliquer", command=modifier_theme)
        btn_appliquer.grid(row=0, column=2, rowspan=2,
                           sticky="ne", padx=10, pady=2)


def appliquer_couleur_jaune_fond(mon_widget):
    style = ttk.Style()
    style.configure("Jaune.TFrame", background="yellow")
    mon_widget.configure(style="Jaune.TFrame")


def appliquer_couleur_bleu_fond(mon_widget):
    style = ttk.Style()
    style.configure("Bleu.TFrame", background="blue")
    mon_widget.configure(style="Bleu.TFrame")


def appliquer_couleur_vert_fond(mon_widget):
    style = ttk.Style()
    style.configure("Vert.TFrame", background="green")
    mon_widget.configure(style="Vert.TFrame")


def appliquer_couleur_orange_fond(mon_widget):
    style = ttk.Style()
    style.configure("Orange.TFrame", background="orange")
    mon_widget.configure(style="Orange.TFrame")


def hierarchie_widgets(widget):
    """
    Retourne un dictionnaire représentant la hiérarchie des widgets
    à partir du widget donné (souvent root).
    Clés : noms Tkinter des widgets
    Valeurs : sous-dictionnaires (même structure)
    """
    enfants = widget.winfo_children()
    return {
        str(widget): {
            child.winfo_name(): hierarchie_widgets(child)
            for child in enfants
        }
    }


def print_widget_tree(widget, indent=""):
    # Couleurs ANSI
    C_RESET = "\033[0m"
    C_CLS = "\033[96m"   # cyan clair pour la classe
    C_PATH = "\033[92m"   # vert pour le chemin
    C_MGR = "\033[93m"   # jaune pour le manager
    C_FORG = "\033[91m"   # rouge pour forgotten
    C_OK = "\033[92m"   # vert status

    cls = widget.winfo_class()
    path = str(widget)
    mgr = widget.winfo_manager()

    if mgr == "":
        status = f"{C_FORG}FORGOTTEN{C_RESET}"
        mgr_display = "none"
    else:
        status = f"{C_OK}active{C_RESET}"
        mgr_display = mgr

    print(
        f"{indent}"
        f"{C_CLS}{cls}{C_RESET} "
        f"{C_PATH}{path}{C_RESET}  "
        f"manager={C_MGR}{mgr_display}{C_RESET}  "
        f"status={status}"
    )

    for child in widget.winfo_children():
        print_widget_tree(child, indent + "    ")


class WidgetTreeManager:
    """ Cette classe permet de visualiser et/ou extraire une hiérarchie de widgets en termes de création,masquage,affichage
        pour les 3 systèmes de gestion:pack,grid,place
        3 fonctionnalités essentielles:
        Si wtm = WidgetTreeManager(widget_contenant)
        ---> root est la racine (ctxt.ecran)
        ---> Gestion récursive. Le manager parcourt widget_contenant, repère tous les enfants, petits enfants quel que soit leur geometry manager
             Peut les cacher, les retaurer en navigant grace au chemin absolu /fr_centre/label1..
        ---> On peut détecter les widgets créés plus tard par wtm.refresh()
        ---> On peut afficher n'importe quel widget wtm.show("/fr_centre/mon_label")
        ---> On peut recupérer un widget: lbl = wtm.get("/fr_centre/mon_label")
        ---> On peut cacher un ou plusieurs widgets: wtm.hide("/page1", "/page2", "/fr_centre/sidebar")
        ---> Représentation de la hiérarchie: wtm.print_tree_status()
        ---> Tous les geometry managers Pack, Grid, Place pris en charge
        ---> Système auto-refresh basé sur les events Tkinter (Map/Unmap/Configure/Destroy)
        ---> Peut restaurer automatiquement les geometry managers d’origine
    """

    def __init__(self, widget):
        self.root = widget
        self.tree = {}   # path → {widget, manager, info}
        self._build_tree()
        self._bind_events()  # activation du refresh automatique

    # ============================================================
    # AUTO-REFRESH
    # ============================================================
    def _bind_events(self):
        """
        Active un système global d'écoute :
        - <Map>       : widget rendu visible
        - <Unmap>     : widget masqué
        - <Configure> : taille/geometry manager changé
        - <Destroy>   : widget détruit

        Le tree est ainsi toujours à jour sans appeler refresh().
        """
        root = self.root.winfo_toplevel()

        root.bind_all("<Map>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Unmap>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Configure>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Destroy>", lambda e: self._build_tree(), add="+")

    # ============================================================
    # BUILD TREE
    # ============================================================
    # ============================================================
    # BUILD TREE
    # ============================================================
    def _build_tree(self):
        """Reconstruit totalement le tree en conservant l'ancien manager si le widget est masqué."""

        # Sauvegarde de l'arbre existant pour récupérer l'ancien manager
        old_tree = self.tree.copy()
        self.tree.clear()

        def recurse(widget, path):
            # --- nom logique pour le chemin ---
            if widget in ctxt.widget_names:
                name = ctxt.widget_names[widget]
            else:
                name = widget.winfo_name()

            fullpath = f"{path}/{name}" if path else name

            # --- infos manager ACTUELLES ---
            current_mgr = widget.winfo_manager()
            if current_mgr == "pack":
                info = widget.pack_info()
            elif current_mgr == "grid":
                info = widget.grid_info()
            elif current_mgr == "place":
                info = widget.place_info()
            else:
                # Widget masqué (current_mgr == "") ou non géré
                info = {}

            # --- CONSERVATION DU MANAGER (LA CORRECTION) ---
            # 1. Tente de récupérer le manager stocké précédemment
            existing_mgr = old_tree.get(fullpath, {}).get("manager", "")

            # 2. Utilise le manager actuel si le widget est visible, sinon utilise le manager stocké
            mgr_to_store = current_mgr if current_mgr else existing_mgr

            self.tree[fullpath] = {
                "widget": widget,
                # Peut contenir 'pack', 'grid', 'place' même si widget.winfo_manager() est ""
                "manager": mgr_to_store,
                # Les infos sont celles du manager ACTIF (ou {})
                "info": info
            }

            for child in widget.winfo_children():
                recurse(child, fullpath)

        recurse(self.root, "")

    # ============================================================
    # INTERNAL TOOLS
    # ============================================================
    def _hide(self, widget):
        mgr = widget.winfo_manager()
        if mgr == "pack":
            widget.pack_forget()
        elif mgr == "grid":
            widget.grid_remove()
        elif mgr == "place":
            widget.place_forget()

    def _restore(self, widget, mgr, info):
        # Le parent réel du widget, toujours valide
        parent = widget.master

        if mgr == "pack":
            parent.pack(**info)
        elif mgr == "grid":
            parent.grid(**info)
        elif mgr == "place":
            parent.place(**info)
        else:
            raise RuntimeError(f"Manager inconnu : {mgr}")

    def _descendants(self, path):
        """Retourne tous les chemins descendants récursifs."""
        prefix = path + "/" if path else ""
        return [
            p for p in self.tree
            if p.startswith(prefix) and p != path
        ]

    def _toggle_single(self, path, visible=True):
        """
        Affiche ou masque uniquement un widget donné,
        sans modifier ses enfants.
        """
        # Reconstruire l'arbre interne
        self._build_tree()

        # Résoudre le chemin ("/frame1/sub/...") en clé interne
        key = self._resolve(path)
        if key is None:
            raise KeyError(f"[WTM.toggle_single] Widget non trouvé : {path}")

        entry = self.tree[key]
        widget = entry["widget"]
        mgr = entry["manager"]
        info = entry["info"]

        # ----------------------------------------------------------
        # Si le manager n'a pas été déterminé (mgr == ""),
        # on le déduit automatiquement à partir des infos du widget
        # ----------------------------------------------------------
        if mgr == "":
            try:
                widget.pack_info()
                mgr = "pack"
            except TclError:
                try:
                    widget.grid_info()
                    mgr = "grid"
                except TclError:
                    try:
                        widget.place_info()
                        mgr = "place"
                    except TclError:
                        raise RuntimeError(
                            f"Impossible de déterminer le manager de {path}"
                        )

        # --- VISIBILITÉ ---
        if visible:
            self._restore(widget, mgr, info)
        else:
            self._hide(widget)

    def _resolve(self, p: str):
        """Trouve le chemin réel associé à p (nom exact, partiel ou segment)."""
        p = p.strip("/")
        if not p:
            return "" if "" in self.tree else None

        # 1) match exact
        if p in self.tree:
            return p

        # 2) match sur les segments
        for key in self.tree.keys():
            if p in key.split("/"):
                return key

        return None

    # ============================================================
    # PUBLIC API
    # ============================================================

    def show(self, path):
        """Affiche un widget + tous ses descendants."""
        self._build_tree()

        key = self._resolve(path)
        if key is None:
            raise KeyError(f"[WTM.show] Chemin non trouvé : {path}")

        # cacher tous les widgets
        for entry in self.tree.values():
            self._hide(entry["widget"])

        # restaurer la cible
        e = self.tree[key]
        self._restore(e["widget"], e["manager"], e["info"])

        # restaurer les descendants
        for child in self._descendants(key):
            e = self.tree[child]
            self._restore(e["widget"], e["manager"], e["info"])

    def hide(self, *paths):
        """Cache un ou plusieurs widgets + leurs descendants."""
        self._build_tree()

        for path in paths:
            key = self._resolve(path)
            if key is None:
                print(f"[WTM.hide] Chemin non trouvé : {path}")
                continue

            # cacher ce widget
            self._hide(self.tree[key]["widget"])

            # cacher tous les descendants
            for c in self._descendants(key):
                self._hide(self.tree[c]["widget"])

    def get(self, path):
        """Renvoie directement l’objet widget."""
        return self.tree[path.lstrip("/")]["widget"]

    def hide_single(self, path):
        self._toggle_single(path, visible=False)

    def show_single(self, path):
        self._toggle_single(path, visible=True)

    def hide_contenu(self, path):
        self.hide(path)
        self.show_single(path)
        # ============================================================
        # PRINT TREE (couleurs)
        # ============================================================

    def print_tree_status(self):
        """Affiche l'arbre avec couleurs + statut actif/inactif + geometry manager."""
        self._build_tree()

        COLOR = {
            "root": "\033[96m",
            "container": "\033[94m",
            "leaf": "\033[92m",
            "inactive": "\033[91m",
            "mgr": "\033[90m",
            "reset": "\033[0m",
        }

        def is_container(widget):
            return len(widget.winfo_children()) > 0

        def is_visible(widget):
            return widget.winfo_manager() != ""

        def indent(level):
            return "  " * level

        def rec(path, level):
            entry = self.tree[path]
            widget = entry["widget"]
            mgr = entry["manager"] or "none"

            # nom python si dispo
            if widget in getattr(ctxt, "widget_names", {}):
                name = ctxt.widget_names[widget]
            else:
                name = widget.winfo_name()

            # couleur du type
            if path == "":
                color = COLOR["root"]
            elif is_container(widget):
                color = COLOR["container"]
            else:
                color = COLOR["leaf"]

            # actif/inactif
            active = is_visible(widget)
            state_color = COLOR["leaf"] if active else COLOR["inactive"]
            state_txt = "actif" if active else "inactif"

            print(
                f"{indent(level)}"
                f"{color}{name}{COLOR['reset']} "
                f"{COLOR['mgr']}[{mgr}]{COLOR['reset']} "
                f"{state_color}({state_txt}){COLOR['reset']}"
            )

            # enfants directs
            prefix = path + "/" if path else ""
            children = [
                p for p in self.tree
                if p.startswith(prefix)
                and p.count("/") == path.count("/") + 1
                and p != path
            ]

            for c in sorted(children):
                rec(c, level + 1)
        # --- Création d'une racine virtuelle "" si elle n'existe pas ---
        if "" not in self.tree:
            # On trouve tous les vrais racines : chemins sans "/"
            real_roots = [p for p in self.tree if "/" not in p]

            # Stockage dans l'entrée racine
            self.tree[""] = {
                "widget": self.root,        # widget racine réel
                "manager": None,
                "visible": True,
                "children": real_roots,
            }

        rec("", 0)


if __name__ == "__main__":
    app = AppUi()
    app.mainloop()
