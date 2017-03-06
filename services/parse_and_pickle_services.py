from Registry import Registry
import cPickle as pickle
import os
import sys


if __name__ == "__main__":
    # Check that the user has enter enough args.
    if len(sys.argv) != 3:
        print("Pickles service entries for later frequency analysis. Place exported SYSTEM hives"
              " within directories indicating which system the data is from, and point this script at their "
              "root folder.")
        print("Usage: input_dir output_dir")
        print("\nExample:")
        print("-" * 50)
        print(r"c:\exported_system_hives c:\results")
        sys.exit()

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pickle_dir = os.path.join(output_dir, "pickle")
    if not os.path.exists(pickle_dir):
        os.makedirs(pickle_dir)

    results = {}
    for path, dirs, files in os.walk(input_dir):
        for filename in files:
            fullpath = os.path.join(path, filename)
            system = os.path.split(path)[1]
            results[system] = []
            # Get the services.
            registry = Registry.Registry(fullpath)

            # Determine current control set.
            control_set = registry.open("Select")
            current_control_set = control_set.value("Current").value()
            if current_control_set < 10:
                current_control_set = "00" + str(current_control_set)
            else:
                current_control_set = "0" + str(current_control_set)

            # Open services key and get results.
            services = registry.open("ControlSet{}\Services".format(current_control_set))
            for service in services.subkeys():
                # noinspection PyBroadException
                try:
                    display_name = service.value("DisplayName").value()
                except:
                    display_name = "Not Present"

                # noinspection PyBroadException
                try:
                    description = service.value("Description").value()
                except:
                    description = "Not Present"

                # noinspection PyBroadException
                try:
                    image_path = service.value("ImagePath").value()
                except:
                    image_path = "Not Present"

                # noinspection PyBroadException
                try:
                    service_dll = service.subkey("Parameters").value("ServiceDll").value()
                except:
                    service_dll = "Not Present"

                results[system].append((display_name, description, image_path, service_dll))

    # Write the data to disk.
    pickle.dump(results, open(os.path.join(pickle_dir, "services.p"), "wb"))
