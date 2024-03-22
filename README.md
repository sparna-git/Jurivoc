# Project Jurivoc


## Requeriments

* Python last version

## Installation

1. Clone the repository

```sh
git clone git@github.com:/sparna-git/Jurivoc.git
```

2. Install 
```sh
sudo apt install python3-pip
```

On Windows, PIP is already included for versions of Python > 3.4.

3. Install environment

```sh
pip install virtualenv 
# You may need to do this on Linux :
# sudo apt install python3.10-venv
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

6. Once in the virtual env, installer the necessary dependencies from `requirements.txt` :
```sh
pip install -r requirements.txt
```

# Running the Python script

```python
  python convert_data_jurivoc.py <directory input files > <directory output>
```

E.g:
```python
python convert_data_jurivoc.py ./inputs/ ./jurivoc_result
```


