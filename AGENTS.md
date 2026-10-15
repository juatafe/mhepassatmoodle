# Agent del projecte mhepassatmoodle

Per connectar Chrome amb qualsevol Moodle (inclòs Aules), revisar cursos, modificar activitats o gestionar còpies,
llig `.agents/skills/aules-chrome/SKILL.md` i usa el connector inclòs. El perfil especialitzat
és `.codex/agents/aules.toml`; la mateixa skill també funciona amb l’agent principal.

Treballa en català/valencià i usa llenguatge inclusiu: preferix «alumnat», «professorat»
i «persona». Si cal alternar exemples personals, comença en femení i després masculí.
Executa els canvis que la persona usuària haja autoritzat i verifica’ls en el Moodle de destinació.
Una petició d’anàlisi no autoritza publicar. No repetisques peticions d’aprovació ja resoltes.

El repositori conté només les eines de connexió, l’agent i la documentació.
Les còpies de cursos i les dades d’exportació es mantenen fora del control de versions.
No restaures, sobreescrigues ni reinicies cap curs només per configurar la connexió.
La URL del curs es proporciona en cada tasca; el nom del repositori no identifica
el curs de destinació.

No copies perfils de navegador, sessions ni entorns virtuals a la distribució portable.
Les rutes han de ser relatives al projecte o derivades de la carpeta personal del sistema.
Per instal·lar les dependències: `python3 aules.py setup` (Windows: `py aules.py setup`).
Les operacions amb Moodle requerixen xarxa i Chrome local; respecta els permisos de l’entorn.
