.PHONY=all

all:
	pdflatex main.tex
	biber main
	pdflatex main.tex

part:
	pdflatex viewone.tex > /dev/null
	biber viewone > /dev/null
	pdflatex viewone.tex > /dev/null

clean_part:
	find resources -type f ! \( -name "*.tex" -o -name "*.bib" -o -name "*.png" -o -name "*.jpg" \) -delete

clean:
	find . -maxdepth 1 -type f ! \( -name "*.tex" -o -name "*.pdf" -o -name "*.sh" -o -name "Makefile" \) -delete