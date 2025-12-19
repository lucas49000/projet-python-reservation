#Projet 2 phyton

from datetime import date


#  Vehicules 
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
        return f"{self.categorie} {self.marque} {self.modele} - {etat}"


class voiture(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Voiture", tarif)


class Camion(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Camion", tarif)


class Moto(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Moto", tarif)


# client
class Client:
    def __init__(self, id, nom, prenom, age, permis):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.permis = permis
        self.historique = []

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.age} ans)"


# Location
class location:
    def __init__(self, customer, vehicle, début_date, fin_date):
        self.customer = customer
        self.vehicle = vehicle
        self.début_date = début_date
        self.fin_date = fin_date
        self.total_cost = self.calculate_cost()

    def calculate_cost(self):
        nb_jours = (self.fin_date - self.début_date).days
        return nb_jours * self.vehicle.tarif

    def __str__(self):
        return (f"Location de {self.vehicle} par {self.customer} "
                f"du {self.début_date} au {self.fin_date} "
                f"= {self.total_cost}€")


# système de location
class systeme_location_voiture:
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
            print("Véhicule indisponible")
            return

        if start_date >= end_date:
            print("Dates invalides")
            return

        rental = location(customer, vehicule, start_date, end_date)
        self.rentals.append(rental)
        customer.historique.append(rental)
        vehicule.disponible = False

        print("Location enregistrée")
        print(rental)

    def available_vehicles(self):
        return [v for v in self.vehicles if v.disponible]

    def revenue(self):
        return sum(r.total_cost for r in self.rentals)


# test du système
if __name__ == "__main__":
    system = systeme_location_voiture()

    voiture1 = voiture(1, "Peugeot", "208", 40)
    moto1 = Moto(2, "Yamaha", "MT-07", 30)

    client1 = Client(1, "Raimbaut", "Lucas", 18, True)

    system.add_vehicle(voiture1)
    system.add_vehicle(moto1)
    system.add_customer(client1)

    system.rent_vehicle(
        client1,
        car1,
        date(2025, 12, 1),
        date(2025, 12, 5)
    )

    print("\nVéhicules disponibles :")
    for v in system.available_vehicles():
        print(v)

    print("\nChiffre d'affaires :", system.revenue(), "€")