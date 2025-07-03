

```bash
python wordsearch-tex-gen.py --width 10 --height 10 words.txt | ./pdflatex-pipe >out.pdf

for i in $(seq 20); do python wordsearch-tex-gen.py --width 20 --height 30 words.txt | ./pdflatex-pipe >out/xhard${i}.pdf; done

pdfunite out/xhard*.pdf out/combine-xhard.pdf
```
