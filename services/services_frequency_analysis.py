#!/usr/bin/env python3
import csv
import os
import pickle
from collections import Counter
from operator import itemgetter
import sys


def parse_services():
    all_paths, processed_systems = [], []
    for system in services:
        # List to store the paths per system.
        temp_paths = []
        processed_systems.append(system)
        for service in services[system]:
            if service[2] == "Not Present":
                continue
            if service[3] == "Not Present":
                continue
            temp_paths.append(service[2])
            temp_paths.append(service[3])

        # We de-dupe this so that we have unique services per system (we are looking for PRESENCE of executables
        # And not their frequency of execution).
        for path in list(set(temp_paths)):
            if ":" in path:
                index = path.find(":")
                all_paths.append(path[index + 1:])
            else:
                all_paths.append(path)

        create_lookups(data=temp_paths, system=system)

    frequency_analysis(services_to_process=all_paths)


def create_lookups(system=None, data=None):
    """Creates a master list of all schtasks."""
    lookup_path = os.path.join(output_dir, "lookups")
    if not os.path.exists(lookup_path):
        os.makedirs(lookup_path)

    lookup_file = os.path.join(lookup_path, "services_all.csv")
    if not os.path.exists(lookup_file):
        with open(lookup_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Path", "Host"])

    with open(lookup_file, "a", encoding="utf-8", newline="") as f:
        for item in data:
            writer = csv.writer(f)
            writer.writerow([item, system])


def frequency_analysis(services_to_process=None):
    results = []
    paths = dict(Counter(services_to_process))

    for path, frequency in dict.items(paths):
        results.append([path, frequency])

    sorted_results = sorted(results, key=itemgetter(1), reverse=True)

    with open(os.path.join(output_dir, "services.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Path", "Count"])
        for item in sorted_results:
            path, frequency = item
            # Write the frequency analysis
            writer.writerow([path, frequency])


if __name__ == "__main__":
    # Check that the user has enter enough args.
    if len(sys.argv) != 3:
        print("Conducts frequency analysis of services. Point script to the \"pickle\" directory created by "
              "the script \"parse_and_pickle_services.py\".")
        print("\nUsage: input_dir output_dir")
        print("\nExample:")
        print("-" * 50)
        print(r"c:\pickle c:\results")
        sys.exit()

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    service_file = open(os.path.join(input_dir, "services.p"), "rb")
    services = pickle.load(service_file)
    parse_services()
