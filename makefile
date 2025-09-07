run: env Stockfish Stockfish/src/stockfish
	./bin/python3 main.py

Stockfish:
	rm -rf Stockfish
	git clone https://github.com/official-stockfish/Stockfish 

Stockfish/src/stockfish: Stockfish
	make -j profile-build -C Stockfish/src

env:
	[ -d "bin" ] || python -m venv .
	[ -d "./lib/python3.13/site-packages/chess" ] || pip install python-chess

