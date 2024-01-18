import simpy
import random
import matplotlib.pyplot as plt

class Restaurant:
    def __init__(self, env, initial_capacity, maximum_capacity):
        self.env = env
        self.tables = simpy.Resource(env, capacity=initial_capacity)
        self.maximum_capacity = maximum_capacity
        self.reservations = []

    def reserve_table(self, guest):
        with self.tables.request() as table:
            yield table
            reservation_duration = random.randint(30, 120)
            self.reservations.append((guest, self.env.now, reservation_duration))
            formatted_time = self.format_time(self.env.now)
            print(f"{guest} gets a table at time {formatted_time}, reservation duration: {reservation_duration} min")

    def format_time(self, minutes):
        hours = minutes // 60
        minutes %= 60
        return f"{int(hours):02d}:{int(minutes):02d}"

    def optimize_capacity(self):
        current_capacity = len(self.tables.users)
        if current_capacity < self.maximum_capacity and len(self.tables.queue) > 3:
            new_capacity = min(self.maximum_capacity, current_capacity + 3)
            self.tables.capacity = new_capacity
            formatted_time = self.format_time(self.env.now)
            print(f"Optimization: Increased capacity to {new_capacity} at time {formatted_time}")
            yield self.env.timeout(1)

def show_graph(reservations):
    times = [reservation[1] for reservation in reservations]
    durations = [reservation[2] for reservation in reservations]

    plt.step(times, durations, where='post')
    plt.xlabel('Time (min)')
    plt.ylabel('Reservation Duration (min)')
    plt.title('Reservations at the restaurant')
    plt.show()

def create_guests(env, restaurant, names):
    for name in names:
        arrival_time = env.now
        yield env.timeout(random.uniform(0.5, 2.5))
        env.process(guest(env, name, restaurant))

def guest(env, name, restaurant):
    formatted_arrival_time = restaurant.format_time(env.now)
    print(f"{name} arrives to the restaurant at time {formatted_arrival_time}")
    yield env.process(restaurant.reserve_table(name))

# Stvarna imena gostiju
guest_names = ["John", "Emma", "Michael", "Sophia", "Daniel", "Olivia"]

# Povećani kapacitet restorana
restaurant_capacity = 8

env = simpy.Environment()
restaurant = Restaurant(env, initial_capacity=restaurant_capacity, maximum_capacity=15)

def report(restaurant):
    print("\nFinal report: ")
    print("Number of reservations:", len(restaurant.reservations))
    print("Longest reservation duration:", max(reservation[2] for reservation in restaurant.reservations), "min")
    print("Average reservation duration:", sum(reservation[2] for reservation in restaurant.reservations) / len(restaurant.reservations), "min")

# Pokreni simulaciju s različitim vremenima dolaska i stvarnim imenima
env.process(create_guests(env, restaurant, guest_names))
env.run(until=120)  # Simuliraj do 2 sata (120 minuta)

# Prikazivanje grafikona
show_graph(restaurant.reservations)