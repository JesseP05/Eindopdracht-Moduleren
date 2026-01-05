## Eindopdracht Moduleren
Dit is de uitwerking voor de eindopracht moduleren door Jesse Postma

### Uitleg
Het project is gefocused op een dataset van de politie van Los Angeles. De dataset is opgebouwd uit incidenten van 2020 tot eind 2025. De dataset bevat een aantal columns met codes uit het vakjargon van de politie, deze worden automatisch vertaald m.b.v. verschillende andere datasets.

---
### Installatie
Met git en curl (*recommended*):
```bash
git clone https://github.com/JesseP05/Eindopdracht-Moduleren.git
cd Eindopracht Moduleren
curl -L -o "data/Crime_Data_from_2020_to_Present.csv" "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
```

#### Maak een virtual environment:
```bash
python -m venv .venv
```
#### Activate venv (optional):
* Windows (powershell):
    ```bash
    ./.venv/scripts/activate
    ```
* Linux & Mac:
    ```bash
    source .venv/bin/activate
    ```
#### Install requirements:
```bash
pip install -r requirements.txt
```
#### Run main.py:
```bash
python main.py
```
---
#### Handmatig:
* Download de zip van dit project.
* Unzip de inhoud naar een locatie van keuze.
* Download de [dataset](https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD) naar de "data/"  folder in het project
* Volg de stappen hierboven vanaf [venv aanmaken](#maak-een-virtual-environment)
