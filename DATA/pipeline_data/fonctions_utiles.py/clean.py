import os
import pandas as pd
from typing import Dict, List, Tuple, Optional

class TooManyMissingError(Exception):
    """Exception levée quand le taux de missing dépasse le seuil autorisé."""
    def __init__(self, cols_too_many: Dict[str, float], message: Optional[str] = None):
        if message is None:
            message = "Colonnes avec trop de valeurs manquantes (au-dessus du seuil) :\n"
            message += "\n".join([f" - {c}: {p:.2%}" for c, p in cols_too_many.items()])
        super().__init__(message)
        self.cols_too_many = cols_too_many

def initial_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoyages de base :
    - normalise noms de colonnes (strip, lower, remplace espaces par underscore)
    - supprime les colonnes entièrement vides
    - supprime les doublons exacts de lignes
    - convertit les colonnes numériques représentées en chaînes en types numériques si possible
    - retire les index inutiles et resette index
    """
    df = df.copy()

    # Normaliser noms de colonnes
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    # Drop columns fully empty
    cols_all_na = [c for c in df.columns if df[c].isna().all()]
    if cols_all_na:
        df.drop(columns=cols_all_na, inplace=True)

    # Convert possible numeric-like columns to numeric
    for col in df.columns:
        if df[col].dtype == object:
            # essayer conversion en numérique (coerce errors => NaN)
            converted = pd.to_numeric(df[col].str.replace(",", "").str.strip(), errors="coerce")
            # si beaucoup de valeurs converties (par ex > 50%), remplacer dtype
            non_na_ratio = converted.notna().mean()
            if non_na_ratio >= 0.5:
                df[col] = converted

    # Drop exact duplicate rows
    df = df.drop_duplicates().reset_index(drop=True)

    return df

def compute_missing_rates(df: pd.DataFrame) -> Dict[str, float]:
    """Retourne un dict col -> taux de missing (float entre 0 et 1)."""
    
    return {col: df[col].isna().mean() for col in df.columns}

def impute_column(series: pd.Series, strategy: str = "median") -> Tuple[pd.Series, Dict]:
    """
    Impute une Series selon strategy :
    - numeric: 'median' (par défaut) ou 'mean' ou 'constant'
    - categorical (object / category): 'mode' ou 'constant'
    Retourne (series_imputed, info_dict)
    """
    info = {"dtype": str(series.dtype), "strategy": strategy, "n_missing_before": int(series.isna().sum())}
    s = series.copy()

    if pd.api.types.is_numeric_dtype(s):
        if strategy == "median":
            fill = s.median()
        elif strategy == "mean":
            fill = s.mean()
        elif strategy == "constant":
            fill = 0
        else:
            raise ValueError(f"Unknown numeric strategy: {strategy}")
        s = s.fillna(fill)
        info.update({"fill_value": float(fill), "n_missing_after": int(s.isna().sum())})
    else:
        # categorical
        if strategy == "mode":
            if s.dropna().empty:
                fill = "missing"
            else:
                fill = s.mode().iloc[0]
        elif strategy == "constant":
            fill = "missing"
        else:
            raise ValueError(f"Unknown categorical strategy: {strategy}")
        s = s.fillna(fill).astype(str)
        info.update({"fill_value": str(fill), "n_missing_after": int(s.isna().sum())})

    return s, info

def handle_missing_values(
    df: pd.DataFrame,
    threshold: float = 0.07,
    numeric_strategy: str = "median",
    categorical_strategy: str = "mode",
    allow_drop_constant: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Dict]]:
    """
    Contrôle et imputation des missing values :
    - si taux_missing(col) <= threshold -> impute automatiquement
    - sinon -> lève TooManyMissingError indiquant les colonnes problématiques
    Retour : (df_imputed, imputation_info)
    """
    df = df.copy()
    n_rows = len(df)
    missing_rates = compute_missing_rates(df)
    cols_exceed = {c: p for c, p in missing_rates.items() if p > threshold}

    if cols_exceed:
        # lève erreur avec colonnes et taux
        raise TooManyMissingError(cols_exceed)

    imputation_info: Dict[str, Dict] = {}
    for col, rate in missing_rates.items():
        if rate == 0:
            # rien à faire, mais enregistrer
            imputation_info[col] = {"n_missing_before": 0, "n_missing_after": 0, "strategy": "none"}
            continue

        # si colonne non-constante et taux <= threshold -> impute
        if rate <= threshold:
            series = df[col]
            if pd.api.types.is_numeric_dtype(series):
                s_imputed, info = impute_column(series, strategy=numeric_strategy)
            else:
                s_imputed, info = impute_column(series, strategy=categorical_strategy)
            df[col] = s_imputed
            imputation_info[col] = info
        else:
            # normalement ne passe pas ici car on lève l'exception plus haut
            imputation_info[col] = {"n_missing_before": int(df[col].isna().sum()), "note": "exceeds_threshold"}

    # Optionnel: drop columns constantes si demandé
    if allow_drop_constant:
        constant_cols = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
        for c in constant_cols:
            # on s'assure de ne pas drop la target si présente
            # (tu peux changer la logique pour préserver 'medv' etc.)
            df.drop(columns=[c], inplace=True)
            imputation_info[c] = imputation_info.get(c, {})
            imputation_info[c].update({"dropped_constant": True})

    return df, imputation_info


data = pd.read_csv(os.getenv('data_path'), header=None, delimiter=r"\s+")


    
df_clean = initial_cleaning(data)
print(f"Après nettoyage initial : {df_clean.shape[0]} lignes, {df_clean.shape[1]} colonnes")

# 2) gestion des missing values - si dépassement -> TooManyMissingError
try:
    df_imputed, imputation_info = handle_missing_values(
    df_clean,
    threshold=0.07,               # 7%
    numeric_strategy="median",
    categorical_strategy="mode",
    allow_drop_constant=True
    )
    print("Imputation réalisée avec succès. Récapitulatif :")
    for col, info in imputation_info.items():
        print(f" - {col}: {info}")
    # # ensuite tu peux sauvegarder df_imputed dans data/processed/
    # df_imputed.to_csv("data/processed/data_imputed.csv", index=False)
    # print("Data imputed saved to data/processed/data_imputed.csv")

except TooManyMissingError as e:
    # gérer l'erreur selon ta stratégie (alerte, logging, suppression colonne, etc.)
    print("Erreur: colonnes avec trop de missing :")
    print(e)
    # Exemples d'actions possibles :
    # - logger l'erreur et arrêter le pipeline (actuel comportement)
    # - envoyer email/alerte
    # - appliquer stratégie alternative (drop columns, imputer avec modèle...)
