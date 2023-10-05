from datetime import datetime, timedelta
from math import ceil
import itertools
import pandas as pd
import copy


class Container:
    def __init__(self, release_time, due_time):
        self.release_time = release_time
        self.due_time = due_time

    def __str__(self):
        return f"Container(release_time={self.release_time}, due_time={self.due_time})"


class Barge:
    def __init__(self, departure_time, containers):
        self.departure_time = departure_time
        self.containers = containers

    def calculate_cost(self):
        delay_hours = 0

        for container in self.containers:
            delay_seconds = max(
                0,
                (
                    self.departure_time + timedelta(hours=10) - container.due_time
                ).total_seconds(),
            )
            delay_hours += ceil(delay_seconds / 3600)

        return delay_hours * 10

    def add_container(self, container):
        self.containers.append(container)
        self.departure_time = max(container.release_time, self.departure_time)

    def __str__(self):
        return (
            f"Barge(departure_time={self.departure_time}, containers={self.containers})"
        )


def main():
    # Replace 'your_file.xlsx' with the actual path to your Excel file
    file_path = 'freight_data.xlsx'

    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    containers = []

    # Loop over the rows and access the values
    for index, row in df.iterrows():
        release_date = row['Release date'].date()
        release_time = row['Release time']
        due_date = row['Due date'].date()
        due_time = row['Due time']

        release_t = datetime(release_date.year, release_date.month, release_date.day, release_time.hour, release_time.minute)
        due_t = datetime(due_date.year, due_date.month, due_date.day, due_time.hour, due_time.minute)

        containers.append(Container(release_t, due_t))

    # Create barges
    barges = [
        Barge(
            departure_time=datetime(year=1, month=1, day=1, hour=1, minute=1),
            containers=[],
        ),
        Barge(
            departure_time=datetime(year=1, month=1, day=1, hour=1, minute=1),
            containers=[],
        ),
        Barge(
            departure_time=datetime(year=1, month=1, day=1, hour=1, minute=1),
            containers=[],
        ),
    ]

    result = "LoL"

    num_containers = len(containers)
    num_barges = 3
    min_cost = 2**63
    barge_capacity = 30

    print("Calculation started! Hold tight...")
    start_time = datetime.now()

    for assignment_tuple in itertools.product(range(num_barges), repeat=num_containers):
        assignments = list(assignment_tuple)

        for barge in barges:
            barge.departure_time = datetime(year=1, month=1, day=1, hour=1, minute=1)
            barge.containers = []


        if (assignments.count(0) > barge_capacity or assignments.count(1) > barge_capacity or assignments.count(2) > barge_capacity):
            continue

        for i, assignment in enumerate(assignments):
            barges[assignment].add_container(containers[i])

        curr_cost = 0

        for barge in barges:
            curr_cost += barge.calculate_cost()

        if min_cost > curr_cost:
            result = assignments
            min_cost = curr_cost

        min_cost = min(curr_cost, min_cost)

    print(f"Calculation ended! It took {datetime.now() - start_time} seconds")
    print(min_cost)
    print(result)
    

if __name__ == '__main__':
    main()
