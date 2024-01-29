# Restaurant Reservation System Simulation

This Python simulation uses SimPy to model a restaurant with a reservation system. Guests arrive, request tables, and provide feedback based on their dining experience. The simulation also includes optimization features, such as increasing the restaurant's capacity during peak times.

## Introduction

This simulation models a restaurant with a reservation system. Guests arrive at random times, request tables, and may be placed on a waiting list if all tables are occupied. The system also collects feedback from guests, including a rating from 1 to 5.

## Features

- **Reservation System:** Guests can reserve tables, and the system allocates tables based on availability.
- **Waiting List:** If all tables are occupied, guests are added to a waiting list and seated as soon as a table becomes available.
- **Feedback Collection:** Guests provide feedback ratings upon leaving the restaurant.
- **Optimization:** The system dynamically increases the restaurant's capacity during peak times to accommodate more guests.

## Getting Started

Clone the repository to your local machine:

```bash
git clone https://github.com/NedzmijaMuminovic/Restaurant-Reservation-System
```
Navigate to the project directory:

```bash
cd Restaurant-Reservation-System
```

Install the required dependencies:
```bash
pip install simpy matplotlib
```
## Usage

Run the simulation using the provided script:

```bash
python app.py
```

Adjust the simulation parameters, such as the restaurant's initial and maximum capacity, guest names, and simulation duration, by modifying the script.

## Optimization

The simulation includes a capacity optimization feature. If the waiting list exceeds a threshold, the system increases the restaurant's capacity to accommodate more guests.

## Simulation Results

After running the simulation, a final report is generated, including the number of reservations, the longest reservation duration, and the average reservation duration. If feedback is collected, the average guest feedback rating is also displayed.

## Graphical Representation

A graphical representation of the simulation results is generated using Matplotlib. The graph shows the reservation durations over time, waiting list entries, and guest feedback ratings.
