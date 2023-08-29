--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 09:53:31

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
-- TOC entry 3508 (class 0 OID 16423)
-- Dependencies: 215
-- Data for Name: accuweather; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accuweather (phrase, weather, precipitation) FROM stdin;
clear	CLEAR	f
sunny	CLEAR	f
mostly sunny	CLEAR	f
mostly clear	CLEAR	f
partly sunny	PARTLY_CLOUDY	f
partly cloudy	PARTLY_CLOUDY	f
intermittent clouds	PARTLY_CLOUDY	f
partly sunny w/ showers	PARTLY_CLOUDY	t
partly cloudy w/ showers	PARTLY_CLOUDY	t
partly sunny w/ t-storms	PARTLY_CLOUDY	t
partly cloudy w/ t-storms	PARTLY_CLOUDY	t
fog	FOG	f
partly sunny w/ flurries	PARTLY_CLOUDY	t
partly cloudy w/ flurries	PARTLY_CLOUDY	t
rain and snow	SNOW	t
flurries	SNOW	t
snow	SNOW	t
partly sunny w/ snow	PARTLY_CLOUDY	t
ice	SNOW	t
windy	WINDY	f
mostly cloudy	OVERCAST	f
cloudy	OVERCAST	f
mostly cloudy w/ showers	OVERCAST	t
mostly cloudy w/ t-storms	OVERCAST	t
hazy sunshine	OVERCAST	f
hazy moonlight	OVERCAST	f
mostly cloudy w/ flurries	OVERCAST	t
dreary (overcast)	OVERCAST	f
mostly cloudy w/ snow	OVERCAST	t
showers	RAINY	t
rain	RAINY	t
t-storms	RAINY	t
sleet	RAINY	t
freezing rain	RAINY	t
\.


-- Completed on 2023-08-29 09:53:31

--
-- PostgreSQL database dump complete
--

