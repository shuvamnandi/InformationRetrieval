import mysql.connector


class MySQL(object):
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.db_connection = mysql.connector.connect(host =self.host,
                                                     database=self.database,
                                                     user=self.user,
                                                     password=self.password)
        self.db_cursor = self.db_connection.cursor()

    def insert_query(self, insert_query, values):
        try:
            self.db_cursor.execute(insert_query, values)
            self.db_connection.commit()
        except Exception as error:
            print error
            self.db_connection.rollback()

    def execute_query(self, sql_query):
        try:
            self.db_cursor.execute(sql_query)

            if sql_query[:6].lower() == "select" or sql_query[1:7].lower() == "select":
                # print "inside if"
                return self.db_cursor.fetchall()
            self.db_connection.commit()
        except Exception as error:
            print error
            self.db_connection.rollback()

    def close(self):
        self.db_connection.close()


def __main__():
    mysql_obj = MySQL()
    # mysql_obj.execute_query("DELETE from Crawl")
    # result = mysql_obj.execute_query("SELECT * from Crawl")
    # for id in result:
    #      print "{}: 1. {} 2. ".format(id, id, id)
    #
# if __name__ == __main__():
#     __main__()
