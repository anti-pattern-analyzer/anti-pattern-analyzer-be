const { Pool } = require("pg");

const pool = new Pool({
    user: "admin",
    host: "localhost",
    database: "logs_db",
    password: "admin",
    port: 5432
});

const saveRawLog = async (logData) => {
    try {
        const client = await pool.connect();
        await client.query(
            `INSERT INTO raw_logs (timestamp, trace_id, span_id, parent_span_id, source, destination, method, request, response) 
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);`,
            [
                logData.timestamp,
                logData.trace_id,
                logData.span_id,
                logData.parent_span_id || null,
                logData.source,
                logData.destination,
                logData.method,
                logData.request || null,
                logData.response
            ]
        );
        console.log(`✅ Log saved: ${logData.trace_id}`);
        client.release();
    } catch (error) {
        console.error("❌ Error saving log:", error);
    }
};

module.exports = { pool, saveRawLog };
