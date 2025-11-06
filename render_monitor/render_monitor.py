import pandas as pd
import numpy as np
import os
import constants as ct

# Set the constants
csv = ct.csv
high_priority_show = ct.high_priority_show
priority_boost = ct.priority_boost
frame_time = ct.frame_time


class RenderDataLoader:
    def __init__(self, file_name):
        """
        Description:
        Reads in the most of to date CSV file and writes it back out.

        Input:
        file_name (str): The name of the csv file ex. 'render_jobs.csv'

        Output:
        self.csv = The string path to the file.
        self.rp = The open csv file.
        """

        # Adds the inputs to variables.
        self.file_name = file_name
        self.csv = None
        self.rp = None

    def find_latest_log(self):
        """
        Description:
        Using the same directory, it grabs the the path and finds the latest csv.

        Input:
        None

        Output:
        self.csv (str): The path of the latest csv.
        """
        # Gets the current working directory and its items.
        root = os.getcwd()
        items = os.listdir()

        # Grabs ths iteams that match the self.filename
        matching_files = [item for item in items if item.startswith(self.file_name)]

        # Grabs the full path of the matching files.
        full_paths = [os.path.join(root, f) for f in matching_files]

        # Rewrites self.csv into the most uptodate csv file in the dir.
        self.csv = max(full_paths, key=os.path.getmtime)

        return self.csv

    def read(self):
        """
        Description:
        Reads in the self.csv

        Input:
        None

        Output:
        self.rp (obj): The opened csv file.
        """
        # Opens the self.csv file into a new object.
        self.rp = pd.read_csv(self.csv)
        return self.rp

    def write(self):
        """
        Description:
        Writes out the self.rp to the self.csv path.

        Input:
        None

        Output:
        None.
        """
        # Writes the modifications back to the database.
        self.rp.to_csv(self.csv, index=False)


# Set the class
class RenderDataAnalyzer:
    def __init__(self, dataframe, high_priority_show, priority_boost, heuristic):
        """
        Description:
        Initialize the Object and sets the variables.

        Input:
        csv (str): Path to the csv file with the render farms data.
        high_priority_show(str): Name of the show you want to be promoted.

        Output:
        None
        """

        # Sets the values.
        self.rp = dataframe
        self.hps = high_priority_show
        self.priority_boost = priority_boost
        self.heuristic = heuristic

    def prioritize_night_renders(self):
        """
        Description:
        Uses the High Priority show name and sets its priority to highest.

        Input:
        None

        Output:
        None
        """
        # Prints the start of the funciton.
        print("\n -- 1. Setting Priorities --")

        # Selects the Pending and High Priorities shows.
        self.prime = (self.rp["Show Name"] == self.hps) & (
            self.rp["Status"] == "PENDING"
        )

        # Check if any jobs need prioritizing.
        if self.prime.any():
            # Gets the name of the jobs affected.
            renders_modified = self.rp[self.prime].shape[0]
            modified_jobs_ids = self.rp.loc[self.prime, "Job ID"].to_list()

            # Apply the priority to the selected shows.
            self.rp.loc[self.prime, "Priority"] = self.priority_boost

            # Modify the status.
            self.rp.loc[self.prime, "Status"] = "Overnight"

            print(f"Prioritized to {self.priority_boost} for {renders_modified}")
            print(modified_jobs_ids)
        else:
            print("No pending jobs.")

    def generate_report(self):
        """
        Description:
        Generates a report of all the requested jobs.

        Input:
        None

        Output:
        None
        """
        print("\n --Generating Reports--")

        # Set the requested and completed values.
        self.sum_requested = self.rp["Frames Requested"].sum()
        self.sum_completed = self.rp["Frames Completed"].sum()

        # Percentage formula
        if self.sum_requested > 0:
            # Get the percentage utility rate.
            self.util_rate = (self.sum_completed / self.sum_requested) * 100

            # Print the results.
            print(f"Total Frames Requested: {self.sum_requested}")
            print(f"Total Frame Completed: {self.sum_completed}")
            print(f"Farm Utilization: {self.util_rate:.2f}%")

        # Print kickback of no requests.
        else:
            print("No frames requested.")

    def generate_failure_report(self):
        """
        Description:
        Generates a report of all the failed render jobs and its time to be completed.

        Input:
        None

        Output:
        None.
        """
        # Starts the function.
        print("\n -- Failure Report--")

        # Set the columns to print.
        report_cols = [
            "Job ID",
            "Show Name",
            "Priority",
            "Frames Remaining",
            "Cleanup Time",
        ]

        # Filter the failed jobs in the csv.
        self.failed_jobs = self.rp[self.rp["Status"] == "FAILED"].copy()

        # Kickback if no failures.
        if self.failed_jobs.empty:
            print("No failed jobs.")
            return

        self.failed_jobs["Frames Remaining"] = (
            self.failed_jobs["Frames Requested"] - self.failed_jobs["Frames Completed"]
        )
        self.failed_jobs["Cleanup Time"] = (
            self.failed_jobs["Frames Remaining"] * self.heuristic
        )

        # Print failed jobs.
        print("The following jobs failed and need artist intervention:")
        print(self.failed_jobs[report_cols].to_markdown(index=False))


# Executes the function.
if __name__ == "__main__":
    # Loads the CSV.
    my_csv = RenderDataLoader(csv)
    my_csv.find_latest_log()
    my_csv.read()
    data = my_csv.rp

    # Passes the CSV
    my_renders = RenderDataAnalyzer(
        data, high_priority_show, priority_boost, frame_time
    )

    # Run the functions.
    my_renders.prioritize_night_renders()
    my_renders.generate_report()
    my_renders.generate_failure_report()

    # Update the csv.
    my_csv.rp = my_renders.rp

    # Exports the information
    my_csv.write()
