CREATE TABLE IF NOT EXISTS btc_sentiment (
    date DATE PRIMARY KEY,
    value INT,
    sentiment TEXT,
    price FLOAT
);