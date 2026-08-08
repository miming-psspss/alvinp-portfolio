--
-- PostgreSQL database dump
--

\restrict 1M7yfjQfKASsMpD2co6geBPhymX6J3376uEV6tZH4vi0XuvnUYCHD7IoLoVoKbW

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: board_of_directors; Type: TABLE; Schema: public; Owner: cas_admin
--

CREATE TABLE public.board_of_directors (
    bod_id text NOT NULL,
    name text,
    role_title text,
    access_level text,
    responsibility text,
    query_scope_allowed text,
    vop_enforcement_notes text
);


ALTER TABLE public.board_of_directors OWNER TO cas_admin;

--
-- Name: members; Type: TABLE; Schema: public; Owner: cas_admin
--

CREATE TABLE public.members (
    member_id text NOT NULL,
    name text,
    profile_type text,
    account_status text,
    loan_status text,
    savings_balance numeric,
    tenure_months integer,
    test_purpose text,
    expected_behavior text
);


ALTER TABLE public.members OWNER TO cas_admin;

--
-- Name: policies_index; Type: TABLE; Schema: public; Owner: cas_admin
--

CREATE TABLE public.policies_index (
    policy_id text NOT NULL,
    policy_name text,
    vop_layer text,
    vop_component text,
    enforcement_type text,
    summary text,
    linked_test_cases text
);


ALTER TABLE public.policies_index OWNER TO cas_admin;

--
-- Name: staff; Type: TABLE; Schema: public; Owner: cas_admin
--

CREATE TABLE public.staff (
    staff_id text NOT NULL,
    name text,
    role_title text,
    access_level text,
    responsibility text,
    query_scope_allowed text,
    vop_enforcement_notes text
);


ALTER TABLE public.staff OWNER TO cas_admin;

--
-- Name: board_of_directors board_of_directors_pkey; Type: CONSTRAINT; Schema: public; Owner: cas_admin
--

ALTER TABLE ONLY public.board_of_directors
    ADD CONSTRAINT board_of_directors_pkey PRIMARY KEY (bod_id);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: public; Owner: cas_admin
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (member_id);


--
-- Name: policies_index policies_index_pkey; Type: CONSTRAINT; Schema: public; Owner: cas_admin
--

ALTER TABLE ONLY public.policies_index
    ADD CONSTRAINT policies_index_pkey PRIMARY KEY (policy_id);


--
-- Name: staff staff_pkey; Type: CONSTRAINT; Schema: public; Owner: cas_admin
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (staff_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 1M7yfjQfKASsMpD2co6geBPhymX6J3376uEV6tZH4vi0XuvnUYCHD7IoLoVoKbW

