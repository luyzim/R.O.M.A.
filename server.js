const express = require("express");
const net = require("net");
const path = require("path");
const { spawn } = require("child_process");
const morgan = require("morgan");
const app = express();


// ===== Constantes de diretório =====
app.use(express.json());
app.use(express.static(path.join(__dirname, "public"))); 
const sseClients = new Set();

const DATA_DIR_MKT   = path.join(__dirname, "data");
const DATA_DIR_CISCO = DATA_DIR_MKT; // Cisco usa a MESMA pasta data/





function sendSseEvent(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const res of sseClients) {
    try {
      res.write(payload);
    } catch (err) {
      // ignore write errors, client will be cleaned on close
    }
  }
}


app.set("trust proxy", true);
morgan.token("date_flask", () => {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const mons = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${pad(d.getDate())}/${mons[d.getMonth()]}/${d.getFullYear()} ` +
         `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
});
const flaskFormat = ':remote-addr - - [:date_flask] ":method :url HTTP/:http-version" :status :res[content-length]';
app.use(morgan(flaskFormat));

app.get("/", (req, res) => {
  res.redirect("/home");
});

app.get("/home", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "home_m7.html"));
});  



app.get("/mkt", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "mkt_m7.html")); // seu formulário MKT
});

app.get("/cisco", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "cisco_m7.html")); // seu formulário MKT
});

app.post("/run/mkt", (req, res) => {
  try {
    const data = req.body?.data || req.body;
    if (!data || typeof data !== "object") {
      return res.status(400).json({ error: "Body inválido: esperado objeto com campos." });
    }

    const tplName = "mktModelo.txt";

    // injeta TEMPLATE por nome para o Python escolher certinho
    const payload = { ...data, TEMPLATE: tplName };

    const pythonCmd = process.platform === "win32" ? "python" : "python3";
    const child = spawn(pythonCmd, ["-u", "mainApi.py", "--cmd", "mkt", "--mode", "stdin"], {
      cwd: __dirname,
      stdio: ["pipe","pipe","pipe"],
      env: { ...process.env, TPL_DIR: DATA_DIR_MKT } // <<< garante pasta
    });

    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();

    let out = "", err = "";
    child.stdout.on("data", c => out += c.toString());
    child.stderr.on("data", c => err += c.toString());

    child.on("close", code => {
      if (code !== 0) return res.status(500).json({ ok:false, code, error: err || "Falha no mainApi.py" });
      try { res.json(JSON.parse(out)); }
      catch { res.json({ ok:true, raw: out.trim() }); }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post("/run/cisco", (req, res) => {
  try {
    const data = req.body?.data || req.body;
    if (!data || typeof data !== "object") {
      return res.status(400).json({ error: "Body inválido: esperado objeto com campos." });
    }

    const tplName = "ciscoModelo.txt";

    const payload = { ...data, TEMPLATE: tplName };

    const pythonCmd = process.platform === "win32" ? "python" : "python3";
    const child = spawn(pythonCmd, ["-u", "mainApi.py", "--cmd", "cisco", "--mode", "stdin"], {
      cwd: __dirname,
      stdio: ["pipe","pipe","pipe"],
      env: { ...process.env, TPL_DIR: DATA_DIR_CISCO } // <<< aqui era DATA_DIR (inexistente)
    });

    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();

    let out = "", err = "";
    child.stdout.on("data", c => out += c.toString());
    child.stderr.on("data", c => err += c.toString());

    child.on("close", code => {
      if (code !== 0) return res.status(500).json({ ok:false, code, error: err || "Falha no mainApi.py" });
      try { res.json(JSON.parse(out)); }
      catch { res.json({ ok:true, raw: out.trim() }); }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});


app.get("/status", (req, res) => {
  res.json({ status: "Servidor Online", hora: new Date().toLocaleString(), uptime: process.uptime() });
  
});


const PORT = process.env.PORT || 3104;
const HOST = "0.0.0.0";

app.listen(PORT, HOST, () => {
  console.log(`API Express ouvindo em http://${HOST}:${PORT}`);
});