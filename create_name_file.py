import csv

with open("name.basics.tsv") as basics:
    with open("new_name_updated.tsv", 'w') as output:
        tsvin = csv.reader(basics, delimiter='\t')
        csvout = csv.writer(output)
        for line in basics:
            items = line.split('\t')
            if "act" in items[4] or "director" in items[4] or "producer" in items[4]:
                try:
                    year = int(items[3])
                except:
                    year = 3000
                if year > 2010:
                    csvout.writerow([items[1]])
