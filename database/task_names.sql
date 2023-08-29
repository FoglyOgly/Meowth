--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:04:23

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
-- TOC entry 3508 (class 0 OID 16627)
-- Dependencies: 260
-- Data for Name: task_names; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_names (task_id, language_id, task_desc, category) FROM stdin;
226	9	Catch 15 Pokémon.	catch
232	9	Win 5 raids.	raid
227	9	Hatch 5 Eggs.	hatch
233	9	Use 10 Nanab Berries while catching Pokémon.	berries
236	9	Send 10 Gifts to friends.	gift
208	9	Make 3 Great Curveball Throws.	throw
209	9	Earn 3 Candies walking with your buddy.	walk
210	9	Catch 5 Normal-type Pokémon.	catch
211	9	Catch 5 Fairy-type Pokémon.	catch
204	9	Spin 10 PokéStops or Gyms.	spin
205	9	Catch 3 different species of Dark-type Pokémon.	catch
206	9	Make an Excellent Throw.	throw
207	9	Catch a Ditto.	catch
230	9	Catch 3 Fire-, Water-, or Electric-type Pokémon.	catch
231	9	Catch 3 different species of Psychic-type Pokémon.	catch
228	9	Power up Pokémon 5 times.	power up
229	9	Make 3 Great Throws.	throw
212	9	Make 3 Excellent Throws in a row.	throw
213	9	Take 5 snapshots of Eevee.	snapshot
224	9	Win a level 3 or higher raid.	raid
225	9	Win 3 Gym battles.	battle
185	9	Use 5 Razz Berries to help catch Pokémon.	berries
184	9	Hatch an Egg.	hatch
187	9	Trade a Pokémon.	trade
186	9	Use a supereffective Charged Attack in 7 Gym battles.	battle
189	9	Battle in a raid.	battle
188	9	Make 3 Nice Throws in a row.	throw
191	9	Battle in a Gym 5 times.	battle
190	9	Make 2 Nice Curveball Throws in a row.	throw
193	9	Catch 10 Pokémon.	catch
192	9	Win a raid.	raid
235	9	Make 5 Curveball Throws in a row.	throw
223	9	Make 5 Nice Throws.	throw
222	9	Battle in a Gym.	battle
195	9	Sponsored: Catch 8 Pokémon.	catch
194	9	Evolve a Pokémon.	evolve
197	9	Win a Gym battle.	battle
196	9	Catch 10 Pokémon with Weather Boost.	catch
199	9	Transfer 3 Pokémon.	transfer
198	9	Use a supereffective Charged Attack in a Gym battle.	battle
201	9	Catch 10 Normal-type Pokémon.	catch
200	9	Catch 4 Grass- or Ice-type Pokémon.	catch
203	9	Sponsored: Send 3 Gifts to friends.	gift
202	9	Catch a Dragon-type Pokémon.	catch
215	9	Make 5 Great Curveball Throws in a row.	throw
214	9	Battle another Trainer.	battle
221	9	Battle a team leader 2 times.	battle
220	9	Use 5 Berries to help catch Pokémon.	berries
219	9	Make 3 Great Curveball Throws in a row.	throw
218	9	Make 3 Great Throws in a row.	throw
217	9	Catch 5 Pokémon with Weather Boost.	catch
216	9	Hatch 3 Eggs.	hatch
234	9	Win 3 raids.	raid
\.


-- Completed on 2023-08-29 10:04:24

--
-- PostgreSQL database dump complete
--

