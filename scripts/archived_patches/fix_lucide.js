const fs = require('fs');
let code = fs.readFileSync('app/static/js/core.js', 'utf8');
code = code.replace('lucide.createIcons();', 'if (typeof lucide !== "undefined") { lucide.createIcons(); } else { console.warn("Lucide failed to load"); }');
fs.writeFileSync('app/static/js/core.js', code);
