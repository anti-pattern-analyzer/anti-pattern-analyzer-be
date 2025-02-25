const express = require("express");
const { pool } = require("./repository");

const router = express.Router();

router.get("/", (req, res) => {
    res.send("🚀 Log Processor API is running!");
});

router.get("/traces", async (req, res) => {
    try {
        const client = await pool.connect();

        // Query for traces with process and span data
        const result = await client.query(`
            SELECT 
                trace_id, 
                json_agg(
                    json_build_object(
                        'span_id', span_id,
                        'parent_span_id', parent_span_id,
                        'source', source,
                        'destination', destination,
                        'method', method,
                        'request', request,
                        'response', response,
                        'timestamp', timestamp,
                        'duration', duration,
                        'process_id', process_id
                    ) ORDER BY timestamp ASC
                ) AS spans,
                jsonb_object_agg(
                    process_id, 
                    json_build_object(
                        'process_id', process_id,
                        'service_name', source
                    )
                ) AS processes
            FROM (
                SELECT 
                    trace_id, 
                    span_id,
                    parent_span_id,
                    source,
                    destination,
                    method,
                    request,
                    response,
                    timestamp,
                    duration,
                    'p' || DENSE_RANK() OVER (PARTITION BY trace_id ORDER BY timestamp) AS process_id
                FROM structured_traces
            ) AS subquery
            GROUP BY trace_id
            ORDER BY trace_id DESC
            LIMIT 100;
        `);

        client.release();
        res.json(result.rows);
    } catch (err) {
        console.error("❌ Error fetching traces:", err);
        res.status(500).json({ error: "Database error" });
    }
});

module.exports = router;
