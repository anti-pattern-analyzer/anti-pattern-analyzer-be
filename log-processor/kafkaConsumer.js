const { Kafka } = require("kafkajs");
const { saveRawLog } = require("./repository");

require("dotenv").config();

const kafka = new Kafka({
    clientId: "log-processor",
    brokers: (process.env.KAFKA_BROKERS || "localhost:29091,localhost:29092").split(","),
});

const consumer = kafka.consumer({
    groupId: "log-processor-group",
});

const parseKafkaMessage = (message) => {
    try {
        const [timestamp, data] = message.split(" | ", 2);
        if (!timestamp || !data) throw new Error("Invalid log format");

        const keyValues = data.split(", ");
        const logObject = { timestamp };

        keyValues.forEach((kv) => {
            const [key, value] = kv.split("=", 2);
            logObject[key.trim()] = value ? value.trim() : null;
        });

        if (logObject.parent_span_id === "null") {
            logObject.parent_span_id = null;
        }

        return logObject;
    } catch (error) {
        console.error("❌ Error parsing Kafka message:", error.message);
        return null;
    }
};

const consumeLogs = async () => {
    await consumer.connect();
    await consumer.subscribe({ topic: "logs-topic", fromBeginning: true });

    console.log("🔥 Kafka Consumer Started...");

    await consumer.run({
        eachBatch: async ({ batch }) => {
            console.log("🔥 Received batch of logs...");

            for (const message of batch.messages) {
                try {
                    const rawMessage = message.value.toString().trim();
                    console.log("🔹 Raw Kafka Message:", rawMessage);

                    const parsedLog = parseKafkaMessage(rawMessage);
                    if (!parsedLog) throw new Error("Failed to parse log");

                    console.log("✅ Parsed Log Data:", parsedLog);

                    await saveRawLog(parsedLog);
                } catch (error) {
                    console.error("❌ Error processing message:", error.message);
                }
            }
        },
    });
};

module.exports = consumeLogs;
