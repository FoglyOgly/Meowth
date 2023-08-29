--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:06:58

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
-- TOC entry 3508 (class 0 OID 16671)
-- Dependencies: 270
-- Data for Name: types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.types (typeid, emoji, weather) FROM stdin;
POKEMON_TYPE_NORMAL	<:normal:345679285945892865>	PARTLY_CLOUDY
POKEMON_TYPE_STEEL	<:steel:345679285811544065>	SNOW
POKEMON_TYPE_FLYING	<:flying:345679283416727552>	WINDY
POKEMON_TYPE_GROUND	<:ground:345679285157101568>	CLEAR
POKEMON_TYPE_ROCK	<:rock:345679285744566283>	PARTLY_CLOUDY
POKEMON_TYPE_PSYCHIC	<:psychic:345679284087554050>	WINDY
POKEMON_TYPE_DARK	<:dark:345679282489655296>	FOG
POKEMON_TYPE_DRAGON	<:dragon1:345679282342723586>	WINDY
POKEMON_TYPE_FIRE	<:fire1:345679285484257290>	CLEAR
POKEMON_TYPE_GRASS	<:grass:345679285958475776>	CLEAR
POKEMON_TYPE_GHOST	<:ghost1:345679285589245972>	FOG
POKEMON_TYPE_FIGHTING	<:fighting:345679285899755520>	OVERCAST
POKEMON_TYPE_FAIRY	<:fairy:345679281755783169>	OVERCAST
POKEMON_TYPE_ELECTRIC	<:electric:345679282175213570>	RAINY
POKEMON_TYPE_WATER	<:water:345679285501165572>	RAINY
POKEMON_TYPE_BUG	<:bug1:345679282472747018>	RAINY
POKEMON_TYPE_POISON	<:poison:512709840422830082>	OVERCAST
POKEMON_TYPE_ICE	<:ice:522104739165634580>	SNOW
\.


-- Completed on 2023-08-29 10:06:58

--
-- PostgreSQL database dump complete
--

