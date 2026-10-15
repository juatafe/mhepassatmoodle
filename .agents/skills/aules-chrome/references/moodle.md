# Operacions natives de Moodle

## Connexió des d’un script del projecte

Desa el script a l’arrel o ajusta `root` segons la seua ubicació. Rep la URL com a argument.

```python
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / '.agents/skills/aules-chrome/scripts'))
from aules_chrome import Session

with Session(sys.argv[1]) as a:
    page = a.open_course()
    # Inspecciona els controls i enllaços de la pàgina abans de triar una operació.
    print(page.title())
```

`a.page` és una pestanya pròpia; `a.context` conté la sessió identificada.
No uses `browser.close()`, `clear_cookies()` ni `storage_state(path=...)`.
No selecciones ni tanques una pestanya aliena. No treballes en paral·lel sobre la mateixa activitat.

## Edició de contingut

Obri l’enllaç d’edició real de l’activitat. Habitualment és `course/modedit.php?update=CMID`;
obtingues el CMID del curs actual. Comprova que el títol i el curs coincidixen.
Inspecciona noms, etiquetes, tipus i botons visibles del formulari, sense imprimir camps secrets.
Preferix `get_by_label`, `fill`, `check`, `select_option` i el botó natiu de guardar.
Els camps ocults, els valors repetits i les caselles desmarcades tenen semàntica pròpia:
no convertisques tot el formulari en un diccionari que perda valors.

Per a TinyMCE, el text de la textarea pot estar ocult. Identifica l’ID real de l’editor i,
si està inicialitzat, usa `tinymce.get(id).setContent(html)` seguit de `save()`; si no,
usa el mode de codi HTML de l’editor. No endevines l’ID ni substituïsques tot el document.
El cos d’una pàgina sol usar `page[text]` i una introducció `introeditor[text]`.
Respecta `format`, `itemid`, referències `@@PLUGINFILE@@` i la resta de camps del formulari.

Abans de guardar, conserva només els camps de contingut i ajustos necessaris per comparar
o recuperar el canvi, sense tokens. Per a formularis amb JavaScript condicional, treballa
amb el DOM renderitzat: el HTML descarregat amb requests pot presentar camps deshabilitats
que el navegador activa després. Guarda amb el botó real; comprova errors de validació
visibles i reobri el formulari. Un HTTP 200 també pot ser un formulari amb errors.

Compara l’HTML amb tolerància a l’espaiat i als identificadors temporals de `draftfile.php`,
però verifica explícitament el text, els enllaços i els ajustos que s’havien de conservar.

## Fitxers i enllaços de descàrrega

Usa el gestor de fitxers o el selector de l’editor. Tria «Puja un fitxer» i el camp de càrrega
real (`set_input_files`); conserva els fitxers ja existents. Si es fa servir l’API interna
del repositori, descobrix `repo_id`, `contextid`, `itemid` i `sesskey` del formulari actual,
només en memòria: els identificadors d’una altra activitat no servixen.

Una pujada crea un esborrany: cal guardar el formulari que el conté. L’enllaç definitiu
ha de ser del fitxer publicat, no de `draftfile.php`. Comprova una descàrrega autenticada,
la mida i, si es disposa de l’original, el SHA-256. Verifica l’accés de l’alumnat quan calga.

## Vista de l’alumnat

La sessió és compartida entre pestanyes. Usa el menú natiu «Canvia el rol», conserva tots
els camps del formulari i restaura el rol normal amb l’enllaç natiu en un `finally`.
Una petició POST incompleta pot no aplicar el canvi encara que retorne 200.
No treballes amb dades d’una persona concreta per comprovar un recurs públic del curs.

## Còpies de seguretat

En Aules, «Còpia de seguretat» pot redirigir de `backup/backup.php` a
`admin/tool/smartbackup/backup.php`. Segueix les accions i els passos del formulari real.
Per preparar una còpia de continguts reutilitzable, exclou les persones usuàries i les
seues entregues, intents, registres i missatges, llevat que la petició indique un altre abast.
No confongues crear una còpia amb restaurar-la o sobreescriure un curs.

Espera el resultat real en la llista de còpies; algunes pantalles contenen missatges ocults
d’èxit i error alhora. Descarrega l’enllaç autenticat amb `expect_download`/`save_as` o amb
`a.context.request.get` si és un fitxer estàtic. No desempaquetes automàticament l’arxiu.
Comprova que és ZIP o TAR llegible, que conté `moodle_backup.xml` i que els recomptes
de seccions i activitats són coherents. Calcula el SHA-256 i registra URL, data i abast.

## Recuperació

No reenvies a cegues un formulari que haja esgotat el temps: comprova abans l’estat actual.
No persistisques el HTML sencer de Moodle, captures HAR, cookies o capçaleres d’autenticació.
Si cal un diagnòstic, guarda només títols, identificadors estructurals i missatges visibles
rellevants, sense noms d’alumnat ni dades personals alienes a la tasca.
