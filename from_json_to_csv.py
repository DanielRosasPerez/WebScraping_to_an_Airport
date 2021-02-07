import json, csv

with open("airport_data.json", 'r', encoding="utf-8") as json_file:
    airport_data = json.load(json_file)

    with open("airport_data.csv", 'w') as csv_outfile:
        field_names = [key for key in airport_data[0].keys()]
        csv_writer = csv.DictWriter(csv_outfile, fieldnames=field_names,
                                    lineterminator = '\n')

        csv_writer.writeheader()  # This way, we save the "field_names" as headers.
        for dct in airport_data:  # "dct" stands for "dictionary".
            csv_writer.writerow(dct)  # We pass every dictionary inside airport_data.

# NOTE: TO CHANGE YOUR "CSV" FILE TO AN "EXCEL FILE" (xlsx), JUST OPEN YOUR ORIGINAL FILE (The one that ends with "csv")
# AND LOOK FOR THE OPTION "Save as" AND  JUST SAVE IT AGAIN AS AN EXCEL FILE. That's all :)
