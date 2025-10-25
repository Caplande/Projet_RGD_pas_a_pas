import os
import io
import sqlite3
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from PyPDF2 import PdfReader
import variables_communes as vc
from src.utils import u_sql_3 as u_sql_3


def creer_pdf_pivot_hierarchique_vue_typ(cdtn='1=1', fichier_pdf="Resultats/Historique (par TYP) vue_typ.pdf"):

    # --- Réglages et Définitions ---
    vue_name = "v_t_base_data"
    annee_debut = 2015
    annee_fin = 2025
    exercices = [str(an) for an in range(int(annee_debut), int(annee_fin) + 1)]
    if not os.path.exists(os.path.dirname(fichier_pdf)):
        os.makedirs(os.path.dirname(fichier_pdf))

    # Créer la vue appropriée
    u_sql_3.creer_vue(cdtn=cdtn)  # Crée la vue "v_t_base_data"

    # --- Connexion SQLite ---
    try:
        conn = sqlite3.connect(vc.rep_bdd)
        cur = conn.cursor()

        cur.execute(f"""
            SELECT bat,batrub,typ,base_rep,bat_tit_yp,batrub_tit_yp,typ_tit_yp,exercice, 
                    SUM(montant) AS montant_total -- Calcule la somme des montants
            FROM {vue_name}
            GROUP BY bat,batrub,typ,exercice -- Grouper par toutes les colonnes à conserver
            ORDER BY
                batrub,
                typ,
                exercice;
            """)
        rows = cur.fetchall()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    # Traitement des entêtes et bas de page
    total_pages = {'n': 0}

    def entete(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawCentredString(
            A4[1] / 2, 20.5 * cm, "Copropriété Monica – Historique Relevé général des dépenses")
        canvas.restoreState()

    def pied_de_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        page_num = canvas.getPageNumber()
        total = total_pages['n']
        texte = f"Page {page_num}" if not total else f"Page {page_num} / {total}"
        canvas.drawString(2 * cm, 0.5 * cm, "Conseil syndical Monica")
        canvas.drawRightString(28.5 * cm, 0.5 * cm, texte)
        canvas.restoreState()

    def on_page(canvas, doc):
        entete(canvas, doc)
        pied_de_page(canvas, doc)

    # --- Largeur des colonnes ---
    # 🔑 AJUSTEMENT: Remis à des largeurs plus grandes pour éviter que les titres (taille 8pt) ne wrappent
    col_widths_titres = [2.0*cm, 2.5*cm, 3.0*cm]

    # Largeur restante pour les colonnes de valeurs
    espace_disponible = landscape(A4)[0] - 1.0*cm - sum(col_widths_titres)
    # Assurer une largeur minimale de 1.0cm par colonne de valeur
    largeur_valeur = max(1.0*cm, espace_disponible / len(exercices))

    col_width_valeurs = [largeur_valeur] * len(exercices)
    col_widths = col_widths_titres + col_width_valeurs

    # --- Couleurs des sous-totaux ---
    couleur_total_batrub = colors.whitesmoke
    couleur_total_bat = colors.lightgrey
    # 🔑 FOND TOTAL GÉNÉRAL : Couleur noire
    couleur_total_general = colors.black

    # --- Préparation des titres complexes et Structuration des données ---
    data_hier = {}
    # Carte pour stocker les titres d'affichage formatés basés sur les codes
    prefix_map = {}

    # Initialisation du dictionnaire pour le total général par exercice
    grand_total = {ex: 0.0 for ex in exercices}

    # 🔑 MODIFICATION: Ajout de 'base_rep_code' dans l'unpacking
    for bat_code, batrub_code, typ_code, base_rep_code, bat_tit, batrub_tit, typ_tit, ex, montant in rows:
        bat_key = str(bat_tit) if bat_tit is not None else ""
        rub_key = str(batrub_tit) if batrub_tit is not None else ""
        typ_key = str(typ_tit) if typ_tit is not None else ""

        # S'assurer que les codes et titres sont des chaînes (pour la concaténation)
        bat_code = str(bat_code if bat_code is not None else "")
        batrub_code = str(batrub_code if batrub_code is not None else "")
        typ_code = str(typ_code if typ_code is not None else "")
        base_rep_code = str(
            base_rep_code if base_rep_code is not None else "")

        # 1. Bat Title: bat - batrub_tit (prend la première combinaison trouvée pour ce bat_key)
        if bat_key and bat_key not in prefix_map:
            prefix_map[bat_key] = f"{bat_code} - {rub_key}"

        # 2. Batrub Title: batrub - batrub_tit (base_rep)
        if rub_key and rub_key not in prefix_map:
            prefix_map[rub_key] = f"{batrub_code} - {rub_key} ({base_rep_code})"

        # 3. Typ Title: typ - typ_tit
        if typ_key and typ_key not in prefix_map:
            prefix_map[typ_key] = f"{typ_code} - {typ_key}"

        # Tenter de convertir le montant en float, sinon utiliser 0.0
        try:
            # 🔑 CORRECTION: Conversion explicite en float pour garantir l'addition numérique
            float_montant = float(montant) if montant is not None else 0.0
        except (ValueError, TypeError):
            print(
                f"⚠️ Avertissement : Montant '{montant}' pour exercice '{ex}' n'est pas un nombre. Traité comme 0.0.")
            float_montant = 0.0

        # Structuration de la hiérarchie pour l'agrégation
        data_hier.setdefault(bat_key, {}).setdefault(
            rub_key, {}).setdefault(typ_key, {})[ex] = float_montant

        # Accumulation du Total Général (en float)
        grand_total[ex] += float_montant

    # --- Styles des Paragraphes ---
    styles = getSampleStyleSheet()

    # Styles pour les titres (Taille 8)
    style_bat = ParagraphStyle(
        # spaceAfter réduit
        'bat', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, spaceAfter=0)
    style_batrub = ParagraphStyle(
        'batrub', parent=styles['Normal'], leftIndent=2, fontName='Helvetica-Bold', fontSize=8)
    style_typ = ParagraphStyle(
        'typ', parent=styles['Normal'], leftIndent=4, fontName='Helvetica', fontSize=8)

    # Alignement à droite (2 = TA_RIGHT) pour les titres de totaux
    style_total = ParagraphStyle(
        # 2 = TA_RIGHT
        'total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2)

    # 🔑 SUPPRESSION : style_grand_total_titre est retiré car nous utilisons maintenant des chaînes simples
    # 🔑 AJUSTEMENT TAILLE : Augmenté à 7pt pour une meilleure visibilité
    style_valeur = ParagraphStyle(
        # 2 = TA_RIGHT
        'valeur', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=2, leading=6)

    # CORRECTION: Utiliser 2 (TA_RIGHT) pour l'alignement des valeurs de totaux (Taille 8)
    style_valeur_total = ParagraphStyle(
        # 2 = TA_RIGHT
        'valeur_total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2)

    # 🔑 SUPPRESSION : style_valeur_grand_total est retiré car nous utilisons maintenant des chaînes simples

    # --- Remplissage du Tableau 'data' ---
    data = [["Bâtiment", "BATRUB", "Type"] + exercices]

    for bat_key, rubs in data_hier.items():
        # 🔑 MODIFICATION: Utiliser prefix_map pour le titre Bâtiment
        display_bat_title = prefix_map.get(bat_key, bat_key)
        data.append([Paragraph(display_bat_title, style_bat)] +
                    [""] * (2 + len(exercices)))

        total_bat = {ex: 0.0 for ex in exercices}

        for rub_key, typs in rubs.items():
            # 🔑 MODIFICATION: Utiliser prefix_map pour le titre batrub
            display_rub_title = prefix_map.get(rub_key, rub_key)
            data.append(["", Paragraph(display_rub_title, style_batrub)] +
                        [""] * (1 + len(exercices)))
            total_rub = {ex: 0.0 for ex in exercices}

            for typ_key, montants in typs.items():

                # 🔑 MODIFICATION: Utiliser prefix_map pour le titre Type
                display_typ_title = prefix_map.get(typ_key, typ_key)

                # Ligne 1 : TITRE 'Typ'
                ligne_titre_typ = ["", "", Paragraph(
                    display_typ_title, style_typ)] + [""] * len(exercices)
                data.append(ligne_titre_typ)

                # Ligne 2 : DÉTAIL pour le 'Typ' (avec les valeurs)
                ligne_detail_typ = ["", "", ""]

                for ex in exercices:
                    val = montants.get(ex, 0.0)
                    val_texte = f"{val:,.2f}".replace(
                        ",", " ").replace(".", ",")
                    # Encapsuler la valeur avec style_valeur (taille 7)
                    ligne_detail_typ.append(
                        Paragraph(val_texte, style_valeur))

                    total_rub[ex] += val
                    total_bat[ex] += val
                data.append(ligne_detail_typ)

            # Ligne sous-total batrub
            ligne_total_rub = ["", Paragraph(
                f"Total {rub_key}", style_total), ""]
            for ex in exercices:
                val = total_rub[ex]
                val_texte = f"{val:,.2f}".replace(
                    ",", " ").replace(".", ",")
                # Encapsuler la valeur avec style_valeur_total
                ligne_total_rub.append(
                    Paragraph(val_texte, style_valeur_total))
            data.append(ligne_total_rub)

        # Ligne sous-total bat
        ligne_total_bat = [
            Paragraph(f"Total {bat_key}", style_total), "", ""]
        for ex in exercices:
            val = total_bat[ex]
            val_texte = f"{val:,.2f}".replace(",", " ").replace(".", ",")
            # Encapsuler la valeur avec style_valeur_total
            ligne_total_bat.append(
                Paragraph(val_texte, style_valeur_total))
        data.append(ligne_total_bat)

    # --- Ajout de la ligne du TOTAL GÉNÉRAL (Maintenant avec des chaînes simples) ---
    titre_grand_total_text = "TOTAL GÉNÉRAL"

    # 🔑 MODIFICATION CRITIQUE : Utilisation de chaînes simples pour garantir que TableStyle s'applique
    ligne_grand_total = [titre_grand_total_text, "", ""]

    for ex in exercices:
        val = grand_total[ex]

        # 🔑 AFFICHAGE VALEUR : Afficher "--" si la valeur est proche de zéro
        if abs(val) < 0.005:
            val_display_text = "--"
        else:
            val_display_text = f"{val:,.2f}".replace(
                ",", " ").replace(".", ",")

        # Ajout de la valeur en tant que simple chaîne
        ligne_grand_total.append(val_display_text)

    data.append(ligne_grand_total)
    # --- FIN MODIFICATION ---

    # --- Création et Styles du Tableau ---
    # repeatRows=1 assure la répétition de la ligne d'en-tête (Exercices)
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Déterminer l'index de la dernière ligne (Total Général)
    index_derniere_ligne = len(data) - 1

    style_table = TableStyle([
        # Styles généraux
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
        # L'alignement des colonnes de valeurs (à partir de l'index 3) est géré ici
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

        # AJUSTEMENT DU PADDING pour laisser ReportLab calculer la hauteur minimale sans couper
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),  # 0.5pt de padding en haut
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),  # 0.5pt de padding en bas
    ])

    # Application du SPAN et de la couleur (logique inchangée)
    for i, row in enumerate(data):
        # 1. Ligne Titre Bâtiment
        # La dernière ligne (Total Général) doit être exclue de cette logique
        if i == index_derniere_ligne:
            continue

        if isinstance(row[0], Paragraph) and row[1] == "" and row[2] == "" and not row[0].getPlainText().startswith("Total "):
            style_table.add('SPAN', (0, i), (-1, i))

        # 2. Ligne Titre batrub
        elif row[0] == "" and isinstance(row[1], Paragraph) and row[2] == "" and not row[1].getPlainText().startswith("Total "):
            style_table.add('SPAN', (1, i), (-1, i))

        # 3. Ligne Titre Typ
        elif row[0] == "" and row[1] == "" and isinstance(row[2], Paragraph):
            style_table.add('SPAN', (2, i), (-1, i))

        # Total BatRub
        if isinstance(row[1], Paragraph) and row[1].getPlainText().startswith("Total "):
            style_table.add('BACKGROUND', (0, i),
                            (-1, i), couleur_total_batrub)
            if row[2] == "":  # Fusionne le titre si la colonne Type est vide
                style_table.add('SPAN', (0, i), (2, i))
            else:  # Sinon, fusionne les deux premières colonnes
                style_table.add('SPAN', (0, i), (1, i))

        # Total Bat
        elif isinstance(row[0], Paragraph) and row[0].getPlainText().startswith("Total "):
            style_table.add('BACKGROUND', (0, i),
                            (-1, i), couleur_total_bat)
            style_table.add('SPAN', (0, i), (2, i))

    # 🔑 FOND NOIR & TEXTE BLANC (Maintenant que la ligne contient des chaînes simples)
    style_table.add('BACKGROUND', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), couleur_total_general)
    # Fusionne les colonnes de titre
    style_table.add('SPAN', (0, index_derniere_ligne),
                    (2, index_derniere_ligne))

    # 🔑 NOUVELLES COMMANDES CRITIQUES : Définition des propriétés de texte pour les chaînes simples
    style_table.add('TEXTCOLOR', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), colors.white)
    style_table.add('FONTNAME', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), 'Helvetica-Bold')
    style_table.add('FONTSIZE', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), 10)

    # Alignement du titre TOTAL GÉNÉRAL à droite (colonnes 0, 1, 2 fusionnées)
    style_table.add('ALIGN', (0, index_derniere_ligne),
                    (2, index_derniere_ligne), 'RIGHT')
    # Alignement des valeurs à droite (à partir de la colonne 3)
    style_table.add('ALIGN', (3, index_derniere_ligne),
                    (-1, index_derniere_ligne), 'RIGHT')

    table.setStyle(style_table)

# Préaration de la création du pdf

    try:
        # --- Première passe pour compter le nombre total de pages ---
        buffer_temp = io.BytesIO()
        temp_doc = SimpleDocTemplate(
            buffer_temp,
            pagesize=landscape(A4),
            leftMargin=0.5*cm,
            rightMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        temp_doc.build([table, Spacer(1, 0.2*cm)],
                       onFirstPage=on_page, onLaterPages=on_page)

        # Calcul du nombre de pages
        # On met l'index de buffer_temp à l'origine
        buffer_temp.seek(0)
        reader = PdfReader(buffer_temp)
        page_count = len(reader.pages)
        total_pages['n'] = page_count

        # --- Deuxième passe pour créer le pdf ---

        final_doc = SimpleDocTemplate(
            fichier_pdf,
            pagesize=landscape(A4),
            leftMargin=0.5*cm,
            rightMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        final_doc.build([table, Spacer(1, 0.2*cm)],
                        onFirstPage=on_page, onLaterPages=on_page)

        buffer_temp.close()
    except Exception as e:
        print("Erreur PDF :", e)

    print(f"✅ Fichier PDF généré : {fichier_pdf}")


def creer_pdf_pivot_hierarchique_vue_groupe(cdtn='1=1', fichier_pdf="Resultats/Historique (par groupe) vue_groupe.pdf"):

    # --- Réglages et Définitions ---
    vue_name = "v_t_base_data"
    annee_debut = 2015
    annee_fin = 2025
    exercices = [str(an) for an in range(int(annee_debut), int(annee_fin) + 1)]
    if not os.path.exists(os.path.dirname(fichier_pdf)):
        os.makedirs(os.path.dirname(fichier_pdf))

    # Créer la vue appropriée
    u_sql_3.creer_vue(cdtn=cdtn)  # Crée la vue "v_t_base_data"

    # --- Connexion SQLite ---
    try:
        conn = sqlite3.connect(vc.rep_bdd)
        cur = conn.cursor()

        cur.execute(f"""
            SELECT bat,batrub,groupe,base_rep,bat_tit_yp,batrub_tit_yp,exercice, 
                    SUM(montant) AS montant_total -- Calcule la somme des montants
            FROM {vue_name}
            GROUP BY bat,batrub,groupe,exercice -- Grouper par toutes les colonnes à conserver
            ORDER BY
                batrub,
                groupe,
                exercice;
            """)
        rows = cur.fetchall()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    # Traitement des entêtes et bas de page
    total_pages = {'n': 0}

    def entete(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawCentredString(
            A4[1] / 2, 20.5 * cm, "Copropriété Monica – Historique Relevé général des dépenses")
        canvas.restoreState()

    def pied_de_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        page_num = canvas.getPageNumber()
        total = total_pages['n']
        texte = f"Page {page_num}" if not total else f"Page {page_num} / {total}"
        canvas.drawString(2 * cm, 0.5 * cm, "Conseil syndical Monica")
        canvas.drawRightString(28.5 * cm, 0.5 * cm, texte)
        canvas.restoreState()

    def on_page(canvas, doc):
        entete(canvas, doc)
        pied_de_page(canvas, doc)

    # --- Largeur des colonnes ---
    # 🔑 AJUSTEMENT: Remis à des largeurs plus grandes pour éviter que les titres (taille 8pt) ne wrappent
    col_widths_titres = [2.0*cm, 2.5*cm, 3.0*cm]

    # Largeur restante pour les colonnes de valeurs
    espace_disponible = landscape(A4)[0] - 1.0*cm - sum(col_widths_titres)
    # Assurer une largeur minimale de 1.0cm par colonne de valeur
    largeur_valeur = max(1.0*cm, espace_disponible / len(exercices))

    col_width_valeurs = [largeur_valeur] * len(exercices)
    col_widths = col_widths_titres + col_width_valeurs

    # --- Couleurs des sous-totaux ---
    couleur_total_batrub = colors.whitesmoke
    couleur_total_bat = colors.lightgrey
    # 🔑 FOND TOTAL GÉNÉRAL : Couleur noire
    couleur_total_general = colors.black

    # --- Préparation des titres complexes et Structuration des données ---
    data_hier = {}
    # Carte pour stocker les titres d'affichage formatés basés sur les codes
    prefix_map = {}

    # Initialisation du dictionnaire pour le total général par exercice
    grand_total = {ex: 0.0 for ex in exercices}

    # 🔑 MODIFICATION: Ajout de 'base_rep_code' dans l'unpacking
    for bat_code, batrub_code, groupe_code, base_rep_code, bat_tit, batrub_tit, ex, montant in rows:
        bat_key = str(bat_tit) if bat_tit is not None else ""
        rub_key = str(batrub_tit) if batrub_tit is not None else ""
        groupe_key = str(groupe_code) if groupe_code is not None else ""

        # S'assurer que les codes et titres sont des chaînes (pour la concaténation)
        bat_code = str(bat_code if bat_code is not None else "")
        batrub_code = str(batrub_code if batrub_code is not None else "")
        groupe_code = str(groupe_code if groupe_code is not None else "")
        base_rep_code = str(
            base_rep_code if base_rep_code is not None else "")

        # 1. Bat Title: bat - batrub_tit (prend la première combinaison trouvée pour ce bat_key)
        if bat_key not in prefix_map:
            prefix_map[bat_key] = f"{bat_code} - {rub_key}"

        # 2. Batrub Title: batrub - batrub_tit (base_rep)
        if rub_key not in prefix_map:
            prefix_map[rub_key] = f"{batrub_code} - {rub_key} ({base_rep_code})"

        # 3. Typ Title: groupe
        if groupe_key not in prefix_map:
            prefix_map[groupe_key] = f"{groupe_code}"

        # Tenter de convertir le montant en float, sinon utiliser 0.0
        try:
            # 🔑 CORRECTION: Conversion explicite en float pour garantir l'addition numérique
            float_montant = float(montant) if montant is not None else 0.0
        except (ValueError, TypeError):
            print(
                f"⚠️ Avertissement : Montant '{montant}' pour exercice '{ex}' n'est pas un nombre. Traité comme 0.0.")
            float_montant = 0.0

        # Structuration de la hiérarchie pour l'agrégation
        data_hier.setdefault(bat_key, {}).setdefault(
            rub_key, {}).setdefault(groupe_key, {})[ex] = float_montant

        # Accumulation du Total Général (en float)
        grand_total[ex] += float_montant

    # --- Styles des Paragraphes ---
    styles = getSampleStyleSheet()

    # Styles pour les titres (Taille 8)
    style_bat = ParagraphStyle(
        # spaceAfter réduit
        'bat', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, spaceAfter=0)
    style_batrub = ParagraphStyle(
        'batrub', parent=styles['Normal'], leftIndent=2, fontName='Helvetica-Bold', fontSize=8)
    style_groupe = ParagraphStyle(
        'groupe', parent=styles['Normal'], leftIndent=4, fontName='Helvetica', fontSize=8)

    # Alignement à droite (2 = TA_RIGHT) pour les titres de totaux
    style_total = ParagraphStyle(
        # 2 = TA_RIGHT
        'total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2)

    # 🔑 SUPPRESSION : style_grand_total_titre est retiré car nous utilisons maintenant des chaînes simples
    # 🔑 AJUSTEMENT TAILLE : Augmenté à 7pt pour une meilleure visibilité
    style_valeur = ParagraphStyle(
        # 2 = TA_RIGHT
        'valeur', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=2, leading=6)

    # CORRECTION: Utiliser 2 (TA_RIGHT) pour l'alignement des valeurs de totaux (Taille 8)
    style_valeur_total = ParagraphStyle(
        # 2 = TA_RIGHT
        'valeur_total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=2)

    # 🔑 SUPPRESSION : style_valeur_grand_total est retiré car nous utilisons maintenant des chaînes simples

    # --- Remplissage du Tableau 'data' ---
    data = [["Bâtiment", "BATRUB", "Type"] + exercices]

    for bat_key, rubs in data_hier.items():
        # 🔑 MODIFICATION: Utiliser prefix_map pour le titre Bâtiment
        display_bat_title = prefix_map.get(bat_key, bat_key)
        data.append([Paragraph(display_bat_title, style_bat)] +
                    [""] * (2 + len(exercices)))

        total_bat = {ex: 0.0 for ex in exercices}

        for rub_key, groupes in rubs.items():
            # 🔑 MODIFICATION: Utiliser prefix_map pour le titre batrub
            display_rub_title = prefix_map.get(rub_key, rub_key)
            data.append(["", Paragraph(display_rub_title, style_batrub)] +
                        [""] * (1 + len(exercices)))
            total_rub = {ex: 0.0 for ex in exercices}

            for groupe_key, montants in groupes.items():

                # 🔑 MODIFICATION: Utiliser prefix_map pour le titre Type
                display_groupe_title = prefix_map.get(groupe_key, groupe_key)

                # Ligne 1 : TITRE 'Typ'
                ligne_titre_groupe = ["", "", Paragraph(
                    display_groupe_title, style_groupe)] + [""] * len(exercices)
                data.append(ligne_titre_groupe)

                # Ligne 2 : DÉTAIL pour le 'Typ' (avec les valeurs)
                ligne_detail_groupe = ["", "", ""]

                for ex in exercices:
                    val = montants.get(ex, 0.0)
                    val_texte = f"{val:,.2f}".replace(
                        ",", " ").replace(".", ",")
                    # Encapsuler la valeur avec style_valeur (taille 7)
                    ligne_detail_groupe.append(
                        Paragraph(val_texte, style_valeur))

                    total_rub[ex] += val
                    total_bat[ex] += val
                data.append(ligne_detail_groupe)

            # Ligne sous-total batrub
            ligne_total_rub = ["", Paragraph(
                f"Total {rub_key}", style_total), ""]
            for ex in exercices:
                val = total_rub[ex]
                val_texte = f"{val:,.2f}".replace(
                    ",", " ").replace(".", ",")
                # Encapsuler la valeur avec style_valeur_total
                ligne_total_rub.append(
                    Paragraph(val_texte, style_valeur_total))
            data.append(ligne_total_rub)

        # Ligne sous-total bat
        ligne_total_bat = [
            Paragraph(f"Total {bat_key}", style_total), "", ""]
        for ex in exercices:
            val = total_bat[ex]
            val_texte = f"{val:,.2f}".replace(",", " ").replace(".", ",")
            # Encapsuler la valeur avec style_valeur_total
            ligne_total_bat.append(
                Paragraph(val_texte, style_valeur_total))
        data.append(ligne_total_bat)

    # --- Ajout de la ligne du TOTAL GÉNÉRAL (Maintenant avec des chaînes simples) ---
    titre_grand_total_text = "TOTAL GÉNÉRAL"

    # 🔑 MODIFICATION CRITIQUE : Utilisation de chaînes simples pour garantir que TableStyle s'applique
    ligne_grand_total = [titre_grand_total_text, "", ""]

    for ex in exercices:
        val = grand_total[ex]

        # 🔑 AFFICHAGE VALEUR : Afficher "--" si la valeur est proche de zéro
        if abs(val) < 0.005:
            val_display_text = "--"
        else:
            val_display_text = f"{val:,.2f}".replace(
                ",", " ").replace(".", ",")

        # Ajout de la valeur en tant que simple chaîne
        ligne_grand_total.append(val_display_text)

    data.append(ligne_grand_total)
    # --- FIN MODIFICATION ---

    # --- Création et Styles du Tableau ---
    # repeatRows=1 assure la répétition de la ligne d'en-tête (Exercices)
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # Déterminer l'index de la dernière ligne (Total Général)
    index_derniere_ligne = len(data) - 1

    style_table = TableStyle([
        # Styles généraux
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
        # L'alignement des colonnes de valeurs (à partir de l'index 3) est géré ici
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

        # AJUSTEMENT DU PADDING pour laisser ReportLab calculer la hauteur minimale sans couper
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),  # 0.5pt de padding en haut
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),  # 0.5pt de padding en bas
    ])

    # Application du SPAN et de la couleur (logique inchangée)
    for i, row in enumerate(data):
        # 1. Ligne Titre Bâtiment
        # La dernière ligne (Total Général) doit être exclue de cette logique
        if i == index_derniere_ligne:
            continue

        if isinstance(row[0], Paragraph) and row[1] == "" and row[2] == "" and not row[0].getPlainText().startswith("Total "):
            style_table.add('SPAN', (0, i), (-1, i))

        # 2. Ligne Titre batrub
        elif row[0] == "" and isinstance(row[1], Paragraph) and row[2] == "" and not row[1].getPlainText().startswith("Total "):
            style_table.add('SPAN', (1, i), (-1, i))

        # 3. Ligne Titre Typ
        elif row[0] == "" and row[1] == "" and isinstance(row[2], Paragraph):
            style_table.add('SPAN', (2, i), (-1, i))

        # Total BatRub
        if isinstance(row[1], Paragraph) and row[1].getPlainText().startswith("Total "):
            style_table.add('BACKGROUND', (0, i),
                            (-1, i), couleur_total_batrub)
            if row[2] == "":  # Fusionne le titre si la colonne Type est vide
                style_table.add('SPAN', (0, i), (2, i))
            else:  # Sinon, fusionne les deux premières colonnes
                style_table.add('SPAN', (0, i), (1, i))

        # Total Bat
        elif isinstance(row[0], Paragraph) and row[0].getPlainText().startswith("Total "):
            style_table.add('BACKGROUND', (0, i),
                            (-1, i), couleur_total_bat)
            style_table.add('SPAN', (0, i), (2, i))

    # 🔑 FOND NOIR & TEXTE BLANC (Maintenant que la ligne contient des chaînes simples)
    style_table.add('BACKGROUND', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), couleur_total_general)
    # Fusionne les colonnes de titre
    style_table.add('SPAN', (0, index_derniere_ligne),
                    (2, index_derniere_ligne))

    # 🔑 NOUVELLES COMMANDES CRITIQUES : Définition des propriétés de texte pour les chaînes simples
    style_table.add('TEXTCOLOR', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), colors.white)
    style_table.add('FONTNAME', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), 'Helvetica-Bold')
    style_table.add('FONTSIZE', (0, index_derniere_ligne),
                    (-1, index_derniere_ligne), 10)

    # Alignement du titre TOTAL GÉNÉRAL à droite (colonnes 0, 1, 2 fusionnées)
    style_table.add('ALIGN', (0, index_derniere_ligne),
                    (2, index_derniere_ligne), 'RIGHT')
    # Alignement des valeurs à droite (à partir de la colonne 3)
    style_table.add('ALIGN', (3, index_derniere_ligne),
                    (-1, index_derniere_ligne), 'RIGHT')

    table.setStyle(style_table)

# Préaration de la création du pdf

    try:
        # --- Première passe pour compter le nombre total de pages ---
        buffer_temp = io.BytesIO()
        temp_doc = SimpleDocTemplate(
            buffer_temp,
            pagesize=landscape(A4),
            leftMargin=0.5*cm,
            rightMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        temp_doc.build([table, Spacer(1, 0.2*cm)],
                       onFirstPage=on_page, onLaterPages=on_page)

        # Calcul du nombre de pages
        # On met l'index de buffer_temp à l'origine
        buffer_temp.seek(0)
        reader = PdfReader(buffer_temp)
        page_count = len(reader.pages)
        total_pages['n'] = page_count

        # --- Deuxième passe pour créer le pdf ---

        final_doc = SimpleDocTemplate(
            fichier_pdf,
            pagesize=landscape(A4),
            leftMargin=0.5*cm,
            rightMargin=0.5*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )
        final_doc.build([table, Spacer(1, 0.2*cm)],
                        onFirstPage=on_page, onLaterPages=on_page)

        buffer_temp.close()
    except Exception as e:
        print("Erreur PDF :", e)

    print(f"✅ Fichier PDF généré : {fichier_pdf}")


if __name__ == "__main__":
    # u_sql_3.creer_vue_v_t_base_data(cdtn="groupe='Honoraires Syndic'")
    # u_sql_3.creer_vue_v_t_base_data()
    # calculs = pivot_cumuls()
    # resultats_sql = calculs["resultats"]
    # noms_colonnes = calculs["noms_colonnes"]
    creer_pdf_pivot_hierarchique_vue_typ(cdtn="groupe='Honoraires Syndic'")
    creer_pdf_pivot_hierarchique_vue_groupe(cdtn="groupe='Honoraires Syndic'")
    # creer_pdf_pivot_hierarchique_par_groupe()
    # resultats_sql, noms_colonnes, nom_fichier="pivot_cumules_correct.pdf")
