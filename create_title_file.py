import csv

with open("title.basics.tsv") as basics:
    with open("new_title_updated.tsv", 'w') as output:
        tsvin = csv.reader(basics, delimiter='\t')
        csvout = csv.writer(output)
        for line in basics:
            items = line.split('\t')
            if items[1] == "tvSeries" or items[1] == "movie":
                try:
                    year = int(items[5])
                except:
                    year = 0
                if year > 2010:
                    csvout.writerow([items[2]])
