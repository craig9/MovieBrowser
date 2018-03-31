#!/bin/bash

sqlite3 /mnt/media/Movies/movies.db "DROP TABLE IF EXISTS tv_shows"
sqlite3 /mnt/media/Movies/movies.db "DROP TABLE IF EXISTS tv_episodes"
sqlite3 /mnt/media/Movies/movies.db "VACUUM"

