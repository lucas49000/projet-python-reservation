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


class Car(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Voiture", tarif)


class Truck(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Camion", tarif)


class Motorcycle(Vehicule):
    def __init__(self, id, marque, modele, tarif):
        super().__init__(id, marque, modele, "Moto", tarif)


# ===== CUSTOMER =====
class Customer:
    def __init__(self, id, nom, prenom, age, permis):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.age = age
        self.permis = permis
        self.historique = []

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.age} ans)"


# ===== RENTAL =====
class Rental:
    def __init__(self, customer, vehicle, start_date, end_date):
        self.customer = customer
        self.vehicle = vehicle
        self.start_date = start_date
        self.end_date = end_date
        self.total_cost = self.calculate_cost()

    def calculate_cost(self):
        nb_jours = (self.end_date - self.start_date).days
        return nb_jours * self.vehicle.tarif

    def __str__(self):
        return (f"Location de {self.vehicle} par {self.customer} "
                f"du {self.start_date} au {self.end_date} "
                f"= {self.total_cost}€")


# ===== CENTRAL SYSTEM =====
class CarRentalSystem:
    def __init__(self):
        self.vehicles = []
        self.customers = []
        self.rentals = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def add_customer(self, customer):
        self.customers.append(customer)

    def rent_vehicle(self, customer, vehicle, start_date, end_date):
        if not vehicle.disponible:
            print("❌ Véhicule indisponible")
            return

        if start_date >= end_date:
            print("❌ Dates invalides")
            return

        rental = Rental(customer, vehicle, start_date, end_date)
        self.rentals.append(rental)
        customer.historique.append(rental)
        vehicle.disponible = False

        print("✅ Location enregistrée")
        print(rental)

    def available_vehicles(self):
        return [v for v in self.vehicles if v.disponible]

    def revenue(self):
        return sum(r.total_cost for r in self.rentals)


# ===== TEST =====
if __name__ == "__main__":
    system = CarRentalSystem()

    car1 = Car(1, "Peugeot", "208", 40)
    moto1 = Motorcycle(2, "Yamaha", "MT-07", 30)

    client1 = Customer(1, "Raimbaut", "Lucas", 18, True)

    system.add_vehicle(car1)
    system.add_vehicle(moto1)
    system.add_customer(client1)

    system.rent_vehicle(
        client1,
        car1,
        date(2025, 12, 1),
        date(2025, 12, 5)
    )

    print("\n🚗 Véhicules disponibles :")
    for v in system.available_vehicles():
        print(v)

    print("\n💰 Chiffre d'affaires :", system.revenue(), "€")