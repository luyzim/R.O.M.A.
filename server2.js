const express = require("express");
const morgan = require("morgan");
const path = require("path");
const app = express();

// Middlewares
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));
app.set("trust proxy", true);

// Logger no formato Flask
morgan.token("date_flask", () => {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const mons = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${pad(d.getDate())}/${mons[d.getMonth()]}/${d.getFullYear()} ` +
         `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
});
const flaskFormat = ':remote-addr - - [:date_flask] ":method :url HTTP/:http-version" :status :res[content-length]';
app.use(morgan(flaskFormat));

// Rotas principais
app.get("/", (req, res) => res.redirect("/home"));
app.get("/home", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "home_m7.html"));
});

app.get("/mkt", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "mkt_m7.html"));
});

app.get("/cisco", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "cisco_m7.html"));
});
// Importa rotas modulares
app.use("/api", require("./routes/templatesRoutes"));
app.use("/run/mkt", require("./routes/MktCcsInternet"));
app.use("/run/cisco", require("./routes/CiscoCcsInternet"));
app.use("/status", require("./routes/statusRoutes"));

// Porta
const PORT = process.env.PORT || 3104;
const HOST = "0.0.0.0";

app.listen(PORT, HOST, () => {
  console.log(`API Express ouvindo em http://${HOST}:${PORT}`);
});