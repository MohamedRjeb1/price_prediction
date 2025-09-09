# 📊 Boston Housing Dataset

Ce dataset est utilisé pour l’analyse et la prédiction des prix des logements dans la région de **Boston**.  
Il contient des variables socio-économiques, environnementales et structurelles liées aux habitations et à leur environnement.  

---

## 🏠 Description des colonnes

- **ZN** : proportion de terrains résidentiels zonés pour des lots de plus de **25 000 sq.ft** (indique les zones avec de grandes parcelles).
- **INDUS** : proportion de terrains occupés par des activités **non-commerciales au détail** (zones industrielles).
- **CHAS** : variable binaire (dummy) — **1** si le secteur borde la rivière Charles, **0** sinon.
- **NOX** : concentration d’**oxydes d’azote** (pollution), mesurée en parties par 10 millions ; valeur plus élevée = plus de pollution.
- **RM** : nombre moyen de **pièces (rooms)** par logement — indicateur direct de la taille du logement.
- **AGE** : part des logements occupés par leur propriétaire construits **avant 1940** (pourcentage) — mesure de l’ancienneté du parc immobilier.
- **DIS** : distance pondérée (distance “harmonisée”) aux **cinq centres d’emploi** de Boston — mesure d’accessibilité à l’emploi.
- **RAD** : indice d’**accessibilité aux autoroutes radiales** (plus la valeur est grande, meilleure est l’accessibilité routière).
- **TAX** : taux d’**imposition foncière** (full-value property-tax rate) par tranche de 10 000$ — indicateur fiscal local.
- **PTRATIO** : ratio **élèves/professeur** dans la ville (pupil-teacher ratio) — proxy pour la qualité des écoles.
- **B** : transformée `1000*(Bk - 0.63)^2` où **Bk** est la proportion de population noire par ville ; c’est une variable démographique transformée.
- **LSTAT** : pourcentage de la population de **statut socio-économique bas** — généralement corrélé négativement avec le prix des logements.
- **MEDV** : **valeur médiane** des logements occupés par leur propriétaire (en milliers de dollars, $1000s).  
  👉 **Cible (target)** à prédire dans un modèle de Machine Learning.

---

## 🎯 Objectif du dataset

Ce dataset est largement utilisé dans le cadre de l’apprentissage automatique pour :  
- La **régression** (prédire le prix médian des logements).  
- L’analyse de l’impact des facteurs socio-économiques et environnementaux sur les prix immobiliers.  

---

## 📌 Source

Dataset disponible via ce [Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Housing).
