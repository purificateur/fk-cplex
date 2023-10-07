from datetime import datetime, timedelta
import pandas as pd
from w_cplex import cplex_solution


# Class representing a container
class Container:
    def __init__(self, release_time, due_time, cluster=None):
        self.release_time = release_time
        self.due_time = due_time
        self.cluster = cluster

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
    containers_1 = parse_containers("clustering_1.xlsx")
    containers_2 = parse_containers("clustering_2.xlsx")

    # Create barges
    barges = [Barge(), Barge(), Barge()]
    barges_1 = [Barge(), Barge(), Barge()]
    barges_2 = [Barge(), Barge(), Barge()]

    # Add containers to the barges according to the clusters
    fill_barges(containers_1, barges_1)
    fill_barges(containers_2, barges_2)

    # Add containers to the barges according to the cplex result
    for idx, container in enumerate(cplex_solution):
        i = container.index(max(container))
        barges[i].add_container(containers[idx])

    # Calculate cost per barge and add it to the final cost (result)
    cplex_result = get_total_cost(barges)
    cluster_1_result = get_total_cost(barges_1)
    cluster_2_result = get_total_cost(barges_2)

    # Print the results
    print(f"CPLEX Result: {cplex_result}")  # 7604.5
    print(f"Clustering 1 Result: {cluster_1_result}")  # 8465.999999999998
    print(f"Clustering 2 Result: {cluster_2_result}")  # 18369.000000000004


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
        cluster = row["Cluster"] if "Cluster" in row else None

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
        containers.append(Container(release_t, due_t, cluster))

    return containers


def get_total_cost(barges):
    result = 0
    for b in barges:
        result += b.calculate_cost()

    return result


def fill_barges(containers, barges):
    for container in containers:
        barges[container.cluster].add_container(container)


if __name__ == "__main__":
    main()
