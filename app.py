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

        if self.occupied_tables < self.tables.capacity:
            with self.tables.request() as table:
                yield table

                self.occupied_tables += 1
                table_allocation_time = self.env.now
                reservation_duration = random.randint(30, 120)
                self.reservations.append((guest, arrival_time, table_allocation_time, reservation_duration))
                formatted_time = self.format_time(self.env.now)
                print(f"{guest} gets a table at time {formatted_time}, reservation duration: {reservation_duration} min")

                # Gost ostavlja rating od 1-5
                feedback_rating = random.randint(1, 5)  
                self.guest_feedback.append((guest, feedback_rating))
                print(f"{guest} provides feedback: Rating - {feedback_rating}")
                
                self.env.process(self.end_reservation(guest, arrival_time, reservation_duration))

        else:
            # Ako su sve stolice zauzete, dodaj gosta na listu čekanja.
            self.waiting_list.append((guest, self.env.now))
            formatted_time = self.format_time(self.env.now)
            print(f"{guest} added to the waiting list at time {formatted_time}")


    def end_reservation(self, guest, arrival_time, reservation_duration):
        yield self.env.timeout(reservation_duration)
        self.occupied_tables -= 1
        formatted_time = self.format_time(arrival_time + reservation_duration)
        print(f"{guest} leaves restaurant at time {formatted_time}")
        # Rasporedi poziv za seat_guest_from_waiting_list nakon proteka vremena.
        self.env.process(self.seat_guest_from_waiting_list())
        
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

    def seat_guest_from_waiting_list(self):

        if self.waiting_list and self.occupied_tables < self.tables.capacity:
            waiting_guest = min(self.waiting_list, key=lambda x: x[1])
            guest, arrival_time = waiting_guest

            # Pokušaj zatražiti stol za gosta na čekanju.
            with self.tables.request() as table:
                yield table

                self.occupied_tables += 1
                table_allocation_time = self.env.now
                reservation_duration = random.randint(30, 120)
                self.reservations.append((guest, arrival_time, table_allocation_time, reservation_duration))
                leaving_time=self.env.now
                formatted_time = self.format_time(leaving_time)
                print(f"{guest} from the waiting list gets a table at time {formatted_time}, reservation duration: {reservation_duration} min")

                # Gost ostavlja rating od 1-5
                feedback_rating = random.randint(1, 5)  
                self.guest_feedback.append((guest, feedback_rating))
                print(f"{guest} provides feedback: Rating - {feedback_rating}")

                self.env.process(self.end_reservation(guest, leaving_time, reservation_duration))

                # Ukloni gosta koji je dobio stol sa liste čekanja.
                self.waiting_list.remove(waiting_guest)

def show_graph(reservations, waiting_list, feedback):
    guest_names = [reservation[0] for reservation in reservations]
    durations = [reservation[3] for reservation in reservations]

    waiting_list_times = [entry[0] for entry in waiting_list]
    waiting_list_markers = [entry[1] for entry in waiting_list]

    feedback_times = [entry[0] for entry in feedback]
    feedback_ratings = [entry[1] for entry in feedback]

    fig, ax1 = plt.subplots()

    # Kreiraj bar graf za prikaz rezervacija
    ax1.bar(guest_names, durations, label='Reservations', color='#58508d', width=0.4)

    ax1.scatter(waiting_list_times, waiting_list_markers, color='red', marker='x', label='Waiting List')

    ax1.set_xlabel('Guests')
    ax1.set_ylabel('Reservation Duration (min)', color='#58508d')
    ax1.tick_params('y', colors='#58508d')

    # Sekundarna y osa za rating
    ax2 = ax1.twinx()
    scatter_ratings = ax2.scatter(feedback_times, feedback_ratings, color='#f95d6a', marker='o', label='Feedback Ratings')
    ax2.set_ylabel('Feedback Ratings', color='#f95d6a')
    ax2.tick_params('y', colors='#f95d6a')

    handles, labels = ax1.get_legend_handles_labels()
    handles.append(scatter_ratings)
    labels.append('Feedback Ratings')

    ax1.legend(handles, labels, loc='upper left', bbox_to_anchor=(1.1,1) )

    fig.suptitle('Reservations at the restaurant')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def create_guests(env, restaurant, names):
    for name in names:
        arrival_time = env.now
        yield env.timeout(random.uniform(0.5, 2.5))

        with restaurant.tables.request():
            env.process(guest(env, name, restaurant))

def guest(env, name, restaurant):
    formatted_arrival_time = restaurant.format_time(env.now)
    print(f"{name} arrives to the restaurant at time {formatted_arrival_time}")
    yield env.process(restaurant.reserve_table(name))


# Stvarna imena gostiju
guest_names = ["John", "Emma", "Michael", "Sophia", "Daniel", "Olivia"]

# Povećanje kapaciteta restorana
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
env.run(until=180)    # Simuliraj do 3 sata (180 minuta)

# Prikazivanje grafikona
show_graph(restaurant.reservations, restaurant.waiting_list, restaurant.guest_feedback)