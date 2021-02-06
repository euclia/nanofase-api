import csv
from csv import reader
import codecs


def read():
    with open("/home/pantelispanka/Jaqpot/nanofase-api/src/data/x9jAMcvG!SMAKm/output_soil.csv", newline='', mode='r') as csvfile:
        csv_reader = reader(csvfile)
        # Iterate over each row in the csv using reader object
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            print(row)


read()
