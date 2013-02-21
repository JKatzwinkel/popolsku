import unicodecsv as csv
import sqlite3

types    = ['INT, INTEGER, TINYINT, SMALLINT, MEDIUMINT, BIGINT, UNSIGNED BIG INT, INT2, INT8: INTEGER',
            'CHARACTER, VARCHAR, VARYING CHARACTER, NCHAR, NATIVE CHARACTER, NVARCHAR, TEXT, CLOB: TEXT',
            'BLOB: ',
            'REAL, DOUBLE, DOUBLE PRECISION, FLOAT: REAL',
            'NUMERIC, DECIMAL, BOOLEAN, DATE, DATETIME: NUMERIC']
            
            
struct= [map(lambda v: {v.strip().lower():correct.lower()}, invalids.split(',')) for invalids,correct in [line.partition(':')[0::2] for line in types]]
typemap={}
map(typemap.update, [inner for outer in struct for inner in outer])


connection = None

def import_csv(filename, table, columns=[], delimiters=[',','\t']):
    """Reads the specified csv file and converts its contents to a table in a sql database
    
    arguments:
        filename    -- the name of the csv file to read
        table       -- the name of the table which is desired to represent the file content in the datadase
        columns     -- a list of parameters for the table's columns. similar to the sqlite3 keywords that
                       would be the part of the sqlite3 query covering this column                  
                       (e.g. 'user_id integer primary key')
        delimiters  -- a list of delimiters to use. default is ','
    """
    global typemap, connection
    
    c = connection.cursor()
    
#   model = [attribute for column in constraints.split(',') for attribute in [column.strip().split(' ')]]
#   print model

    useinquery=[[]]
    primarykeys=set()

    for column in columns:
        useinquery.append([])
        stage=None
        for attr in column.split(' '):
            if attr in typemap:
#               print column, " %s -> %s " % (attr, typemap.get(attr))
                if any([keys in useinquery[-1] for keys in typemap.keys()]):
                    print column, "  Error: too many type identifier: %s " % attr
                else:
                    useinquery[-1].append(attr)
                continue
            if attr == 'primary':
#               print column, " is primary key "
                useinquery[-1].append(attr)
                continue
            if attr == 'key':
                if stage:
                    if stage == 'primary':
#                       print " primary key ok"
                        stage=None
                continue
            if attr == 'unique':
                useinquery[-1].append(attr)
                continue
            if any([key.endswith(attr) for key in typemap.keys()]):
                candidates=filter(lambda x:x.endswith(attr), typemap.keys())
                if attr in candidates:
                    if stage:
                        multiword=' '.join([stage, attr])
                        if multiword in candidates:
                            stage=None
                            useinquery[-1].append(typemap.get(multiword))
 #                         print column, " found multiword identifier for foreign type: %s -> %s " % (multiword, typemap.get(multiword))
                            continue
                            
            if stage:
                if not any([entry.startswith('$name:') for entry in useinquery[-1]]):
 #                 print column, " use %s as column title " % stage
                    useinquery[-1].append('$name:%s' % stage)
                    
            stage=attr
            
        if stage:
            if not any([entry.startswith('$name:') for entry in useinquery[-1]]):
#               print column, " use %s as column title " % stage
                useinquery[-1].append('$name:%s' % stage)
           
        name=[entry for entry in useinquery[-1] if entry.startswith('$name:')][0]
        useinquery[-1].remove(name)
        name=name.split(':')[1].strip('$')
        useinquery[-1]=[name]+useinquery[-1]
        
#       useinquery[-1]+=['not', 'null']
           
        if 'primary' in useinquery[-1]:
            primarykeys.add(name)
            useinquery[-1].remove('primary')
            
    query = 'create table if not exists %s ' % table
    query += '(%s%s) ' % (', '.join([' '.join(col) for col in useinquery if len(col)>0]),
                ['', ', primary key (%s)' % ', '.join([pk for pk in primarykeys])][len(primarykeys)>0]
                 )
    
    print query
    
    c.execute(query)
    
    query = 'insert or ignore into %s values (%s)' % (table, ', '.join(['?']*len(columns)))
    
    print '...opening %s ' % filename, 
    csvfile = open(filename, 'rb')

    for delimiter in delimiters:

        reader = csv.reader(csvfile, encoding='utf-8', delimiter=delimiter)

        print '...reading csv: '
        try:
            for row in reader:
                if reader.line_num < 3:
                    print '%s' % ','.join(row)
                c.execute(query, tuple(row))
            break
        except Exception as e:
            print '\nerror in line: %d; ' % reader.line_num
            print e
            
    connection.commit()
        
    csvfile.close()
                    



def connect_db(filename):

    global connection
    
    connection = sqlite3.connect(filename)
    print "settings up connection to splite3 database %s" % filename
#   return connection.cursor()


def disconnect_db():
    global connection
    print "close database"
    connection.close()


def main():

    connect_db("polymorf.sqlite3")
    sourcefile = "PoliMorf-0.6.1.tab"
    import_csv(sourcefile, "words", ["inflected text", "word text", "parameters text", "domain text"], ['\t'])
    disconnect_db()

