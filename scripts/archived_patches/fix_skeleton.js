const fs = require('fs');
let js = fs.readFileSync('app/static/js/views/memories.js', 'utf8');

js = js.replace(
    /\$\{Array\(3\)\.fill\('<div class=\"skeleton-card\" style=\"aspect-ratio: 1; border-radius: 12px; flex: 1; min-width: 0;\"><\/div>'\)\.join\(''\)\}/g,
    "\"
);

js = js.replace(
    /\\$\\{Array\(6\)\.fill\\\(\\'<div class="skeleton-card" style="width: 100px; height: 140px; border-radius: 12px; flex: 0 0 auto;"><\/div>\\'\\\)\.join\\\(\\'\\'\\\)\\}/g,
    "\"
);

fs.writeFileSync('app/static/js/views/memories.js', js, 'utf8');
console.log('Fixed');
