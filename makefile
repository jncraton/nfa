all: test hw1.html

hw1.pdf: hw1.md
	pandoc --variable mainfont="Noto Sans CJK KR" --variable monofont="Noto Sans Mono CJK KR" --latex-engine=xelatex -fmarkdown-implicit_figures hw1.md -o hw1.pdf

hw1.png: hw1.html
	firefox -screenshot hw1.html

hw1.html: hw1.pmd nfa/nfa.py
	pweave --format=md2html hw1.pmd

test:
	python3 -m doctest nfa/nfa.py

test-verbose:
	python3 -m doctest -v nfa/nfa.py

clean:
	rm -f hw1.html
	rm -rf figures
	rm -rf __pycache__