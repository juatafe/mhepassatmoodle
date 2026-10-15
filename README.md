# mhepassatmoodle · Connexió amb Moodle

Este projecte inclou un agent, una skill i les eines perquè Codex es connecte a
Chrome, revise un curs Moodle i aplique els canvis que li demanes. Accepta cursos
d’altres Moodle, a més d’Aules: indica **l’adreça completa del curs i la tasca**.

Exemple: `https://campus.example.org/moodle/course/view.php?id=123`.
La pàgina inicial del campus no substituïx l’adreça del curs. Els noms `aules`,
`aules-chrome` i `aules.py` es conserven per compatibilitat; no limiten el domini.

## 1. Què cal instal·lar en un equip nou

| Component | Instal·lació i funció |
| --- | --- |
| Google Chrome | [Descàrrega oficial](https://www.google.com/chrome/). Navegador que obrirà el connector. |
| Python | [Descàrrega oficial](https://www.python.org/downloads/). El llançador requerix Python 3.10 o posterior; comprovat amb 3.12. |
| Codex amb accés local | Pots usar l’[extensió de Codex en VS Code](https://learn.chatgpt.com/docs/codex/ide). Inicia sessió amb el teu compte i obri esta carpeta com a projecte. |
| Dependències Python | Les instal·la `aules.py setup` a partir de `requirements.txt`. Inclouen Playwright 1.64.0. |
| Accés al Moodle | Cal un compte amb accés al curs i permisos per a les modificacions demanades. |

Cal Internet per instal·lar les dependències i accedir al campus. Chrome, Python i Codex
han de treballar en el mateix equip. No cal instal·lar Moodle, Odoo, Node.js ni un servidor
MCP per usar este connector amb l’extensió de Codex. Tampoc cal una clau API de Moodle
ni executar `playwright install`: es reutilitza Chrome.

### Linux (Ubuntu, Debian o derivats)

Instal·la Chrome des de la seua web i Codex en VS Code. Si no tens Python i `venv`:

```sh
sudo apt update
sudo apt install python3 python3-venv python3-pip
python3 --version
```

Comprova que la versió és 3.10 o posterior. En altres distribucions usa el gestor de
paquets corresponent per instal·lar Python i el suport d’entorns virtuals.

### Windows

Instal·la Chrome, Python i Codex en VS Code des de les fonts oficials anteriors.
Obri una terminal PowerShell nova i comprova:

```powershell
py --version
```

Si `py` no està disponible però `python --version` mostra la versió correcta, usa `python`
en les ordres següents. Esta guia usa Python i Chrome natius de Windows; no cobrix WSL.

### macOS

Instal·la Chrome, Python des de python.org i Codex en VS Code. Obri Terminal i comprova:

```sh
python3 --version
```

La detecció de Chrome i les rutes estan previstes per a Windows i macOS, però les proves
reals d’esta entrega s’han fet en Linux.

## 2. Descarregar el projecte

Pots descarregar-lo des del botó **Code → Download ZIP** del repositori
[juatafe/mhepassatmoodle](https://github.com/juatafe/mhepassatmoodle).
Descomprimix-lo i obri la carpeta resultant `mhepassatmoodle-main` en Codex/VS Code.
Esta opció no requerix instal·lar Git.

Si tens Git instal·lat, també pots clonar-lo:

```sh
git clone https://github.com/juatafe/mhepassatmoodle.git
cd mhepassatmoodle
```

Es copiaran també `.agents` i `.codex`, encara que el gestor de fitxers les mostre ocultes.
Si trasllades la carpeta manualment, inclou-les i exclou `.venv` i `__pycache__`.
No copies perfils de Chrome ni sessions: inicia sessió en cada equip.

El repositori no inclou continguts, còpies ni dades de cap curs. Indica l’adreça del curs
sobre el qual vols treballar. Si restaures una còpia Moodle pel teu compte, usa l’adreça nova.

## 3. Preparar les dependències (una vegada per equip)

Obri la terminal de VS Code dins de la carpeta que conté `aules.py` i `requirements.txt`.
En Linux o macOS:

```sh
python3 aules.py setup
```

En Windows:

```powershell
py aules.py setup
```

L’ordre crea `.venv` en el projecte i instal·la les dependències. No cal activar l’entorn
manualment: el llançador selecciona el seu Python. `requirements.txt` remet a la llista
de la skill per mantindre una única versió de les dependències.

Si preferixes la instal·lació manual, tria esta alternativa en lloc de `setup`:

```sh
# Linux / macOS
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

```powershell
# Windows / PowerShell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Els entorns virtuals [s’han de recrear en canviar d’ubicació o d’equip](https://docs.python.org/3/library/venv.html).
Si has copiat `.venv` per error, elimina només eixa carpeta i torna a executar `setup`.

## 4. Obrir Chrome i identificar-se

Substituïx l’adreça d’exemple per la del teu curs. En Linux/macOS:

```sh
python3 aules.py start --url 'https://campus.example.org/moodle/course/view.php?id=123'
```

En Windows/PowerShell:

```powershell
py aules.py start --url 'https://campus.example.org/moodle/course/view.php?id=123'
```

S’obri una finestra dedicada de Chrome, o una pestanya nova si ja hi ha una connexió
activa. Inicia sessió en el Moodle **en eixa finestra**, inclòs el segon factor si en té.
No introduïsques contrasenyes en Codex ni en fitxers del projecte.

Comprova la connexió amb la mateixa adreça:

```sh
python3 aules.py status --url 'https://campus.example.org/moodle/course/view.php?id=123'
```

En Windows canvia `python3` per `py`. El resultat correcte inclou `"connected": true`,
l’adreça i el títol del curs. Açò confirma l’accés; l’agent comprovarà els permisos
d’edició abans de modificar res.

## 5. Demanar modificacions a Codex

Amb el projecte obert, pots escriure:

> Usa l’agent aules i la skill $aules-chrome en este curs:
> https://campus.example.org/moodle/course/view.php?id=123
> Revisa les activitats de la unitat 1 i aplica estos canvis: [indicacions].

Després de la preparació inicial, també pots donar només la URL i la tasca i demanar
a Codex que prepare la connexió. Si la sessió ha caducat, tornaràs a identificar-te
en Chrome. Per treballar en un altre curs no cal reinstal·lar res: canvia l’adreça.

El connector prepara la connexió; l’agent fa les edicions amb els formularis de Moodle
i comprova el resultat guardat. No modifica cursos automàticament només per obrir-los.
Les versions, els temes i els connectors de Moodle poden requerir ajustar selectors
o passos. La connexió real s’ha comprovat en Aules; altres plataformes no s’han provat.

## 6. Ordres útils

| Ordre | Funció |
| --- | --- |
| `python3 aules.py setup` | Crea l’entorn i instal·la dependències. |
| `python3 aules.py start --url 'URL_DEL_CURS'` | Obri el curs en Chrome amb connexió local. |
| `python3 aules.py status --url 'URL_DEL_CURS'` | Comprova la sessió i el curs. |
| `python3 aules.py inspect --url 'URL_DEL_CURS'` | Mostra noms i enllaços de les activitats. |
| `python3 aules.py --help` | Mostra les opcions del connector. |

En Windows usa `py`. Mantín l’adreça entre cometes, especialment si conté `&`.

## 7. Si alguna cosa falla

| Situació | Solució |
| --- | --- |
| No es troba `python3`, `py` o `python` | Instal·la Python i obri una terminal nova. Comprova’n la versió. |
| Falta `venv` o `ensurepip` en Linux | Instal·la `python3-venv` i repetix `setup`. |
| Falta Playwright | Executa `setup` des de la carpeta del projecte. |
| Chrome no es detecta | Afegix a `start` l’opció `--chrome '/ruta/completa/al/navegador'`. En Windows usa la ruta a `chrome.exe`. |
| Hi ha un Chrome normal obert però no connecta | Executa `start`; la finestra habitual pot no tindre activat el port de control. |
| El port 9222 està ocupat | Afegix `--port 9223` a `start`, `status` i `inspect`, i indica eixe port a l’agent. |
| Moodle demana identificació | Inicia sessió en la finestra dedicada i repetix `status`. |
| La skill o l’agent no apareixen | Comprova `.agents` i `.codex`, reobri el projecte i actualitza Codex si cal. També pots demanar a l’agent principal que llija `AGENTS.md` i use la skill. |
| El curs és visible però no editable | Revisa els permisos del compte i del rol en Moodle. |
| `status` no reconeix un tema personalitzat | Demana a l’agent que inspeccione els controls reals i adapte la comprovació de sessió/curs. |
| Codex bloqueja la connexió local | Autoritza l’operació concreta de xarxa o obertura de Chrome quan ho demane. El perfil de l’agent no anul·la els permisos de l’equip. |

Esta configuració necessita accés local a Chrome en `127.0.0.1`; no connecta directament
una sessió de Codex Cloud amb el navegador del teu ordinador.

## 8. Quins fitxers es conserven i es traslladen

| Fitxer o carpeta | Funció |
| --- | --- |
| `AGENTS.md` | Instruccions comunes del projecte. |
| `.codex/agents/aules.toml` | Agent especialitzat. |
| `.agents/skills/aules-chrome/` | Skill, connector, dependències i proves. |
| `aules.py` i `requirements.txt` | Llançador i punt d’entrada d’instal·lació. |
| `LICENSE` | Llicència GNU GPL v3 del repositori. |
| `.venv/` | Entorn local: es recrea i no es trasllada ni es publica. |

El perfil de Chrome queda fora del projecte: `~/.cache/aules-chrome` en Linux,
`~/Library/Caches/aules-chrome` en macOS o `%LOCALAPPDATA%\aules-chrome` en Windows.
El port de control es limita a la interfície local.

`.gitignore` exclou les còpies `.mbz`, els ZIP, les dades d’exportació, els entorns locals
i els fitxers habituals de sessió. Mantín les descàrregues i els materials particulars
del curs en una carpeta separada. Abans de publicar canvis, revisa els fitxers inclosos.

Per actualitzar una còpia clonada amb Git, guarda primer els teus canvis locals i executa
`git pull --ff-only`; després torna a executar `python3 aules.py setup` (Windows: `py`).
Si vas descarregar un ZIP, descarrega la versió nova en una carpeta nova i repetix la preparació.

## Comprovacions i documentació

Les 9 proves locals del connector han passat en Linux. Comproven les URLs, la sessió,
el curs de destinació i la conservació del navegador. Pots executar-les sense modificar cap curs:

```sh
python3 -m unittest discover -s .agents/skills/aules-chrome/tests
```

Formats basats en la documentació oficial d’[agents de Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents)
i [skills locals](https://learn.chatgpt.com/docs/build-skills). La connexió usa
[Playwright connect_over_cdp](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp)
i el [perfil separat de Chrome per a depuració remota](https://developer.chrome.com/blog/remote-debugging-port).
