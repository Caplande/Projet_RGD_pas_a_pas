import os
import sqlite3
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
import variables_communes as vc
import textwrap
import re


def creer_pdf_pivot_hierarchique_V1(fichier_pdf="Resultats/Historique 1.pdf"):
    """
    Export hiérarchie -> PDF (page paysage).
    - db_path : chemin vers la DB sqlite
    - output_pdf : chemin/nom du PDF de sortie
    - annee_debut / annee_fin : bornes incluses
    - col_widths_titres : tuple largeur (bat, batrub, typ) en points (ex: (4*cm,3*cm,3*cm))
    - col_width_an : largeur d'une colonne exercice
    """
    # Réglages
    vue_name = "v_t_base_data"
    annee_debut = 2015
    annee_fin = 2025
    exercices = [str(an) for an in range(int(annee_debut), int(annee_fin) + 1)]
    # --- Largeur des colonnes ---
    col_widths_titres = [1*cm, 1*cm, 1*cm]
    col_width_valeurs = [1.5*cm]*len(exercices)
    col_widths = col_widths_titres + col_width_valeurs

    # --- Lecture et agrégation ---
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    cur.execute("""
        SELECT bat_tit_yp, batrub_tit_yp, typ_tit_yp, exercice, SUM(montant)
        FROM v_t_base_data
        GROUP BY bat_tit_yp, batrub_tit_yp, typ_tit_yp, exercice
        ORDER BY bat_tit_yp, batrub_tit_yp, typ_tit_yp, exercice
    """)
    rows = cur.fetchall()
    conn.close()

    data_hier = {}
    for bat, rub, typ, exo, montant in rows:
        data_hier.setdefault(bat, {}).setdefault(
            rub, {}).setdefault(typ, {})[exo] = montant

      # --- construction du tableau
    data = [["Bâtiment", "Rubrique", "Type"] + exercices]

    for bat, rubs in data_hier.items():
        # ligne titre Bâtiment : texte brut fusionné sur toute la largeur
        data.append([f"{bat}"] + [""] * (2 + len(exercices)))

        for rub, typs in rubs.items():
            # ligne titre Rubrique (à partir de col 2)
            data.append(["", f"{rub}"] + [""] * (1 + len(exercices)))

            for typ, montants in typs.items():
                # ligne titre Type (col 3)
                data.append(["", "", f"{typ}"] + [""] * len(exercices))
                # ligne de montants
                ligne = ["", "", ""]
                for exo in exercices:
                    val = montants.get(exo)
                    ligne.append(f"{val:,.2f}".replace(",", " ").replace(
                        ".", ",")) if val else ligne.append("")
                data.append(ligne)

    # --- largeurs
    table = Table(data, colWidths=col_widths, repeatRows=1)

    # --- style
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("SPAN", (0, len(data_hier)+1), (-1, len(data_hier)+1)),
        # styles de titres
        ("FONTNAME", (0, 1), (2, -1), "Helvetica-Bold"),
        ("SPAN", (0, 1), (-1, 1)),  # bat sur toute la ligne
        ("SPAN", (1, 2), (-1, 2)),  # rub sur toute la ligne (sauf col1)
        ("SPAN", (2, 3), (-1, 3)),  # typ sur toute la ligne (sauf col1,2)
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))

    # --- pdf
    doc = SimpleDocTemplate(fichier_pdf, pagesize=landscape(A4))
    doc.build([table])

    print(f"✅ PDF créé : {fichier_pdf}")

    # Réglages
    vue_name = "v_t_base_data"
    annee_debut = 2015
    annee_fin = 2025
    exercices = [str(an) for an in range(int(annee_debut), int(annee_fin) + 1)]
    # --- Largeur des colonnes ---
    col_widths_titres = [0.5*cm, 0.5*cm, 0.5*cm]
    col_width_valeurs = [1*cm]*len(exercices)
    col_widths = col_widths_titres + col_width_valeurs
    # --- Couleurs des sous-totaux ---
    couleur_total_batrub = colors.whitesmoke
    couleur_total_bat = colors.lightgrey

    # Connexion SQLite
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()


def creer_pdf_pivot_hierarchique_V2(fichier_pdf="Resultats/Historique 2.pdf"):

    # --- Réglages et Définitions ---
    vue_name = "v_t_base_data"
    annee_debut = 2015
    annee_fin = 2025
    exercices = [str(an) for an in range(int(annee_debut), int(annee_fin) + 1)]

    # --- Largeur des colonnes (Ajustées pour un A4 Paysage) ---
    # Largeur disponible sur A4 Paysage avec marges 0.5cm : ~28.7 cm

    # Largeurs Titres : Ajustées pour donner plus de place aux textes
    col_widths_titres = [.5*cm, .5*cm, .5*cm]  # Total : 1.5 cm

    # Largeurs Valeurs : Réparties sur le reste de l'espace (~22.2 cm pour ~11 colonnes)
    # 22.2 cm / 11 colonnes = ~2.0 cm
    largeur_valeur = 1.0*cm
    col_width_valeurs = [largeur_valeur] * len(exercices)

    col_widths = col_widths_titres + col_width_valeurs

    # --- Couleurs des sous-totaux ---
    couleur_total_batrub = colors.whitesmoke
    couleur_total_bat = colors.lightgrey

    # --- Connexion SQLite ---
    conn = sqlite3.connect(vc.rep_bdd)
    cur = conn.cursor()

    # Charger les données
    cur.execute(f"""
        SELECT bat, batrub, typ, bat_tit_yp, batrub_tit_yp, typ_tit_yp, exercice, montant
        FROM {vue_name}
        ORDER BY bat, batrub, typ, exercice
    """)
    rows = cur.fetchall()
    conn.close()

    # Structurer les données en hiérarchie
    data_hier = {}
    for bat, batrub, typ, bat_tit, batrub_tit, typ_tit, ex, montant in rows:
        # CORRECTION ANTICIPÉE : Utilisez 'typ_tit' au lieu de 'typ_tit_yp' si c'est la bonne clé
        # Assurez-vous que les clés ne sont pas None
        bat_key = str(bat_tit) if bat_tit is not None else ""
        rub_key = str(batrub_tit) if batrub_tit is not None else ""
        typ_key = str(typ_tit) if typ_tit is not None else ""

        data_hier.setdefault(bat_key, {}).setdefault(
            rub_key, {}).setdefault(typ_key, {})[ex] = montant

    # --- Styles des Paragraphes ---
    styles = getSampleStyleSheet()

    # Réduction de la police et des indentations pour optimiser l'espace
    style_bat = ParagraphStyle(
        'bat', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, spaceAfter=1)

    style_batrub = ParagraphStyle(
        'batrub', parent=styles['Normal'], leftIndent=2, fontName='Helvetica-Bold', fontSize=8)

    style_typ = ParagraphStyle(
        'typ', parent=styles['Normal'], leftIndent=4, fontName='Helvetica', fontSize=8)

    style_total = ParagraphStyle(
        'total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8)

    # Style pour les valeurs numériques (texte normal et alignement à droite)
    style_valeur = ParagraphStyle(
        # 4 = TA_RIGHT
        'valeur', parent=styles['Normal'], fontName='Helvetica', fontSize=5, alignment=4)

    # --- Remplissage du Tableau 'data' ---
    data = [["Bâtiment", "Bâtrub", "Type"] + exercices]

    for bat, rubs in data_hier.items():
        # Ligne titre bâtiment (fusionnée sur toute la largeur)
        data.append([Paragraph(bat, style_bat)] + [""] * (2 + len(exercices)))

        total_bat = {ex: 0 for ex in exercices}

        for rub, typs in rubs.items():
            # Ligne titre bâtrub (fusionnée à partir de la colonne 1)
            data.append(["", Paragraph(rub, style_batrub)] +
                        [""] * (1 + len(exercices)))
            total_rub = {ex: 0 for ex in exercices}

            for typ, montants in typs.items():
                typ_propre = str(typ) if typ is not None else ""

                # Ligne 1 : TITRE 'Typ' (à fusionner)
                # Contient le titre dans la colonne 2 et des "" partout ailleurs
                ligne_titre_typ = ["", "", Paragraph(
                    typ_propre, style_typ)] + [""] * len(exercices)
                data.append(ligne_titre_typ)

                # Ligne 2 : DÉTAIL pour le 'Typ' (avec les valeurs)
                # Colonnes de titre vides, puis les montants
                ligne_detail_typ = ["", "", ""]

                # Ligne 2 : DÉTAIL pour le 'Typ' (avec les valeurs)
                # Colonnes de titre vides, puis les montants
                ligne_detail_typ = ["", "", ""]
                for ex in exercices:
                    val = montants.get(ex, 0.0)
                    # Formattage des valeurs
                    val_texte = f"{val:,.2f}".replace(
                        ",", " ").replace(".", ",")
                    # 💡 CORRECTION : Encapsuler la valeur dans un Paragraph avec
                    ligne_detail_typ.append(Paragraph(val_texte, style_valeur))

                    total_rub[ex] += val
                    total_bat[ex] += val
                data.append(ligne_detail_typ)  # <-- LIGNE AVEC LES DONNÉES

            # Ligne sous-total batrub
            ligne_total_rub = ["", Paragraph(f"Total {rub}", style_total), ""]

            for ex in exercices:
                val = total_rub[ex]
                ligne_total_rub.append(
                    f"{val:,.2f}".replace(",", " ").replace(".", ","))
            data.append(ligne_total_rub)

        # Ligne sous-total bat
        ligne_total_bat = [Paragraph(f"Total {bat}", style_total), "", ""]
        for ex in exercices:
            val = total_bat[ex]
            ligne_total_bat.append(
                f"{val:,.2f}".replace(",", " ").replace(".", ","))
        data.append(ligne_total_bat)

    # --- Création et Styles du Tableau ---
    table = Table(data, colWidths=col_widths)

    style_table = TableStyle([
        # Styles généraux
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),  # Alignement des valeurs
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

        # Réduction du PADDING (Rembourrage) pour réduire l'espace
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ])

    # Application du SPAN (Fusion) et de la couleur
    for i, row in enumerate(data):

        # --- Application du SPAN aux LIGNES de TITRE (Bat, Rub, Typ) ---

        # 1. Ligne Titre Bâtiment (Paragraph en col 0)
        if isinstance(row[0], Paragraph) and row[1] == "" and row[2] == "":
            # Fusionne de col 0 à la fin
            style_table.add('SPAN', (0, i), (-1, i))

        # 2. Ligne Titre Bâtrub (Paragraph en col 1)
        elif row[0] == "" and isinstance(row[1], Paragraph) and row[2] == "":
            # Fusionne de col 1 à la fin
            style_table.add('SPAN', (1, i), (-1, i))

        # 3. Ligne Titre Typ (Paragraph en col 2)
        # S'applique à la ligne de TITRE, pas à la ligne de DÉTAIL suivante
        elif row[0] == "" and row[1] == "" and isinstance(row[2], Paragraph):
            # Fusionne de col 2 à la fin
            style_table.add('SPAN', (2, i), (-1, i))

        # --- Application du SPAN et de la couleur aux LIGNES de TOTAUX ---

        # Total BatRub
        if isinstance(row[1], Paragraph) and str(row[1].getPlainText()).startswith("Total "):
            style_table.add('BACKGROUND', (0, i),
                            (-1, i), couleur_total_batrub)
            # Fusionne la colonne 0 et 1 pour le titre "Total Rub"
            style_table.add('SPAN', (0, i), (1, i))

        # Total Bat
        elif isinstance(row[0], Paragraph) and str(row[0].getPlainText()).startswith("Total "):
            style_table.add('BACKGROUND', (0, i), (-1, i), couleur_total_bat)
            # Fusionne les colonnes 0, 1 et 2 pour le titre "Total Bat"
            style_table.add('SPAN', (0, i), (2, i))

    table.setStyle(style_table)

    # --- Génération du PDF avec Marges Réduites ---
    doc = SimpleDocTemplate(
        fichier_pdf,
        pagesize=landscape(A4),
        leftMargin=0.5*cm,      # Marges réduites
        rightMargin=0.5*cm,     # Marges réduites
        topMargin=0.5*cm,       # Marges réduites
        bottomMargin=0.5*cm     # Marges réduites
    )

    doc.build([table, Spacer(1, 0.2*cm)])
    print(f"✅ Fichier PDF généré : {fichier_pdf}")


def creer_pdf_pivot_hierarchique_V3(fichier_pdf="Resultats/Historique 3.pdf"):

    # --- Réglages et Définitions ---
    vue_name = "v_t_base_data"
    annee_debut = 2015
    annee_fin = 2025
    exercices = [str(an) for an in range(int(annee_debut), int(annee_fin) + 1)]

    # --- Largeur des colonnes ---
    col_widths_titres = [0.5*cm, 0.5*cm, 0.5*cm]

    # Largeur restante pour les colonnes de valeurs
    espace_disponible = landscape(A4)[0] - 1.0*cm - sum(col_widths_titres)
    # Assurer une largeur minimale de 1.0cm par colonne de valeur
    largeur_valeur = max(1.0*cm, espace_disponible / len(exercices)) 

    col_width_valeurs = [largeur_valeur] * len(exercices)
    col_widths = col_widths_titres + col_width_valeurs

    # --- Couleurs des sous-totaux ---
    couleur_total_batrub = colors.whitesmoke
    couleur_total_bat = colors.lightgrey

    # --- Connexion SQLite ---
    try:
        conn = sqlite3.connect(vc.rep_bdd)
        cur = conn.cursor()
        cur.execute(f"""
            SELECT bat, batrub, typ, bat_tit_yp, batrub_tit_yp, typ_tit_yp, exercice, montant
            FROM {vue_name}
            ORDER BY bat, batrub, typ, exercice
        """)
        rows = cur.fetchall()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    # Structurer les données en hiérarchie (Identique à l'original)
    data_hier = {}
    for bat, batrub, typ, bat_tit, batrub_tit, typ_tit, ex, montant in rows:
        bat_key = str(bat_tit) if bat_tit is not None else ""
        rub_key = str(batrub_tit) if batrub_tit is not None else ""
        typ_key = str(typ_tit) if typ_tit is not None else ""
        data_hier.setdefault(bat_key, {}).setdefault(
            rub_key, {}).setdefault(typ_key, {})[ex] = montant

    # --- Styles des Paragraphes ---
    styles = getSampleStyleSheet()

    # Styles pour les titres (Taille 8)
    style_bat = ParagraphStyle(
        'bat', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, spaceAfter=0) # spaceAfter réduit
    style_batrub = ParagraphStyle(
        'batrub', parent=styles['Normal'], leftIndent=2, fontName='Helvetica-Bold', fontSize=8)
    style_typ = ParagraphStyle(
        'typ', parent=styles['Normal'], leftIndent=4, fontName='Helvetica', fontSize=8)
    style_total = ParagraphStyle(
        'total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=4)

    # Style pour les valeurs numériques (Taille 5)
    style_valeur = ParagraphStyle(
        'valeur', parent=styles['Normal'], fontName='Helvetica', fontSize=5, alignment=4, leading=6) # leading (hauteur de ligne) ajusté à 6pt
    
    # Style pour les valeurs de totaux (Taille 8, Alignement à droite)
    style_valeur_total = ParagraphStyle(
        'valeur_total', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, alignment=4)

    # --- Remplissage du Tableau 'data' ---
    data = [["Bâtiment", "Bâtrub", "Type"] + exercices]

    # 🔑 SUPPRESSION DE LA GESTION MANUELLE DES HAUTEURS (hauteurs)

    for bat, rubs in data_hier.items():
        # Ligne titre bâtiment
        data.append([Paragraph(bat, style_bat)] + [""] * (2 + len(exercices)))

        total_bat = {ex: 0.0 for ex in exercices}

        for rub, typs in rubs.items():
            # Ligne titre bâtrub
            data.append(["", Paragraph(rub, style_batrub)] +
                        [""] * (1 + len(exercices)))
            total_rub = {ex: 0.0 for ex in exercices}

            for typ, montants in typs.items():
                typ_propre = str(typ) if typ is not None else ""

                # Ligne 1 : TITRE 'Typ'
                ligne_titre_typ = ["", "", Paragraph(
                    typ_propre, style_typ)] + [""] * len(exercices)
                data.append(ligne_titre_typ)

                # Ligne 2 : DÉTAIL pour le 'Typ' (avec les valeurs)
                ligne_detail_typ = ["", "", ""]

                for ex in exercices:
                    val = montants.get(ex, 0.0)
                    val_texte = f"{val:,.2f}".replace(
                        ",", " ").replace(".", ",")
                    # Encapsuler la valeur avec style_valeur (taille 5)
                    ligne_detail_typ.append(Paragraph(val_texte, style_valeur))

                    total_rub[ex] += val
                    total_bat[ex] += val
                data.append(ligne_detail_typ)

            # Ligne sous-total batrub
            ligne_total_rub = ["", Paragraph(f"Total {rub}", style_total), ""]
            for ex in exercices:
                val = total_rub[ex]
                val_texte = f"{val:,.2f}".replace(",", " ").replace(".", ",")
                # Encapsuler la valeur avec style_valeur_total
                ligne_total_rub.append(
                    Paragraph(val_texte, style_valeur_total))
            data.append(ligne_total_rub)

        # Ligne sous-total bat
        ligne_total_bat = [Paragraph(f"Total {bat}", style_total), "", ""]
        for ex in exercices:
            val = total_bat[ex]
            val_texte = f"{val:,.2f}".replace(",", " ").replace(".", ",")
            # Encapsuler la valeur avec style_valeur_total
            ligne_total_bat.append(Paragraph(val_texte, style_valeur_total))
        data.append(ligne_total_bat)

    # --- Création et Styles du Tableau ---
    # 🔑 RETRAIT DE rowHeights
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_table = TableStyle([
        # Styles généraux
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),

        # 🔑 AJUSTEMENT DU PADDING pour laisser ReportLab calculer la hauteur minimale sans couper
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5), # 0.5pt de padding en haut
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5), # 0.5pt de padding en bas
    ])

    # Application du SPAN et de la couleur (logique inchangée)
    for i, row in enumerate(data):
        # 1. Ligne Titre Bâtiment
        if isinstance(row[0], Paragraph) and row[1] == "" and row[2] == "" and not row[0].getPlainText().startswith("Total "):
            style_table.add('SPAN', (0, i), (-1, i))

        # 2. Ligne Titre Bâtrub
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
            style_table.add('BACKGROUND', (0, i), (-1, i), couleur_total_bat)
            style_table.add('SPAN', (0, i), (2, i))

    table.setStyle(style_table)

    # --- Génération du PDF ---
    doc = SimpleDocTemplate(
        fichier_pdf,
        pagesize=landscape(A4),
        leftMargin=0.5*cm,
        rightMargin=0.5*cm,
        topMargin=0.5*cm,
        bottomMargin=0.5*cm
    )

    if not os.path.exists(os.path.dirname(fichier_pdf)):
        os.makedirs(os.path.dirname(fichier_pdf))

    doc.build([table, Spacer(1, 0.2*cm)])
    print(f"✅ Fichier PDF généré : {fichier_pdf}")



if __name__ == "__main__":
    # calculs = pivot_cumuls()
    # resultats_sql = calculs["resultats"]
    # noms_colonnes = calculs["noms_colonnes"]
    creer_pdf_pivot_hierarchique_V3()
    # resultats_sql, noms_colonnes, nom_fichier="pivot_cumules_correct.pdf")
    # creer_vue("v_t_base_data")
