# Project Jurivoc


## Requirements

* Python 3.6 - do not use python3.12


## Installation

1. Clone the repository

```sh
git clone git@github.com:/sparna-git/Jurivoc.git
```

2. Install pip

```sh
sudo apt install python3-pip
```

On Windows, PIP is already included for versions of Python > 3.4.

3. Install virtualenv

```sh
pip install virtualenv 
# You may need to do this on Linux :
# sudo apt install python3.12-venv
# or :
# sudo apt install python3-venv
```

4. Create virtualenv

```sh
python3 -m venv virtualenv
```

5. Activate virtualenv

```sh
Windows : virtualenv/Scripts/activate.bat
Linux : source virtualenv/bin/activate
```

6. Once in the virtual env, install the necessary dependencies from `requirements.txt` :

```sh
pip install -r requirements.txt
```


## Running the Python script

/!\ Make sure you are in the virtualenv !

The command synopsis is the following:

```sh
  python convert_data_jurivoc.py --data <directory input files > --output <directory output> --log <directory log> --previousVersion <directory of previous version> [--noComplexSubjects]
```

e.g, without a previous version (= initial run):

```sh
python convert_data_jurivoc.py --data inputs --output jurivoc_graph --log jurivoc_log --noComplexSubjects
```

with a previous version :

```sh
python convert_data_jurivoc.py --data inputs --output jurivoc_graph --log jurivoc_log --previousVersion jurivoc_graph_v1 --noComplexSubjects
```

The parameters are the following:

- `--data` Directory containing the Jurivoc files. (required) :
  - jurivoc_fre.txt
  - jurivoc_ger.txt
  - jurivoc_ita.txt
  - jurivoc_fre_ger.txt
  - jurivoc_fre_ita.txt
- `--output` Result Directory (required)
- `--log` (optional) Log Directory where the raw dataframes resulting from file parsing will be logged (optional). This directory will also contain a Turtle log of the graph before trying to retrieve the URIs from the previous version.
- `--previousVersion` (optional) directory where the previous version of jurivoc will be read to fetch the previous URIs (that directory is expected to contain the file `jurivoc.ttl` that was the output of the previous run)
- `--noComplexSubjects` : do not generate any `madsrdf:ComplexSubject` entity

## Notes on URI

### Concepts URI

The URI generation works in 2 steps :

1. In the first step, URIs are given based on the French labels. e.g. `jurivoc:PUBLICATION_ELECTRONIQUE`. The SKOS thesaurus with these URIs is logged into `<log directory>/jurivoc_with_label_uris.ttl`
2. Then, in a second step, 2 things can happen :
  1. Either the parameter `--previousVersion` was *not* provided, indicating that it is the initial run, then a sequential id will be given to every concept based on the alphabetical order of their URI in the first step
  2. Either the parameter `--previousVersion` was provided, then an attempt is made to retrieve the previous URI from the previous version :

    - A search is made on the French, Italian and German prefLabel of each concept. If _1_ prefLabel matches, then the URI is retrieved from the previous concept. This means that if 1 or 2 prefLabel have changed, but one stayed the same, the Concept will retain its previous URI
    - If no prefLabel matched, a new URI based on the sequential identifier will be given to the concept 

The mapping table between the URIs of the first step, and the corresponding URI found in the previous version is in `jurivoc_log/data_for_graph/Merge_GraphNew_OldGraph.csv`.

### ComplexSubject URI

The URIs for the `ComplexSubject` (USA / AND blocks in the original file) is always created based on:
- The concatenation of the URI of the Concepts composing the composite synonym
- A counter based on the alphabetical order of the synonym, since more than one synonym can correspond to the combination of the same set of Concepts

e.g.

```turtle
jurivoc:1_1415_4875_8192 a madsrdf:ComplexSubject ;
    madsrdf:authoritativeLabel "principe de déterminance"@fr ;
    madsrdf:componentList ( jurivoc:1415 jurivoc:4875 jurivoc:8192 ) .
```

this implies that, in the case when 1/ multiple composite synonyms are associated to the same set of concepts and 2/ one of them is changed and it changes its alphabetical order, then its URI will change.

### Testing the URI matching behavior with the previous version

The repository contains 2 directories that contain a tiny sample of Jurivoc entries : `inputs_small` and `inputs_small_v2`. The "inputs_small_v2" folder contains some modifications compared to the "inputs_small" and this can be used to easily test the behavior when new entries are being added or renamed.


## Notes

The conversion takes about 30 minutes to complete.

The conversion assumes that the input files are named like the one documented above, to know the language of the labels. Do not rename the files.

The structure of the thesaurus is read from the French variant. The german and italian variants are used to fetch the corresponding labels (pref and alt) and notes, plus "composite synonyms", but not the broader/narrower/related.

## Note on data consistency

Some entries in the "ger" file do not have their French equivalent. They are logged in the log file `terms_in_ger_ita_not_found_in_fra.csv`. The consequence is that some Concepts could miss a german prefLabel

```
title|language|title_traduction
APPARTHOTEL|de|APPARTHOTEL
ARTHRODESE|de|ARTHRODESE
ATHETOSE|de|ATHETOSE
ATRESIE|de|ATRESIE
BATTERIE(ENERGIE)|de|BATTERIE(ENERGIE)
BELARUS|de|BELARUS
BENIN|de|BENIN
BETON|de|BETON
BIOMETRIE|de|BIOMETRIE
DÄNEMARK|de|DÄNEMARK
DEFLATION|de|DEFLATION
DEPARTEMENT|de|DEPARTEMENT
DEPRESSION|de|DEPRESSION
DYSMELIE|de|DYSMELIE
ENERGIE|de|ENERGIE
EPIDEMIE|de|EPIDEMIE
EPILEPSIE|de|EPILEPSIE
ERGOTHERAPIE|de|ERGOTHERAPIE
GENEALOGIE|de|GENEALOGIE
GEOGRAPHIE|de|GEOGRAPHIE
GEOLOGIE|de|GEOLOGIE
GERIATRIE|de|GERIATRIE
HEMIHYPERTROPHIE|de|HEMIHYPERTROPHIE
HEMIPLEGIE|de|HEMIPLEGIE
HERPES|de|HERPES
HOTEL|de|HOTEL
HYDRONEPHROSE|de|HYDRONEPHROSE
HYGIENE|de|HYGIENE
HYSTERIE|de|HYSTERIE
ILEUS|de|ILEUS
INGENIEUR|de|INGENIEUR
INTERREGIONAL|de|INTERREGIONAL
ISRAEL|de|ISRAEL
LEGASTHENIE|de|LEGASTHENIE
LIBERIA|de|LIBERIA
MAIS|de|MAIS
METEOROLOGIE|de|METEOROLOGIE
MODERATION|de|MODERATION
MONTENEGRO|de|MONTENEGRO
NEPAL|de|NEPAL
NEPHROSE|de|NEPHROSE
NIGERIA|de|NIGERIA
OPERATION|de|OPERATION
OSTEOCHONDROSE|de|OSTEOCHONDROSE
OSTEOPOROSE|de|OSTEOPOROSE
OSTEOSYNTHESE|de|OSTEOSYNTHESE
OSTEOTOMIE|de|OSTEOTOMIE
PARAPLEGIE|de|PARAPLEGIE
PHYSIOTHERAPIE|de|PHYSIOTHERAPIE
PHYTOTHERAPIE|de|PHYTOTHERAPIE
PIEMONT|de|PIEMONT
PSYCHOTHERAPIE|de|PSYCHOTHERAPIE
QUEBEC|de|QUEBEC
REFERENDUM|de|REFERENDUM
REGIMENT|de|REGIMENT
REGION|de|REGION
REGISSEUR|de|REGISSEUR
RETINOPATHIE|de|RETINOPATHIE
RHONE|de|RHONE
SCHIZOPHRENIE|de|SCHIZOPHRENIE
SENEGAL|de|SENEGAL
SPONDYLODESE|de|SPONDYLODESE
SPONDYLOLISTHESIS|de|SPONDYLOLISTHESIS
STENOSE|de|STENOSE
STERILISATION|de|STERILISATION
SUBDELEGATION|de|SUBDELEGATION
SYNECHIE|de|SYNECHIE
TANTIEME|de|TANTIEME
TETRAPLEGIE|de|TETRAPLEGIE
THEOLOGIE|de|THEOLOGIE
THERAPIE|de|THERAPIE
TURKMENISTAN|de|TURKMENISTAN
VENEZUELA|de|VENEZUELA
VIDEOTEX|de|VIDEOTEX
VOLIERE|de|VOLIERE
ZOOTHERAPIE|de|ZOOTHERAPIE
```