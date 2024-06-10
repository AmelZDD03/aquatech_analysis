import pandas as pd
import py7zr
import plotly.express as px


# Décompresser le fichier db.7z
with py7zr.SevenZipFile('db.7z', mode='r') as z:
    z.extractall("data")

# Lecture des fichiers CSV
sensors = pd.read_csv('data/sensors.csv') 
records = pd.read_csv('data/records.csv') 

print(sensors.isna().sum()) # 1 nan
print(records.isna().sum()) # 0 nan

#Calcul du total d'eau pour chaque sensor
totals = records.groupby('transmitter_addr')['value'].sum().reset_index()
totals.rename(columns = {"transmitter_addr":"sensor_addr", "value": "total"}, inplace = True)
totals.set_index("sensor_addr", inplace= True)


# Initialiser les fuites à 0
leaks = sensors[['sensor_addr']].copy()
leaks['total'] = 0

# Calculer les fuites pour chaque capteur parent
for parent in sensors['parent_addr'].unique():
    # gérer les valeurs manquantes
    if pd.isna(parent):
        continue
    # le total d'eau pour chaque parent
    parent_total = totals.loc[parent, 'total']
    # liste des enfants du parent
    childs_list = sensors[sensors["parent_addr"] == parent]["sensor_addr"].values
    # total d'eau des enfants du parent
    childs_total_values = totals.loc[childs_list, "total"].values.sum()
    if childs_total_values < parent_total:
        leaks.loc[leaks['sensor_addr'] == parent, "total"] = (parent_total - childs_total_values)

# Sauvegarder les résultats
totals.to_csv('output/totals.csv')
leaks.to_csv('output/leaks.csv', index=False)

# Data visualization
totals.reset_index(inplace=True)
fig1 = px.bar(totals, x = 'sensor_addr', y = 'total', title = "Total d'eau par capteur",
              labels = {'sensor_addr': 'Adresse du capteur', 'total': "Total d'eau (litres)"},
              hover_data = ['sensor_addr', 'total'])

# Visualisation des fuites par capteur
fig2 = px.bar(leaks, x= 'sensor_addr', y= 'total', title='Fuites par capteur',
              labels={'sensor_addr': 'Adresse du capteur', 'total': 'Total des fuites (litres)'},
              hover_data=['sensor_addr', 'total'])

# Enregistrer les graphiques interactifs sous forme de fichiers HTML
fig1.write_html('output/totals.html')
fig2.write_html('output/leaks.html')