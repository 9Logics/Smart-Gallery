const fs = require('fs');
let html = fs.readFileSync('app/templates/index.html', 'utf8');
const target = '<script src="https://unpkg.com/lucide@latest"></script>';
const replacement = target + '\n    <script>\n        if (typeof lucide === "undefined") {\n            console.warn("Lucide failed to load. Polyfilling to prevent crashes.");\n            window.lucide = { createIcons: function() {} };\n        }\n    </script>';
if(html.includes(target)) {
    html = html.replace(target, replacement);
    fs.writeFileSync('app/templates/index.html', html);
    console.log("Polyfilled lucide!");
} else {
    console.log("Could not find lucide script tag");
}
