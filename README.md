# Project Jurivoc


## Requirements

* Python 3.12


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
```

4. Create virtualenv

```sh
python3.12 -m venv virtualenv
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

[!IMPORTANT]
Python version 3.6:

```sh
python -m pip install pandas 
```

```sh
python -m -m pip install rdflib
```


## Running the Python script

/!\ Make sure you are in the virtualenv !

The command synopsis is the following:

```python
  python convert_data_jurivoc.py --data <directory input files > --output <directory output> --log <directory log>
```

e.g:

```python
python convert_data_jurivoc.py --data inputs --output jurivoc_graph --log jurivoc_log
```

The parameters are the following:

- `--data` Directory containing the Jurivoc files. (required) :
  - jurivoc_fre.txt
  - jurivoc_ger.txt
  - jurivoc_ita.txt
  - jurivoc_fre_ger.txt
  - jurivoc_fre_ita.txt
- `--output` Result Directory (required)
- `--log` Log Directory where the raw dataframes resulting from file parsing will be logged (optional)


## Notes

The conversion takes about 15 minutes to complete.

The conversion assumes that the input files are named like the one documented above, to know the language of the labels. Do not rename the files.

The structure of the thesaurus is read from the French variant. The german and italian variants are used to fetch the corresponding labels (pref and alt) and notes, but not the broader/narrower/related.
