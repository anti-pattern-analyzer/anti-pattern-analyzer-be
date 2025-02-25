const { Pool } = require("pg");

const pool = new Pool({
    user: "admin",
    host: "localhost",
    database: "postgres",
    password: "admin",
    port: 5432
});

const createDatabase = async () => {
    try {
        const client = await pool.connect();
        const result = await client.query("SELECT 1 FROM pg_database WHERE datname='logs_db'");

        if (result.rowCount === 0) {
            await client.query("CREATE DATABASE logs_db;");
            console.log("✅ Database 'logs_db' created.");
        } else {
            console.log("✅ Database 'logs_db' already exists.");
        }
        client.release();
    } catch (error) {
        console.error("❌ Error checking/creating database:", error);
    }
};

const createTables = async () => {
    const dbPool = new Pool({
        user: "admin",
        host: "localhost",
        database: "logs_db", // Connecting to the actual logs_db
        password: "admin",
        port: 5432
    });

    const client = await dbPool.connect();
    try {
        // Creating raw_logs table
        await client.query(`
            CREATE TABLE IF NOT EXISTS raw_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                trace_id UUID NOT NULL,
                span_id UUID NOT NULL UNIQUE,
                parent_span_id UUID NULL,
                source TEXT NOT NULL,
                destination TEXT NOT NULL,
                method TEXT NOT NULL,
                request TEXT,
                response TEXT NOT NULL
            );
        `);

        // Creating the services table
        await client.query(`
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                service_name VARCHAR(255) UNIQUE NOT NULL,
                metadata JSONB
            );
        `);

        // Creating a materialized view for structured traces
        await client.query(`
            CREATE MATERIALIZED VIEW IF NOT EXISTS structured_traces AS
            WITH spans AS (
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
                    LAG(timestamp) OVER (PARTITION BY trace_id ORDER BY timestamp) AS parent_timestamp
                FROM raw_logs
            )
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
                COALESCE(EXTRACT(EPOCH FROM (timestamp - parent_timestamp)) * 1000, 0) AS duration
            FROM spans
            ORDER BY timestamp;
        `);

        // Adding indexes for optimized queries
        await client.query(`
            CREATE INDEX IF NOT EXISTS idx_trace_id ON raw_logs(trace_id);
            CREATE INDEX IF NOT EXISTS idx_span_trace_id ON raw_logs(span_id);
            CREATE INDEX IF NOT EXISTS idx_service_name ON services(service_name);
        `);

        console.log("✅ Tables & Materialized View created successfully.");

        // Adding a trigger for refresh of materialized view on data insertion
        await client.query(`
            CREATE OR REPLACE FUNCTION refresh_structured_traces_view()
            RETURNS TRIGGER AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW structured_traces;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER refresh_structured_traces_trigger
            AFTER INSERT ON raw_logs
            FOR EACH STATEMENT
            EXECUTE FUNCTION refresh_structured_traces_view();
        `);

    } catch (error) {
        console.error("❌ Error creating tables:", error.message);
    } finally {
        client.release();
        dbPool.end();
    }
};

const initDB = async () => {
    await createDatabase();
    await createTables();
};

module.exports = { initDB };
