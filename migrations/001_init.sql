CREATE TABLE IF NOT EXISTS stocks_master (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(20) UNIQUE NOT NULL,
  company_name VARCHAR(120) NOT NULL,
  sector VARCHAR(80) NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_prices (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(20) NOT NULL,
  trade_date DATE NOT NULL,
  open_price DOUBLE PRECISION NOT NULL,
  close_price DOUBLE PRECISION NOT NULL,
  high_price DOUBLE PRECISION NOT NULL,
  low_price DOUBLE PRECISION NOT NULL,
  volume INTEGER NOT NULL,
  percent_change DOUBLE PRECISION NOT NULL,
  CONSTRAINT uq_daily_ticker_date UNIQUE (ticker, trade_date)
);

CREATE TABLE IF NOT EXISTS technical_indicators (
  id SERIAL PRIMARY KEY,
  ticker VARCHAR(20) NOT NULL,
  trade_date DATE NOT NULL,
  ma20 DOUBLE PRECISION NOT NULL,
  ma50 DOUBLE PRECISION NOT NULL,
  volume_spike_score DOUBLE PRECISION NOT NULL,
  momentum_score DOUBLE PRECISION NOT NULL,
  CONSTRAINT uq_ti_ticker_date UNIQUE (ticker, trade_date)
);

CREATE TABLE IF NOT EXISTS ai_insights (
  id SERIAL PRIMARY KEY,
  insight_date DATE UNIQUE NOT NULL,
  market_sentiment VARCHAR(20) NOT NULL,
  risk_level VARCHAR(20) NOT NULL,
  sector_leader VARCHAR(80) NOT NULL,
  insight_text VARCHAR(500) NOT NULL,
  ussd_text VARCHAR(160) NOT NULL
);

CREATE TABLE IF NOT EXISTS subscribers (
  msisdn VARCHAR(20) PRIMARY KEY,
  subscription_status VARCHAR(20) NOT NULL,
  plan_type VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
