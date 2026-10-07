const { execSync } = require("child_process");
try {
    const output = execSync("node -e \"try { require('vm').runInThisContext('throw new Error(); async function foo() {}'); } catch(e){} console.log(typeof foo);\"", { encoding: 'utf8' });
    console.log(output.trim());
} catch (e) {
    console.log("Error:", e.message);
}
