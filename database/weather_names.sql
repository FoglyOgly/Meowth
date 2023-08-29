--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:07:41

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3508 (class 0 OID 16697)
-- Dependencies: 275
-- Data for Name: weather_names; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.weather_names (weather, language_id, name, night_name) FROM stdin;
CLEAR	9	Sunny	Clear
PARTLY_CLOUDY	9	Partly Cloudy	\N
SNOW	9	Snow	\N
FOG	9	Fog	\N
WINDY	9	Windy	\N
OVERCAST	9	Cloudy	\N
RAINY	9	Rain	\N
NO_WEATHER	9	Unknown	\N
\.


-- Completed on 2023-08-29 10:07:42

--
-- PostgreSQL database dump complete
--

