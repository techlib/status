--
-- PostgreSQL database dump
--

-- Dumped from database version 10.1
-- Dumped by pg_dump version 10.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: wifi_stations; Type: TABLE; Schema: public; Owner: status
--

CREATE TABLE wifi_stations (
    id bigint NOT NULL,
    ts timestamp with time zone NOT NULL,
    dev character varying COLLATE pg_catalog."und-x-icu" NOT NULL,
    affi character varying COLLATE pg_catalog."und-x-icu" NOT NULL,
    ap macaddr NOT NULL,
    essid character varying COLLATE pg_catalog."und-x-icu" NOT NULL,
    phy character varying COLLATE pg_catalog."und-x-icu" NOT NULL,
    "user" character varying COLLATE pg_catalog."und-x-icu" DEFAULT '?'::character varying NOT NULL
);


ALTER TABLE wifi_stations OWNER TO status;

--
-- Name: wifi_stations_id_seq; Type: SEQUENCE; Schema: public; Owner: status
--

CREATE SEQUENCE wifi_stations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE wifi_stations_id_seq OWNER TO status;

--
-- Name: wifi_stations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: status
--

ALTER SEQUENCE wifi_stations_id_seq OWNED BY wifi_stations.id;


--
-- Name: wifi_stations id; Type: DEFAULT; Schema: public; Owner: status
--

ALTER TABLE ONLY wifi_stations ALTER COLUMN id SET DEFAULT nextval('wifi_stations_id_seq'::regclass);


--
-- Name: wifi_stations wifi_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: status
--

ALTER TABLE ONLY wifi_stations
    ADD CONSTRAINT wifi_stations_pkey PRIMARY KEY (id);


--
-- Name: wifi_stations_affi_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_affi_idx ON wifi_stations USING btree (affi COLLATE "default");


--
-- Name: wifi_stations_ap_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_ap_idx ON wifi_stations USING btree (ap);


--
-- Name: wifi_stations_dev_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_dev_idx ON wifi_stations USING btree (dev COLLATE "default");


--
-- Name: wifi_stations_essid_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_essid_idx ON wifi_stations USING btree (essid COLLATE "default");


--
-- Name: wifi_stations_phy_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_phy_idx ON wifi_stations USING btree (phy COLLATE "default");


--
-- Name: wifi_stations_ts_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_ts_idx ON wifi_stations USING btree (ts);


--
-- Name: wifi_stations_user_idx; Type: INDEX; Schema: public; Owner: status
--

CREATE INDEX wifi_stations_user_idx ON wifi_stations USING btree ("user");


--
-- Name: public; Type: ACL; Schema: -; Owner: status
--

REVOKE ALL ON SCHEMA public FROM postgres;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO status;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

