# python_backend
Basic backend code backup for Flask server ConradsWebsite

In production all of this runs in a Docker container. Will update with the exact Python version and docker container soon enough.

My main website runs Nginx Vue.js -> Flask Python (Docker) -> PostgreSQL (Docker) with Reddis (Docker) as a supplement for rate limiting queries.

Note: This isn't 100% the exact production version, but shows basic usages --- 

app.py is the main entry point. The files messages.py and authorization.py allow secure user logins and connections to PostgreSQL.

The Blackjack game using blackjack_game.py and first_routes.py runs at https://conradswebsite.com/projects/cards -- at the moment since the Reddis database is global for all users who play online, if more than 1 person tries to play the gamestate is going to be the same as any other user since the logic for this runs in 100% backend code.

