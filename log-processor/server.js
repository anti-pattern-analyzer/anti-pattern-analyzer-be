const express = require("express");
const { initDB } = require("./db");
const routes = require("./routes");
const consumeLogs = require("./kafkaConsumer");

require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 8085;

app.use(express.json());
app.use("/", routes);

const startServer = async () => {
    await initDB();
    console.log("✅ Database Initialized");

    app.listen(PORT, async () => {
        console.log(`🚀 Server running on http://localhost:${PORT}`);
        await consumeLogs();
    });
};

startServer();
