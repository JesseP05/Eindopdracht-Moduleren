## Eindopdracht Moduleren
Dit is de uitwerking voor de eindopracht moduleren door Jesse Postma

- [Eindopdracht Moduleren](#eindopdracht-moduleren)
  - [Uitleg](#uitleg)
  - [Installatie](#installatie)
    - [Maak een virtual environment (optional):](#maak-een-virtual-environment-optional)
    - [Activate venv (optional):](#activate-venv-optional)
    - [Install requirements:](#install-requirements)
    - [Run main.py:](#run-mainpy)
    - [Handmatig:](#handmatig)


### Uitleg
Het project is gefocused op een dataset van de politie van Los Angeles. De dataset is opgebouwd uit incidenten van 2020 tot eind 2025. De dataset bevat een aantal columns met codes die vaag zijn, deze worden automatisch vertaald m.b.v. verschillende andere datasets.

De dataset bestaat uit ruim 1 miljoen rows aan data. 
<details>
<summary><i>De data waarin ik in het bijzonder geinteresseerd in ben:</i></summary>

* DATE OCC
    > Datum waarop het incident heeft plaatsgevonden
* TIME OCC
    > Tijdstip waarop het incident heeft plaatsgevonden
* AREA NAME
    > ~Wijk
* Rpt Dist No
    > Dit is welk politie district het incident onder valt, ik vervang dit met welk bureau verantwoordelijk is m.b.v. LAPD_Reporting_District.csv
* Crm Cd
    > Code waarmee wordt aangetoond wat er is gebeurd. Ik vervang dit met een classificatie m.b.v. criminal_codes.csv
* Crm Cd Desc
    > Descriptie van wat er in *aanklaagbare termen* is gebeurd
* Mocodes
    > Kan een lijst van codes zijn die omschrijven wat er exact heeft plaatsgevonden, ik vertaal deze codes m.b.v. mocodes.csv
* Vict Age
    > Leeftijd van het slachtoffer
* Vict Sex
    > Geslacht van het slachtoffer
* Vit Descent
    > Afkomst van het slachtoffer
* Premis Desc
    > Omschrijving van waar het incident heeft plaatsgevonden
* Weapon Desc
    > Omschrijving van een eventueel wapen dat is gebruikt
* Status
    > Status van het onderzoek naar het incident
* LAT
    > Latitude van waar het incident heeft plaatsgevonden
* LON
    > Longitude van waar het incident heeft plaatsgevonden
</details>

---
### Installatie
Met git en curl (*recommended*):
```bash
git clone https://github.com/JesseP05/Eindopdracht-Moduleren.git
cd Eindopracht Moduleren
curl -L -o "data/Crime_Data_from_2020_to_Present.csv" "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"
```

#### Maak een virtual environment (optional):
```bash
python -m venv .venv
```
#### Activate venv (optional):
* Windows (powershell of bash):
    ```bash
    ./.venv/scripts/activate
    ```
* Windows (cmd):
    ```bash
    cd .venv/scripts/
    activate
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
