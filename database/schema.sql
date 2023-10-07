--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

-- Started on 2023-08-29 08:58:37

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
-- TOC entry 2 (class 3079 OID 16399)
-- Name: adminpack; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS adminpack WITH SCHEMA pg_catalog;


--
-- TOC entry 3710 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION adminpack; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION adminpack IS 'administrative functions for PostgreSQL';


--
-- TOC entry 280 (class 1255 OID 16409)
-- Name: cancel(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.cancel() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
oldid bigint;
BEGIN
SELECT COALESCE (OLD.coming, OLD.here) INTO oldid;
PERFORM pg_notify('cancel_' || oldid::text, OLD.id::text);
RETURN NULL;
END;
$$;


ALTER FUNCTION public.cancel() OWNER TO meowth;

--
-- TOC entry 281 (class 1255 OID 16410)
-- Name: enable_forecast(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.enable_forecast() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
UPDATE current_weather SET forecast=NEW.enabled WHERE guild_id=NEW.guild_id;
RETURN NEW;
END;
$$;


ALTER FUNCTION public.enable_forecast() OWNER TO meowth;

--
-- TOC entry 282 (class 1255 OID 16411)
-- Name: get_message_ids(bigint); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.get_message_ids(bigint) RETURNS text[]
    LANGUAGE sql
    AS $_$
SELECT messages FROM raids WHERE id = $1
$_$;


ALTER FUNCTION public.get_message_ids(bigint) OWNER TO meowth;

--
-- TOC entry 283 (class 1255 OID 16412)
-- Name: get_raid_messages(bigint); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.get_raid_messages(x bigint) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
DECLARE
list text[];
BEGIN
SELECT message_ids into list FROM raids WHERE id=x;
RETURN list;
END;
$$;


ALTER FUNCTION public.get_raid_messages(x bigint) OWNER TO meowth;

--
-- TOC entry 284 (class 1255 OID 16413)
-- Name: insert_reverse_travel(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.insert_reverse_travel() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
INSERT INTO gym_travel (origin_id, dest_id, travel_time)
VALUES (NEW.dest_id, NEW.origin_id, NEW.travel_time)
ON CONFLICT ON CONSTRAINT gym_travel_pkey DO UPDATE
SET travel_time = EXCLUDED.travel_time;
RETURN NEW;
END;
$$;


ALTER FUNCTION public.insert_reverse_travel() OWNER TO meowth;

--
-- TOC entry 285 (class 1255 OID 16414)
-- Name: notify_messages(bigint, text[]); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.notify_messages(raidid bigint, list text[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
PERFORM pg_notify('raid_unhere_' || raidid::text, list);
END;
$$;


ALTER FUNCTION public.notify_messages(raidid bigint, list text[]) OWNER TO meowth;

--
-- TOC entry 286 (class 1255 OID 16415)
-- Name: rsvp_notify(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.rsvp_notify() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
RETURN OLD.here;
END;
$$;


ALTER FUNCTION public.rsvp_notify() OWNER TO meowth;

--
-- TOC entry 287 (class 1255 OID 16416)
-- Name: unhere(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.unhere() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE id_list text[];
id text;
BEGIN
SELECT get_message_ids(OLD.here) INTO id_list;
FOREACH id IN ARRAY id_list
LOOP
PERFORM pg_notify('unhere_' || OLD.here::text, id);
END LOOP;
RETURN NULL;
END;
$$;


ALTER FUNCTION public.unhere() OWNER TO meowth;

--
-- TOC entry 288 (class 1255 OID 16417)
-- Name: update_cells(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.update_cells() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
_enabled boolean;
BEGIN
SELECT enabled FROM forecast_config WHERE guild_id=NEW.guild INTO _enabled;
IF (_enabled = true) THEN
	IF NOT EXISTS (SELECT 1 FROM current_weather WHERE cellid=NEW.l10 AND guild_id=NEW.guild) THEN
		INSERT INTO current_weather (cellid, guild_id, forecast, pull_hour) VALUES (NEW.l10, NEW.guild, true, 0);
	END IF;
END IF;
RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_cells() OWNER TO meowth;

--
-- TOC entry 289 (class 1255 OID 16418)
-- Name: update_meetuprsvp(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.update_meetuprsvp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
IF (TG_OP = 'DELETE') THEN
    PERFORM pg_notify('meetup', OLD.meetup_id || '/' || OLD.user_id || '/cancel');
    RETURN OLD;
END IF;
IF (TG_OP = 'INSERT') THEN
    PERFORM pg_notify('meetup', NEW.meetup_id || '/' || NEW.user_id || '/' || NEW.status);
    RETURN NEW;
END IF;
IF (TG_OP = 'UPDATE') THEN
    IF OLD.party IS DISTINCT FROM NEW.party THEN
        PERFORM pg_notify('train', NEW.meetup_id || '/' || NEW.user_id || '/' || NEW.status);
    END IF;
    RETURN NEW;
END IF;
RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_meetuprsvp() OWNER TO meowth;

--
-- TOC entry 290 (class 1255 OID 16419)
-- Name: update_raid_weather(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.update_raid_weather() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
IF (TG_OP = 'INSERT') THEN
    PERFORM pg_notify('weather', NEW.cellid || '/' || NEW.current_weather);
    RETURN NEW;
ELSIF (TG_OP = 'UPDATE') THEN
    IF NEW.current_weather IS DISTINCT FROM OLD.current_weather THEN
        PERFORM pg_notify('weather', NEW.cellid || '/' || NEW.current_weather);
        RETURN NEW;
    END IF;
END IF;
RETURN NULL;
END;
$$;


ALTER FUNCTION public.update_raid_weather() OWNER TO meowth;

--
-- TOC entry 302 (class 1255 OID 16420)
-- Name: update_rsvp(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.update_rsvp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
oldid bigint;
BEGIN
IF (TG_OP = 'DELETE') THEN
    IF OLD.status != 'lobby' THEN
        PERFORM pg_notify('rsvp', OLD.raid_id || '/' || OLD.user_id || '/cancel');
    END IF;
    RETURN OLD;
END IF;
IF NEW.status = 'here' THEN
    SELECT raid_id FROM raid_rsvp WHERE user_id = NEW.user_id AND status = 'here' INTO oldid;
    IF oldid IS NOT NULL AND oldid IS DISTINCT FROM NEW.raid_id THEN
        DELETE FROM raid_rsvp WHERE user_id = NEW.user_id AND status = 'here' AND raid_id = oldid;
        PERFORM pg_notify('rsvp', oldid || '/' || NEW.user_id || '/cancel');
    END IF;
END IF;
IF (TG_OP = 'UPDATE') THEN
    IF OLD.status = 'lobby' THEN
        RETURN OLD;
    ELSIF NEW.status IS DISTINCT FROM OLD.status OR NEW.party IS DISTINCT FROM OLD.party THEN
        PERFORM pg_notify('rsvp', NEW.raid_id || '/' || NEW.user_id || '/' || NEW.status);
    ELSIF NEW.bosses IS DISTINCT FROM OLD.bosses THEN
        PERFORM pg_notify('rsvp', NEW.raid_id || '/bosses');
    ELSIF NEW.est_power IS DISTINCT FROM OLD.est_power THEN
        PERFORM pg_notify('rsvp', NEW.raid_id || '/power');
    ELSIF NEW.raid_id IS DISTINCT FROM OLD.raid_id THEN
        PERFORM pg_notify('rsvp', NEW.raid_id || '/' || NEW.user_id || '/' || NEW.status);
    END IF;
ELSIF (TG_OP = 'INSERT') THEN
    PERFORM pg_notify('rsvp', NEW.raid_id || '/' || NEW.user_id || '/' || NEW.status);
END IF;
RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_rsvp() OWNER TO meowth;

--
-- TOC entry 303 (class 1255 OID 16421)
-- Name: update_trainrsvp(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.update_trainrsvp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
IF (TG_OP = 'DELETE') THEN
    PERFORM pg_notify('train', OLD.train_id || '/' || OLD.user_id || '/cancel');
    RETURN OLD;
END IF;
IF (TG_OP = 'INSERT') THEN
    PERFORM pg_notify('train', NEW.train_id || '/' || NEW.user_id || '/join');
    RETURN NEW;
END IF;
IF (TG_OP = 'UPDATE') THEN
    IF OLD.train_id IS DISTINCT FROM NEW.train_id THEN
        PERFORM pg_notify('train', OLD.train_id || '/' || OLD.user_id || '/cancel');
        PERFORM pg_notify('train', NEW.train_id || '/' || NEW.user_id || '/join');
    END IF;
    ELSIF OLD.party IS DISTINCT FROM NEW.party THEN
        PERFORM pg_notify('train', NEW.train_id || '/' || NEW.user_id || '/join');
    RETURN NEW;
END IF;
RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_trainrsvp() OWNER TO meowth;

--
-- TOC entry 304 (class 1255 OID 16422)
-- Name: update_weather(); Type: FUNCTION; Schema: public; Owner: meowth
--

CREATE FUNCTION public.update_weather() RETURNS void
    LANGUAGE plpgsql
    AS $$DECLARE
cur int := EXTRACT(HOUR FROM now())::int % 8;
col text := 'forecast_' || cur::text;
BEGIN
EXECUTE 'UPDATE weather_forecasts SET current_weather=' || col;
EXECUTE 'UPDATE current_weather c SET current_weather = f.current_weather FROM weather_forecasts f WHERE c.cellid = f.cellid AND c.forecast = true AND c.pull_hour = f.pull_hour';
RETURN;
END;
$$;


ALTER FUNCTION public.update_weather() OWNER TO meowth;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 16423)
-- Name: accuweather; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.accuweather (
    phrase text NOT NULL,
    weather text NOT NULL,
    precipitation boolean
);


ALTER TABLE public.accuweather OWNER TO meowth;

--
-- TOC entry 216 (class 1259 OID 16428)
-- Name: archive; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.archive (
    guild_id numeric(20,0) NOT NULL,
    category numeric(20,0),
    phrase_list text[]
);


ALTER TABLE public.archive OWNER TO meowth;

--
-- TOC entry 217 (class 1259 OID 16433)
-- Name: command_log; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.command_log (
    message_id bigint NOT NULL,
    sent bigint NOT NULL,
    author_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    guild_id bigint,
    prefix text NOT NULL,
    command text NOT NULL,
    invoked_with text NOT NULL,
    invoked_subcommand text,
    subcommand_passed text,
    command_failed boolean DEFAULT false NOT NULL,
    cog text
);


ALTER TABLE public.command_log OWNER TO meowth;

--
-- TOC entry 218 (class 1259 OID 16439)
-- Name: counters_data; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.counters_data (
    boss_id text NOT NULL,
    level text NOT NULL,
    weather text NOT NULL,
    fast_move text NOT NULL,
    charge_move text NOT NULL,
    estimator_20 double precision,
    counter_1_id text,
    counter_1_fast text,
    counter_1_charge text,
    counter_2_id text,
    counter_2_fast text,
    counter_2_charge text,
    counter_3_id text,
    counter_3_fast text,
    counter_3_charge text,
    counter_4_id text,
    counter_4_fast text,
    counter_4_charge text,
    counter_5_id text,
    counter_5_fast text,
    counter_5_charge text,
    counter_6_id text,
    counter_6_fast text,
    counter_6_charge text,
    estimator_min double precision
);


ALTER TABLE public.counters_data OWNER TO meowth;

--
-- TOC entry 219 (class 1259 OID 16444)
-- Name: cpm_table; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.cpm_table (
    level double precision NOT NULL,
    cpm double precision NOT NULL
);


ALTER TABLE public.cpm_table OWNER TO meowth;

--
-- TOC entry 220 (class 1259 OID 16447)
-- Name: current_weather; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.current_weather (
    cellid text NOT NULL,
    guild_id numeric(20,0) NOT NULL,
    current_weather text,
    forecast boolean,
    pull_hour integer
);


ALTER TABLE public.current_weather OWNER TO meowth;

--
-- TOC entry 221 (class 1259 OID 16452)
-- Name: custom_roles; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.custom_roles (
    guild_id numeric(20,0) NOT NULL,
    role_id numeric(20,0) NOT NULL
);


ALTER TABLE public.custom_roles OWNER TO meowth;

--
-- TOC entry 222 (class 1259 OID 16455)
-- Name: discord_logs; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.discord_logs (
    log_id bigint NOT NULL,
    created bigint NOT NULL,
    logger_name text,
    level_name text,
    file_path text,
    module text,
    func_name text,
    line_no integer,
    message text,
    traceback text
);


ALTER TABLE public.discord_logs OWNER TO meowth;

--
-- TOC entry 223 (class 1259 OID 16460)
-- Name: discord_messages; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.discord_messages (
    message_id bigint NOT NULL,
    sent bigint NOT NULL,
    is_edit boolean DEFAULT false NOT NULL,
    deleted boolean DEFAULT false NOT NULL,
    author_id bigint NOT NULL,
    channel_id bigint NOT NULL,
    guild_id bigint,
    content text,
    clean_content text,
    embeds jsonb[],
    webhook_id bigint,
    attachments text[]
);


ALTER TABLE public.discord_messages OWNER TO meowth;

--
-- TOC entry 224 (class 1259 OID 16467)
-- Name: forecast_config; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.forecast_config (
    guild_id numeric(20,0) NOT NULL,
    enabled boolean,
    patron_id numeric(20,0)
);


ALTER TABLE public.forecast_config OWNER TO meowth;

--
-- TOC entry 225 (class 1259 OID 16470)
-- Name: form_names; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.form_names (
    formid integer NOT NULL,
    language_id integer NOT NULL,
    name text
);


ALTER TABLE public.form_names OWNER TO meowth;

--
-- TOC entry 226 (class 1259 OID 16475)
-- Name: forms; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.forms (
    pokemonid text NOT NULL,
    formid integer NOT NULL
);


ALTER TABLE public.forms OWNER TO meowth;

--
-- TOC entry 227 (class 1259 OID 16480)
-- Name: guild_config; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.guild_config (
    guild_id bigint NOT NULL,
    config_name text NOT NULL,
    config_value text NOT NULL
);


ALTER TABLE public.guild_config OWNER TO meowth;

--
-- TOC entry 228 (class 1259 OID 16485)
-- Name: guild_settings; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.guild_settings (
    guild_id numeric(20,0) NOT NULL,
    version text
);


ALTER TABLE public.guild_settings OWNER TO meowth;

--
-- TOC entry 229 (class 1259 OID 16490)
-- Name: gym_travel; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.gym_travel (
    origin_id bigint NOT NULL,
    dest_id bigint NOT NULL,
    travel_time bigint
);


ALTER TABLE public.gym_travel OWNER TO meowth;

--
-- TOC entry 230 (class 1259 OID 16493)
-- Name: gyms; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.gyms (
    id bigint NOT NULL,
    name text NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    l10 text NOT NULL,
    exraid boolean,
    nickname text,
    guild numeric(20,0)
);


ALTER TABLE public.gyms OWNER TO meowth;

--
-- TOC entry 231 (class 1259 OID 16498)
-- Name: gyms_id_seq; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.gyms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.gyms_id_seq OWNER TO meowth;

--
-- TOC entry 3711 (class 0 OID 0)
-- Dependencies: 231
-- Name: gyms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: meowth
--

ALTER SEQUENCE public.gyms_id_seq OWNED BY public.gyms.id;


--
-- TOC entry 232 (class 1259 OID 16499)
-- Name: integers; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.integers
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.integers OWNER TO meowth;

--
-- TOC entry 233 (class 1259 OID 16500)
-- Name: item_names; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.item_names (
    item_id text NOT NULL,
    language_id integer NOT NULL,
    name text
);


ALTER TABLE public.item_names OWNER TO meowth;

--
-- TOC entry 234 (class 1259 OID 16505)
-- Name: languages; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.languages (
    language_id bigint NOT NULL,
    iso639 text NOT NULL,
    iso3166 text NOT NULL,
    identifier text NOT NULL,
    official boolean NOT NULL
);


ALTER TABLE public.languages OWNER TO meowth;

--
-- TOC entry 235 (class 1259 OID 16510)
-- Name: meetup_rsvp; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.meetup_rsvp (
    meetup_id bigint NOT NULL,
    user_id numeric(20,0) NOT NULL,
    status text NOT NULL,
    party integer[]
);


ALTER TABLE public.meetup_rsvp OWNER TO meowth;

--
-- TOC entry 236 (class 1259 OID 16515)
-- Name: meetups; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.meetups (
    id bigint NOT NULL,
    guild_id numeric(20,0) NOT NULL,
    report_channel_id numeric(20,0) NOT NULL,
    channel_id numeric(20,0) NOT NULL,
    location text NOT NULL,
    start double precision,
    tz text,
    message_ids text[],
    endtime double precision
);


ALTER TABLE public.meetups OWNER TO meowth;

--
-- TOC entry 237 (class 1259 OID 16520)
-- Name: meowth_logs; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.meowth_logs (
    log_id bigint NOT NULL,
    created bigint NOT NULL,
    logger_name text,
    level_name text,
    file_path text,
    module text,
    func_name text,
    line_no integer,
    message text,
    traceback text
);


ALTER TABLE public.meowth_logs OWNER TO meowth;

--
-- TOC entry 238 (class 1259 OID 16525)
-- Name: modifiers; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.modifiers (
    id bigint NOT NULL,
    guild numeric(20,0),
    location text,
    reporter_id numeric(20,0),
    kind text,
    created double precision,
    messages text[],
    pokemon text[]
);


ALTER TABLE public.modifiers OWNER TO meowth;

--
-- TOC entry 239 (class 1259 OID 16530)
-- Name: move_names; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.move_names (
    moveid text NOT NULL,
    language_id integer NOT NULL,
    name text
);


ALTER TABLE public.move_names OWNER TO meowth;

--
-- TOC entry 240 (class 1259 OID 16535)
-- Name: moves; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.moves (
    moveid text NOT NULL,
    fast boolean NOT NULL,
    type text NOT NULL,
    power integer,
    criticalchance double precision,
    staminalossscalar double precision,
    durationms integer NOT NULL,
    damagewindowstartms integer NOT NULL,
    damagewindowendms integer NOT NULL,
    energydelta integer
);


ALTER TABLE public.moves OWNER TO meowth;

--
-- TOC entry 241 (class 1259 OID 16540)
-- Name: movesets; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.movesets (
    pokemonid text NOT NULL,
    moveid text NOT NULL,
    legacy boolean
);


ALTER TABLE public.movesets OWNER TO meowth;

--
-- TOC entry 242 (class 1259 OID 16545)
-- Name: pokedex; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.pokedex (
    pokemonid text NOT NULL,
    language_id integer NOT NULL,
    name text,
    description text,
    category text
);


ALTER TABLE public.pokedex OWNER TO meowth;

--
-- TOC entry 243 (class 1259 OID 16550)
-- Name: pokemon; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.pokemon (
    pokemonid text NOT NULL,
    num integer NOT NULL,
    gen integer NOT NULL,
    type text NOT NULL,
    type2 text,
    formid integer,
    gender_type text NOT NULL,
    mythical boolean NOT NULL,
    legendary boolean NOT NULL,
    wild_available boolean NOT NULL,
    shiny_available boolean NOT NULL,
    basestamina integer NOT NULL,
    baseattack integer NOT NULL,
    basedefense integer NOT NULL,
    heightm double precision NOT NULL,
    weightkg double precision NOT NULL,
    heightstddev double precision NOT NULL,
    weightstddev double precision NOT NULL,
    familyid text NOT NULL,
    stageid integer NOT NULL,
    evolves_from text,
    evo_cost_candy integer,
    evo_cost_item text,
    evo_condition text,
    is_regional boolean,
    trade_available boolean,
    buddydistance integer,
    initial_mega_cost integer,
    mega_cost integer,
    mega_available boolean
);


ALTER TABLE public.pokemon OWNER TO meowth;

--
-- TOC entry 244 (class 1259 OID 16555)
-- Name: pokestops; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.pokestops (
    id bigint NOT NULL,
    name text NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    l10 text NOT NULL,
    nickname text,
    guild numeric(20,0) NOT NULL
);


ALTER TABLE public.pokestops OWNER TO meowth;

--
-- TOC entry 245 (class 1259 OID 16560)
-- Name: pokestops_id_seq; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.pokestops_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pokestops_id_seq OWNER TO meowth;

--
-- TOC entry 3712 (class 0 OID 0)
-- Dependencies: 245
-- Name: pokestops_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: meowth
--

ALTER SEQUENCE public.pokestops_id_seq OWNED BY public.pokestops.id;


--
-- TOC entry 246 (class 1259 OID 16561)
-- Name: prefixes; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.prefixes (
    guild_id numeric(20,0) NOT NULL,
    prefix text NOT NULL
);


ALTER TABLE public.prefixes OWNER TO meowth;

--
-- TOC entry 247 (class 1259 OID 16566)
-- Name: raid_bosses; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.raid_bosses (
    level text NOT NULL,
    pokemon_id text NOT NULL,
    verified boolean,
    available boolean,
    shiny boolean,
    is_regional boolean,
    start_time double precision,
    end_time double precision
);


ALTER TABLE public.raid_bosses OWNER TO meowth;

--
-- TOC entry 248 (class 1259 OID 16571)
-- Name: raid_groups; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.raid_groups (
    raid_id bigint NOT NULL,
    starttime double precision,
    users numeric(20,0)[],
    est_power double precision,
    grp_id bigint NOT NULL
);


ALTER TABLE public.raid_groups OWNER TO meowth;

--
-- TOC entry 249 (class 1259 OID 16576)
-- Name: raid_groups_grp_id_seq; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.raid_groups_grp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.raid_groups_grp_id_seq OWNER TO meowth;

--
-- TOC entry 3713 (class 0 OID 0)
-- Dependencies: 249
-- Name: raid_groups_grp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: meowth
--

ALTER SEQUENCE public.raid_groups_grp_id_seq OWNED BY public.raid_groups.grp_id;


--
-- TOC entry 250 (class 1259 OID 16577)
-- Name: raid_rsvp; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.raid_rsvp (
    user_id numeric(20,0) NOT NULL,
    raid_id bigint NOT NULL,
    status text,
    bosses text[],
    estimator double precision,
    party integer[] DEFAULT ARRAY[0, 0, 0, 1],
    est_power double precision,
    invites numeric(20,0)[]
);


ALTER TABLE public.raid_rsvp OWNER TO meowth;

--
-- TOC entry 251 (class 1259 OID 16583)
-- Name: raids; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.raids (
    id bigint NOT NULL,
    gym text,
    guild numeric(20,0) NOT NULL,
    level text NOT NULL,
    pkmn text[],
    hatch double precision,
    endtime double precision NOT NULL,
    messages text[],
    channels text[],
    tz text,
    train_msgs text[],
    report_channel numeric(20,0),
    reporter_id numeric(20,0),
    completed_by numeric(20,0)[]
);


ALTER TABLE public.raids OWNER TO meowth;

--
-- TOC entry 252 (class 1259 OID 16588)
-- Name: raids_id_seq; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.raids_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.raids_id_seq OWNER TO meowth;

--
-- TOC entry 3714 (class 0 OID 0)
-- Dependencies: 252
-- Name: raids_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: meowth
--

ALTER SEQUENCE public.raids_id_seq OWNED BY public.raids.id;


--
-- TOC entry 253 (class 1259 OID 16589)
-- Name: regional_raids; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.regional_raids (
    boss text NOT NULL,
    min_lat double precision NOT NULL,
    max_lat double precision NOT NULL,
    min_lon double precision NOT NULL,
    max_lon double precision NOT NULL
);


ALTER TABLE public.regional_raids OWNER TO meowth;

--
-- TOC entry 254 (class 1259 OID 16594)
-- Name: report_channels; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.report_channels (
    channelid numeric(20,0) NOT NULL,
    lat double precision,
    lon double precision,
    radius double precision,
    users boolean DEFAULT false,
    raid boolean DEFAULT false,
    train boolean DEFAULT false,
    wild boolean DEFAULT false,
    research boolean DEFAULT false,
    clean boolean DEFAULT false,
    category_1 text,
    category_2 text,
    category_3 text,
    category_4 text,
    category_5 text,
    city text,
    timezone text,
    guild_id numeric(20,0),
    trade boolean DEFAULT false,
    category_ex text,
    category_ex_gyms text,
    meetup boolean,
    category_meetup numeric(20,0),
    rocket boolean,
    category_7 text
);


ALTER TABLE public.report_channels OWNER TO meowth;

--
-- TOC entry 255 (class 1259 OID 16606)
-- Name: research; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.research (
    id bigint NOT NULL,
    guild_id numeric(20,0),
    reporter_id numeric(20,0),
    task text,
    reward text,
    location text,
    tz text,
    reported_at double precision,
    message_ids text[],
    completed_by numeric(20,0)[]
);


ALTER TABLE public.research OWNER TO meowth;

--
-- TOC entry 256 (class 1259 OID 16611)
-- Name: research_tasks; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.research_tasks (
    task text NOT NULL,
    reward text NOT NULL
);


ALTER TABLE public.research_tasks OWNER TO meowth;

--
-- TOC entry 257 (class 1259 OID 16616)
-- Name: restart_savedata; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.restart_savedata (
    restart_snowflake bigint NOT NULL,
    restart_by bigint NOT NULL,
    restart_channel bigint NOT NULL,
    restart_guild bigint,
    restart_message bigint
);


ALTER TABLE public.restart_savedata OWNER TO meowth;

--
-- TOC entry 258 (class 1259 OID 16619)
-- Name: rockets; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.rockets (
    id bigint NOT NULL,
    guild numeric(20,0),
    location text,
    reporter_id numeric(20,0),
    kind integer,
    created double precision,
    messages text[],
    pokemon text[]
);


ALTER TABLE public.rockets OWNER TO meowth;

--
-- TOC entry 259 (class 1259 OID 16624)
-- Name: scoreboard; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.scoreboard (
    guild_id numeric(20,0) NOT NULL,
    user_id numeric(20,0) NOT NULL,
    raid integer,
    wild integer,
    trade integer,
    research integer,
    service integer
);


ALTER TABLE public.scoreboard OWNER TO meowth;

--
-- TOC entry 260 (class 1259 OID 16627)
-- Name: task_names; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.task_names (
    task_id bigint NOT NULL,
    language_id integer NOT NULL,
    task_desc text NOT NULL,
    category text
);


ALTER TABLE public.task_names OWNER TO meowth;

--
-- TOC entry 261 (class 1259 OID 16632)
-- Name: team_names; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.team_names (
    team_id bigint NOT NULL,
    language_id bigint NOT NULL,
    team_name text
);


ALTER TABLE public.team_names OWNER TO meowth;

--
-- TOC entry 262 (class 1259 OID 16637)
-- Name: team_roles; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.team_roles (
    guild_id numeric(20,0) NOT NULL,
    blue_role_id numeric(20,0),
    yellow_role_id numeric(20,0),
    red_role_id numeric(20,0)
);


ALTER TABLE public.team_roles OWNER TO meowth;

--
-- TOC entry 263 (class 1259 OID 16640)
-- Name: teams; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.teams (
    team_id bigint NOT NULL,
    color_id bigint,
    identifier text,
    emoji bigint
);


ALTER TABLE public.teams OWNER TO meowth;

--
-- TOC entry 264 (class 1259 OID 16645)
-- Name: to_archive; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.to_archive (
    channel_id numeric(20,0) NOT NULL,
    user_id numeric(20,0) NOT NULL,
    reason text
);


ALTER TABLE public.to_archive OWNER TO meowth;

--
-- TOC entry 265 (class 1259 OID 16650)
-- Name: trades; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.trades (
    id bigint NOT NULL,
    guild_id numeric(20,0) NOT NULL,
    lister_id numeric(20,0) NOT NULL,
    listing_id text NOT NULL,
    offers text[] NOT NULL,
    wants text[] NOT NULL,
    offer_list text[]
);


ALTER TABLE public.trades OWNER TO meowth;

--
-- TOC entry 266 (class 1259 OID 16655)
-- Name: trades_id_seq; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.trades_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trades_id_seq OWNER TO meowth;

--
-- TOC entry 3715 (class 0 OID 0)
-- Dependencies: 266
-- Name: trades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: meowth
--

ALTER SEQUENCE public.trades_id_seq OWNED BY public.trades.id;


--
-- TOC entry 267 (class 1259 OID 16656)
-- Name: train_rsvp; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.train_rsvp (
    user_id numeric(20,0) NOT NULL,
    train_id bigint NOT NULL,
    party integer[]
);


ALTER TABLE public.train_rsvp OWNER TO meowth;

--
-- TOC entry 268 (class 1259 OID 16661)
-- Name: trains; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.trains (
    id bigint NOT NULL,
    guild_id numeric(20,0) NOT NULL,
    channel_id numeric(20,0) NOT NULL,
    report_channel_id numeric(20,0) NOT NULL,
    current_raid_id bigint,
    next_raid_id bigint,
    report_msg_ids numeric(20,0)[],
    multi_msg_ids text[],
    done_raid_ids bigint[],
    message_ids text[]
);


ALTER TABLE public.trains OWNER TO meowth;

--
-- TOC entry 269 (class 1259 OID 16666)
-- Name: type_chart; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.type_chart (
    attack_type_id text NOT NULL,
    defender_type_id text NOT NULL,
    dmg_multiplier double precision NOT NULL
);


ALTER TABLE public.type_chart OWNER TO meowth;

--
-- TOC entry 270 (class 1259 OID 16671)
-- Name: types; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.types (
    typeid text NOT NULL,
    emoji text NOT NULL,
    weather text NOT NULL
);


ALTER TABLE public.types OWNER TO meowth;

--
-- TOC entry 271 (class 1259 OID 16676)
-- Name: unhandled_errors; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.unhandled_errors (
    command_name text,
    guild_id numeric(20,0),
    channel_id numeric(20,0),
    author_id numeric(20,0),
    created double precision,
    full_traceback text
);


ALTER TABLE public.unhandled_errors OWNER TO meowth;

--
-- TOC entry 272 (class 1259 OID 16681)
-- Name: users; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.users (
    id numeric(20,0) NOT NULL,
    team integer,
    level integer,
    silph text,
    pokebattler integer,
    party integer[] DEFAULT ARRAY[0, 0, 0, 1],
    ign text,
    default_party integer[],
    friendcode text
);


ALTER TABLE public.users OWNER TO meowth;

--
-- TOC entry 273 (class 1259 OID 16687)
-- Name: wants; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.wants (
    guild numeric(20,0) NOT NULL,
    want text NOT NULL,
    users numeric(20,0)[],
    role numeric(20,0)
);


ALTER TABLE public.wants OWNER TO meowth;

--
-- TOC entry 274 (class 1259 OID 16692)
-- Name: weather_forecasts; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.weather_forecasts (
    cellid text NOT NULL,
    forecast_0 text,
    forecast_1 text,
    forecast_2 text,
    forecast_3 text,
    forecast_4 text,
    forecast_5 text,
    forecast_6 text,
    forecast_7 text,
    current_weather text,
    pull_hour integer NOT NULL
);


ALTER TABLE public.weather_forecasts OWNER TO meowth;

--
-- TOC entry 275 (class 1259 OID 16697)
-- Name: weather_names; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.weather_names (
    weather text NOT NULL,
    language_id integer NOT NULL,
    name text NOT NULL,
    night_name text
);


ALTER TABLE public.weather_names OWNER TO meowth;

--
-- TOC entry 276 (class 1259 OID 16702)
-- Name: web_sessions; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.web_sessions (
    session_id bigint NOT NULL,
    access_token text,
    expires double precision,
    refresh_token text
);


ALTER TABLE public.web_sessions OWNER TO meowth;

--
-- TOC entry 277 (class 1259 OID 16707)
-- Name: welcome; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.welcome (
    guild_id numeric(20,0) NOT NULL,
    channelid text NOT NULL,
    message text
);


ALTER TABLE public.welcome OWNER TO meowth;

--
-- TOC entry 278 (class 1259 OID 16712)
-- Name: wilds; Type: TABLE; Schema: public; Owner: meowth
--

CREATE TABLE public.wilds (
    id bigint NOT NULL,
    location text,
    guild numeric(20,0) NOT NULL,
    pkmn text,
    created double precision NOT NULL,
    messages text[],
    caught_by numeric(20,0)[],
    reporter_id numeric(20,0)
);


ALTER TABLE public.wilds OWNER TO meowth;

--
-- TOC entry 279 (class 1259 OID 16717)
-- Name: wilds_id_seq; Type: SEQUENCE; Schema: public; Owner: meowth
--

CREATE SEQUENCE public.wilds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wilds_id_seq OWNER TO meowth;

--
-- TOC entry 3716 (class 0 OID 0)
-- Dependencies: 279
-- Name: wilds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: meowth
--

ALTER SEQUENCE public.wilds_id_seq OWNED BY public.wilds.id;


--
-- TOC entry 3425 (class 2604 OID 16718)
-- Name: gyms id; Type: DEFAULT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.gyms ALTER COLUMN id SET DEFAULT nextval('public.gyms_id_seq'::regclass);


--
-- TOC entry 3426 (class 2604 OID 16719)
-- Name: pokestops id; Type: DEFAULT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.pokestops ALTER COLUMN id SET DEFAULT nextval('public.pokestops_id_seq'::regclass);


--
-- TOC entry 3427 (class 2604 OID 16720)
-- Name: raid_groups grp_id; Type: DEFAULT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.raid_groups ALTER COLUMN grp_id SET DEFAULT nextval('public.raid_groups_grp_id_seq'::regclass);


--
-- TOC entry 3438 (class 2606 OID 32398)
-- Name: accuweather accuweather_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.accuweather
    ADD CONSTRAINT accuweather_pkey PRIMARY KEY (phrase);


--
-- TOC entry 3440 (class 2606 OID 32400)
-- Name: archive archive_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.archive
    ADD CONSTRAINT archive_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 3442 (class 2606 OID 32402)
-- Name: command_log command_log_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.command_log
    ADD CONSTRAINT command_log_pkey PRIMARY KEY (message_id, sent);


--
-- TOC entry 3444 (class 2606 OID 32404)
-- Name: counters_data counters_data_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.counters_data
    ADD CONSTRAINT counters_data_pkey PRIMARY KEY (boss_id, level, weather, fast_move, charge_move);


--
-- TOC entry 3446 (class 2606 OID 32406)
-- Name: cpm_table cpm_table_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.cpm_table
    ADD CONSTRAINT cpm_table_pkey PRIMARY KEY (level);


--
-- TOC entry 3448 (class 2606 OID 32408)
-- Name: current_weather current_weather_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.current_weather
    ADD CONSTRAINT current_weather_pkey PRIMARY KEY (cellid, guild_id);


--
-- TOC entry 3450 (class 2606 OID 32410)
-- Name: custom_roles custom_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.custom_roles
    ADD CONSTRAINT custom_roles_pkey PRIMARY KEY (guild_id, role_id);


--
-- TOC entry 3452 (class 2606 OID 32412)
-- Name: discord_logs discord_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.discord_logs
    ADD CONSTRAINT discord_logs_pkey PRIMARY KEY (log_id);

ALTER TABLE ONLY public.discord_messages
    ADD CONSTRAINT discord_messages_pkey PRIMARY KEY (message_id, sent);

--
-- TOC entry 3454 (class 2606 OID 32501)
-- Name: forecast_config forecast_config_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.forecast_config
    ADD CONSTRAINT forecast_config_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 3456 (class 2606 OID 32503)
-- Name: form_names form_names_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.form_names
    ADD CONSTRAINT form_names_pkey PRIMARY KEY (formid, language_id);


--
-- TOC entry 3458 (class 2606 OID 32505)
-- Name: forms forms_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.forms
    ADD CONSTRAINT forms_pkey PRIMARY KEY (pokemonid, formid);


--
-- TOC entry 3460 (class 2606 OID 32507)
-- Name: guild_config guild_config_pk; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.guild_config
    ADD CONSTRAINT guild_config_pkey PRIMARY KEY (guild_id, config_name);


--
-- TOC entry 3462 (class 2606 OID 32509)
-- Name: guild_settings guild_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.guild_settings
    ADD CONSTRAINT guild_settings_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 3464 (class 2606 OID 32511)
-- Name: gym_travel gym_travel_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.gym_travel
    ADD CONSTRAINT gym_travel_pkey PRIMARY KEY (origin_id, dest_id);


--
-- TOC entry 3466 (class 2606 OID 32513)
-- Name: gyms gyms_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.gyms
    ADD CONSTRAINT gyms_pkey PRIMARY KEY (id);


--
-- TOC entry 3468 (class 2606 OID 32515)
-- Name: item_names item_names_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.item_names
    ADD CONSTRAINT item_names_pkey PRIMARY KEY (item_id, language_id);


--
-- TOC entry 3470 (class 2606 OID 32517)
-- Name: languages languages_identifier_key; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_identifier_key UNIQUE (identifier);


--
-- TOC entry 3472 (class 2606 OID 32519)
-- Name: languages languages_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (language_id);


--
-- TOC entry 3474 (class 2606 OID 32521)
-- Name: meetup_rsvp meetup_rsvp_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.meetup_rsvp
    ADD CONSTRAINT meetup_rsvp_pkey PRIMARY KEY (meetup_id, user_id);


--
-- TOC entry 3476 (class 2606 OID 32523)
-- Name: meetups meetups_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.meetups
    ADD CONSTRAINT meetups_pkey PRIMARY KEY (id);


--
-- TOC entry 3478 (class 2606 OID 32525)
-- Name: meowth_logs meowth_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.meowth_logs
    ADD CONSTRAINT meowth_logs_pkey PRIMARY KEY (log_id);


--
-- TOC entry 3480 (class 2606 OID 32527)
-- Name: modifiers modifiers_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.modifiers
    ADD CONSTRAINT modifiers_pkey PRIMARY KEY (id);


--
-- TOC entry 3482 (class 2606 OID 32529)
-- Name: move_names move_names_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.move_names
    ADD CONSTRAINT move_names_pkey PRIMARY KEY (moveid, language_id);


--
-- TOC entry 3484 (class 2606 OID 32531)
-- Name: moves moves_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.moves
    ADD CONSTRAINT moves_pkey PRIMARY KEY (moveid);


--
-- TOC entry 3486 (class 2606 OID 32533)
-- Name: pokedex pokedex_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.pokedex
    ADD CONSTRAINT pokedex_pkey PRIMARY KEY (pokemonid, language_id);


--
-- TOC entry 3488 (class 2606 OID 32535)
-- Name: pokemon pokemon_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.pokemon
    ADD CONSTRAINT pokemon_pkey PRIMARY KEY (pokemonid);


--
-- TOC entry 3490 (class 2606 OID 32537)
-- Name: pokestops pokestops_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.pokestops
    ADD CONSTRAINT pokestops_pkey PRIMARY KEY (id);


--
-- TOC entry 3492 (class 2606 OID 32539)
-- Name: prefixes prefixes_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.prefixes
    ADD CONSTRAINT prefixes_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 3494 (class 2606 OID 32541)
-- Name: raid_bosses raid_bosses_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.raid_bosses
    ADD CONSTRAINT raid_bosses_pkey PRIMARY KEY (level, pokemon_id);


--
-- TOC entry 3496 (class 2606 OID 32543)
-- Name: raid_groups raid_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.raid_groups
    ADD CONSTRAINT raid_groups_pkey PRIMARY KEY (raid_id, grp_id);


--
-- TOC entry 3498 (class 2606 OID 32545)
-- Name: raid_rsvp raid_rsvp_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.raid_rsvp
    ADD CONSTRAINT raid_rsvp_pkey PRIMARY KEY (user_id, raid_id);


--
-- TOC entry 3500 (class 2606 OID 32547)
-- Name: raids raids_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.raids
    ADD CONSTRAINT raids_pkey PRIMARY KEY (id);


--
-- TOC entry 3502 (class 2606 OID 32549)
-- Name: regional_raids regional_raids_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.regional_raids
    ADD CONSTRAINT regional_raids_pkey PRIMARY KEY (boss, min_lat, max_lat, min_lon, max_lon);


--
-- TOC entry 3504 (class 2606 OID 32551)
-- Name: report_channels report_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.report_channels
    ADD CONSTRAINT report_channels_pkey PRIMARY KEY (channelid);


--
-- TOC entry 3506 (class 2606 OID 32553)
-- Name: research research_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.research
    ADD CONSTRAINT research_pkey PRIMARY KEY (id);


--
-- TOC entry 3508 (class 2606 OID 32555)
-- Name: research_tasks research_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.research_tasks
    ADD CONSTRAINT research_tasks_pkey PRIMARY KEY (task, reward);


--
-- TOC entry 3510 (class 2606 OID 32557)
-- Name: restart_savedata restart_savedata_pk; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.restart_savedata
    ADD CONSTRAINT restart_savedata_pkey PRIMARY KEY (restart_snowflake);


--
-- TOC entry 3512 (class 2606 OID 32559)
-- Name: rockets rockets_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.rockets
    ADD CONSTRAINT rockets_pkey PRIMARY KEY (id);


--
-- TOC entry 3514 (class 2606 OID 32561)
-- Name: scoreboard scoreboard_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.scoreboard
    ADD CONSTRAINT scoreboard_pkey PRIMARY KEY (guild_id, user_id);


--
-- TOC entry 3516 (class 2606 OID 32563)
-- Name: task_names task_names_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.task_names
    ADD CONSTRAINT task_names_pkey PRIMARY KEY (task_id, language_id);


--
-- TOC entry 3518 (class 2606 OID 32565)
-- Name: team_names team_names_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.team_names
    ADD CONSTRAINT team_names_pkey PRIMARY KEY (team_id, language_id);


--
-- TOC entry 3520 (class 2606 OID 32567)
-- Name: team_roles team_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.team_roles
    ADD CONSTRAINT team_roles_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 3522 (class 2606 OID 32569)
-- Name: teams teams_color_id_key; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_color_id_key UNIQUE (color_id);


--
-- TOC entry 3524 (class 2606 OID 32571)
-- Name: teams teams_identifier_key; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_identifier_key UNIQUE (identifier);


--
-- TOC entry 3526 (class 2606 OID 32573)
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- TOC entry 3528 (class 2606 OID 32575)
-- Name: to_archive to_archive_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.to_archive
    ADD CONSTRAINT to_archive_pkey PRIMARY KEY (channel_id, user_id);


--
-- TOC entry 3530 (class 2606 OID 32577)
-- Name: trades trades_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pkey PRIMARY KEY (id);


--
-- TOC entry 3532 (class 2606 OID 32579)
-- Name: train_rsvp train_rsvp_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.train_rsvp
    ADD CONSTRAINT train_rsvp_pkey PRIMARY KEY (user_id);


--
-- TOC entry 3534 (class 2606 OID 32581)
-- Name: trains trains_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.trains
    ADD CONSTRAINT trains_pkey PRIMARY KEY (id);


--
-- TOC entry 3536 (class 2606 OID 32583)
-- Name: type_chart type_chart_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.type_chart
    ADD CONSTRAINT type_chart_pkey PRIMARY KEY (attack_type_id, defender_type_id);


--
-- TOC entry 3538 (class 2606 OID 32585)
-- Name: types types_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.types
    ADD CONSTRAINT types_pkey PRIMARY KEY (typeid);


--
-- TOC entry 3540 (class 2606 OID 32587)
-- Name: users users_ign_key; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_ign_key UNIQUE (ign);


--
-- TOC entry 3542 (class 2606 OID 32589)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3544 (class 2606 OID 32591)
-- Name: wants wants_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.wants
    ADD CONSTRAINT wants_pkey PRIMARY KEY (guild, want);


--
-- TOC entry 3546 (class 2606 OID 32593)
-- Name: weather_forecasts weather_forecasts_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.weather_forecasts
    ADD CONSTRAINT weather_forecasts_pkey PRIMARY KEY (cellid, pull_hour);


--
-- TOC entry 3548 (class 2606 OID 32595)
-- Name: weather_names weather_names_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.weather_names
    ADD CONSTRAINT weather_names_pkey PRIMARY KEY (weather, language_id);


--
-- TOC entry 3550 (class 2606 OID 32597)
-- Name: web_sessions web_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.web_sessions
    ADD CONSTRAINT web_sessions_pkey PRIMARY KEY (session_id);


--
-- TOC entry 3552 (class 2606 OID 32599)
-- Name: welcome welcome_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.welcome
    ADD CONSTRAINT welcome_pkey PRIMARY KEY (guild_id);


--
-- TOC entry 3554 (class 2606 OID 32601)
-- Name: wilds wilds_pkey; Type: CONSTRAINT; Schema: public; Owner: meowth
--

ALTER TABLE ONLY public.wilds
    ADD CONSTRAINT wilds_pkey PRIMARY KEY (id);


--
-- TOC entry 3559 (class 2620 OID 32602)
-- Name: meetup_rsvp meetup_rsvp; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER meetup_rsvp BEFORE INSERT OR DELETE OR UPDATE ON public.meetup_rsvp FOR EACH ROW EXECUTE FUNCTION public.update_meetuprsvp();


--
-- TOC entry 3561 (class 2620 OID 32603)
-- Name: raid_rsvp notify_rsvp; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER notify_rsvp AFTER INSERT OR DELETE OR UPDATE ON public.raid_rsvp FOR EACH ROW EXECUTE FUNCTION public.update_rsvp();


--
-- TOC entry 3555 (class 2620 OID 32604)
-- Name: current_weather notify_weather; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER notify_weather BEFORE INSERT OR UPDATE OF current_weather ON public.current_weather FOR EACH ROW EXECUTE FUNCTION public.update_raid_weather();


--
-- TOC entry 3557 (class 2620 OID 32605)
-- Name: gym_travel reverse_travel; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER reverse_travel AFTER INSERT ON public.gym_travel FOR EACH ROW EXECUTE FUNCTION public.insert_reverse_travel();


--
-- TOC entry 3562 (class 2620 OID 32606)
-- Name: train_rsvp train_rsvp; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER train_rsvp BEFORE INSERT OR DELETE OR UPDATE ON public.train_rsvp FOR EACH ROW EXECUTE FUNCTION public.update_trainrsvp();


--
-- TOC entry 3558 (class 2620 OID 32607)
-- Name: gyms update_cells; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER update_cells AFTER INSERT ON public.gyms FOR EACH ROW EXECUTE FUNCTION public.update_cells();


--
-- TOC entry 3560 (class 2620 OID 32608)
-- Name: pokestops update_cells; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER update_cells AFTER INSERT ON public.pokestops FOR EACH ROW EXECUTE FUNCTION public.update_cells();


--
-- TOC entry 3556 (class 2620 OID 32609)
-- Name: forecast_config update_forecast_config; Type: TRIGGER; Schema: public; Owner: meowth
--

CREATE TRIGGER update_forecast_config AFTER INSERT OR UPDATE ON public.forecast_config FOR EACH ROW EXECUTE FUNCTION public.enable_forecast();


-- Completed on 2023-08-29 08:58:37

--
-- PostgreSQL database dump complete
--

