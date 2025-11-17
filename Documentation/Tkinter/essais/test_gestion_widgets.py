from re import X
import tkinter as tk
from tkinter import ttk
from tkinter import TclError


widget_names = {}


class WidgetTreeManager:
    """ 
    Gère et visualise la hiérarchie des widgets Tkinter (Pack, Grid, Place), 
    avec des fonctionnalités pour afficher, masquer et imprimer l'état.
    """

    def __init__(self, widget, name_mapping=None):
        self.root = widget
        self.tree = {}    # path → {widget, manager, info}
        # 🔑 Stockage du dictionnaire de mappage de noms
        self.name_mapping = name_mapping if name_mapping is not None else {}
        self._build_tree()
        self._bind_events()

    # ============================================================
    # AUTO-REFRESH
    # ============================================================
    def _bind_events(self):
        """
        Active un système global d'écoute sur les événements majeurs (Map, Unmap, Configure, Destroy) 
        pour maintenir le tree à jour automatiquement.
        """
        root = self.root.winfo_toplevel()

        # Attention: l'erreur TclError: window ".!frame" isn't packed est souvent levée ici
        # car _build_tree() est appelé à chaque événement.
        # Il faut que _build_tree gère correctement les widgets non packés/gridés/placés.
        root.bind_all("<Map>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Unmap>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Configure>", lambda e: self._build_tree(), add="+")
        root.bind_all("<Destroy>", lambda e: self._build_tree(), add="+")

    # ============================================================
    # BUILD TREE
    # ============================================================
    def _build_tree(self):
        """Reconstruit totalement le tree en conservant l'ancien manager si le widget est masqué."""

        # Sauvegarde de l'arbre existant pour récupérer l'ancien manager
        old_tree = self.tree.copy()
        self.tree.clear()

        def recurse(widget, path):
            # 1. --- nom logique pour le chemin ---
            if widget in self.name_mapping:
                name = self.name_mapping[widget]
            else:
                name = widget.winfo_name()

            fullpath = f"{path}/{name}" if path else name

            # 2. --- infos manager ACTUELLES ---
            current_mgr = widget.winfo_manager()
            info = {}

            if current_mgr == "pack":
                try:
                    info = widget.pack_info()
                except TclError:
                    pass
            elif current_mgr == "grid":
                try:
                    info = widget.grid_info()
                except TclError:
                    pass
            elif current_mgr == "place":
                try:
                    info = widget.place_info()
                except TclError:
                    pass

            # 3. --- CONSERVATION DU MANAGER ---
            # Tente de récupérer le manager stocké précédemment
            existing_mgr = old_tree.get(fullpath, {}).get("manager", "")

            # Utilise le manager actuel si le widget est visible, sinon utilise le manager stocké
            mgr_to_store = current_mgr if current_mgr else existing_mgr

            self.tree[fullpath] = {
                "widget": widget,
                "manager": mgr_to_store,
                "info": info
            }

            for child in widget.winfo_children():
                recurse(child, fullpath)

        # La récursivité commence à partir de la racine fournie
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
        # Pour restaurer, on utilise le widget lui-même (et non son parent, correction de mon ancien code)
        if mgr == "pack":
            widget.pack(**info)
        elif mgr == "grid":
            widget.grid(**info)
        elif mgr == "place":
            widget.place(**info)
        else:
            raise RuntimeError(f"Manager inconnu ou non stocké : {mgr}")

    def _descendants(self, path):
        """Retourne tous les chemins descendants récursifs."""
        prefix = path + "/" if path else ""
        return [
            p for p in self.tree
            if p.startswith(prefix) and p != path
        ]

    def _toggle_single(self, path, visible=True):
        """Affiche ou masque uniquement un widget donné, sans modifier ses enfants."""
        # Reconstruire l'arbre interne (assure que les infos sont à jour)
        self._build_tree()

        key = self._resolve(path)
        if key is None:
            raise KeyError(f"[WTM.toggle_single] Widget non trouvé : {path}")

        entry = self.tree[key]
        widget = entry["widget"]
        mgr = entry["manager"]
        info = entry["info"]

        # Si le manager n'a pas été déterminé lors du build (mgr == ""), on essaie de le déduire
        if not mgr:
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
                            f"Impossible de déterminer le manager de {path}")

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

        # 2) match sur les segments (permet de trouver 'label1' dans '/frame1/label1')
        for key in self.tree.keys():
            # Cherche si le nom est le dernier segment du chemin
            if key.split("/")[-1] == p:
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
        key = self._resolve(path)
        if key is None:
            raise KeyError(f"[WTM.get] Chemin non trouvé : {path}")
        return self.tree[key]["widget"]

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

            # nom python si dispo (Utilisation de self.name_mapping)
            if widget in self.name_mapping:
                name = self.name_mapping[widget]
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

        # --- L'arbre est construit par recurse(self.root, ""), le plus souvent "" existe
        if self.root.winfo_name() not in self.tree:
            self.tree[""] = {
                "widget": self.root,
                "manager": self.root.winfo_manager() or "root",
                "info": {}
            }

        rec(self.root.winfo_name() or "", 0)


def set_widget_names(widget, name):
    widget_names[widget] = name
    return widget


root = tk.Tk()
root.geometry("1200x800")
root.title("Fenêtre test")


# --- Cadre 1 (au-dessus) ---
fr1_n1 = tk.Frame(root, bg="blue")
fr1_n1.pack(side=tk.TOP, fill="both", expand=True)
set_widget_names(fr1_n1, "fr1_n1")

lb_fr1_n1 = tk.Label(fr1_n1, text="Label de fr1_n1", bg="darkorchid4")
lb_fr1_n1.pack(expand=True)
set_widget_names(lb_fr1_n1, "lb1_fr1_n1")

# --- Cadre 2 (en bas) ---
fr2_n1 = tk.Frame(root, height=100, bg="orange")
fr2_n1.pack(side=tk.BOTTOM, fill="x")
fr2_n1.pack_propagate(False)
set_widget_names(fr2_n1, "fr2_n1")

fr1_n2 = tk.Frame(fr2_n1, height=20, bg="green")
fr1_n2.pack(side=tk.TOP, fill="x", padx=5, pady=5)
set_widget_names(fr1_n2, "fr1_n2")

fr2_n2 = tk.Frame(fr2_n1, bg="red")
fr2_n2.pack(side=tk.BOTTOM, fill="both", expand=True)
set_widget_names(fr2_n2, "fr2_n2")


root.mainloop()
