const fs = require('fs');
let code = fs.readFileSync('app/static/js/recap_player.js', 'utf8');

const target = `                        wrapper.appendChild(row1);
                        wrapper.appendChild(row2);
                        heroContainer.appendChild(wrapper);
                    }
                    }
                }
            }
            
            // Finish loader`;

const replacement = `                        wrapper.appendChild(row1);
                        wrapper.appendChild(row2);
                        heroContainer.appendChild(wrapper);
                    }
                }
            }
            
            // Finish loader`;

if (code.includes(target)) {
    code = code.replace(target, replacement);
    fs.writeFileSync('app/static/js/recap_player.js', code);
    console.log("Fixed extra braces");
} else {
    console.log("Could not find exact block, trying regex...");
    code = code.replace(/\}\s*\}\s*\}\s*\}\s*\/\/\s*Finish loader/g, '}\n                }\n            }\n            \n            // Finish loader');
    fs.writeFileSync('app/static/js/recap_player.js', code);
}
