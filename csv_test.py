import csv
from io import StringIO

def print_dialect(dialect):
    print('dialect: {}'.format(dialect))
    print('dialect.delimiter: {}'.format(dialect.delimiter))
    print('dialect.escapechar: {}'.format(dialect.escapechar))
    print('dialect.lineterminator: {}'.format(dialect.lineterminator))
    print('dialect.quotechar: {}'.format(dialect.quotechar))
    print('dialect.quoting: {}'.format(dialect.quoting))
    print('dialect.skipinitialspace: {}'.format(dialect.skipinitialspace))


#print('dialects: {}'.format(csv.list_dialects()))

s = input('input a list: ')
buffer = StringIO(s)

dialect = csv.Sniffer().sniff(s)
dialect.skipinitialspace = True
print_dialect(dialect)

reader = csv.reader(buffer, dialect)
for line in reader:
        print(line)


#reader = csv.reader(s, dialect)


#row = next(reader)
#print('row: {}'.format(row))
