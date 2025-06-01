--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.4

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
-- Name: _heroku; Type: SCHEMA; Schema: -; Owner: heroku_admin
--

CREATE SCHEMA _heroku;


ALTER SCHEMA _heroku OWNER TO heroku_admin;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: u3vc533281r78p
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO u3vc533281r78p;

--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: create_ext(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.create_ext() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  databaseowner TEXT;

  r RECORD;

BEGIN

  IF tg_tag = 'CREATE EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        CONTINUE WHEN r.command_tag != 'CREATE EXTENSION' OR r.object_type != 'extension';

        schemaname = (
            SELECT n.nspname
            FROM pg_catalog.pg_extension AS e
            INNER JOIN pg_catalog.pg_namespace AS n
            ON e.extnamespace = n.oid
            WHERE e.oid = r.objid
        );

        databaseowner = (
            SELECT pg_catalog.pg_get_userbyid(d.datdba)
            FROM pg_catalog.pg_database d
            WHERE d.datname = current_database()
        );
        --RAISE NOTICE 'Record for event trigger %, objid: %,tag: %, current_user: %, schema: %, database_owenr: %', r.object_identity, r.objid, tg_tag, current_user, schemaname, databaseowner;
        IF r.object_identity = 'address_standardizer_data_us' THEN
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_gaz TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_lex TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.us_rules TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'amcheck' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.bt_index_check TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.bt_index_parent_check TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'dict_int' THEN
            EXECUTE format('ALTER TEXT SEARCH DICTIONARY %I.intdict OWNER TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'pg_partman' THEN
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.part_config TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.part_config_sub TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.custom_time_partitions TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'pg_stat_statements' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %I.pg_stat_statements_reset TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'postgis' THEN
            PERFORM _heroku.postgis_after_create();
        ELSIF r.object_identity = 'postgis_raster' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT SELECT ON TABLE %I.raster_columns TO %I;', schemaname, databaseowner);
            EXECUTE format('GRANT SELECT ON TABLE %I.raster_overviews TO %I;', schemaname, databaseowner);
        ELSIF r.object_identity = 'postgis_topology' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT USAGE ON SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA topology TO %I;', databaseowner);
            EXECUTE format('GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA topology TO %I;', databaseowner);
        ELSIF r.object_identity = 'postgis_tiger_geocoder' THEN
            PERFORM _heroku.postgis_after_create();
            EXECUTE format('GRANT USAGE ON SCHEMA tiger TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tiger TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tiger TO %I;', databaseowner);

            EXECUTE format('GRANT USAGE ON SCHEMA tiger_data TO %I;', databaseowner);
            EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA tiger_data TO %I;', databaseowner);
            EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON ALL TABLES IN SCHEMA tiger_data TO %I;', databaseowner);
        END IF;
    END LOOP;
  END IF;
END;
$$;


ALTER FUNCTION _heroku.create_ext() OWNER TO heroku_admin;

--
-- Name: drop_ext(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.drop_ext() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  databaseowner TEXT;

  r RECORD;

BEGIN

  IF tg_tag = 'DROP EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_dropped_objects()
    LOOP
      CONTINUE WHEN r.object_type != 'extension';

      databaseowner = (
            SELECT pg_catalog.pg_get_userbyid(d.datdba)
            FROM pg_catalog.pg_database d
            WHERE d.datname = current_database()
      );

      --RAISE NOTICE 'Record for event trigger %, objid: %,tag: %, current_user: %, database_owner: %, schemaname: %', r.object_identity, r.objid, tg_tag, current_user, databaseowner, r.schema_name;

      IF r.object_identity = 'postgis_topology' THEN
          EXECUTE format('DROP SCHEMA IF EXISTS topology');
      END IF;
    END LOOP;

  END IF;
END;
$$;


ALTER FUNCTION _heroku.drop_ext() OWNER TO heroku_admin;

--
-- Name: extension_before_drop(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.extension_before_drop() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  query TEXT;

BEGIN
  query = (SELECT current_query());

  -- RAISE NOTICE 'executing extension_before_drop: tg_event: %, tg_tag: %, current_user: %, session_user: %, query: %', tg_event, tg_tag, current_user, session_user, query;
  IF tg_tag = 'DROP EXTENSION' and not pg_has_role(session_user, 'rds_superuser', 'MEMBER') THEN
    -- DROP EXTENSION [ IF EXISTS ] name [, ...] [ CASCADE | RESTRICT ]
    IF (regexp_match(query, 'DROP\s+EXTENSION\s+(IF\s+EXISTS)?.*(plpgsql)', 'i') IS NOT NULL) THEN
      RAISE EXCEPTION 'The plpgsql extension is required for database management and cannot be dropped.';
    END IF;
  END IF;
END;
$$;


ALTER FUNCTION _heroku.extension_before_drop() OWNER TO heroku_admin;

--
-- Name: postgis_after_create(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.postgis_after_create() RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    schemaname TEXT;
    databaseowner TEXT;
BEGIN
    schemaname = (
        SELECT n.nspname
        FROM pg_catalog.pg_extension AS e
        INNER JOIN pg_catalog.pg_namespace AS n ON e.extnamespace = n.oid
        WHERE e.extname = 'postgis'
    );
    databaseowner = (
        SELECT pg_catalog.pg_get_userbyid(d.datdba)
        FROM pg_catalog.pg_database d
        WHERE d.datname = current_database()
    );

    EXECUTE format('GRANT EXECUTE ON FUNCTION %I.st_tileenvelope TO %I;', schemaname, databaseowner);
    EXECUTE format('GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE %I.spatial_ref_sys TO %I;', schemaname, databaseowner);
END;
$$;


ALTER FUNCTION _heroku.postgis_after_create() OWNER TO heroku_admin;

--
-- Name: validate_extension(); Type: FUNCTION; Schema: _heroku; Owner: heroku_admin
--

CREATE FUNCTION _heroku.validate_extension() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$

DECLARE

  schemaname TEXT;
  r RECORD;

BEGIN

  IF tg_tag = 'CREATE EXTENSION' and current_user != 'rds_superuser' THEN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
      CONTINUE WHEN r.command_tag != 'CREATE EXTENSION' OR r.object_type != 'extension';

      schemaname = (
        SELECT n.nspname
        FROM pg_catalog.pg_extension AS e
        INNER JOIN pg_catalog.pg_namespace AS n
        ON e.extnamespace = n.oid
        WHERE e.oid = r.objid
      );

      IF schemaname = '_heroku' THEN
        RAISE EXCEPTION 'Creating extensions in the _heroku schema is not allowed';
      END IF;
    END LOOP;
  END IF;
END;
$$;


ALTER FUNCTION _heroku.validate_extension() OWNER TO heroku_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: u3vc533281r78p
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO u3vc533281r78p;

--
-- Name: gifts; Type: TABLE; Schema: public; Owner: u3vc533281r78p
--

CREATE TABLE public.gifts (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    code character varying(255) NOT NULL,
    status character varying(255) NOT NULL,
    validation character varying(255) NOT NULL,
    duration character varying(255) NOT NULL
);


ALTER TABLE public.gifts OWNER TO u3vc533281r78p;

--
-- Name: gifts_id_seq; Type: SEQUENCE; Schema: public; Owner: u3vc533281r78p
--

CREATE SEQUENCE public.gifts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.gifts_id_seq OWNER TO u3vc533281r78p;

--
-- Name: gifts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: u3vc533281r78p
--

ALTER SEQUENCE public.gifts_id_seq OWNED BY public.gifts.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: u3vc533281r78p
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    review character varying(10000),
    author character varying(255)
);


ALTER TABLE public.reviews OWNER TO u3vc533281r78p;

--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: u3vc533281r78p
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_id_seq OWNER TO u3vc533281r78p;

--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: u3vc533281r78p
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: schedule; Type: TABLE; Schema: public; Owner: u3vc533281r78p
--

CREATE TABLE public.schedule (
    id integer NOT NULL,
    date integer NOT NULL,
    "time" integer NOT NULL,
    availability character varying(255) NOT NULL,
    booked character varying(255) NOT NULL,
    "user" character varying(255) NOT NULL
);


ALTER TABLE public.schedule OWNER TO u3vc533281r78p;

--
-- Name: schedule_backup; Type: TABLE; Schema: public; Owner: u3vc533281r78p
--

CREATE TABLE public.schedule_backup (
    id integer,
    date integer,
    "time" integer,
    availability character varying(255),
    booked character varying(255),
    "user" character varying(255)
);


ALTER TABLE public.schedule_backup OWNER TO u3vc533281r78p;

--
-- Name: schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: u3vc533281r78p
--

CREATE SEQUENCE public.schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_id_seq OWNER TO u3vc533281r78p;

--
-- Name: schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: u3vc533281r78p
--

ALTER SEQUENCE public.schedule_id_seq OWNED BY public.schedule.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: u3vc533281r78p
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    hash character varying(255) NOT NULL,
    date timestamp without time zone,
    admin boolean,
    email character varying(255) NOT NULL,
    validation character varying(255),
    reset character varying(255),
    "timestamp" timestamp without time zone
);


ALTER TABLE public.users OWNER TO u3vc533281r78p;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: u3vc533281r78p
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO u3vc533281r78p;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: u3vc533281r78p
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: gifts id; Type: DEFAULT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.gifts ALTER COLUMN id SET DEFAULT nextval('public.gifts_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: schedule id; Type: DEFAULT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.schedule ALTER COLUMN id SET DEFAULT nextval('public.schedule_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: u3vc533281r78p
--

COPY public.alembic_version (version_num) FROM stdin;
5a968697fa31
\.


--
-- Data for Name: gifts; Type: TABLE DATA; Schema: public; Owner: u3vc533281r78p
--

COPY public.gifts (id, username, code, status, validation, duration) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: u3vc533281r78p
--

COPY public.reviews (id, review, author) FROM stdin;
1	Working with Daniel has been a dream, he helped me understand many new things with my problems post surgery and helped address them in ways other therapists did not. He's always open to learning and looking into a problem he's yet to encounter to provide the best treatment. Every session flew by and felt like a catch up with a friend. I cannot recommend this treatment enough!	-Kurt, C
2	From the moment I walked in, the atmosphere was calming and serene, setting the tone for a perfect session. Daniel was exceptionally skilled and attentive, taking the time to understand my specific needs and areas of tension.\r\nThe combination of techniques used was spot on, leaving me feeling rejuvenated and refreshed.	-Lucy, G
\.


--
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: u3vc533281r78p
--

COPY public.schedule (id, date, "time", availability, booked, "user") FROM stdin;
7	28	1430	Available	None	None
23	28	1500	Available	None	None
24	28	1530	Available	None	None
25	28	1600	Available	None	None
9	28	1700	Available	None	None
10	28	1730	Available	None	None
11	28	1800	Available	None	None
26	29	1200	Available	None	None
27	29	1230	Available	None	None
28	29	1300	Available	None	None
12	29	1330	Available	None	None
13	29	1400	Available	None	None
14	29	1430	Available	None	None
29	29	1500	Available	None	None
30	29	1530	Available	None	None
31	29	1600	Available	None	None
15	29	1630	Available	None	None
16	29	1700	Available	None	None
17	29	1730	Available	None	None
19	27	1630	Available	None	None
1	27	1700	Available	None	None
2	27	1730	Available	None	None
3	27	1800	Available	None	None
4	27	1830	Available	None	None
20	28	1200	Available	None	None
21	28	1230	Available	None	None
22	28	1300	Available	None	None
5	28	1330	Available	None	None
6	28	1400	Available	None	None
8	28	1630	Available	None	None
18	27	1600	Available	None	None
\.


--
-- Data for Name: schedule_backup; Type: TABLE DATA; Schema: public; Owner: u3vc533281r78p
--

COPY public.schedule_backup (id, date, "time", availability, booked, "user") FROM stdin;
1	27	1700	Available	\N	\N
2	27	1730	Available	\N	\N
3	27	1800	Available	\N	\N
4	27	1830	Available	\N	\N
5	28	1330	Available	\N	\N
6	28	1400	Available	\N	\N
7	28	1430	Available	\N	\N
8	28	1630	Available	\N	\N
9	28	1700	Available	\N	\N
10	28	1730	Available	\N	\N
11	28	1800	Available	\N	\N
12	29	1330	Available	\N	\N
13	29	1400	Available	\N	\N
14	29	1430	Available	\N	\N
15	29	1630	Available	\N	\N
16	29	1700	Available	\N	\N
17	29	1730	Available	\N	\N
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: u3vc533281r78p
--

COPY public.users (id, username, hash, date, admin, email, validation, reset, "timestamp") FROM stdin;
3	MossyUser	scrypt:32768:8:1$8hvMX7nTMdk2GOVH$88cd1299ec57e0c69f9556a557d08a2253ca0bfcbbf97299c7f88dfa6843511a6141e4793cea61976798d0c8437cc73196779ff65ee23549b1374c16760724a0	\N	f	daniil.sam.o@gmail.com	Valid	\N	2024-08-27 14:14:59.390921
2	MossyAdmin	scrypt:32768:8:1$HJ9UdEJQz6Bknb7p$9ef12e6fe05041667df8cb1afbe8ab35a7666d19d72458621c824356ecd1ec2ac78fed98e6843e04e2eaab50c8b64ad58247bef7feb30241de20ae2da4f93ee4	\N	t	themossfox@gmail.com	Valid	\N	\N
4	test	scrypt:32768:8:1$hVFDPPa0w2zB67fM$fa9f3f0fa4914cff446a64f2eddb9fea4d83c59a034b5e5216a7ad14102c86525b02e0db9b1001f34fe2427c1b7c4214555dfeeefc3e6268f672e6a0a30b9c3a	\N	f	d.samo.trfm@gmail.com	666b723a	\N	2024-09-06 15:48:15.001906
5	new_user	password_hash	\N	\N	new_user@example.com	\N	\N	\N
6	test2	scrypt:32768:8:1$JX8RuL2BVVWw9MVb$3b59dec8d523fe785ec3d1181f2e74b3ec16f48a39fb22b516aa3d40a9e3063ab41bc5ca760597822bb31bb944c3d13f0f934bf89d2bb1d43cad0be86ec19283	\N	f	bobsamox@gmail.com	34b95051	\N	2024-09-06 21:53:39.350675
\.


--
-- Name: gifts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: u3vc533281r78p
--

SELECT pg_catalog.setval('public.gifts_id_seq', 4, true);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: u3vc533281r78p
--

SELECT pg_catalog.setval('public.reviews_id_seq', 1, false);


--
-- Name: schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: u3vc533281r78p
--

SELECT pg_catalog.setval('public.schedule_id_seq', 31, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: u3vc533281r78p
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: gifts gifts_pkey; Type: CONSTRAINT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.gifts
    ADD CONSTRAINT gifts_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: u3vc533281r78p
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: u3vc533281r78p
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint); Type: ACL; Schema: public; Owner: rdsadmin
--

GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint) TO u3vc533281r78p;


--
-- Name: extension_before_drop; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER extension_before_drop ON ddl_command_start
   EXECUTE FUNCTION _heroku.extension_before_drop();


ALTER EVENT TRIGGER extension_before_drop OWNER TO heroku_admin;

--
-- Name: log_create_ext; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER log_create_ext ON ddl_command_end
   EXECUTE FUNCTION _heroku.create_ext();


ALTER EVENT TRIGGER log_create_ext OWNER TO heroku_admin;

--
-- Name: log_drop_ext; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER log_drop_ext ON sql_drop
   EXECUTE FUNCTION _heroku.drop_ext();


ALTER EVENT TRIGGER log_drop_ext OWNER TO heroku_admin;

--
-- Name: validate_extension; Type: EVENT TRIGGER; Schema: -; Owner: heroku_admin
--

CREATE EVENT TRIGGER validate_extension ON ddl_command_end
   EXECUTE FUNCTION _heroku.validate_extension();


ALTER EVENT TRIGGER validate_extension OWNER TO heroku_admin;

--
-- PostgreSQL database dump complete
--

