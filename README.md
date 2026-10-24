# Baston Arcade

Treize mini-jeux multijoueurs dans le navigateur, de 1 à 5 joueurs : un salon, un code (ou un lien), et c'est parti.
Site : https://bastonarcade.com

## Fonctionnement
- Une seule page (`index.html`), sans serveur de jeu : les navigateurs se connectent entre eux (WebRTC via PeerJS, `lib/peerjs.min.js`).
  Le créateur du salon fait tourner la partie, les autres reçoivent l'état.
- Relais réseau Metered (application `baston`) pour les réseaux qui bloquent la connexion directe.
- Liste publique des salons : table `salons` sur Supabase (région eu-central-1), clé publique dans le code.
  `.github/workflows/supabase-keepalive.yml` lit la table deux fois par semaine pour que le projet gratuit ne s'endorme pas.
- Version anglaise : `lib/en.js`, appliquée automatiquement selon la langue du navigateur.
- Publication : `.github/workflows/pages.yml` publie le dépôt sur GitHub Pages à chaque envoi sur `main`.

## Dossiers
- `img/` : vignettes des jeux et images peintes (voir `img/LISEZMOI.md`)
- `fonts/` : polices Bangers et Nunito (SIL Open Font License)
- `lib/` : PeerJS (licence MIT) et les textes anglais
- `legal.html` : mentions légales et confidentialité
