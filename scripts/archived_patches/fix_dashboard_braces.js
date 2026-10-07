const fs = require('fs');
let code = fs.readFileSync('app/static/js/recap_dashboard.js', 'utf8');
code = code.replace('                            }', '                            }\n                        }');
fs.writeFileSync('app/static/js/recap_dashboard.js', code);
