#!/usr/bin/env python3
import csv
import sys
import os
from collections import Counter
from operator import itemgetter
import xmltodict


def parse_scheduled_tasks():
    """Parses the xml tasks."""
    all_tasks = []
    for path, dirs, files in os.walk(input_dir):
        for filename in files:
            system = os.path.split(path)[1]
            fullpath = os.path.join(path, filename)
            extracted_tasks, temp_paths = [], []
            with open(fullpath, "r") as f:
                line_counter = 0
                record = ""
                for line in f:
                    line_counter += 1
                    if line_counter == 2:
                        continue
                    if "<!-- " in line or "<?xml version=\"1.0" in line:
                        continue
                    record += line
                    if "</Task>" in line:
                        extracted_tasks.append(record)
                        record = ""

            # Get an ordered dict from the line
            structured_tasks = [xmltodict.parse(task) for task in extracted_tasks]

            # Now we add a list of tasks for the system in focus.
            tasks = []
            for task in structured_tasks:
                try:
                    if "Exec" in task["Task"]["Actions"]:
                        if type(task["Task"]["Actions"]["Exec"]) is list:
                            for command in task["Task"]["Actions"]["Exec"]:
                                if command["Command"]:
                                    tasks.append(command["Command"])
                        else:
                            if task["Task"]["Actions"]["Exec"]["Command"]:
                                tasks.append(task["Task"]["Actions"]["Exec"]["Command"])
                except KeyError:
                    pass

            # We de-dupe this so that we have unique executions per system (we are looking for PRESENCE of executables
            # And not their frequency of execution).
            for item in list(set(tasks)):
                if ":" in item:
                    index = item.find(":")
                    all_tasks.append(item[index + 1:])
                    temp_paths.append(item[index + 1:])
                else:
                    all_tasks.append(item)
                    temp_paths.append(item)

            create_lookups(data=temp_paths, system=system)

    frequency_analysis(tasks=all_tasks)


def create_lookups(system=None, data=None):
    """Creates a master list of all schtasks."""
    lookup_path = os.path.join(output_dir, "lookups")
    if not os.path.exists(lookup_path):
        os.makedirs(lookup_path)

    lookup_file = os.path.join(lookup_path, "schtasks_all.csv")
    if not os.path.exists(lookup_file):
        with open(lookup_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Path", "Host"])

    with open(lookup_file, "a", encoding="utf-8", newline="") as f:
        for item in data:
            writer = csv.writer(f)
            writer.writerow([item, system])


def frequency_analysis(tasks=None):
    """Conducts the frequency analysis."""
    results = []
    commands = dict(Counter(tasks))

    for command, frequency in dict.items(commands):
        results.append([command, frequency])
    sorted_results = sorted(results, key=itemgetter(1))

    with open(os.path.join(output_dir, "scheduled_tasks.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Command", "Count"])
        for item in sorted_results:
            command, frequency = item
            writer.writerow([command, frequency])


if __name__ == "__main__":
    # Check that the user has enter enough args.
    if len(sys.argv) != 3:
        print("Conducts frequency analysis of exported scheduled task xml files. Place exported XML files"
              " within directories indicating which system the data is from, and point this script at their "
              "root folder.")
        print("\nUsage: input_dir output_dir")
        print("\nExample:")
        print("-" * 50)
        print(r"c:\exported_scheduled_tasks_xml c:\results")
        sys.exit()

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    parse_scheduled_tasks()
