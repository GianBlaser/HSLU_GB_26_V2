# Etappe 0 - Sofortmassnahmen und Projektgeruest

Abhaken von oben nach unten. Alles im Windows-Terminal, Startordner
`C:\HSLU_Programming\HSLU_GB_26`.
Ziel-Datum: SW3, 28.09.2026. Aufwand ca. 3 h.

---

## Schritt 1 - Token widerrufen (zuerst, im Browser)

1. github.com -> Settings -> Developer settings -> Personal access tokens
   -> Tokens (classic)
2. Den bestehenden Token **Delete / Revoke**
3. Gleiche Seite offen lassen, falls Schritt 3 einen neuen braucht

## Schritt 2 - Repo-Sichtbarkeit pruefen

github.com/GianBlaser/HSLU_GB_26 -> Settings -> General -> ganz unten
"Danger Zone" -> muss **Public** sein. Wenn privat: "Change visibility"
-> Make public.

## Schritt 3 - Remote bereinigen

```
cd C:\HSLU_Programming\HSLU_GB_26
git remote set-url origin https://github.com/GianBlaser/HSLU_GB_26.git
git remote remove upstream
git remote -v
```
Erwartete Ausgabe: nur noch `origin` mit der sauberen URL, **ohne** `ghp_...`.

Test, ob die Anmeldung funktioniert:
```
git fetch origin
```
Es oeffnet sich ein Browser-Fenster (Git Credential Manager) -> einloggen.
Falls stattdessen nach Username/Passwort gefragt wird: Username `GianBlaser`,
als Passwort einen **neu erstellten** Token eingeben. Er wird dann im
Windows-Anmeldeinformationsspeicher abgelegt, nicht in einer Datei.

## Schritt 4 - Auf main wechseln

```
git checkout main
git pull origin main
git status
```
Erwartet: "On branch main", "nothing to commit, working tree clean".

## Schritt 5 - Python-Kompatibilitaet testen (kritisch)

```
myenv\Scripts\activate
pip install ifcopenshell
python -c "import ifcopenshell; print(ifcopenshell.version)"
```

**Erfolgreich** (eine Versionsnummer erscheint) -> weiter mit Schritt 6.

**Fehlgeschlagen** (kein Wheel fuer Python 3.13, Build-Fehler):
1. Python 3.12 von python.org installieren - **nicht** aus dem Microsoft Store.
   Bei der Installation "Add python.exe to PATH" ankreuzen.
2. Alte venv loeschen und neu anlegen:
   ```
   rmdir /s /q myenv
   py -3.12 -m venv myenv
   myenv\Scripts\activate
   python --version
   pip install ifcopenshell
   ```
3. Erst wenn `import ifcopenshell` laeuft, weitermachen.

## Schritt 6 - Restliche Module installieren

```
pip install matplotlib streamlit pyvista stpyvista pytest
pip freeze > requirements.txt
```
(pandas und numpy sind bereits vorhanden.)

Kurztest:
```
python -c "import pandas, matplotlib, streamlit, pyvista, stpyvista; print('alle Module ok')"
```

## Schritt 7 - .gitignore erweitern

Datei `.gitignore` im Repo-Root oeffnen und auf diesen Inhalt setzen:

```
myenv/
__pycache__/
*.pyc
*.db
02_Semesterprojekt/cache/
02_Semesterprojekt/output/
.streamlit/secrets.toml
```

## Schritt 8 - Ordnerstruktur anlegen

```
cd C:\HSLU_Programming\HSLU_GB_26
mkdir 02_Semesterprojekt\src
mkdir 02_Semesterprojekt\tools
mkdir 02_Semesterprojekt\tests
mkdir 02_Semesterprojekt\docs
mkdir 02_Semesterprojekt\docs\screenshots
mkdir 02_Semesterprojekt\data
mkdir 02_Semesterprojekt\cache
mkdir 02_Semesterprojekt\output
type nul > 02_Semesterprojekt\src\__init__.py
```

## Schritt 9 - Testdaten kopieren

Aus
`...\05_SEMESTER 5\02_PROG\02_Uebungen\IFC Testfiles\Certification-datasets-main\IFC 4.0.2.1 (IFC 4 ADD2 TC1)\Simple-Scene\`
nach `02_Semesterprojekt\data\` kopieren:

- `Building-Architecture.ifc` (142 KB)
- `Building-Structural.ifc` (185 KB)

**Nicht** kopieren: `Infra-Landscaping.ifc` (2.3 MB) - fuer den Performance-Test
spaeter direkt vom Originalpfad referenzieren, damit das Repo schlank bleibt.

## Schritt 10 - config.py

Datei `02_Semesterprojekt\src\config.py` anlegen. Inhalt schreibt Claude Code -
Aufbau vorher abnicken lassen. Enthalten sein muessen:
Farben und Opazitaeten nach Projektplan Kap. 11, Toleranzen (Laenge 1 mm,
Zahlen 1e-6), Pfade (data, cache, output, Datenbank), Liste der zu
vergleichenden Direktattribute, Liste der ausgeschlossenen Attribute.

## Schritt 11 - Smoke-Test

Datei `02_Semesterprojekt\smoke_test.py`: oeffnet
`data/Building-Architecture.ifc`, gibt Schema-Version, Gesamtzahl `IfcProduct`
und die fuenf haeufigsten IfcClasses aus. Danach wieder loeschen oder nach
`tests/` verschieben.

**Abnahmekriterium Etappe 0:** Das Skript laeuft durch und gibt plausible
Zahlen aus.

## Schritt 12 - README-Geruest

`02_Semesterprojekt\README.md` mit den Abschnitten:
Titel und Kurzbeschrieb, Kontext (Modul, HSLU, HS26), Zielsetzung,
Entwicklungsumgebung, Installation, Nutzung, Projektstruktur, Stand der
Entwicklung. Unter "Stand der Entwicklung" ab jetzt nach jeder Etappe zwei bis
drei Saetze ergaenzen.

Im Semester-README (`README.md` im Root) eine Zeile ergaenzen, die auf
`02_Semesterprojekt/` verweist.

## Schritt 13 - Commit und Push

```
git add .
git commit -m "[E0] Projektgeruest Semesterprojekt IFC-Diff Viewer"
git push origin main
```

Auf github.com pruefen, ob die Struktur sichtbar ist und `myenv/` **nicht**
mitgepusht wurde.

---

## Checkliste

- [ ] Alter Token widerrufen
- [ ] Repository ist public
- [ ] Remote ohne Token, `upstream` entfernt, `git fetch` funktioniert
- [ ] Auf Branch `main`
- [ ] `import ifcopenshell` laeuft
- [ ] Alle Module installiert, `requirements.txt` aktualisiert
- [ ] `.gitignore` erweitert
- [ ] Ordnerstruktur angelegt
- [ ] Testdaten in `data/`
- [ ] `config.py` vorhanden
- [ ] Smoke-Test laeuft durch
- [ ] README-Geruest steht
- [ ] Commit auf `main` gepusht, `myenv/` nicht im Repo
