import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Color definitions
    NAVY = RGBColor(30, 58, 138)       # #1E3A8A
    BLUE = RGBColor(59, 130, 246)      # #3B82F6
    DARK_TEXT = RGBColor(30, 41, 59)   # #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139) # #64748B
    BG_LIGHT = RGBColor(248, 250, 252) # #F8FAFC
    WHITE = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240)
    
    # Speaker colors
    COLOR_M1 = RGBColor(37, 99, 235)   # Blue
    COLOR_M2 = RGBColor(124, 58, 237)  # Purple
    COLOR_M3 = RGBColor(5, 150, 105)   # Green
    COLOR_M4 = RGBColor(217, 119, 6)   # Amber
    COLOR_M5 = RGBColor(220, 38, 38)   # Red

    def add_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_LIGHT
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, speaker_name, speaker_role, speaker_color, timing):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.5), Inches(0.8))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.font.name = "Segoe UI"

        # Speaker Badge Shape
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.4), Inches(0.4), Inches(3.1), Inches(0.6))
        badge.fill.solid()
        badge.fill.fore_color.rgb = speaker_color
        badge.line.fill.background()
        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.text = f"👤 {speaker_name} ({timing})"
        bp.alignment = PP_ALIGN.CENTER
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = WHITE
        bp.font.name = "Segoe UI"

        bp2 = btf.add_paragraph()
        bp2.text = speaker_role
        bp2.alignment = PP_ALIGN.CENTER
        bp2.font.size = Pt(9)
        bp2.font.color.rgb = WHITE
        bp2.font.name = "Segoe UI"

    def set_notes(slide, speech_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = speech_text

    def add_card(slide, left, top, width, height, title, items, top_border_color=BLUE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        # Top border accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.08))
        line.fill.solid()
        line.fill.fore_color.rgb = top_border_color
        line.line.fill.background()

        # Text inside card
        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(height - 0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.font.name = "Segoe UI"

        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"• {item}"
            p_item.font.size = Pt(12)
            p_item.font.color.rgb = DARK_TEXT
            p_item.font.name = "Segoe UI"
            p_item.space_before = Pt(6)

    # ==========================================
    # SLIDE 1 : Titre & Introduction (Membre 1)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1)
    
    # Title Box Center
    tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.33), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "🎓 EduAccess"
    p.font.size = Pt(44)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    p.font.color.rgb = NAVY

    p2 = tf1.add_paragraph()
    p2.text = "Système Intelligent de Détection Précoce des Difficultés d'Apprentissage"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = BLUE
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(10)

    p3 = tf1.add_paragraph()
    p3.text = "École Marocaine des Sciences de l'Ingénieur (EMSI) • Année 2026\nModule : Développement & Déploiement d'Applications Intelligentes\nEncadrement : Pr. Soukaina Gouraguine\nProjet de Groupe : 5 Membres"
    p3.font.size = Pt(13)
    p3.font.color.rgb = MUTED_TEXT
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(24)

    set_notes(s1, 
        "👤 MEMBRE 1 (Chef de Projet & Data Engineer) — ⏱️ 1 min :\n\n"
        "« Bonjour à tous et bienvenue à la soutenance de notre projet EduAccess. "
        "Nous sommes un groupe de 5 étudiants-ingénieurs et nous avons conçu, développé et déployé "
        "une application intelligente complète d'aide à la décision pour repérer précocement "
        "les risques d'échec et de décrochage dans l'enseignement supérieur à distance. "
        "Les 4 livrables du cahier des charges sont intégralement réalisés et validés. "
        "Je vais commencer par vous présenter l'organisation de notre équipe et notre démarche. »"
    )

    # ==========================================
    # SLIDE 2 : Organisation de l'Équipe (Membre 1)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2)
    add_header(s2, "Organisation du Groupe & Répartition des Tâches", "Membre 1", "Chef de Projet & Data Eng.", COLOR_M1, "1 min 30")

    members_data = [
        ("Membre 1", "Data Engineering", "Pipeline ETL par chunks, consolidation OULAD (10.6M lignes), cadrage.", COLOR_M1, "Slides 1-4"),
        ("Membre 2", "Data Science", "Feature engineering (22 vars), benchmark ML, CV 5-folds, métriques.", COLOR_M2, "Slides 5-6"),
        ("Membre 3", "Backend & API", "Architecture FastAPI asynchrone, schémas Pydantic v2, endpoints d'inférence.", COLOR_M3, "Slides 7-8"),
        ("Membre 4", "Frontend & UX", "Dashboard interactif Streamlit (5 vues), moteur de recommandations tutorales.", COLOR_M4, "Slides 9-10"),
        ("Membre 5", "DevOps & Qualité", "13 tests Pytest, conteneurisation Docker, script CLI, cadre éthique & bilan.", COLOR_M5, "Slides 11-13"),
    ]

    for i, (m_name, m_role, m_desc, m_color, m_slides) in enumerate(members_data):
        left = 0.8 + (i * 2.4)
        c = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(1.8), Inches(2.2), Inches(4.5))
        c.fill.solid()
        c.fill.fore_color.rgb = WHITE
        c.line.color.rgb = CARD_BORDER
        
        # accent
        acc = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(1.8), Inches(2.2), Inches(0.1))
        acc.fill.solid()
        acc.fill.fore_color.rgb = m_color
        acc.line.fill.background()

        ctf = c.text_frame
        ctf.word_wrap = True
        p = ctf.paragraphs[0]
        p.text = f"👤 {m_name}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = m_color
        p.alignment = PP_ALIGN.CENTER

        p_r = ctf.add_paragraph()
        p_r.text = m_role
        p_r.font.size = Pt(11)
        p_r.font.bold = True
        p_r.font.color.rgb = NAVY
        p_r.alignment = PP_ALIGN.CENTER
        p_r.space_before = Pt(4)

        p_d = ctf.add_paragraph()
        p_d.text = m_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = DARK_TEXT
        p_d.alignment = PP_ALIGN.CENTER
        p_d.space_before = Pt(12)

        p_s = ctf.add_paragraph()
        p_s.text = f"📍 {m_slides}"
        p_s.font.size = Pt(10)
        p_s.font.bold = True
        p_s.font.color.rgb = MUTED_TEXT
        p_s.alignment = PP_ALIGN.CENTER
        p_s.space_before = Pt(20)

    set_notes(s2, 
        "👤 MEMBRE 1 (Chef de Projet & Data Engineer) — ⏱️ 1 min 30 :\n\n"
        "« Pour aborder ce projet complexe, notre équipe a adopté un découpage clair selon 5 expertises complémentaires :\n"
        "- Moi-même, j'assure le cadrage fonctionnel et l'ingénierie des données OULAD.\n"
        "- Membre 2 est notre Lead Data Scientist, en charge de la conception des variables et du benchmark des modèles.\n"
        "- Membre 3 a développé l'API REST FastAPI de production.\n"
        "- Membre 4 a conçu le tableau de bord Streamlit et le moteur de recommandations pédagogiques.\n"
        "- Membre 5 garantit la qualité logicielle avec 13 tests automatisés, le déploiement Docker et le cadre éthique.\n"
        "Voyons tout de suite le contexte et les objectifs du projet. »"
    )

    # ==========================================
    # SLIDE 3 : Contexte & Problématique (Membre 1)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3)
    add_header(s3, "1. Contexte, Problématique & Démarche Bienveillante", "Membre 1", "Chef de Projet & Data Eng.", COLOR_M1, "1 min 30")

    add_card(s3, 0.8, 1.8, 5.7, 4.5, "⚠️ Le Constat Traditionnel en E-Learning", [
        "Les décrochages scolaires surviennent souvent en silence.",
        "Le constat d'échec n'intervient qu'après les examens finaux.",
        "Il est alors trop tard pour mettre en place une remédiation.",
        "Sentiment d'isolement des étudiants face aux plateformes à distance.",
        "Nécessité critique d'un système d'alerte anticipé."
    ], RGBColor(245, 158, 11))

    add_card(s3, 6.8, 1.8, 5.7, 4.5, "🎯 La Réponse EduAccess & Éthique", [
        "Exploiter les traces d'apprentissage dès les 30 à 60 premiers jours.",
        "Détecter les signaux faibles (baisse de clics, retards aux premiers devoirs).",
        "Aide à la décision : L'outil assiste le tuteur sans jamais le remplacer.",
        "Principe de Bienveillance : Aucune sanction ou exclusion automatique.",
        "Génération de plans d'accompagnement humain individualisés."
    ], RGBColor(16, 185, 129))

    set_notes(s3,
        "👤 MEMBRE 1 (Chef de Projet & Data Engineer) — ⏱️ 1 min 30 :\n\n"
        "« Dans les cours à distance, un étudiant en difficulté ne prévient presque jamais. "
        "Le constat d'échec est traditionnellement établi lors des jurys de fin de semestre : "
        "c'est bien trop tard pour intervenir. EduAccess répond à ce problème en détectant "
        "les signaux faibles dès les 30 à 60 premiers jours de formation.\n"
        "J'insiste sur un principe éthique fondamental : EduAccess est un outil d'assistance "
        "pour les tuteurs et les enseignants, et en AUCUN CAS un système de décision ou d'exclusion "
        "automatique. Passons maintenant aux données sous-jacentes. »"
    )

    # ==========================================
    # SLIDE 4 : Données OULAD & ETL (Membre 1)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4)
    add_header(s4, "2. Données OULAD & Défi Big Data de Volumétrie", "Membre 1", "Chef de Projet & Data Eng.", COLOR_M1, "2 min")

    add_card(s4, 0.8, 1.8, 3.6, 2.5, "👥 32 593 Étudiants", [
        "22 sessions de cours (AAA à GGG).",
        "Données sociodémographiques.",
        "Charge de crédits et inscriptions."
    ], BLUE)

    add_card(s4, 4.8, 1.8, 3.6, 2.5, "💻 10.6M d'Interactions VLE", [
        "Fichier studentVle.csv (453 Mo).",
        "Journal quotidien de chaque clic.",
        "Défi majeur de mémoire vive (RAM)."
    ], RGBColor(16, 185, 129))

    add_card(s4, 8.8, 1.8, 3.6, 2.5, "📝 173 912 Évaluations", [
        "Devoirs continus (TMA/CMA) & examens.",
        "Notes obtenues et dates de soumission.",
        "Détection des retards de rendu."
    ], RGBColor(245, 158, 11))

    # Bottom ETL card
    add_card(s4, 0.8, 4.6, 11.6, 2.0, "⚡ Pipeline ETL Optimisé par Morceaux (src/data_loader.py)", [
        "Traitement par chunks de 1 000 000 lignes avec Pandas pour ne jamais saturer la RAM.",
        "Agrégation des clics avant rentrée (date < 0), clics à 30 jours et jours actifs en moins de 6 secondes.",
        "Dataset unifié généré : data/processed_students.csv (32 593 lignes x 26 colonnes)."
    ], NAVY)

    set_notes(s4,
        "👤 MEMBRE 1 (Chef de Projet & Data Engineer) — ⏱️ 2 min :\n\n"
        "« Nous nous appuyons sur le dataset universitaire de référence OULAD : 32 593 profils "
        "d'étudiants, 173 000 notes d'évaluations et surtout 10,6 millions d'interactions de clics "
        "dans le fichier studentVle.csv de 453 Mo.\n"
        "Pour traiter cette volumétrie sans saturer la RAM, j'ai implémenté dans data_loader.py "
        "un traitement par blocs de 1 million de lignes. Cela nous permet d'extraire les clics précoces "
        "à 30 jours et les jours actifs en moins de 6 secondes chrono, générant notre dataset nettoyé.\n\n"
        "➡️ TRANSITION : Je passe la parole à Membre 2 pour vous expliquer comment ces données "
        "ont été transformées en variables prédictives et modélisées. »"
    )

    # ==========================================
    # SLIDE 5 : Feature Engineering (Membre 2)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5)
    add_header(s5, "3. Feature Engineering & Prévention du Data Leakage", "Membre 2", "Lead Data Scientist", COLOR_M2, "2 min")

    add_card(s5, 0.8, 1.8, 5.7, 4.8, "🔍 22 Variables Extraites (src/feature_engineering.py)", [
        "Engagement VLE Précoce : pre_course_clicks, early_30_clicks, active_days, total_clicks.",
        "Dynamique d'Évaluation : early_assessments_count, early_avg_score, early_late_submissions, failed_assessments_count.",
        "Contexte Étudiant : date_registration, studied_credits, num_of_prev_attempts, highest_education, imd_band.",
        "Pipeline Scikit-Learn : Imputation médiane/mode + OneHotEncoder + RobustScaler."
    ], COLOR_M2)

    add_card(s5, 6.8, 1.8, 5.7, 4.8, "🚫 Règle Anti-Leakage & Cible Équilibrée", [
        "Bannissement strict de date_unregistration : Sa simple présence introduirait une fuite d'information évidente (100% de corrélation avec l'abandon).",
        "Cible Binaire Équilibrée (Target) :",
        "  • 1 (À Risque : Échec / Abandon) = 52.8%",
        "  • 0 (En Réussite : Pass / Distinction) = 47.2%",
        "Pas de problème de déséquilibre de classe : Métriques fiables sans suréchantillonnage artificiel."
    ], RGBColor(220, 38, 38))

    set_notes(s5,
        "👤 MEMBRE 2 (Lead Data Scientist & Modélisation) — ⏱️ 2 min :\n\n"
        "« Merci Membre 1. Une fois les données nettoyées, notre premier impératif en Feature Engineering "
        "a été la prévention absolue du Data Leakage. Dans le dataset OULAD, la variable date_unregistration "
        "donne la date exacte d'abandon de l'étudiant : l'inclure donnerait un modèle parfait mais inutilisable "
        "en précoce. Nous l'avons donc formellement bannie.\n"
        "Notre cible est parfaitement équilibrée avec 52.8% d'étudiants à risque et 47.2% en réussite. "
        "Nous avons extrait 22 caractéristiques capturant l'assiduité VLE à 30 jours, les notes aux "
        "premiers devoirs, les retards de soumission et la charge de crédits. »"
    )

    # ==========================================
    # SLIDE 6 : Modèles ML & Benchmark (Membre 2)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6)
    add_header(s6, "4. Benchmark & Sélection du Meilleur Modèle ML", "Membre 2", "Lead Data Scientist", COLOR_M2, "2 min")

    add_card(s6, 0.8, 1.8, 11.6, 2.7, "📊 Résultats Comparatifs en Validation Croisée Stratifiée (5-Folds)", [
        "Régression Logistique (Baseline) : Accuracy 92.77% | Précision 95.64% | Rappel 90.44% | F1 92.97% | ROC-AUC 0.9735",
        "Random Forest (Bagging 100 arbres) : Accuracy 92.39% | Précision 95.88% | Rappel 89.37% | F1 92.51% | ROC-AUC 0.9787",
        "🏆 HistGradientBoosting (Retenu) : Accuracy 93.04% | Précision 95.88% | Rappel 90.70% | F1 93.22% | ROC-AUC 0.9812",
        "Justification : Le Gradient Boosting offre la meilleure discrimination avec un F1 de 93.22% et une excellente précision de 95.88% évitant de submerger les tuteurs de fausses alertes."
    ], COLOR_M2)

    add_card(s6, 0.8, 4.7, 11.6, 1.9, "🔍 Facteurs Déterminants (Permutation Feature Importance)", [
        "1. early_avg_score : Les notes obtenues aux devoirs initiaux sont le 1er signal de maîtrise.",
        "2. early_30_clicks : Le volume de connexions au VLE dans le 1er mois reflète l'assiduité réelle.",
        "3. failed_assessments_count & late_submissions_count : Révélateurs de décrochage organisationnel."
    ], NAVY)

    set_notes(s6,
        "👤 MEMBRE 2 (Lead Data Scientist & Modélisation) — ⏱️ 2 min :\n\n"
        "« Pour sélectionner notre modèle de production, nous avons évalué trois algorithmes "
        "en validation croisée stratifiée à 5 plis : une Régression Logistique, un Random Forest "
        "et un HistGradientBoosting.\n"
        "C'est le Gradient Boosting qui l'emporte sur tous les critères avec 93.04% d'accuracy, "
        "un F1-score de 93.22% et un score ROC-AUC de 0.9812.\n"
        "Dans un contexte pédagogique, notre priorité était la précision sur le risque : avec 95.88%, "
        "lorsqu'une alerte est levée, le tuteur peut intervenir en toute sérénité car le risque est quasi certain.\n\n"
        "➡️ TRANSITION : Je passe la main à Membre 3 pour l'architecture logicielle et l'API REST. »"
    )

    # ==========================================
    # SLIDE 7 : Architecture Système (Membre 3)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7)
    add_header(s7, "5. Architecture Système Globale & Modulaire", "Membre 3", "Ingénieur Backend & API", COLOR_M3, "1 min 30")

    add_card(s7, 0.8, 1.8, 3.6, 4.8, "1. Données & Registre ML", [
        "Pipeline ETL modulaire (src/data_loader.py).",
        "Feature engineering réutilisable (src/feature_engineering.py).",
        "Model Registry (models/) : 3 modèles sérialisés au format Joblib.",
        "Traçabilité complète des scores dans metrics.json."
    ], BLUE)

    add_card(s7, 4.8, 1.8, 3.6, 4.8, "2. Backend REST API", [
        "Serveur FastAPI asynchrone ultra-performant.",
        "Contrats d'interface validés par Pydantic v2.",
        "Documentation OpenAPI interactive (Swagger UI /docs).",
        "Découplage total : L'API peut alimenter Moodle ou tout autre ERP."
    ], COLOR_M3)

    add_card(s7, 8.8, 1.8, 3.6, 4.8, "3. Clients & DevOps", [
        "Frontend interactif Streamlit pour enseignants et tuteurs.",
        "Suite de 13 tests Pytest automatisés.",
        "Conteneurisation Docker & orchestration Docker Compose.",
        "Interface en ligne de commande unifiée run_project.py."
    ], RGBColor(245, 158, 11))

    set_notes(s7,
        "👤 MEMBRE 3 (Ingénieur Backend & API) — ⏱️ 1 min 30 :\n\n"
        "« Merci Membre 2. Un modèle de Machine Learning ne prend sa valeur que s'il est intégré "
        "dans un système robuste et découplé. Nous avons donc bâti une architecture modulaire en 5 piliers :\n"
        "1. L'ingestion ETL et le Feature Engineering Scikit-Learn ;\n"
        "2. Le registre des modèles sérialisés Joblib et le suivi des métriques JSON ;\n"
        "3. Notre API REST FastAPI pour exposer l'inférence de manière sécurisée ;\n"
        "4. Le frontend interactif Streamlit pour les tuteurs ;\n"
        "5. Et la chaîne de qualité DevOps avec Pytest et Docker.\n"
        "Ce découpage garantit que le modèle peut être consommé aussi bien par notre dashboard "
        "que par le système Moodle officiel de l'école. »"
    )

    # ==========================================
    # SLIDE 8 : API REST FastAPI (Membre 3)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8)
    add_header(s8, "6. Backend & Endpoints d'Inférence FastAPI", "Membre 3", "Ingénieur Backend & API", COLOR_M3, "2 min")

    add_card(s8, 0.8, 1.8, 5.7, 4.8, "📡 Endpoints Opérationnels (api/main.py)", [
        "GET /health : Statut du service et confirmation du chargement du modèle.",
        "GET /metrics : Traçabilité des scores et matrices de confusion.",
        "GET /sample_profiles : 3 profils types pré-configurés (Faible, Moyen, Élevé).",
        "POST /predict : Diagnostic unitaire temps réel avec jauge de risque.",
        "POST /predict_batch : Inférence vectorisée sur une liste d'étudiants.",
        "POST /predict_csv : Enrichissement automatique d'un fichier CSV de cohorte."
    ], COLOR_M3)

    add_card(s8, 6.8, 1.8, 5.7, 4.8, "🛡️ Schémas Pydantic v2 & Documentation", [
        "Validation stricte des types de données (api/schemas.py).",
        "Contrôle automatique des bornes : Notes entre 0 et 100, crédits positifs.",
        "Gestion moderne du cycle de vie du serveur via lifespan.",
        "CORS activé pour intégration facile avec tout client frontend.",
        "Documentation interactive Swagger accessible sur http://127.0.0.1:8000/docs."
    ], NAVY)

    set_notes(s8,
        "👤 MEMBRE 3 (Ingénieur Backend & API) — ⏱️ 2 min :\n\n"
        "« Pour le backend, nous avons retenu FastAPI pour sa rapidité d'exécution asynchrone "
        "et sa génération automatique de documentation OpenAPI. Nous avons sécurisé l'intégralité "
        "des échanges grâce aux schémas Pydantic v2 dans schemas.py : chaque champ est strictement typé "
        "et les notes sont validées dans l'intervalle 0 à 100.\n"
        "Notre API propose des endpoints de diagnostic comme /health et /metrics, mais surtout "
        "trois modes d'inférence : unitaire avec /predict, en liste avec /predict_batch, et par fichier "
        "entier avec /predict_csv pour les cohortes complètes.\n"
        "Tout est testable interactivement via Swagger sur /docs.\n\n"
        "➡️ TRANSITION : Je passe la main à Membre 4 pour la découverte de l'application Streamlit. »"
    )

    # ==========================================
    # SLIDE 9 : Interface Streamlit (Membre 4)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9)
    add_header(s9, "7. Interface Décisionnelle Interactive Streamlit", "Membre 4", "Frontend & UX Décisionnelle", COLOR_M4, "2 min")

    add_card(s9, 0.8, 1.8, 3.6, 2.3, "📊 1. Analyse Exploratoire (EDA)", [
        "Visualisations interactives Plotly.",
        "Impact des clics VLE sur la réussite.",
        "Distribution des résultats et crédits."
    ], COLOR_M4)

    add_card(s9, 4.8, 1.8, 3.6, 2.3, "🤖 2. Comparateur de Modèles", [
        "Tableaux comparatifs des 3 modèles.",
        "Matrices de confusion interactives.",
        "Courbes d'importance des variables."
    ], BLUE)

    add_card(s9, 8.8, 1.8, 3.6, 2.3, "🎯 3. Simulateur Interactif", [
        "Formulaire de saisie en 3 volets.",
        "Jauge Plotly de risque tricolore.",
        "Prescription tutorale immédiate."
    ], RGBColor(16, 185, 129))

    add_card(s9, 0.8, 4.3, 5.7, 2.3, "📁 4. Analyse par Cohorte (Batch)", [
        "Exploration filtrable des cohortes OULAD existantes.",
        "Upload d'un fichier CSV externe et scoring automatique.",
        "Export Excel/CSV de la liste des étudiants prioritaires."
    ], RGBColor(124, 58, 237))

    add_card(s9, 6.8, 4.3, 5.7, 2.3, "📚 5. Support Pédagogique & Éthique", [
        "Rappel des objectifs d'aide à la décision.",
        "Charte de bienveillance pour les enseignants.",
        "Explications claires des facteurs influençant l'IA."
    ], NAVY)

    set_notes(s9,
        "👤 MEMBRE 4 (Frontend & UX Décisionnelle) — ⏱️ 2 min :\n\n"
        "« Merci Membre 3. Pour que les enseignants et tuteurs puissent facilement s'approprier "
        "notre modèle sans taper une seule ligne de code, j'ai développé une application web avec Streamlit.\n"
        "Le tableau de bord est structuré en 5 vues métier :\n"
        "1. Une vue d'analyse exploratoire pour visualiser les distributions de l'OULAD ;\n"
        "2. Un comparateur interactif affichant les matrices de confusion et courbes ROC ;\n"
        "3. Le simulateur où l'on charge un profil étudiant pour afficher instantanément sa jauge de risque ;\n"
        "4. La vue cohorte pour importer un fichier CSV complet de classe et exporter les alertes ;\n"
        "5. Et un volet éthique et pédagogique rappelant la charte d'utilisation bienveillante. »"
    )

    # ==========================================
    # SLIDE 10 : Moteur de Recommandations (Membre 4)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10)
    add_header(s10, "8. Diagnostic Actionnable & Tutorat Personnalisé", "Membre 4", "Frontend & UX Décisionnelle", COLOR_M4, "2 min")

    add_card(s10, 0.8, 1.8, 5.7, 4.8, "⚠️ Signaux Faibles Détectés par l'Algorithme", [
        "Faible assiduité VLE : Moins de 100 clics dans le premier mois de cours.",
        "Notes d'évaluation initiales : Score moyen < 40/100 ou devoir non rendu.",
        "Retard de soumission : Devoir déposé après la date limite officielle.",
        "Inscription tardive : Arrivée après le démarrage des enseignements.",
        "Surcharge académique : Plus de 120 crédits suivis simultanément."
    ], RGBColor(220, 38, 38))

    add_card(s10, 6.8, 1.8, 5.7, 4.8, "💡 Actions Tutorales Recommandées Clé en Main", [
        "📞 Prise de contact proactive : Vérifier l'accès technique et la prise en main du VLE.",
        "👨‍🏫 Tutorat individualisé : Remise à niveau méthodologique et révision ciblée.",
        "⏰ Gestion du temps : Réaménagement concerté du calendrier des rendus.",
        "📦 Kit de rattrapage : Fiches de synthèse pour combler le retard initial.",
        "♿ Aménagements spécifiques : Activation de tiers-temps ou soutien renforcé."
    ], RGBColor(16, 185, 129))

    set_notes(s10,
        "👤 MEMBRE 4 (Frontend & UX Décisionnelle) — ⏱️ 2 min :\n\n"
        "« La vraie force d'EduAccess réside dans son moteur de recommandations d'accompagnement. "
        "Prédire qu'un étudiant est à risque n'a aucune utilité si on n'explique pas POURQUOI et COMMENT l'aider.\n"
        "Notre système décompose les facteurs d'alerte :\n"
        "- Si l'activité VLE est faible, il suggère un contact proactif pour vérifier les accès informatiques ;\n"
        "- Si les notes de départ sont fragiles, il recommande un tutorat méthodologique d'urgence ;\n"
        "- En cas de retards fréquents, il préconise un aménagement de calendrier et un atelier d'organisation.\n"
        "Le tuteur dispose ainsi d'un plan d'action immédiat et individualisé.\n\n"
        "➡️ TRANSITION : Je passe la parole à Membre 5 pour la qualité logicielle, Docker et la conclusion. »"
    )

    # ==========================================
    # SLIDE 11 : Tests & DevOps (Membre 5)
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_background(s11)
    add_header(s11, "9. Qualité Logicielle, Tests & Déploiement Reproductible", "Membre 5", "Lead DevOps & QA", COLOR_M5, "2 min")

    add_card(s11, 0.8, 1.8, 5.7, 4.8, "🧪 Suite Pytest : 13 Tests Validés (100%)", [
        "test_data.py : Intégrité des 22 colonnes, types et absence de valeurs nulles critiques.",
        "test_models.py : Sérialisation Joblib, bornage strict des probabilités dans [0, 1] et logique de recommandation.",
        "test_api.py : Inférence HTTP unitaire (/predict) et par lot (/predict_batch) via TestClient FastAPI.",
        "Résultat : 13 passed in 4.38s ✅ (Zéro régression logicielle)."
    ], RGBColor(16, 185, 129))

    add_card(s11, 6.8, 1.8, 5.7, 4.8, "🐳 Déploiement Docker & CLI Universelle", [
        "Dockerfile multi-services optimisé avec dépendances figées.",
        "docker-compose.yml : Lancement simultané de l'API (port 8000) et de Streamlit (port 8501) en une commande :",
        "  $ docker-compose up --build",
        "CLI unifiée run_project.py : Pilotage complet en local (prepare, train, test, api, app, full)."
    ], COLOR_M5)

    set_notes(s11,
        "👤 MEMBRE 5 (Lead DevOps, QA & Conclusion) — ⏱️ 2 min :\n\n"
        "« Merci Membre 4. Pour garantir la qualité industrielle et la maintenabilité d'EduAccess, "
        "nous avons mis en place une suite de tests rigoureuse avec Pytest. Treize tests automatisés "
        "vérifient l'intégrité des 22 variables, la cohérence mathématique des probabilités et la réponse "
        "des endpoints HTTP. L'ensemble s'exécute avec succès en seulement 4,38 secondes.\n"
        "Pour assurer une reproductibilité parfaite sur n'importe quel serveur, l'ensemble est conteneurisé "
        "avec Docker et orchestré par Docker Compose : un simple docker-compose up démarre l'API et Streamlit.\n"
        "Enfin, notre script CLI unifié run_project.py simplifie l'exécution locale de chaque phase du projet. »"
    )

    # ==========================================
    # SLIDE 12 : Éthique & Limites (Membre 5)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_background(s12)
    add_header(s12, "10. Cadre Éthique & Limites Reconnues de l'IA", "Membre 5", "Lead DevOps & QA", COLOR_M5, "1 min 30")

    add_card(s12, 0.8, 1.8, 5.7, 4.8, "⚖️ Principes Éthiques Fondamentaux", [
        "Assistance bienveillante, pas de sanction : L'alerte déclenche un soutien, jamais une pénalité.",
        "Explicabilité & Transparence : Tous les facteurs de risque sont détaillés aux enseignants.",
        "Humain dans la boucle : La décision pédagogique appartient toujours au tuteur et à l'étudiant.",
        "Protection des données personnelles : Données anonymisées conformément au RGPD académique."
    ], RGBColor(245, 158, 11))

    add_card(s12, 6.8, 1.8, 5.7, 4.8, "🔍 Limites Techniques Reconnues", [
        "Problème du Cold-Start : La prédiction est moins précise avant les toutes premières connexions sur le VLE.",
        "Activités hors ligne non enregistrées : Les lectures sur livres physiques ou le travail en groupe présentiel ne génèrent pas de clics numériques.",
        "Nécessité d'un réentraînement périodique lors de l'ouverture de nouvelles filières."
    ], NAVY)

    set_notes(s12,
        "👤 MEMBRE 5 (Lead DevOps, QA & Conclusion) — ⏱️ 1 min 30 :\n\n"
        "« En tant que futurs ingénieurs, nous plaçons l'éthique au cœur de notre conception. "
        "EduAccess respecte scrupuleusement le principe de l'humain dans la boucle : "
        "l'algorithme éclaire mais ne tranche jamais. L'alerte est une opportunité d'écoute et d'aide.\n"
        "Nous reconnaissons également en toute transparence les limites du système : "
        "notamment le cold-start lors des tous premiers jours, et le fait que les séances de travail "
        "sur support papier ou hors connexion ne sont pas enregistrées par la plateforme en ligne. »"
    )

    # ==========================================
    # SLIDE 13 : Conclusion & Livrables (Membre 5)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_background(s13)
    add_header(s13, "Conclusion & Validation des Livrables", "Membre 5", "Lead DevOps & QA", COLOR_M5, "1 min 30")

    add_card(s13, 1.5, 1.8, 10.33, 4.8, "✅ Bilan Complet des Livrables du Cahier des Charges EMSI", [
        "Livrable 1 : Support pédagogique complet (docs/SUPPORT_PEDAGOGIQUE.md + Diaporama interactif)",
        "Livrable 2 : Code source complet et modulaire (ETL, Feature Engineering, Entraînement, API FastAPI, Streamlit, Docker, Pytest)",
        "Livrable 3 : Énoncé du TP guidé pas-à-pas (tp/TP_EduAccess_Enonce.md et Notebook Jupyter associé)",
        "Livrable 4 : Correction détaillée du TP (tp/TP_EduAccess_Correction.md et Notebook corrigé exécutable)",
        "Tous les livrables sont opérationnels, testés et prêts pour la production.",
        "Merci vivement pour votre attention ! Nous sommes à votre entière disposition pour répondre à vos questions."
    ], RGBColor(16, 185, 129))

    set_notes(s13,
        "👤 MEMBRE 5 (Lead DevOps, QA & Conclusion) — ⏱️ 1 min 30 :\n\n"
        "« En conclusion, nous sommes fiers de vous présenter un projet où l'ensemble des 4 livrables "
        "du cahier des charges de l'EMSI est rigoureusement achevé et validé :\n"
        "1. Le support pédagogique et les présentations ;\n"
        "2. Le code source complet, testé et conteneurisé ;\n"
        "3. L'énoncé du TP guidé avec ses notebooks Jupyter ;\n"
        "4. Et enfin le corrigé détaillé.\n\n"
        "Au nom de toute l'équipe d'EduAccess, nous vous remercions chaleureusement pour votre attention, "
        "et nous sommes maintenant à votre entière disposition pour répondre à toutes vos questions ! »"
    )

    output_path = "docs/presentation_EduAccess_5_membres.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_deck()
