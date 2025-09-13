VENV = .
PYTHON = $(VENV)/bin/python3
PYINSTALLER = $(VENV)/bin/pyinstaller
SCRIPT = main.py
DIST = .

run: env Stockfish/src/stockfish
	$(PYTHON) $(SCRIPT)

Stockfish:
	rm -rf Stockfish
	git clone https://github.com/official-stockfish/Stockfish 

Stockfish/src/stockfish: Stockfish
	make -j profile-build -C Stockfish/src

env:
	[ -d "$(VENV)/bin" ] || python -m venv $(VENV)
	[ -d "$(VENV)/lib/python3.13/site-packages/chess" ] || $(PYTHON) -m pip install python-chess pyinstaller

install: env Stockfish/src/stockfish
	$(PYINSTALLER) --onefile --distpath $(DIST) $(SCRIPT) -n chess \
		--add-data "Stockfish/src/stockfish:Stockfish/src" \
		--console \
		--hidden-import=chess
