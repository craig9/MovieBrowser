#!/usr/bin/python

import os
import sqlite3


class Database:

    
    def __init__(self, movies_path):

        self.db_path = os.path.join(movies_path, "movies.db")

        self.sqlite_db = sqlite3.connect(self.db_path)
        self.sqlite_db.text_factory = str
        self.sqlite_db.row_factory = sqlite3.Row
        self.cursor = self.sqlite_db.cursor()

        if not self.movie_table_exists():
            self.create_movie_table()

        if not self.table_exists('tv_shows'):
            self.create_tv_shows_table()

        if not self.table_exists('tv_episodes'):
            self.create_tv_episodes_table()

    def table_exists(self, table_name):
        return (len(self.select("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", [table_name])) > 0)

    def movie_table_exists(self):
        return (len(self.select("SELECT name FROM sqlite_master WHERE type='table' AND name='movies';")) > 0) 
 
    def create_movie_table(self):
            self.exec_sql("CREATE TABLE movies (filenames, nfo, title, year, rating, resolution, genres, filesize, runtime, nfo_date, nfo_bytes, movie_date, movie_bytes)")

    def create_tv_shows_table(self):
        self.exec_sql("CREATE TABLE tv_shows (directory, title, year, starred, watched)")

    def create_tv_episodes_table(self):
        self.exec_sql("CREATE TABLE tv_episodes (directory, filename, title, watched, file_date, file_bytes)")

    def get_movie_filenames(self):
        return self.select("SELECT filenames FROM movies;"); 

    def get_show_directories(self):
        return self.select("SELECT directory FROM tv_shows;");
    
    def get_episode_filenames(self):
        return self.select("SELECT filename FROM tv_episodes;");

    def exec_sql(self, sql, *args):
        self.cursor.execute(sql, *args)
        self.sqlite_db.commit()

    def select(self, sql, *args):
        self.cursor.execute(sql, *args)
        return self.cursor.fetchall()



