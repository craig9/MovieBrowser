#!/usr/bin/python

import os
import sqlite3


class Database:

    
    def __init__(self, movies_path):

        self.db_path = os.path.join(movies_path, "movies.db")

        self.sqlite_db = sqlite3.connect(self.db_path)
        self.sqlite_db.text_factory = str
        self.cursor = self.sqlite_db.cursor()

        if not self.movie_table_exists():
            self.create_movie_table()

    def movie_table_exists(self):
        return (len(self.select("SELECT name FROM sqlite_master WHERE type='table' AND name='movies';")) > 0)

    def create_movie_table(self):
            self.exec_sql("CREATE TABLE movies (filenames, nfo, title, year, rating, resolution, genres, filesize, runtime, nfo_date, nfo_bytes, movie_date, movie_bytes)")

    def get_movie_filenames(self):
        return self.select("SELECT filenames FROM movies;"); 

    def exec_sql(self, sql, *args):
        self.cursor.execute(sql, *args)
        self.sqlite_db.commit()

    def select(self, sql, *args):
        self.cursor.execute(sql, *args)
        return self.cursor.fetchall()



