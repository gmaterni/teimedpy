PER INSTALLARE
 
python3 setup.py install

-------------------------------------
teimxml.py
usage: teimxml.py [-h] [-t] -i  -o
optional arguments:
  -h, --help  show this help message and exit
  -t          [-t <file tags>] default:tags.csv
  -i          -i <file input>
  -o          -o <file output>

sostituisce entities con tag leggendo da tag.csv

es.
 tag inserita nel testo
&tag_name;

con args.
&tag_name;(arg1,arg2,..)
{'name':tag_name,'args':[arg1,arg2,..],'len':num char}

tag di un carattere:
*^°

punteggiatura:
, : . ? : !
<pc resp="#ed">.</pc>

Caratteri utilizzati nei processi e non utilizzabili:
$
|

Lettura log

n) numero riga  riga originale
tag1             : sostituzione1
tag2             : sostituzione2
=> riga con sostituzioni

n] numero riga pre funzione di funzione riga originale con la prima sostituzione
tag1               : sostituzone1
tag2                :sostituzione 2
-> riga con sostituzioni

es.

17) toz &corr;(io&r;sr,io&r;s) mais en +iert rame&n;bra&n;çe.
&corr;(io&r;sr,io&r;s)                  : <choice><sic>io&r;sr</sic><corr>io&r;s</corr></choice>
&n;                                     : <ex>n</ex>
&n;                                     : <ex>n</ex>
.                                       : <pc resp="#ED">.</pc>
=>  toz <choice><sic>io&r;sr</sic><corr>io&r;s</corr></choice> mais en +iert rame<ex>n</ex>bra<ex>n</ex>çe<pc resp="#ED">.</pc>
17] toz <choice><sic>io&r;sr</sic><corr>io&r;s</corr></choice> mais en +iert rame<ex>n</ex>bra<ex>n</ex>çe<pc resp="#ED">.</pc>
&r;                                     : <ex>r</ex>
&r;                                     : <ex>r</ex>
->  toz <choice><sic>io<ex>r</ex>sr</sic><corr>io<ex>r</ex>s</corr></choice> mais en +iert rame<ex>n</ex>bra<ex>n</ex>çe<pc resp="#ED">.</pc>

---------------------------------------------
teimlineword.py
usage: teimlineword.py [-h] -i  -o  -s  [-n]
optional arguments:
  -h, --help  show this help message and exit
  -i          -i <file input>
  -o          -o <file output>
  -s          -s <sigla mano scritto> (prefisso id)
  -n          -n <'pb:1,cb:1,lg:1,l:1,ptr:1'> (start id elementi)

aggiuge i tag <l> e <w>
numera pb,cb,lg,l,w,ptr
è possibile settare il numero iniziale per pb,cb,lg,lptr

parole <w rend="...">  </w>
punteggiatura <pc>.</pc>
tipizza <w> utilizzando alcuni caratteri:

elisione:
[word1,word2] => <seg type:"aggl_s'>word1,word2</seg>
[word1,word2,word3, ..] => <seg type:"aggl_c'>word1,word2,word3,..</seg>

'$    <w ana="#elis">$</w>
\$    <w ana="#encl">$</w>
°$    <w ana="#degl">$</w>

[ ]    <seg type="aggl_s"> </seg>
oppure <seg type="aggl_c"> </seg>

[_ ]  <seg type="aggl_s" cert="no"> </seg>
oppure <seg type="aggl_c" cert="no"> </seg>

{ }  <span from="$" to="$" type="directspeech"> </span>
{_ } <span from="$" to="$" type="monologue"> </span>

utilizza i si simboli  '  /  -'
's
<w ana="#elis">s</w>
/eus
<w ana="#encl">eus</w>
-parola
<w ana="#degl">parola</w>
----------------------------------------------
teimspan.py
usage: teimspan.py [-h] [-t] -i  -o
optional arguments:
  -h, --help  show this help message and exit
  -t          [-t <file tags span>]
  -i          -i <file input>
  -o          -o <file output>

gestione span

definite in un file esterno passato come argomento:
flori:span.csv

directspeech|kl1w1|kl2w3
directspeech|kl9w2|kl12w1
directspeech|kl100w1|kl110w1
monologue|kl200w1|kl210w2


definite nel testo

dicorso diretto:
{}

monologo:
{_}

la parentesi chiusa  può stare rispetto  all'ultima patola o punto:
}word
word}
word }
.}
. }
----------------------------------------------
teimnote.py
usage: teimnote.py [-h] -n  -i  -o
optional arguments:
  -h, --help  show this help message and exit
  -n          -n <file note>
  -i          -i <file input>
  -o          -o <file output>

legge le note da un file csv e le aggiunge al file xml
es.
flori_note.csv

nota|kn1|
La mia anima è pervasa da una mirabile serenità, simile a queste belle
righe per getire con comodità
nota|kn2|
Quando l'amata valle intorno a me si avvolge nei suoi vapori,
nota|kn3|Nota di prova numero 3
Riga di testo generica per veder come impagina.

----------------------------------------------
teimdict.py
usage: teimdict.py [-h] -i  -o
optional arguments:
  -h, --help  show this help message and exit
  -i          -i <file input>
  -o          -o <file output>

crrea dizionario
-------------------------------------------
teimxmllint.py -i
usage: teimdict.py [-h] -i  -o
optional arguments:
  -h, --help  show this help message and exit
  -i          -i <file input>
  -o          -o <file output>

formatta e controlla un file xml
--------------------------------------
teimprj.py filename.json
esegue progetto

es.
file:
teimed_flori.json
contenuto
{
    "exe": [
        "teimxml.py -i flori.txt -t fl_teimed_tags.csv -o flori1.txt",
        "teimlineword.py -i flori1.txt -o flori2.xml -s k -n 'pb:1,cb:1,lg:1,l:1'",
        "teimxmllint.py -i flori2.xml -o flori3.xml ",
        "teimspan.py -i flori3.xml -o flori4.xml",
        "teimnote.py -i flori4.xml -o flori5.xml -n flori_note.csv",
        "teimxmllint.py -i flori5.xml -o flori6.xml ",
        "teimdict.py -i flori.txt -o flori_dict.csv"
    ]
}


