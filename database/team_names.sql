--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:05:04

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
-- TOC entry 3508 (class 0 OID 16632)
-- Dependencies: 261
-- Data for Name: team_names; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.team_names (team_id, language_id, team_name) FROM stdin;
1	9	mystic
1	12	mystic
1	1	ミスティック
1	2	misutikku
1	5	sagesse
1	6	weisheit
1	7	sabiduría
1	8	saggezza
2	9	instinct
2	12	instinct
2	1	インスティンクト
2	2	insutinkuto
2	5	intuition
2	6	intuition
2	7	instinto
2	8	istinto
3	9	valor
3	12	valour
3	1	ヴァーラー
3	2	ba-ra
3	5	bravoure
3	6	wagemut
3	7	valor
3	8	coraggio
\.


-- Completed on 2023-08-29 10:05:04

--
-- PostgreSQL database dump complete
--

