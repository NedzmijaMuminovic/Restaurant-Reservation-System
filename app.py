import simpy
import random
import matplotlib.pyplot as plt

class Restaurant:
    def __init__(self, env, initial_capacity, maximum_capacity):
        self.env = env
        self.tables = simpy.Resource(env, capacity=initial_capacity)
        self.maximum_capacity = maximum_capacity
        self.reservations = []
        self.waiting_list = []
        self.occupied_tables = 0
        self.guest_feedback = []

    def reserve_table(self, guest):
        arrival_time = self.env.now

        if self.occupied_tables == self.maximum_capacity:
            # Svi stolovi su zauzeti, dodaje gosta u listu za čekanje
            self.add_to_waiting_list(guest, arrival_time)

        with self.tables.request() as table:
            yield table

            self.occupied_tables += 1
            table_allocation_time = self.env.now
            reservation_duration = random.randint(30, 120)
            self.reservations.append((guest, arrival_time, table_allocation_time, reservation_duration))
            formatted_time = self.format_time(self.env.now)
            print(f"{guest} gets a table at time {formatted_time}, reservation duration: {reservation_duration} min")

            yield self.env.timeout(reservation_duration)

            # Gost ostavlja rating od 1-5
            feedback_rating = random.randint(1, 5)  
            self.guest_feedback.append((guest, feedback_rating))
            print(f"{guest} provides feedback: Rating - {feedback_rating}")

            # Rezervacijsko vrijeme je isteklo, sjednite goste s liste čekanja
            yield self.env.process(self.seat_guest_from_waiting_list())

        self.occupied_tables -= 1

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

    def add_to_waiting_list(self, guest, arrival_time):
        self.waiting_list.append((guest, arrival_time))
        formatted_time = self.format_time(arrival_time)
        print(f"{guest} added to the waiting list at time {formatted_time}")

    def seat_guest_from_waiting_list(self):
        if self.waiting_list and self.occupied_tables < self.maximum_capacity:
            guest, arrival_time = self.waiting_list.pop(0)
            formatted_time = self.format_time(self.env.now)

            reservation_duration = random.randint(30, 120)
            yield self.env.timeout(reservation_duration)

            formatted_time = self.format_time(self.env.now)
            self.occupied_tables -= 1

def show_graph(reservations, waiting_list, feedback):
    times = [reservation[0] for reservation in reservations]
    durations = [reservation[1] for reservation in reservations]

    waiting_list_times = [entry[0] for entry in waiting_list]
    waiting_list_markers = [entry[1] for entry in waiting_list]

    feedback_times = [entry[0] for entry in feedback]
    feedback_ratings = [entry[1] for entry in feedback]

    plt.step(times, durations, where='post', label='Reservations')
    plt.scatter(waiting_list_times, waiting_list_markers, color='red', marker='x', label='Waiting List')

    if feedback:
        plt.scatter(feedback_times, feedback_ratings, color='green', marker='o', label='Feedback Ratings')

    plt.xlabel('Time (min)')
    plt.ylabel('Reservation Duration (min)')
    plt.title('Reservations at the restaurant')
    plt.legend()
    plt.show()

def create_guests(env, restaurant, names):
    for name in names:
        arrival_time = env.now
        yield env.timeout(random.uniform(0.5, 2.5))

        with restaurant.tables.request() as table:
            env.process(guest(env, name, restaurant, table))

def guest(env, name, restaurant, table):
    formatted_arrival_time = restaurant.format_time(env.now)
    print(f"{name} arrives to the restaurant at time {formatted_arrival_time}")

    try:
        with table:
            yield env.process(restaurant.reserve_table(name))
    except simpy.Interrupt:
        print(f"{name} leaves the restaurant early.")

# Stvarna imena gostiju
guest_names = ["John", "Emma", "Michael", "Sophia", "Daniel", "Olivia"]

# POvećanje kapaciteta restorana
restaurant_capacity = 4

env = simpy.Environment()
restaurant = Restaurant(env, initial_capacity=restaurant_capacity, maximum_capacity=4)

def report(restaurant):
    print("\nFinal report: ")
    print("Number of reservations:", len(restaurant.reservations))
    print("Longest reservation duration:", max(reservation[3] for reservation in restaurant.reservations), "min")
    print("Average reservation duration:", sum(reservation[3] for reservation in restaurant.reservations) / len(restaurant.reservations), "min")
    if restaurant.guest_feedback:
        average_feedback = sum(feedback[1] for feedback in restaurant.guest_feedback) / len(restaurant.guest_feedback)
        print("Average guest feedback rating:", round(average_feedback, 2))

# Pokreni simulaciju s različitim vremenima dolaska i stvarnim imenima
env.process(create_guests(env, restaurant, guest_names))
env.run(until=120)    # Simuliraj do 2 sata (120 minuta)

# Prikazivanje grafikona
show_graph(restaurant.reservations, restaurant.waiting_list, restaurant.guest_feedback)