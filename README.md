jour = str(input("Quel jour de la semaine somme nous ?"))
date = int(input("Quel est la date aujourd'hui ?"))

if jour == "samedi" or jour == "dimanche":
    jour_txt = "du weekend"
else:
    jour_txt = "de la semaine"

if date <= 15:
    date_txt = "au debut de mois"
else:
    date_txt = "a la fin du mois"

print(f"{jour} est un jour {jour_txt} et appartient {date_txt} ")
