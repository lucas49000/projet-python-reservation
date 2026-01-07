from datetime import date

# Classes Véhicules 
class Vehicule:
    def __init__(self, id, marque, modele, categorie, tarif):
        self.id = id
        self.marque = marque
        self.modele = modele
        self.categorie = categorie
        self.tarif = tarif
        self.disponible = True

    def __str__(self):
        etat = "Disponible" if self.disponible else "Loué"
        return f"[{self.categorie}] {self.marque} {self.modele} - {etat} ({self.tarif}€/j)"

class Voiture(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Voiture", tarif)

class Camion(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Camion", tarif)

class Moto(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Moto", tarif)


# Classe Clien
class Client:
    def __init__(self, id, nom, prenom, age, permis):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.permis = permis
        self.historique = []

    def __str__(self):
        return f"Client: {self.prenom} {self.nom} ({self.age} ans)"


# Classe Location 
class Location:
    def __init__(self, customer, vehicle, debut_date, fin_date):
        self.customer = customer
        self.vehicle = vehicle
        self.debut_date = debut_date
        self.fin_date = fin_date
        self.total_cost = self.calculate_cost()

    def calculate_cost(self):
        # Calcule la différence en jours
        delta = self.fin_date - self.debut_date
        nb_jours = delta.days
        if nb_jours < 1: nb_jours = 1 # Minimum 1 jour facturé
        return nb_jours * self.vehicle.tarif

    def __str__(self):
        return (f"Location: {self.vehicle.marque} {self.vehicle.modele} "
                f"pour {self.customer.prenom} "
                f"(Total: {self.total_cost}€)")


#  Système de Gestion
class SystemeLocationVoiture:
    def __init__(self):
        self.vehicules = []
        self.customers = []
        self.rentals = []

    def add_vehicle(self, vehicule):
        self.vehicules.append(vehicule)

    def add_customer(self, customer):
        self.customers.append(customer)

    def rent_vehicle(self, customer, vehicule, start_date, end_date):
        if not vehicule.disponible:
            print(f"Erreur: Le véhicule {vehicule.marque} est déjà loué.")
            return

        if start_date >= end_date:
            print("Erreur: Les dates sont invalides.")
            return

        # Création de la location
        rental = Location(customer, vehicule, start_date, end_date)
        self.rentals.append(rental)
        customer.historique.append(rental)
        
        # Mise à jour de la disponibilité
        vehicule.disponible = False

        print("--> Location enregistrée avec succès !")
        print(rental)

    def available_vehicles(self):
        # Retourne la liste des véhicules où disponible est True
        return [v for v in self.vehicules if v.disponible]

    def revenue(self):
        # Somme des coûts de toutes les locations
        return sum(r.total_cost for r in self.rentals)

