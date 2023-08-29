--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:05:21

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
-- TOC entry 3512 (class 0 OID 16640)
-- Dependencies: 263
-- Data for Name: teams; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teams (team_id, color_id, identifier, emoji) FROM stdin;
1	2	mystic	350686962388303873
2	10	instinct	350686957703135232
3	8	valor	350686957820706816
\.


-- Completed on 2023-08-29 10:05:22

--
-- PostgreSQL database dump complete
--

