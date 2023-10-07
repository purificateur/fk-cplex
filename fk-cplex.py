from datetime import datetime, timedelta
import pandas as pd
from cplex_solution import cplex_solution
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


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
    cluster_1_containers = parse_containers("clustering_1.xlsx")
    cluster_2_containers = parse_containers("clustering_2.xlsx")

    # Create barges
    barges = [Barge(), Barge(), Barge()]
    cluster_1_barges = [Barge(), Barge(), Barge()]
    cluster_2_barges = [Barge(), Barge(), Barge()]

    # Add containers to the barges according to the clusters
    fill_barges(cluster_1_containers, cluster_1_barges)
    fill_barges(cluster_2_containers, cluster_2_barges)

    # Add containers to the barges according to the cplex result
    cplex_labels = []
    for idx, container in enumerate(cplex_solution):
        i = container.index(max(container))
        cplex_labels.append(i)
        barges[i].add_container(containers[idx])

    # Calculate cost per barge and add it to the final cost (result)
    cplex_result = get_total_cost(barges)
    cluster_1_result = get_total_cost(cluster_1_barges)
    cluster_2_result = get_total_cost(cluster_2_barges)

    # Print the results
    print(f"CPLEX Result: {cplex_result}")              # 7604.5
    print(f"Clustering 1 Result: {cluster_1_result}")   # 8466
    print(f"Clustering 2 Result: {cluster_2_result}")   # 18369

    # Display confusion matrixes
    generate_confusion_matrices(
        cluster1=list(map(lambda c: c.cluster, cluster_1_containers)),
        cluster2=list(map(lambda c: c.cluster, cluster_2_containers)),
        cplex=cplex_labels,
    )


def parse_containers(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    containers = []

    # Loop over the rows and read containers
    for _, row in df.iterrows():
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


def generate_confusion_matrices(cluster1, cluster2, cplex):
    def create_plot(cluster, index):
        confusion = confusion_matrix(cplex, cluster)

        cm_display = ConfusionMatrixDisplay(confusion_matrix=confusion)
        cm_display.plot()

        plt.xlabel(f"K-Means Cluster {index}")
        plt.ylabel("CPLEX Solution")

    # Create the two plots and reorder the barges in
    # order to match it with out CPLEX allocation
    create_plot(list(map(lambda c: 2 - c, cluster1)), 1)
    create_plot(list(map(lambda c: 2 - c, cluster2)), 2)

    plt.show()


if __name__ == "__main__":
    main()
