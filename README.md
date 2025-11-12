# render_monitor
From a CSV file produced by a render farm in the project folder. It produces a render status for the render jobs for TDs to analyze in the command line.

# The Problem.
Get a better clarification on the jobs status for each render project and get a better understading of the pandas library and CLI usage for render wrangler positions.

# The solution.
Grabs the CSV file and separate it using an algorithm. After it determine its status to either promote the job or to publish the status of the failed jobs.

# Libraries Used:
pandas, numpy, os, and tabulate

# How to use:
As long as you have your CSV in the same folder as your project, it should run, and print all the necessary information, and make the adjustments.
Run the main code in your CLI: 
python render_monitor 
