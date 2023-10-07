from datetime import datetime, timedelta
import pandas as pd
from w_cplex import cplex_solution


# Class representing a container
class Container:
    def __init__(self, release_time, due_time):
        self.release_time = release_time
        self.due_time = due_time

    def __str__(self):
        return f"Container(release_time={self.release_time}, due_time={self.due_time})"


# Class representing a barge
class Barge:
    def __init__(self):
        self.departure_time = datetime(year=1, month=1, day=1, hour=1, minute=1)
        self.containers = []

    # Calculates the cost of the barge
    def calculate_cost(self):
        delay_hours = 0

        for container in self.containers:
            delay_seconds = max(
                0,
                (
                    self.departure_time + timedelta(hours=10) - container.due_time
                ).total_seconds(),
            )
            delay_hours += delay_seconds / 3600

        return delay_hours * 10

    # Adds a container to the barge
    def add_container(self, container):
        self.containers.append(container)
        self.departure_time = max(container.release_time, self.departure_time)

    def __str__(self):
        return (
            f"Barge(departure_time={self.departure_time}, containers={self.containers})"
        )


def main():
    containers = parse_containers("freight_data.xlsx")

    # Create barges
    barges = [Barge(), Barge(), Barge()]

    # Add containers to the barges according to the cplex result
    for idx, container in enumerate(cplex_solution):
        i = container.index(max(container))
        barges[i].add_container(containers[idx])

    # Calculate cost per barge and add it to the final cost (result)
    result = 0
    for b in barges:
        result += b.calculate_cost()

    # Print the result
    print(result)


def parse_containers(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    containers = []

    # Loop over the rows and read containers
    for idx, row in df.iterrows():
        release_date = row["Release date"].date()
        release_time = row["Release time"]
        due_date = row["Due date"].date()
        due_time = row["Due time"]

        # Parse dates
        release_t = datetime(
            release_date.year,
            release_date.month,
            release_date.day,
            release_time.hour,
            release_time.minute,
        )
        due_t = datetime(
            due_date.year,
            due_date.month,
            due_date.day,
            due_time.hour,
            due_time.minute,
        )

        # Create the container and add it to the container list
        containers.append(Container(release_t, due_t))

    return containers


if __name__ == "__main__":
    main()
