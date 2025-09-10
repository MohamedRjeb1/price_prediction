
from typing import List, Optional
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
load_dotenv()

# --- Configuration visuelle (professionnelle) ---
sns.set_style("whitegrid")
plt.rcParams.update({
    "figure.titlesize": 16,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10
})


def summary_stats(series: pd.Series) -> dict:
    s = series.dropna()
    return {
        "count": int(s.count()),
        "mean": float(s.mean()),
        "median": float(s.median()),
        "std": float(s.std()),
        "min": float(s.min()),
        "25%": float(s.quantile(0.25)),
        "50%": float(s.quantile(0.50)),
        "75%": float(s.quantile(0.75)),
        "max": float(s.max()),
        "skew": float(s.skew()),
        "kurtosis": float(s.kurtosis()),
    }

# --- Fonction principale de plotting ---
def plot_distribution_and_box(
    df: pd.DataFrame,
    cols: Optional[List[str]] = None,
    show: bool = True,
    bins: int = 30,
    figsize: tuple = (14, 5)
):
  
   

    # Choisir les colonnes numériques si pas fournies
    if cols is None:
        cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in cols:
        s = df[col].dropna()
        if s.empty:
            print(f"[SKIP] {col} : colonne vide")
            continue

        # Eviter colonnes constantes
        if s.nunique() <= 1:
            print(f"[SKIP] {col} : colonne constante ({s.nunique()} unique value)")
            continue

        stats = summary_stats(s)

        # Build figure avec 2 subplots côte-à-côte
        fig, axes = plt.subplots(ncols=2, nrows=1, figsize=figsize, gridspec_kw={'width_ratios':[3,1]})
        ax_hist, ax_box = axes[0], axes[1]

        # --- Histogramme + KDE ---
        sns.histplot(s, bins=bins, kde=True, ax=ax_hist)
        ax_hist.set_title(f"Distribution — {col}", fontsize=14, fontweight='semibold')
        ax_hist.set_xlabel(col, fontsize=11)
        ax_hist.set_ylabel("Effectif", fontsize=11)

        # Lignes moyenne & médiane
        ax_hist.axvline(stats['mean'], color='black', linestyle='--', linewidth=1.5, label=f"Moyenne = {stats['mean']:.2f}")
        ax_hist.axvline(stats['median'], color='darkred', linestyle=':', linewidth=1.5, label=f"Médiane = {stats['median']:.2f}")
        ax_hist.legend(loc='upper right', frameon=True)

        # Encadré statique (coin supérieur droit)
        stats_text = (
            f"N = {stats['count']}\n"
            f"Mean = {stats['mean']:.2f}\n"
            f"Median = {stats['median']:.2f}\n"
            f"Std = {stats['std']:.2f}\n"
            f"Min = {stats['min']:.2f}\n"
            f"Max = {stats['max']:.2f}\n"
            f"Skew = {stats['skew']:.2f}"
        )
        ax_hist.text(
            0.98, 0.98, stats_text,
            transform=ax_hist.transAxes,
            fontsize=10,
            va='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='0.8')
        )

        # --- Boxplot ---
        sns.boxplot(x=s, ax=ax_box, orient='h')
        ax_box.set_title(f"Boxplot — {col}", fontsize=14, fontweight='semibold')
        ax_box.set_xlabel(col, fontsize=11)

        # Calcul des outliers (IQR)
        Q1 = s.quantile(0.25)
        Q3 = s.quantile(0.75)
        IQR = Q3 - Q1
        outliers = s[(s < Q1 - 1.5 * IQR) | (s > Q3 + 1.5 * IQR)]
        outlier_text = f"Outliers: {outliers.count()}"
        ax_box.text(
            0.98, 0.98, outlier_text,
            transform=ax_box.transAxes,
            fontsize=10,
            va='top', ha='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, edgecolor='0.8')
        )

        # Titre général et layout
        plt.suptitle(f"Analyse de la variable — {col}", fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.95])

       
        plt.show()
        

        
print(os.getenv("data_path"))
data = pd.read_csv(os.getenv("data_path"), header=None, delimiter=r"\s+")
plot_distribution_and_box(data, cols=data.columns, show=True, bins=30)
