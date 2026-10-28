"""
Application Web Interactive Streamlit - EduAccess
Système d'analyse et de détection précoce des difficultés d'apprentissage.
Projet académique - Module Développement et déploiement d'applications intelligentes.
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuration de la page Streamlit
st.set_page_config(
    page_title="EduAccess - Détection Précoce des Difficultés",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chemins des données et modèles
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed_students.csv"
FEATURE_METADATA_PATH = BASE_DIR / "data" / "feature_metadata.json"
MODELS_DIR = BASE_DIR / "models"
BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .recommendation-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 0.98rem;
    }
    .alert-high {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 14px 18px;
        border-radius: 6px;
    }
    .alert-safe {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 14px 18px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_processed_data():
    """Charge le jeu de données OULAD consolidé."""
    if PROCESSED_DATA_PATH.exists():
        return pd.read_csv(PROCESSED_DATA_PATH)
    return None


@st.cache_data
def load_metrics_data():
    """Charge les métriques d'évaluation."""
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_resource
def load_ml_model(model_choice: str):
    """Charge le modèle sélectionné."""
    slug_map = {
        "Gradient Boosting (Recommandé)": "model_gradient_boosting.joblib",
        "Gradient Boosting": "model_gradient_boosting.joblib",
        "Random Forest": "model_random_forest.joblib",
        "Logistic Regression": "model_logistic_regression.joblib"
    }
    filename = slug_map.get(model_choice, "best_model.joblib")
    filepath = MODELS_DIR / filename
    if filepath.exists():
        return joblib.load(filepath)
    elif BEST_MODEL_PATH.exists():
        return joblib.load(BEST_MODEL_PATH)
    return None


def generate_educational_actions(profile: dict, risk_prob: float) -> list:
    """Génère les recommandations pédagogiques ciblées."""
    from src.feature_engineering import generate_recommendations
    return generate_recommendations(profile, risk_prob)


# -------------------------------------------------------------
# BARRE LATÉRALE (SIDEBAR)
# -------------------------------------------------------------
with st.sidebar:
    st.title("EduAccess")
    st.caption("Plateforme d'analyse et d'accompagnement académique précoce (OULAD)")
    st.markdown("---")

    menu = st.radio(
        "Navigation",
        [
            "Vue d'ensemble et Analyse OULAD",
            "Modèles et Performances",
            "Simulateur de Risque Précoce",
            "Analyse par Cohorte"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("Paramètres de Prédiction")
    model_choice = st.selectbox(
        "Modèle actif :",
        ["Gradient Boosting", "Random Forest", "Logistic Regression"]
    )

    risk_threshold = st.slider(
        "Seuil d'alerte précoce :",
        min_value=0.20,
        max_value=0.80,
        value=0.50,
        step=0.05,
        help="Ajuster le seuil pour équilibrer la sensibilité et la spécificité de la détection."
    )

    st.markdown("---")
    st.caption("Projet EMSI - Ingénierie des Données")


# Chargement des données
df_students = load_processed_data()
metrics_dict = load_metrics_data()
current_model = load_ml_model(model_choice)


# -------------------------------------------------------------
# PAGE 1 : VUE D'ENSEMBLE & ANALYSE EXPLORATOIRE (EDA)
# -------------------------------------------------------------
if menu == "Vue d'ensemble et Analyse OULAD":
    st.markdown('<div class="main-header">Vue d\'ensemble et Analyse des Données OULAD</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Exploration statistique de la cohorte d\'étudiants et signaux d\'engagement.</div>', unsafe_allow_html=True)

    if df_students is None:
        st.error("Données traitées introuvables. Veuillez exécuter le pipeline de préparation.")
    else:
        # Ligne d'indicateurs
        col1, col2, col3, col4 = st.columns(4)
        total_students = len(df_students)
        at_risk_count = int(df_students["is_at_risk"].sum())
        success_count = total_students - at_risk_count
        avg_clicks = df_students["total_clicks"].mean()

        with col1:
            st.metric("Total Étudiants", f"{total_students:,}")
        with col2:
            st.metric("Profils à Risque (Fail / Withdrawn)", f"{at_risk_count:,}", f"{(at_risk_count/total_students)*100:.1f}%", delta_color="inverse")
        with col3:
            st.metric("Profils en Réussite (Pass / Distinction)", f"{success_count:,}", f"{(success_count/total_students)*100:.1f}%")
        with col4:
            st.metric("Moyenne Clics VLE", f"{avg_clicks:.0f} clics")

        st.markdown("---")

        # Visualisations
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("1. Répartition des Résultats Finaux")
            result_counts = df_students["final_result"].value_counts().reset_index()
            result_counts.columns = ["Résultat", "Effectif"]
            fig_pie = px.pie(
                result_counts,
                names="Résultat",
                values="Effectif",
                color="Résultat",
                color_discrete_map={
                    "Distinction": "#10B981",
                    "Pass": "#3B82F6",
                    "Fail": "#F59E0B",
                    "Withdrawn": "#EF4444"
                },
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        with row1_col2:
            st.subheader("2. Engagement Précoce VLE (30 premiers jours)")
            fig_box = px.box(
                df_students,
                x="final_result",
                y="early_30_clicks",
                color="final_result",
                points=False,
                category_orders={"final_result": ["Distinction", "Pass", "Fail", "Withdrawn"]},
                color_discrete_map={
                    "Distinction": "#10B981",
                    "Pass": "#3B82F6",
                    "Fail": "#F59E0B",
                    "Withdrawn": "#EF4444"
                },
                labels={"final_result": "Résultat Final", "early_30_clicks": "Clics (30 premiers jours)"}
            )
            fig_box.update_yaxes(range=[0, 1200])
            fig_box.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_box, use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("3. Taux de Difficulté par Module de Cours")
            module_stats = df_students.groupby("code_module")["is_at_risk"].agg(
                total="count",
                at_risk="sum"
            ).reset_index()
            module_stats["taux_risque"] = (module_stats["at_risk"] / module_stats["total"]) * 100

            fig_bar = px.bar(
                module_stats,
                x="code_module",
                y="taux_risque",
                text=module_stats["taux_risque"].apply(lambda v: f"{v:.1f}%"),
                color="taux_risque",
                color_continuous_scale="Reds",
                labels={"code_module": "Module", "taux_risque": "Taux d'étudiants à risque (%)"}
            )
            fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with row2_col2:
            st.subheader("4. Impact du Retard d'Évaluation sur le Risque")
            late_stats = df_students.groupby("late_submissions_count")["is_at_risk"].agg(
                total="count",
                at_risk="sum"
            ).reset_index()
            late_stats = late_stats[late_stats["late_submissions_count"] <= 5]
            late_stats["taux_risque"] = (late_stats["at_risk"] / late_stats["total"]) * 100

            fig_line = px.bar(
                late_stats,
                x="late_submissions_count",
                y="taux_risque",
                text=late_stats["taux_risque"].apply(lambda v: f"{v:.1f}%"),
                labels={"late_submissions_count": "Nombre de Devoirs en Retard", "taux_risque": "Taux de Risque (%)"},
                color_discrete_sequence=["#EF4444"]
            )
            fig_line.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_line, use_container_width=True)


# -------------------------------------------------------------
# PAGE 2 : COMPARAISON DES MODÈLES & MÉTRIQUES ML
# -------------------------------------------------------------
elif menu == "Modèles et Performances":
    st.markdown('<div class="main-header">Comparaison et Évaluation des Modèles</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comparatif des algorithmes de classification (Accuracy, Precision, Recall, F1-Score, ROC-AUC).</div>', unsafe_allow_html=True)

    if metrics_dict is None:
        st.warning("Métriques introuvables. Entraînez les modèles avec `python -m src.train`.")
    else:
        st.success(f"Meilleur modèle retenu : **{metrics_dict.get('best_model', 'N/A')}** (critère : F1-Score sur l'ensemble de test).")

        # Tableau récapitulatif
        rows = []
        for name, data in metrics_dict["models"].items():
            test_m = data["test_metrics"]
            cv_m = data["cv_metrics_mean"]
            rows.append({
                "Modèle": name,
                "Accuracy (Test)": f"{test_m['accuracy']*100:.2f}%",
                "Precision (Test)": f"{test_m['precision']*100:.2f}%",
                "Recall (Test)": f"{test_m['recall']*100:.2f}%",
                "F1-Score (Test)": f"{test_m['f1_score']*100:.2f}%",
                "ROC-AUC (Test)": f"{test_m['roc_auc']:.4f}",
                "F1-Score (5-Fold CV)": f"{cv_m['f1_score']*100:.2f}%"
            })
        st.dataframe(pd.DataFrame(rows).set_index("Modèle"), use_container_width=True)

        st.markdown("---")
        mcol1, mcol2 = st.columns(2)

        with mcol1:
            st.subheader("Matrice de Confusion (Ensemble de test)")
            active_name = model_choice.replace(" (Recommandé)", "")
            cm_data = metrics_dict["models"].get(active_name, {}).get("confusion_matrix", [[0, 0], [0, 0]])

            cm_df = pd.DataFrame(
                cm_data,
                index=["Réel : Réussite (0)", "Réel : À Risque (1)"],
                columns=["Prédit : Réussite (0)", "Prédit : À Risque (1)"]
            )
            fig_cm = px.imshow(
                cm_df,
                text_auto=True,
                color_continuous_scale="Blues",
                labels=dict(x="Prédiction", y="Vérité Terrain", color="Effectif")
            )
            fig_cm.update_layout(margin=dict(t=20, b=20, l=20, r=20), coloraxis_showscale=False)
            st.plotly_chart(fig_cm, use_container_width=True)

        with mcol2:
            st.subheader("Variables Clés (Permutation Importance)")
            fi_list = metrics_dict.get("feature_importances", [])[:10]
            if fi_list:
                fi_df = pd.DataFrame(fi_list)
                fig_fi = px.bar(
                    fi_df,
                    x="importance",
                    y="feature",
                    orientation="h",
                    labels={"importance": "Importance relative (Gain F1)", "feature": "Variable"},
                    color="importance",
                    color_continuous_scale="Viridis"
                )
                fig_fi.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=20, b=20, l=20, r=20), coloraxis_showscale=False)
                st.plotly_chart(fig_fi, use_container_width=True)


# -------------------------------------------------------------
# PAGE 3 : SIMULATEUR DE RISQUE PRÉCOCE & RECOMMANDATIONS
# -------------------------------------------------------------
elif menu == "Simulateur de Risque Précoce":
    st.markdown('<div class="main-header">Simulateur de Détection Précoce et Diagnostic</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Évaluation du profil d\'un étudiant en début de cursus et identification des pistes d\'accompagnement.</div>', unsafe_allow_html=True)

    # Profils types
    st.markdown("##### Charger un profil type pour tester :")
    bcol1, bcol2, bcol3 = st.columns(3)
    preset = None
    if bcol1.button("Profil Autonome / Réussite"):
        preset = "brillant"
    if bcol2.button("Profil Intermédiaire"):
        preset = "moyen"
    if bcol3.button("Profil Fragile / Difficultés"):
        preset = "fragile"

    # Valeurs par défaut selon preset
    if preset == "brillant":
        def_clicks_pre, def_clicks_30, def_total_clicks, def_active_days = 90.0, 450.0, 1800.0, 42.0
        def_early_eval_count, def_early_avg, def_failed, def_late = 2.0, 84.0, 0.0, 0.0
        def_credits, def_prev_att, def_reg = 60, 0, -35.0
    elif preset == "fragile":
        def_clicks_pre, def_clicks_30, def_total_clicks, def_active_days = 0.0, 30.0, 75.0, 4.0
        def_early_eval_count, def_early_avg, def_failed, def_late = 1.0, 30.0, 1.0, 1.0
        def_credits, def_prev_att, def_reg = 120, 1, 8.0
    else:
        def_clicks_pre, def_clicks_30, def_total_clicks, def_active_days = 25.0, 180.0, 520.0, 18.0
        def_early_eval_count, def_early_avg, def_failed, def_late = 2.0, 56.0, 0.0, 1.0
        def_credits, def_prev_att, def_reg = 60, 0, -10.0

    st.markdown("---")

    with st.form("simulation_form"):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            st.subheader("1. Contexte & Cursus")
            mod_val = st.selectbox("Module d'enseignement", ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG"], index=1)
            gender_val = st.selectbox("Genre", ["F", "M"], index=0)
            edu_val = st.selectbox("Niveau d'études initial", [
                "HE Qualification", "A Level or Equivalent", "Lower Than A Level", "Post Graduate Qualification", "No Formal quals"
            ], index=1)
            imd_val = st.selectbox("Indice défavorisation (IMD Band)", [
                "0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%", "Missing"
            ], index=4)
            age_val = st.selectbox("Tranche d'âge", ["0-35", "35-55", "55<="], index=0)
            disability_val = st.selectbox("Situation de handicap", ["N", "Y"], index=0)
            region_val = st.selectbox("Région", [
                "East Anglian Region", "London Region", "South Region", "South West Region", "North Western Region", "West Midlands Region"
            ], index=1)

        with col_f2:
            st.subheader("2. Engagement VLE")
            clicks_pre = st.number_input("Clics avant le cours (J < 0)", min_value=0.0, value=float(def_clicks_pre), step=10.0)
            clicks_30 = st.number_input("Clics dans les 30 premiers jours", min_value=0.0, value=float(def_clicks_30), step=20.0)
            total_clicks_inp = st.number_input("Total clics cumulés", min_value=0.0, value=float(def_total_clicks), step=50.0)
            active_days_inp = st.number_input("Jours de connexion distincts", min_value=0.0, value=float(def_active_days), step=1.0)
            date_reg_inp = st.number_input("Date d'inscription (jours p/r au début)", min_value=-150.0, max_value=60.0, value=float(def_reg), step=1.0)
            credits_inp = st.number_input("Nombre de crédits étudiés", min_value=30, max_value=300, value=int(def_credits), step=30)
            prev_attempts_inp = st.number_input("Tentatives antérieures sur ce module", min_value=0, max_value=6, value=int(def_prev_att), step=1)

        with col_f3:
            st.subheader("3. Évaluations & Notes")
            early_eval_count_inp = st.number_input("Devoirs soumis tôt (<= 60j)", min_value=0.0, max_value=5.0, value=float(def_early_eval_count), step=1.0)
            early_avg_inp = st.slider("Note moyenne précoce (0-100)", min_value=0.0, max_value=100.0, value=float(def_early_avg), step=1.0)
            late_sub_inp = st.number_input("Devoirs soumis en retard", min_value=0.0, max_value=10.0, value=float(def_late), step=1.0)
            failed_sub_inp = st.number_input("Devoirs échoués (note < 40)", min_value=0.0, max_value=10.0, value=float(def_failed), step=1.0)
            total_eval_sub_inp = st.number_input("Total devoirs soumis", min_value=0.0, max_value=15.0, value=max(float(def_early_eval_count), 2.0), step=1.0)
            overall_avg_inp = st.slider("Note moyenne globale estimée", min_value=0.0, max_value=100.0, value=float(def_early_avg), step=1.0)
            min_score_inp = st.slider("Note minimale obtenue", min_value=0.0, max_value=100.0, value=max(0.0, float(def_early_avg) - 10.0), step=1.0)

        submitted = st.form_submit_button("Diagnostiquer le profil étudiant", use_container_width=True)

    if submitted:
        if current_model is None:
            st.error("Modèle introuvable. Veuillez d'abord entraîner le modèle.")
        else:
            profile_dict = {
                "code_module": mod_val,
                "gender": gender_val,
                "region": region_val,
                "highest_education": edu_val,
                "imd_band": imd_val,
                "age_band": age_val,
                "disability": disability_val,
                "num_of_prev_attempts": prev_attempts_inp,
                "studied_credits": credits_inp,
                "date_registration": date_reg_inp,
                "pre_course_clicks": clicks_pre,
                "early_30_clicks": clicks_30,
                "total_clicks": total_clicks_inp,
                "active_days": active_days_inp,
                "early_assessments_count": early_eval_count_inp,
                "early_avg_score": early_avg_inp,
                "early_late_submissions": late_sub_inp,
                "total_assessments_submitted": total_eval_sub_inp,
                "overall_avg_score": overall_avg_inp,
                "min_score": min_score_inp,
                "late_submissions_count": late_sub_inp,
                "failed_assessments_count": failed_sub_inp
            }

            from src.config import ALL_FEATURES
            input_df = pd.DataFrame([profile_dict])[ALL_FEATURES]

            probabilities = current_model.predict_proba(input_df)[0]
            risk_prob = float(probabilities[1])
            is_at_risk = risk_prob >= risk_threshold

            st.markdown("---")
            st.subheader("Résultat du Diagnostic Précoce")

            res_col1, res_col2 = st.columns([1, 1])

            with res_col1:
                # Jauge de probabilité
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=risk_prob * 100,
                    number={"suffix": "%"},
                    title={"text": "Probabilité estimée de difficulté académique"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#1E3A8A"},
                        "steps": [
                            {"range": [0, 35], "color": "#D1FAE5"},
                            {"range": [35, 65], "color": "#FEF3C7"},
                            {"range": [65, 100], "color": "#FEE2E2"}
                        ],
                        "threshold": {
                            "line": {"color": "#DC2626", "width": 4},
                            "thickness": 0.75,
                            "value": risk_threshold * 100
                        }
                    }
                ))
                fig_gauge.update_layout(height=280, margin=dict(t=30, b=10, l=20, r=20))
                st.plotly_chart(fig_gauge, use_container_width=True)

            with res_col2:
                if is_at_risk:
                    st.markdown("""
                    <div class="alert-high">
                        <h3 style="color: #991B1B; margin-top:0;">Profil Identifié à Risque Académique</h3>
                        <p>Les indicateurs d'engagement et de progression signalent une fragilité nécessitant un suivi pédagogique.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert-safe">
                        <h3 style="color: #065F46; margin-top:0;">Profil Favorable / Réussite Probable</h3>
                        <p>Les indicateurs d'engagement et de progression sont conformes aux attentes pour ce stade du cursus.</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"**Modèle actif :** {model_choice}")
                st.markdown(f"**Seuil d'alerte configuré :** `{risk_threshold*100:.0f}%`")
                st.markdown(f"**Indice de certitude du modèle :** `{max(probabilities)*100:.1f}%`")

            # Recommandations pédagogiques
            st.markdown("### Recommandations Pédagogiques Individualisées")
            recs = generate_educational_actions(profile_dict, risk_prob)
            for r in recs:
                st.markdown(f'<div class="recommendation-box">{r}</div>', unsafe_allow_html=True)


# -------------------------------------------------------------
# PAGE 4 : ANALYSE PAR COHORTE (BATCH / CSV)
# -------------------------------------------------------------
elif menu == "Analyse par Cohorte":
    st.markdown('<div class="main-header">Analyse par Cohorte d\'Étudiants</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Évaluation globale d\'un groupe d\'étudiants pour identifier les profils prioritaires.</div>', unsafe_allow_html=True)

    tab_explore, tab_upload = st.tabs(["Cohorte OULAD Enregistrée", "Téléverser un Fichier CSV"])

    with tab_explore:
        if df_students is not None:
            c1, c2 = st.columns(2)
            with c1:
                selected_module = st.selectbox("Filtrer par module :", ["Tous"] + list(df_students["code_module"].unique()))
            with c2:
                risk_filter = st.selectbox("Filtrer par statut :", ["Tous", "À risque uniquement", "En réussite uniquement"])

            subset = df_students.copy()
            if selected_module != "Tous":
                subset = subset[subset["code_module"] == selected_module]
            if risk_filter == "À risque uniquement":
                subset = subset[subset["is_at_risk"] == 1]
            elif risk_filter == "En réussite uniquement":
                subset = subset[subset["is_at_risk"] == 0]

            st.write(f"Affichage de **{len(subset):,}** étudiants correspondant aux critères.")
            display_cols = ["id_student", "code_module", "gender", "highest_education", "studied_credits", "total_clicks", "early_avg_score", "final_result", "is_at_risk"]
            st.dataframe(subset[display_cols].head(50), use_container_width=True)

            csv_export = subset[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger cette sélection en CSV", csv_export, "etudiants_selection.csv", "text/csv")

    with tab_upload:
        st.write("Importez un fichier CSV contenant les colonnes de l'OULAD pour générer un rapport de diagnostic.")
        uploaded_file = st.file_uploader("Fichier CSV à analyser", type=["csv"])
        if uploaded_file is not None and current_model is not None:
            batch_df = pd.read_csv(uploaded_file)
            from src.config import ALL_FEATURES
            missing = [c for c in ALL_FEATURES if c not in batch_df.columns]
            if missing:
                st.error(f"Colonnes manquantes dans votre fichier : {missing}")
            else:
                probs = current_model.predict_proba(batch_df[ALL_FEATURES])[:, 1]
                batch_df["Probabilite_Risque"] = (probs * 100).round(1)
                batch_df["Statut_Alerte"] = np.where(probs >= risk_threshold, "À Risque", "Réussite")
                st.success(f"Analyse réussie pour {len(batch_df)} étudiants.")
                st.dataframe(batch_df[["id_student", "Statut_Alerte", "Probabilite_Risque"] + ALL_FEATURES[:6]].head(20), use_container_width=True)
