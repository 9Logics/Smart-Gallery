// create a simple html file
const fs = require("fs");
fs.writeFileSync("test.html", `
<!DOCTYPE html>
<html>
<head>
  <script>
    throw new Error("Crash");
    function myHoistedFunction() {}
  </script>
  <script>
    console.log(typeof myHoistedFunction);
  </script>
</head>
<body></body>
</html>
`);
