#!/bin/bash

sqlite3 /mnt/media/Movies/movies.db "DROP TABLE IF EXISTS movies"
sqlite3 /mnt/media/Movies/movies.db "VACUUM"

