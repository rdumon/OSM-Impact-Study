import sys
import psycopg2

class DB(object):
    """encaspulate a database connection."""

    def __init__(self,config):
        try:
            self.connection = psycopg2.connect("dbname='"+config['DB_NAME']+"' user='"+config['DB_USER']+"' password='"+config['DB_PWD']+"' host='"+config['DB_HOST']+"' port='"+config['DB_PORT']+"'")
        except:
            print('\033[91m'+"Unable to connect to the database."+'\033[0m')
            sys.exit(-1)
        print("Connected to db!")

    def execute(self,commands=[]):

        try:
            cur = self.connection.cursor()
            # create table one by one
            for command in commands:
                cur.execute(command)

            result = cur.fetchall()

            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            self.connection.commit()
            return result

        except (Exception, psycopg2.DatabaseError) as error:
            print('\033[91m'+"\nSQL ERROR:\n"+str(error)+'\033[0m')
            sys.exit(-1)
