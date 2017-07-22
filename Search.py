#!/usr/bin/python

# TODO also search for actor>name, and dateadded

from Database import Database

class Search:

    def __init__(self, movie_root):
        self.movie_root = movie_root
        self.db = Database(movie_root)

    def get_sub_op(self, arg):
        if arg.startswith(">=") or arg.startswith("<="):
            sub_op = arg[:2]
            arg = arg[2:]
        elif arg.startswith(">") or arg.startswith("<"):
            sub_op = arg[:1]
            arg = arg[1:]
        else:
            sub_op = "="
        return (arg, sub_op)

    def build_sql(self, query_words): # e.g. from sys.argv[1:]
        query_words = [word.lower() for word in query_words]

        sql = "SELECT title, year, rating, resolution, genres, filesize, runtime, filenames FROM movies "

        where = ["WHERE 1"]
        params = []
        next_op = "AND"
        order = " title ASC"
        limit = ""

        for arg in query_words:
            if arg.startswith("-"):
                next_op = next_op + " NOT"
                arg = arg[1:]

            if arg.startswith("year:"):
                arg = arg[5:]
                (arg, sub_op) = self.get_sub_op(arg)
                where.append(next_op + " year " + sub_op + " ?")
                params.append(arg)
                next_op = "AND"

            elif arg.startswith("rating:"):
                arg = arg[7:]
                (arg, sub_op) = self.get_sub_op(arg)
                where.append(next_op + " rating " + sub_op + " ?")
                params.append(arg)
                next_op = "AND"

            elif arg.startswith("res:"):
                arg = arg[4:]
                where.append(next_op + " resolution LIKE ?") # So it's case insensitive
                params.append(arg)
                next_op = "AND"

            elif arg.startswith("genre:"):
                arg = arg[6:]
                arg = r"%" + arg + r"%"
                where.append(next_op + " genres LIKE ?")
                params.append(arg)
                next_op = "AND"

            elif arg.startswith("size:"):
                arg = arg[5:]
                (arg, sub_op) = self.get_sub_op(arg)
                
                if arg.endswith("mb") or arg.endswith("gb"):
                    arg = arg[:-1]

                try:
                    if arg.endswith("m"):
                        arg = arg[:-1]
                        arg = int(arg) * 2**20
                    elif arg.endswith("g"):
                        arg = arg[:-1]
                        arg = int(arg) * 2**30
                    else:
                        arg = (int(arg)) * 2**20
                except ValueError:
                    pass

                where.append(next_op + " movie_bytes " + sub_op + " ?")
                params.append(arg)
                next_op = "AND"

            elif arg.startswith("runtime:"):
                arg = arg[8:]
                (arg, sub_op) = self.get_sub_op(arg)

                where.append(next_op + " CAST(runtime AS INTEGER) " + sub_op + " ?")
                params.append(arg)
                next_op = "AND"    

            elif arg.startswith("top:"):
                arg = arg[4:]
                
                order = " rating DESC"
                limit = " LIMIT " + str(int(arg))

                next_op = "AND"

            elif arg.startswith("bottom:"):
                arg = arg[7:]
                
                order = " rating ASC"
                limit = " LIMIT " + str(int(arg))

                next_op = "AND"

            elif arg == "or":
                next_op = "OR"

            else:
                arg = r"%" + arg + r"%"
                where.append(next_op + " title LIKE ?")
                params.append(arg)
                next_op = "AND"

        sql += " ".join(where) + " ORDER BY" + order + limit

        self.sql = sql
        self.params = params

    def print_sql(self):
        print self.sql
        print self.params

    def get_results(self):
        return self.db.select(self.sql, self.params)

