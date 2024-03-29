--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 10:01:44

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
-- TOC entry 3508 (class 0 OID 16535)
-- Dependencies: 240
-- Data for Name: moves; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.moves (moveid, fast, type, power, criticalchance, staminalossscalar, durationms, damagewindowstartms, damagewindowendms, energydelta) FROM stdin;
SHADOW_PUNCH	f	POKEMON_TYPE_GHOST	40	0.05	0.06	1700	1300	1500	-33
OMINOUS_WIND	f	POKEMON_TYPE_GHOST	50	0.05	0.06	2300	1850	2100	-33
SHADOW_BALL	f	POKEMON_TYPE_GHOST	100	0.05	0.08	3000	2400	2800	-50
MAGNET_BOMB	f	POKEMON_TYPE_STEEL	70	0.05	0.06	2800	2200	2600	-33
IRON_HEAD	f	POKEMON_TYPE_STEEL	60	0.05	0.08	1900	1300	1700	-50
PARABOLIC_CHARGE	f	POKEMON_TYPE_ELECTRIC	25	0.05	0.05	2800	1200	2400	-50
THUNDER_PUNCH	f	POKEMON_TYPE_ELECTRIC	45	0.05	0.075	1800	1700	1550	-33
THUNDER	f	POKEMON_TYPE_ELECTRIC	100	0.05	0.11	2400	1200	2200	-100
THUNDERBOLT	f	POKEMON_TYPE_ELECTRIC	80	0.05	0.09	2500	1800	2300	-50
TWISTER	f	POKEMON_TYPE_DRAGON	45	0.05	0.04	2800	950	2600	-33
DRAGON_PULSE	f	POKEMON_TYPE_DRAGON	90	0.05	0.085	3600	2150	3300	-50
DRAGON_CLAW	f	POKEMON_TYPE_DRAGON	50	0.25	0.08	1700	1100	1300	-33
DISARMING_VOICE	f	POKEMON_TYPE_FAIRY	70	0.05	0.04	3900	3200	3500	-33
DRAINING_KISS	f	POKEMON_TYPE_FAIRY	60	0.05	0.05	2600	1000	1300	-50
DAZZLING_GLEAM	f	POKEMON_TYPE_FAIRY	100	0.05	0.08	3500	2100	3300	-50
MOONBLAST	f	POKEMON_TYPE_FAIRY	130	0.05	0.095	3900	2200	3700	-100
PLAY_ROUGH	f	POKEMON_TYPE_FAIRY	90	0.05	0.1	2900	1300	2700	-50
CROSS_POISON	f	POKEMON_TYPE_POISON	40	0.25	0.07	1500	900	1300	-33
SLUDGE_BOMB	f	POKEMON_TYPE_POISON	80	0.05	0.09	2300	1100	2100	-50
SLUDGE_WAVE	f	POKEMON_TYPE_POISON	110	0.05	0.095	3200	2000	3000	-100
GUNK_SHOT	f	POKEMON_TYPE_POISON	130	0.05	0.12	3100	1700	2700	-100
BONE_CLUB	f	POKEMON_TYPE_GROUND	40	0.05	0.065	1600	1000	1400	-33
BULLDOZE	f	POKEMON_TYPE_GROUND	80	0.05	0.06	3500	2600	3100	-50
MUD_BOMB	f	POKEMON_TYPE_GROUND	55	0.05	0.065	2300	1700	2100	-33
SIGNAL_BEAM	f	POKEMON_TYPE_BUG	75	0.05	0.075	2900	1800	2600	-50
X_SCISSOR	f	POKEMON_TYPE_BUG	45	0.05	0.08	1600	1200	1400	-33
FLAME_CHARGE	f	POKEMON_TYPE_FIRE	70	0.05	0.05	3800	2900	3450	-33
FLAME_BURST	f	POKEMON_TYPE_FIRE	70	0.05	0.07	2600	1000	2100	-50
FIRE_BLAST	f	POKEMON_TYPE_FIRE	140	0.05	0.11	4200	3100	3900	-100
BRINE	f	POKEMON_TYPE_WATER	60	0.05	0.065	2300	1500	2100	-50
WATER_PULSE	f	POKEMON_TYPE_WATER	70	0.05	0.06	3200	2200	2900	-50
SCALD	f	POKEMON_TYPE_WATER	80	0.05	0.08	3700	1300	3400	-50
HYDRO_PUMP	f	POKEMON_TYPE_WATER	130	0.05	0.11	3300	900	3000	-100
PSYCHIC	f	POKEMON_TYPE_PSYCHIC	100	0.05	0.09	2800	1300	2600	-100
PSYSTRIKE	f	POKEMON_TYPE_PSYCHIC	100	0.05	0.1	4400	3000	4200	-50
ICY_WIND	f	POKEMON_TYPE_ICE	60	0.05	0.055	3300	2000	2800	-33
GIGA_DRAIN	f	POKEMON_TYPE_GRASS	50	0.05	0.075	3900	1200	2200	-100
FIRE_PUNCH	f	POKEMON_TYPE_FIRE	55	0.05	0.075	2200	1500	1900	-33
SOLAR_BEAM	f	POKEMON_TYPE_GRASS	180	0.05	0.12	4900	2700	4700	-100
LEAF_BLADE	f	POKEMON_TYPE_GRASS	70	0.25	0.09	2400	1250	2200	-33
POWER_WHIP	f	POKEMON_TYPE_GRASS	90	\N	0.12	2600	1250	2350	-50
AIR_CUTTER	f	POKEMON_TYPE_FLYING	60	0.25	0.06	2700	1800	2500	-50
HURRICANE	f	POKEMON_TYPE_FLYING	110	0.05	0.11	2700	1200	2400	-100
BRICK_BREAK	f	POKEMON_TYPE_FIGHTING	40	0.25	0.075	1600	800	1400	-33
SWIFT	f	POKEMON_TYPE_NORMAL	60	0.05	0.06	2800	2000	2600	-50
HORN_ATTACK	f	POKEMON_TYPE_NORMAL	40	0.05	0.065	1850	800	1650	-33
STOMP	f	POKEMON_TYPE_NORMAL	55	0.05	0.065	1700	1100	1500	-50
HYPER_FANG	f	POKEMON_TYPE_NORMAL	80	0.05	0.08	2500	1500	2000	-50
BODY_SLAM	f	POKEMON_TYPE_NORMAL	50	0.05	0.085	1900	1200	1700	-33
REST	f	POKEMON_TYPE_NORMAL	50	\N	\N	1900	1500	1700	-33
STRUGGLE	f	POKEMON_TYPE_NORMAL	35	\N	0.1	2200	1200	2000	\N
SCALD_BLASTOISE	f	POKEMON_TYPE_WATER	50	0.05	0.08	4700	2500	4600	-100
HYDRO_PUMP_BLASTOISE	f	POKEMON_TYPE_WATER	90	0.05	0.11	4500	2200	4300	-100
WRAP_GREEN	f	POKEMON_TYPE_NORMAL	25	0.05	0.06	2900	2050	2700	-33
WRAP_PINK	f	POKEMON_TYPE_NORMAL	25	0.05	0.06	2900	2050	2700	-33
FURY_CUTTER_FAST	t	POKEMON_TYPE_BUG	3	\N	0.01	400	100	400	6
BUG_BITE_FAST	t	POKEMON_TYPE_BUG	5	\N	0.01	500	250	450	6
BITE_FAST	t	POKEMON_TYPE_DARK	6	\N	0.01	500	300	500	4
SUCKER_PUNCH_FAST	t	POKEMON_TYPE_DARK	7	\N	0.01	700	300	700	8
DRAGON_BREATH_FAST	t	POKEMON_TYPE_DRAGON	6	\N	0.01	500	300	500	4
THUNDER_SHOCK_FAST	t	POKEMON_TYPE_ELECTRIC	5	\N	0.01	600	300	600	8
SPARK_FAST	t	POKEMON_TYPE_ELECTRIC	6	\N	0.01	700	300	700	9
LOW_KICK_FAST	t	POKEMON_TYPE_FIGHTING	6	\N	0.01	600	300	600	6
KARATE_CHOP_FAST	t	POKEMON_TYPE_FIGHTING	8	\N	0.01	800	600	800	10
EMBER_FAST	t	POKEMON_TYPE_FIRE	10	\N	0.01	1000	600	800	10
WING_ATTACK_FAST	t	POKEMON_TYPE_FLYING	8	\N	0.01	800	550	750	9
PECK_FAST	t	POKEMON_TYPE_FLYING	10	\N	0.01	1000	450	900	10
LICK_FAST	t	POKEMON_TYPE_GHOST	5	\N	0.01	500	200	500	6
SHADOW_CLAW_FAST	t	POKEMON_TYPE_GHOST	9	\N	0.01	700	250	500	6
VINE_WHIP_FAST	t	POKEMON_TYPE_GRASS	7	\N	0.01	600	350	600	6
RAZOR_LEAF_FAST	t	POKEMON_TYPE_GRASS	13	\N	0.01	1000	600	850	7
MUD_SHOT_FAST	t	POKEMON_TYPE_GROUND	5	\N	0.01	600	350	550	7
ICE_SHARD_FAST	t	POKEMON_TYPE_ICE	12	\N	0.01	1200	600	900	12
FROST_BREATH_FAST	t	POKEMON_TYPE_ICE	10	\N	0.01	900	450	750	8
QUICK_ATTACK_FAST	t	POKEMON_TYPE_NORMAL	8	\N	0.01	800	250	550	10
SCRATCH_FAST	t	POKEMON_TYPE_NORMAL	6	\N	0.01	500	300	500	4
TACKLE_FAST	t	POKEMON_TYPE_NORMAL	5	\N	0.01	500	300	500	5
POUND_FAST	t	POKEMON_TYPE_NORMAL	7	\N	0.01	600	340	540	6
CUT_FAST	t	POKEMON_TYPE_NORMAL	5	\N	0.01	500	300	500	5
POISON_JAB_FAST	t	POKEMON_TYPE_POISON	10	\N	0.01	800	200	800	7
ACID_FAST	t	POKEMON_TYPE_POISON	9	\N	0.01	800	400	600	8
AQUA_JET	f	POKEMON_TYPE_WATER	45	0.05	0.04	2600	1700	2100	-33
AQUA_TAIL	f	POKEMON_TYPE_WATER	50	0.05	0.09	1900	1200	1650	-33
SEED_BOMB	f	POKEMON_TYPE_GRASS	55	0.05	0.08	2100	1200	1900	-33
PSYSHOCK	f	POKEMON_TYPE_PSYCHIC	65	0.05	0.08	2700	2000	2600	-33
ANCIENT_POWER	f	POKEMON_TYPE_ROCK	70	0.05	0.06	3500	2850	3100	-33
ROCK_TOMB	f	POKEMON_TYPE_ROCK	70	0.25	0.06	3200	2250	3000	-50
ROCK_SLIDE	f	POKEMON_TYPE_ROCK	80	0.05	0.075	2700	1500	2600	-50
POWER_GEM	f	POKEMON_TYPE_ROCK	80	0.05	0.08	2900	1950	2700	-50
SHADOW_SNEAK	f	POKEMON_TYPE_GHOST	50	0.05	0.04	2900	2200	2700	-33
PSYCHO_CUT_FAST	t	POKEMON_TYPE_PSYCHIC	5	\N	0.01	600	370	570	8
ROCK_THROW_FAST	t	POKEMON_TYPE_ROCK	12	\N	0.01	900	500	800	7
METAL_CLAW_FAST	t	POKEMON_TYPE_STEEL	8	\N	0.01	700	430	630	7
BULLET_PUNCH_FAST	t	POKEMON_TYPE_STEEL	9	\N	0.01	900	300	900	10
WATER_GUN_FAST	t	POKEMON_TYPE_WATER	5	\N	0.01	500	300	500	5
SPLASH_FAST	t	POKEMON_TYPE_WATER	\N	\N	0.01	1730	1030	1230	20
WATER_GUN_FAST_BLASTOISE	t	POKEMON_TYPE_WATER	10	\N	0.01	1000	300	500	6
MUD_SLAP_FAST	t	POKEMON_TYPE_GROUND	15	\N	0.01	1400	1150	1350	12
ZEN_HEADBUTT_FAST	t	POKEMON_TYPE_PSYCHIC	12	\N	0.01	1100	850	1050	10
CONFUSION_FAST	t	POKEMON_TYPE_PSYCHIC	20	\N	0.01	1600	600	1600	15
ZAP_CANNON	f	POKEMON_TYPE_ELECTRIC	140	0.05	0.04	3700	3000	3500	-100
DRAGON_TAIL_FAST	t	POKEMON_TYPE_DRAGON	15	\N	0.01	1100	850	1050	9
AVALANCHE	f	POKEMON_TYPE_ICE	90	0.05	0.04	2700	1700	2100	-50
AIR_SLASH_FAST	t	POKEMON_TYPE_FLYING	14	\N	0.01	1200	1000	1200	10
BRAVE_BIRD	f	POKEMON_TYPE_FLYING	90	0.05	0.04	2000	1000	1600	-100
SKY_ATTACK	f	POKEMON_TYPE_FLYING	80	0.05	0.04	2000	1500	1700	-50
SAND_TOMB	f	POKEMON_TYPE_GROUND	80	0.05	0.04	4000	1700	4000	-50
ROCK_BLAST	f	POKEMON_TYPE_ROCK	50	0.05	0.04	2100	1600	2000	-33
INFESTATION_FAST	t	POKEMON_TYPE_BUG	10	\N	0.01	1100	850	1050	14
HEX_FAST	t	POKEMON_TYPE_GHOST	10	\N	0.01	1200	1000	1200	15
NIGHT_SHADE	f	POKEMON_TYPE_GHOST	60	0.05	0.04	2600	2100	2500	-50
IRON_TAIL_FAST	t	POKEMON_TYPE_STEEL	15	\N	0.01	1100	850	1050	7
GYRO_BALL	f	POKEMON_TYPE_STEEL	80	0.05	0.04	3300	3000	3300	-50
HEAVY_SLAM	f	POKEMON_TYPE_STEEL	70	0.05	0.04	2100	1500	1900	-50
FIRE_SPIN_FAST	t	POKEMON_TYPE_FIRE	14	\N	0.01	1100	850	1050	10
OVERHEAT	f	POKEMON_TYPE_FIRE	160	0.05	0.04	4000	2600	3800	-100
BULLET_SEED_FAST	t	POKEMON_TYPE_GRASS	8	\N	0.01	1100	850	1050	14
GRASS_KNOT	f	POKEMON_TYPE_GRASS	90	0.05	0.04	2600	1700	2600	-50
ENERGY_BALL	f	POKEMON_TYPE_GRASS	90	0.05	0.04	3900	3000	3800	-50
EXTRASENSORY_FAST	t	POKEMON_TYPE_PSYCHIC	12	\N	0.01	1100	850	1050	12
FUTURESIGHT	f	POKEMON_TYPE_PSYCHIC	120	0.05	0.04	2700	1400	2700	-100
MIRROR_COAT	f	POKEMON_TYPE_PSYCHIC	60	0.05	0.04	2600	2300	2500	-50
OUTRAGE	f	POKEMON_TYPE_DRAGON	110	0.05	0.04	3900	2500	3700	-50
SNARL_FAST	f	POKEMON_TYPE_DARK	12	\N	0.01	1100	850	1050	12
CRUNCH	f	POKEMON_TYPE_DARK	70	0.05	0.04	3200	1300	3000	-33
FOUL_PLAY	f	POKEMON_TYPE_DARK	70	0.05	0.04	2000	1700	1900	-50
TAKE_DOWN_FAST	t	POKEMON_TYPE_NORMAL	8	\N	0.01	1200	950	1100	10
WATERFALL_FAST	t	POKEMON_TYPE_WATER	16	\N	0.01	1200	950	1100	8
SURF	f	POKEMON_TYPE_WATER	65	\N	0.01	1700	1400	1600	-50
DRACO_METEOR	f	POKEMON_TYPE_DRAGON	150	\N	0.01	3600	3000	3500	-100
DOOM_DESIRE	f	POKEMON_TYPE_STEEL	80	\N	0.01	1700	1400	1600	-50
YAWN_FAST	t	POKEMON_TYPE_NORMAL	\N	\N	0.01	1700	1400	1600	15
PSYCHO_BOOST	f	POKEMON_TYPE_PSYCHIC	70	\N	0.01	4000	3500	4000	-50
ORIGIN_PULSE	f	POKEMON_TYPE_WATER	130	\N	0.01	1700	1400	1600	-100
PRECIPICE_BLADES	f	POKEMON_TYPE_GROUND	130	\N	0.01	1700	1400	1600	-100
PRESENT_FAST	t	POKEMON_TYPE_NORMAL	5	\N	0.01	1300	1100	1300	20
WEATHER_BALL_FIRE	f	POKEMON_TYPE_FIRE	60	\N	0.01	1600	1350	1600	-33
WEATHER_BALL_ICE	f	POKEMON_TYPE_ICE	60	\N	0.01	1600	1350	1600	-33
WEATHER_BALL_ROCK	f	POKEMON_TYPE_ROCK	60	\N	0.01	1600	1350	1600	-33
WEATHER_BALL_WATER	f	POKEMON_TYPE_WATER	60	\N	0.01	1600	1350	1600	-33
METEOR_MASH	f	POKEMON_TYPE_STEEL	100	0.05	0.065	2600	2300	2500	-50
SKULL_BASH	f	POKEMON_TYPE_NORMAL	130	\N	0.01	3100	1800	2300	-100
ACID_SPRAY	f	POKEMON_TYPE_POISON	20	\N	0.01	3000	2100	2800	-50
EARTH_POWER	f	POKEMON_TYPE_GROUND	100	\N	0.01	3600	2700	3400	-50
CRABHAMMER	f	POKEMON_TYPE_WATER	85	\N	0.01	1900	1500	1750	-50
LEAF_TORNADO	f	POKEMON_TYPE_GRASS	45	\N	0.01	3100	2000	2600	-33
POWER_UP_PUNCH	f	POKEMON_TYPE_FIGHTING	50	\N	0.01	2000	1700	1900	-33
CHARM_FAST	t	POKEMON_TYPE_FAIRY	20	\N	0.01	1500	900	1200	11
FRUSTRATION	f	POKEMON_TYPE_NORMAL	10	\N	0.01	2000	1000	1800	-33
RETURN	f	POKEMON_TYPE_NORMAL	35	\N	0.01	700	100	350	-33
SACRED_SWORD	f	POKEMON_TYPE_FIGHTING	55	\N	0.01	1200	500	1000	-33
FLYING_PRESS	f	POKEMON_TYPE_FIGHTING	110	\N	0.01	2300	1000	2000	-50
WRAP	f	POKEMON_TYPE_NORMAL	60	0.05	0.06	2900	2050	2700	-33
HYPER_BEAM	f	POKEMON_TYPE_NORMAL	150	0.05	0.15	3800	3300	3600	-100
DARK_PULSE	f	POKEMON_TYPE_DARK	80	0.05	0.08	3000	1400	2300	-50
SLUDGE	f	POKEMON_TYPE_POISON	50	0.05	0.065	2100	1200	1550	-33
VICE_GRIP	f	POKEMON_TYPE_NORMAL	35	0.05	0.055	1900	1100	1500	-33
FLAME_WHEEL	f	POKEMON_TYPE_FIRE	60	0.05	0.06	2700	2100	2400	-50
MEGAHORN	f	POKEMON_TYPE_BUG	90	0.05	0.12	2200	1700	1900	-100
FLAMETHROWER	f	POKEMON_TYPE_FIRE	70	0.05	0.09	2200	1500	1700	-50
DIG	f	POKEMON_TYPE_GROUND	100	0.05	0.08	4700	2800	4500	-50
CROSS_CHOP	f	POKEMON_TYPE_FIGHTING	50	0.25	0.1	1500	800	1200	-50
PSYBEAM	f	POKEMON_TYPE_PSYCHIC	70	0.05	0.065	3200	1300	2700	-50
EARTHQUAKE	f	POKEMON_TYPE_GROUND	120	0.05	0.1	3600	2700	3500	-100
STONE_EDGE	f	POKEMON_TYPE_ROCK	100	0.5	0.1	2300	700	2100	-100
ICE_PUNCH	f	POKEMON_TYPE_ICE	50	0.05	0.075	1900	1300	1600	-33
HEART_STAMP	f	POKEMON_TYPE_PSYCHIC	40	0.05	0.06	1900	1100	1600	-33
DISCHARGE	f	POKEMON_TYPE_ELECTRIC	65	0.05	0.08	2500	1700	2100	-33
FLASH_CANNON	f	POKEMON_TYPE_STEEL	100	0.05	0.08	2700	1600	2500	-100
DRILL_PECK	f	POKEMON_TYPE_FLYING	60	0.05	0.08	2300	1700	2100	-33
ICE_BEAM	f	POKEMON_TYPE_ICE	90	0.05	0.09	3300	1300	2800	-50
BLIZZARD	f	POKEMON_TYPE_ICE	130	0.05	0.11	3100	1500	2900	-100
HEAT_WAVE	f	POKEMON_TYPE_FIRE	95	0.05	0.095	3000	1700	2800	-100
AERIAL_ACE	f	POKEMON_TYPE_FLYING	55	0.05	0.06	2400	1900	2200	-33
DRILL_RUN	f	POKEMON_TYPE_GROUND	80	0.25	0.08	2800	1700	2600	-50
PETAL_BLIZZARD	f	POKEMON_TYPE_GRASS	110	0.05	0.09	2600	1700	2300	-100
MEGA_DRAIN	f	POKEMON_TYPE_GRASS	25	0.05	0.04	2600	950	2000	-50
BUG_BUZZ	f	POKEMON_TYPE_BUG	90	0.05	0.09	3700	2000	3100	-50
POISON_FANG	f	POKEMON_TYPE_POISON	35	0.05	0.05	1700	900	1400	-33
NIGHT_SLASH	f	POKEMON_TYPE_DARK	50	0.25	0.07	2200	1300	2000	-33
BUBBLE_BEAM	f	POKEMON_TYPE_WATER	45	0.05	0.065	1900	1450	1700	-33
SUBMISSION	f	POKEMON_TYPE_FIGHTING	60	0.05	0.08	2200	1800	2000	-50
LOW_SWEEP	f	POKEMON_TYPE_FIGHTING	40	0.05	0.065	1900	1300	1650	-33
POISON_STING_FAST	t	POKEMON_TYPE_POISON	5	\N	0.01	600	375	575	7
BUBBLE_FAST	t	POKEMON_TYPE_WATER	12	\N	0.01	1200	750	1000	14
FEINT_ATTACK_FAST	t	POKEMON_TYPE_DARK	10	\N	0.01	900	750	900	9
STEEL_WING_FAST	t	POKEMON_TYPE_STEEL	11	\N	0.01	800	500	800	6
FIRE_FANG_FAST	t	POKEMON_TYPE_FIRE	11	\N	0.01	900	640	840	8
ROCK_SMASH_FAST	t	POKEMON_TYPE_FIGHTING	15	\N	0.01	1300	550	800	10
TRANSFORM_FAST	t	POKEMON_TYPE_NORMAL	\N	\N	0.01	2230	300	700	\N
COUNTER_FAST	t	POKEMON_TYPE_FIGHTING	12	\N	0.01	900	700	900	8
POWDER_SNOW_FAST	t	POKEMON_TYPE_ICE	6	\N	0.01	1000	850	1000	15
CLOSE_COMBAT	f	POKEMON_TYPE_FIGHTING	100	0.05	0.04	2300	1000	2300	-100
DYNAMIC_PUNCH	f	POKEMON_TYPE_FIGHTING	90	0.05	0.04	2700	1200	2700	-50
FOCUS_BLAST	f	POKEMON_TYPE_FIGHTING	140	0.05	0.04	3500	3000	3500	-100
AURORA_BEAM	f	POKEMON_TYPE_ICE	80	0.05	0.04	3550	3350	3550	-50
CHARGE_BEAM_FAST	t	POKEMON_TYPE_ELECTRIC	8	\N	0.01	1100	850	1050	15
VOLT_SWITCH_FAST	t	POKEMON_TYPE_ELECTRIC	20	\N	0.01	2300	1800	2100	25
WILD_CHARGE	f	POKEMON_TYPE_ELECTRIC	90	0.05	0.04	2600	1700	2100	-50
STRUGGLE_BUG_FAST	t	POKEMON_TYPE_BUG	15	\N	0.01	1500	1200	1500	15
SILVER_WIND	f	POKEMON_TYPE_BUG	70	0.05	0.04	3700	1700	3500	-33
ASTONISH_FAST	t	POKEMON_TYPE_GHOST	8	\N	0.01	1100	700	1050	14
HIDDEN_POWER_FAST	t	POKEMON_TYPE_NORMAL	15	0.05	0.01	1500	1100	1400	15
FRENZY_PLANT	f	POKEMON_TYPE_GRASS	100	\N	0.01	2600	2145	2550	-50
SMACK_DOWN_FAST	t	POKEMON_TYPE_ROCK	16	\N	0.01	1200	800	1100	8
BLAST_BURN	f	POKEMON_TYPE_FIRE	110	\N	0.01	3300	2750	3200	-50
HYDRO_CANNON	f	POKEMON_TYPE_WATER	90	0.05	0.065	1900	500	1600	-50
LAST_RESORT	f	POKEMON_TYPE_NORMAL	90	0.05	0.065	2900	2700	2850	-50
SYNCHRONOISE	f	POKEMON_TYPE_PSYCHIC	80	\N	0.01	2600	850	1600	-50
LOCK_ON_FAST	t	POKEMON_TYPE_NORMAL	1	\N	0.01	300	170	300	6
THUNDER_FANG_FAST	t	POKEMON_TYPE_ELECTRIC	12	\N	0.01	1200	400	900	16
ICE_FANG_FAST	t	POKEMON_TYPE_ICE	12	\N	0.01	1500	400	1000	20
HORN_DRILL	f	POKEMON_TYPE_NORMAL	\N	\N	0.01	1900	500	1500	\N
FISSURE	f	POKEMON_TYPE_GROUND	0	0	0.01	2800	1000	2300	\N
HIDDEN_POWER_NORMAL_FAST	t	POKEMON_TYPE_NORMAL	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_FIGHTING_FAST	t	POKEMON_TYPE_FIGHTING	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_FLYING_FAST	t	POKEMON_TYPE_FLYING	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_POISON_FAST	t	POKEMON_TYPE_POISON	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_GROUND_FAST	t	POKEMON_TYPE_GROUND	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_ROCK_FAST	t	POKEMON_TYPE_ROCK	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_BUG_FAST	t	POKEMON_TYPE_BUG	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_GHOST_FAST	t	POKEMON_TYPE_GHOST	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_STEEL_FAST	t	POKEMON_TYPE_STEEL	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_FIRE_FAST	t	POKEMON_TYPE_FIRE	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_WATER_FAST	t	POKEMON_TYPE_WATER	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_GRASS_FAST	t	POKEMON_TYPE_GRASS	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_ELECTRIC_FAST	t	POKEMON_TYPE_ELECTRIC	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_PSYCHIC_FAST	t	POKEMON_TYPE_PSYCHIC	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_ICE_FAST	t	POKEMON_TYPE_ICE	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_DRAGON_FAST	t	POKEMON_TYPE_DRAGON	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_DARK_FAST	t	POKEMON_TYPE_DARK	15	0.05	0.01	1500	1100	1400	15
HIDDEN_POWER_FAIRY_FAST	t	POKEMON_TYPE_FAIRY	15	0.05	0.01	1500	1100	1400	15
AURA_SPHERE	f	POKEMON_TYPE_FIGHTING	90	\N	0.01	1800	1000	1600	-50
PAYBACK	f	POKEMON_TYPE_DARK	100	\N	0.01	2200	1100	2000	-100
ROCK_WRECKER	f	POKEMON_TYPE_ROCK	110	\N	0.01	3600	2000	2700	-50
AEROBLAST	f	POKEMON_TYPE_FLYING	180	\N	0.01	3400	3200	3400	-100
TECHNO_BLAST_NORMAL	f	POKEMON_TYPE_NORMAL	120	\N	\N	2000	1600	2000	-100
TECHNO_BLAST_BURN	f	POKEMON_TYPE_FIRE	120	\N	\N	2000	1400	2000	-100
TECHNO_BLAST_CHILL	f	POKEMON_TYPE_ICE	120	\N	\N	2000	1400	2000	-100
TECHNO_BLAST_WATER	f	POKEMON_TYPE_WATER	120	\N	\N	2000	1500	2000	-100
TECHNO_BLAST_SHOCK	f	POKEMON_TYPE_ELECTRIC	120	\N	\N	2000	1600	2000	-100
FLY	f	POKEMON_TYPE_FLYING	80	\N	0.01	1800	1200	1500	-50
V_CREATE	f	POKEMON_TYPE_FIRE	95	\N	0.01	2800	1700	2500	-33
LEAF_STORM	f	POKEMON_TYPE_GRASS	130	\N	0.01	2500	1100	1250	-100
TRI_ATTACK	f	POKEMON_TYPE_NORMAL	75	\N	0.01	2500	1300	2400	-50
GUST_FAST	t	POKEMON_TYPE_FLYING	25	\N	0.01	2000	900	2000	20
INCINERATE_FAST	t	POKEMON_TYPE_FIRE	29	\N	0.01	2300	500	2300	20
FEATHER_DANCE	f	POKEMON_TYPE_FLYING	35	\N	0.01	2800	1700	2500	-50
\.


-- Completed on 2023-08-29 10:01:44

--
-- PostgreSQL database dump complete
--

