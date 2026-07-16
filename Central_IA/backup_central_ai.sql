--
-- PostgreSQL database dump
--

\restrict d5WG5DLLstxF6jDLyfosC4KE3GNa51kmBB98pEuhpUHDRY6cibGAcca69IVSBn7

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

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

ALTER TABLE ONLY public.whatsapp_message_log DROP CONSTRAINT whatsapp_message_log_merchant_id_fkey;
ALTER TABLE ONLY public.merchant DROP CONSTRAINT merchant_loja_pai_id_fkey;
ALTER TABLE ONLY public.client_chat_state DROP CONSTRAINT client_chat_state_merchant_id_fkey;
ALTER TABLE ONLY public.chat_message DROP CONSTRAINT chat_message_merchant_id_fkey;
ALTER TABLE ONLY moura_schema.custos DROP CONSTRAINT custos_categoria_id_fkey;
ALTER TABLE ONLY moura_schema.appointments DROP CONSTRAINT appointments_service_id_fkey;
ALTER TABLE ONLY moura_schema.appointments DROP CONSTRAINT appointments_customer_id_fkey;
ALTER TABLE ONLY moura_schema.appointment DROP CONSTRAINT appointment_id_cliente_fkey;
ALTER TABLE ONLY jessiely_moura.custos DROP CONSTRAINT custos_categoria_id_fkey;
DROP INDEX public.ix_whatsapp_message_log_merchant_id;
DROP INDEX public.ix_whatsapp_message_log_id;
DROP INDEX public.ix_usuarios_telefone;
DROP INDEX public.ix_usuarios_nome;
DROP INDEX public.ix_usuarios_id;
DROP INDEX public.ix_client_chat_state_merchant_id;
DROP INDEX public.ix_client_chat_state_id;
DROP INDEX public.ix_client_chat_state_client_phone;
DROP INDEX public.ix_chat_message_merchant_id;
DROP INDEX public.ix_chat_message_id;
DROP INDEX public.ix_chat_message_client_phone;
ALTER TABLE ONLY template_petshop.services DROP CONSTRAINT services_pkey;
ALTER TABLE ONLY template_petshop.customers DROP CONSTRAINT customers_telefone_whatsapp_key;
ALTER TABLE ONLY template_petshop.customers DROP CONSTRAINT customers_pkey;
ALTER TABLE ONLY template_petshop.appointments DROP CONSTRAINT appointments_pkey;
ALTER TABLE ONLY public.whatsapp_message_log DROP CONSTRAINT whatsapp_message_log_pkey;
ALTER TABLE ONLY public.usuarios DROP CONSTRAINT usuarios_pkey;
ALTER TABLE ONLY public.rascunhos_agendamento DROP CONSTRAINT rascunhos_agendamento_telefone_cliente_key;
ALTER TABLE ONLY public.rascunhos_agendamento DROP CONSTRAINT rascunhos_agendamento_pkey;
ALTER TABLE ONLY public.merchant DROP CONSTRAINT merchant_pkey;
ALTER TABLE ONLY public.merchant DROP CONSTRAINT merchant_nome_do_schema_key;
ALTER TABLE ONLY public.merchant DROP CONSTRAINT merchant_email_key;
ALTER TABLE ONLY public.merchant DROP CONSTRAINT merchant_codigo_loja_key;
ALTER TABLE ONLY public.client_chat_state DROP CONSTRAINT client_chat_state_pkey;
ALTER TABLE ONLY public.chat_message DROP CONSTRAINT chat_message_pkey;
ALTER TABLE ONLY public.active_sessions DROP CONSTRAINT active_sessions_pkey;
ALTER TABLE ONLY petshop_demo.services DROP CONSTRAINT services_pkey;
ALTER TABLE ONLY petshop_demo.customers DROP CONSTRAINT customers_telefone_whatsapp_key;
ALTER TABLE ONLY petshop_demo.customers DROP CONSTRAINT customers_pkey;
ALTER TABLE ONLY petshop_demo.appointments DROP CONSTRAINT appointments_pkey;
ALTER TABLE ONLY moura_schema.services DROP CONSTRAINT services_pkey;
ALTER TABLE ONLY moura_schema.custos DROP CONSTRAINT custos_pkey;
ALTER TABLE ONLY moura_schema.customers DROP CONSTRAINT customers_telefone_whatsapp_key;
ALTER TABLE ONLY moura_schema.customers DROP CONSTRAINT customers_pkey;
ALTER TABLE ONLY moura_schema.client DROP CONSTRAINT client_pkey;
ALTER TABLE ONLY moura_schema.client DROP CONSTRAINT client_numero_whatsapp_key;
ALTER TABLE ONLY moura_schema.categorias_custo DROP CONSTRAINT categorias_custo_pkey;
ALTER TABLE ONLY moura_schema.business_hours DROP CONSTRAINT business_hours_pkey;
ALTER TABLE ONLY moura_schema.appointments DROP CONSTRAINT appointments_pkey;
ALTER TABLE ONLY moura_schema.appointment DROP CONSTRAINT appointment_pkey;
ALTER TABLE ONLY moura_schema.agendamentos DROP CONSTRAINT agendamentos_pkey;
ALTER TABLE ONLY jessiely_moura.services DROP CONSTRAINT services_pkey;
ALTER TABLE ONLY jessiely_moura.custos DROP CONSTRAINT custos_pkey;
ALTER TABLE ONLY jessiely_moura.customers DROP CONSTRAINT customers_telefone_whatsapp_key;
ALTER TABLE ONLY jessiely_moura.customers DROP CONSTRAINT customers_pkey;
ALTER TABLE ONLY jessiely_moura.client DROP CONSTRAINT client_pkey;
ALTER TABLE ONLY jessiely_moura.client DROP CONSTRAINT client_numero_whatsapp_key;
ALTER TABLE ONLY jessiely_moura.categorias_custo DROP CONSTRAINT categorias_custo_pkey;
ALTER TABLE ONLY jessiely_moura.business_hours DROP CONSTRAINT business_hours_pkey;
ALTER TABLE ONLY jessiely_moura.appointments DROP CONSTRAINT appointments_pkey;
ALTER TABLE ONLY jessiely_moura.appointment DROP CONSTRAINT appointment_pkey;
ALTER TABLE ONLY jessiely_moura.agendamentos DROP CONSTRAINT agendamentos_pkey;
ALTER TABLE public.whatsapp_message_log ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.usuarios ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.rascunhos_agendamento ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.merchant ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.client_chat_state ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.chat_message ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.active_sessions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.services ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.custos ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.customers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.client ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.categorias_custo ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.business_hours ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.appointments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.appointment ALTER COLUMN id DROP DEFAULT;
ALTER TABLE moura_schema.agendamentos ALTER COLUMN id DROP DEFAULT;
ALTER TABLE jessiely_moura.custos ALTER COLUMN id DROP DEFAULT;
ALTER TABLE jessiely_moura.categorias_custo ALTER COLUMN id DROP DEFAULT;
DROP TABLE template_petshop.services;
DROP TABLE template_petshop.customers;
DROP TABLE template_petshop.appointments;
DROP SEQUENCE public.whatsapp_message_log_id_seq;
DROP TABLE public.whatsapp_message_log;
DROP SEQUENCE public.usuarios_id_seq;
DROP TABLE public.usuarios;
DROP SEQUENCE public.rascunhos_agendamento_id_seq;
DROP TABLE public.rascunhos_agendamento;
DROP SEQUENCE public.merchant_id_seq;
DROP TABLE public.merchant;
DROP SEQUENCE public.client_chat_state_id_seq;
DROP TABLE public.client_chat_state;
DROP SEQUENCE public.chat_message_id_seq;
DROP TABLE public.chat_message;
DROP SEQUENCE public.active_sessions_id_seq;
DROP TABLE public.active_sessions;
DROP TABLE petshop_demo.services;
DROP TABLE petshop_demo.customers;
DROP TABLE petshop_demo.appointments;
DROP SEQUENCE moura_schema.custos_id_seq;
DROP TABLE moura_schema.custos;
DROP SEQUENCE moura_schema.categorias_custo_id_seq;
DROP TABLE moura_schema.categorias_custo;
DROP TABLE jessiely_moura.services;
DROP SEQUENCE moura_schema.services_id_seq;
DROP TABLE moura_schema.services;
DROP SEQUENCE jessiely_moura.custos_id_seq;
DROP TABLE jessiely_moura.custos;
DROP TABLE jessiely_moura.customers;
DROP SEQUENCE moura_schema.customers_id_seq;
DROP TABLE moura_schema.customers;
DROP TABLE jessiely_moura.client;
DROP SEQUENCE moura_schema.client_id_seq;
DROP TABLE moura_schema.client;
DROP SEQUENCE jessiely_moura.categorias_custo_id_seq;
DROP TABLE jessiely_moura.categorias_custo;
DROP TABLE jessiely_moura.business_hours;
DROP SEQUENCE moura_schema.business_hours_id_seq;
DROP TABLE moura_schema.business_hours;
DROP TABLE jessiely_moura.appointments;
DROP SEQUENCE moura_schema.appointments_id_seq;
DROP TABLE moura_schema.appointments;
DROP TABLE jessiely_moura.appointment;
DROP SEQUENCE moura_schema.appointment_id_seq;
DROP TABLE moura_schema.appointment;
DROP TABLE jessiely_moura.agendamentos;
DROP SEQUENCE moura_schema.agendamentos_id_seq;
DROP TABLE moura_schema.agendamentos;
DROP SCHEMA template_petshop;
DROP SCHEMA petshop_demo;
DROP SCHEMA moura_schema;
DROP SCHEMA jessiely_moura;
--
-- Name: jessiely_moura; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA jessiely_moura;


ALTER SCHEMA jessiely_moura OWNER TO postgres;

--
-- Name: moura_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA moura_schema;


ALTER SCHEMA moura_schema OWNER TO postgres;

--
-- Name: petshop_demo; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA petshop_demo;


ALTER SCHEMA petshop_demo OWNER TO postgres;

--
-- Name: template_petshop; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA template_petshop;


ALTER SCHEMA template_petshop OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agendamentos; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.agendamentos (
    id integer NOT NULL,
    cliente_nome character varying(100),
    cliente_whatsapp character varying(20),
    data_horario timestamp without time zone,
    servico character varying(100)
);


ALTER TABLE moura_schema.agendamentos OWNER TO postgres;

--
-- Name: agendamentos_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.agendamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.agendamentos_id_seq OWNER TO postgres;

--
-- Name: agendamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.agendamentos_id_seq OWNED BY moura_schema.agendamentos.id;


--
-- Name: agendamentos; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.agendamentos (
    id integer DEFAULT nextval('moura_schema.agendamentos_id_seq'::regclass) NOT NULL,
    cliente_nome character varying(100),
    cliente_whatsapp character varying(20),
    data_horario timestamp without time zone,
    servico character varying(100)
);


ALTER TABLE jessiely_moura.agendamentos OWNER TO postgres;

--
-- Name: appointment; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.appointment (
    id integer NOT NULL,
    id_cliente integer,
    data_hora_inicio timestamp without time zone NOT NULL,
    data_hora_fim timestamp without time zone NOT NULL,
    status character varying(50) DEFAULT 'pendente'::character varying
);


ALTER TABLE moura_schema.appointment OWNER TO postgres;

--
-- Name: appointment_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.appointment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.appointment_id_seq OWNER TO postgres;

--
-- Name: appointment_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.appointment_id_seq OWNED BY moura_schema.appointment.id;


--
-- Name: appointment; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.appointment (
    id integer DEFAULT nextval('moura_schema.appointment_id_seq'::regclass) NOT NULL,
    id_cliente integer,
    data_hora_inicio timestamp without time zone NOT NULL,
    data_hora_fim timestamp without time zone NOT NULL,
    status character varying(50) DEFAULT 'pendente'::character varying
);


ALTER TABLE jessiely_moura.appointment OWNER TO postgres;

--
-- Name: appointments; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.appointments (
    id integer NOT NULL,
    customer_id integer,
    service_id integer,
    data_agendamento date NOT NULL,
    horario_agendamento time without time zone NOT NULL,
    status character varying(50) DEFAULT 'pendente'::character varying,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    origem character varying(50),
    recurrence_id text,
    valor_cobrado numeric(10,2),
    is_paid_in_package boolean DEFAULT false,
    numero_ticket integer,
    reagendamento_hora time without time zone,
    tipo_pendencia character varying(20),
    reagendamento_data date,
    motivo_cancelamento text
);


ALTER TABLE moura_schema.appointments OWNER TO postgres;

--
-- Name: appointments_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.appointments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.appointments_id_seq OWNER TO postgres;

--
-- Name: appointments_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.appointments_id_seq OWNED BY moura_schema.appointments.id;


--
-- Name: appointments; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.appointments (
    id integer DEFAULT nextval('moura_schema.appointments_id_seq'::regclass) NOT NULL,
    customer_id integer,
    service_id integer,
    data_agendamento date NOT NULL,
    horario_agendamento time without time zone NOT NULL,
    status character varying(50) DEFAULT 'pendente'::character varying,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    origem character varying(50),
    recurrence_id text,
    valor_cobrado numeric(10,2),
    is_paid_in_package boolean DEFAULT false,
    numero_ticket integer,
    tipo_pendencia character varying(20),
    reagendamento_data date,
    reagendamento_hora time without time zone,
    motivo_cancelamento text
);


ALTER TABLE jessiely_moura.appointments OWNER TO postgres;

--
-- Name: business_hours; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.business_hours (
    id integer NOT NULL,
    dia_da_semana integer NOT NULL,
    hora_abertura time without time zone NOT NULL,
    hora_fechamento time without time zone NOT NULL,
    tempo_atendimento_minutos integer NOT NULL,
    CONSTRAINT business_hours_dia_da_semana_check CHECK (((dia_da_semana >= 0) AND (dia_da_semana <= 6)))
);


ALTER TABLE moura_schema.business_hours OWNER TO postgres;

--
-- Name: business_hours_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.business_hours_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.business_hours_id_seq OWNER TO postgres;

--
-- Name: business_hours_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.business_hours_id_seq OWNED BY moura_schema.business_hours.id;


--
-- Name: business_hours; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.business_hours (
    id integer DEFAULT nextval('moura_schema.business_hours_id_seq'::regclass) NOT NULL,
    dia_da_semana integer NOT NULL,
    hora_abertura time without time zone NOT NULL,
    hora_fechamento time without time zone NOT NULL,
    tempo_atendimento_minutos integer NOT NULL,
    CONSTRAINT business_hours_dia_da_semana_check CHECK (((dia_da_semana >= 0) AND (dia_da_semana <= 6)))
);


ALTER TABLE jessiely_moura.business_hours OWNER TO postgres;

--
-- Name: categorias_custo; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.categorias_custo (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE jessiely_moura.categorias_custo OWNER TO postgres;

--
-- Name: categorias_custo_id_seq; Type: SEQUENCE; Schema: jessiely_moura; Owner: postgres
--

CREATE SEQUENCE jessiely_moura.categorias_custo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jessiely_moura.categorias_custo_id_seq OWNER TO postgres;

--
-- Name: categorias_custo_id_seq; Type: SEQUENCE OWNED BY; Schema: jessiely_moura; Owner: postgres
--

ALTER SEQUENCE jessiely_moura.categorias_custo_id_seq OWNED BY jessiely_moura.categorias_custo.id;


--
-- Name: client; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.client (
    id integer NOT NULL,
    numero_whatsapp character varying(50) NOT NULL,
    nome character varying(255)
);


ALTER TABLE moura_schema.client OWNER TO postgres;

--
-- Name: client_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.client_id_seq OWNER TO postgres;

--
-- Name: client_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.client_id_seq OWNED BY moura_schema.client.id;


--
-- Name: client; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.client (
    id integer DEFAULT nextval('moura_schema.client_id_seq'::regclass) NOT NULL,
    numero_whatsapp character varying(50) NOT NULL,
    nome character varying(255)
);


ALTER TABLE jessiely_moura.client OWNER TO postgres;

--
-- Name: customers; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.customers (
    id integer NOT NULL,
    nome character varying(255),
    telefone_whatsapp character varying(50) NOT NULL,
    ultima_interacao timestamp without time zone DEFAULT now(),
    data_nascimento character varying(20),
    origem character varying(50) DEFAULT 'Manual'::character varying,
    anotacoes text
);


ALTER TABLE moura_schema.customers OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.customers_id_seq OWNER TO postgres;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.customers_id_seq OWNED BY moura_schema.customers.id;


--
-- Name: customers; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.customers (
    id integer DEFAULT nextval('moura_schema.customers_id_seq'::regclass) NOT NULL,
    nome character varying(255),
    telefone_whatsapp character varying(50) NOT NULL,
    ultima_interacao timestamp without time zone DEFAULT now(),
    data_nascimento character varying(20),
    origem character varying(50) DEFAULT 'Manual'::character varying,
    anotacoes text
);


ALTER TABLE jessiely_moura.customers OWNER TO postgres;

--
-- Name: custos; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.custos (
    id integer NOT NULL,
    categoria_id integer,
    valor numeric(10,2) NOT NULL,
    data date DEFAULT CURRENT_DATE,
    descricao text,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE jessiely_moura.custos OWNER TO postgres;

--
-- Name: custos_id_seq; Type: SEQUENCE; Schema: jessiely_moura; Owner: postgres
--

CREATE SEQUENCE jessiely_moura.custos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jessiely_moura.custos_id_seq OWNER TO postgres;

--
-- Name: custos_id_seq; Type: SEQUENCE OWNED BY; Schema: jessiely_moura; Owner: postgres
--

ALTER SEQUENCE jessiely_moura.custos_id_seq OWNED BY jessiely_moura.custos.id;


--
-- Name: services; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.services (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    duracao_minutos integer DEFAULT 30,
    preco numeric(10,2)
);


ALTER TABLE moura_schema.services OWNER TO postgres;

--
-- Name: services_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.services_id_seq OWNER TO postgres;

--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.services_id_seq OWNED BY moura_schema.services.id;


--
-- Name: services; Type: TABLE; Schema: jessiely_moura; Owner: postgres
--

CREATE TABLE jessiely_moura.services (
    id integer DEFAULT nextval('moura_schema.services_id_seq'::regclass) NOT NULL,
    nome character varying(100) NOT NULL,
    duracao_minutos integer DEFAULT 30,
    preco numeric(10,2)
);


ALTER TABLE jessiely_moura.services OWNER TO postgres;

--
-- Name: categorias_custo; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.categorias_custo (
    id integer NOT NULL,
    nome character varying(255) NOT NULL,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE moura_schema.categorias_custo OWNER TO postgres;

--
-- Name: categorias_custo_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.categorias_custo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.categorias_custo_id_seq OWNER TO postgres;

--
-- Name: categorias_custo_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.categorias_custo_id_seq OWNED BY moura_schema.categorias_custo.id;


--
-- Name: custos; Type: TABLE; Schema: moura_schema; Owner: postgres
--

CREATE TABLE moura_schema.custos (
    id integer NOT NULL,
    categoria_id integer,
    valor numeric(10,2) NOT NULL,
    data date DEFAULT CURRENT_DATE,
    descricao text,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE moura_schema.custos OWNER TO postgres;

--
-- Name: custos_id_seq; Type: SEQUENCE; Schema: moura_schema; Owner: postgres
--

CREATE SEQUENCE moura_schema.custos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE moura_schema.custos_id_seq OWNER TO postgres;

--
-- Name: custos_id_seq; Type: SEQUENCE OWNED BY; Schema: moura_schema; Owner: postgres
--

ALTER SEQUENCE moura_schema.custos_id_seq OWNED BY moura_schema.custos.id;


--
-- Name: appointments; Type: TABLE; Schema: petshop_demo; Owner: postgres
--

CREATE TABLE petshop_demo.appointments (
    id integer DEFAULT nextval('moura_schema.appointments_id_seq'::regclass) NOT NULL,
    customer_id integer,
    service_id integer,
    data_agendamento date NOT NULL,
    horario_agendamento time without time zone NOT NULL,
    status character varying(50) DEFAULT 'pendente'::character varying,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    origem character varying(50),
    recurrence_id text,
    valor_cobrado numeric(10,2),
    is_paid_in_package boolean DEFAULT false,
    numero_ticket integer,
    reagendamento_hora time without time zone,
    tipo_pendencia character varying(20),
    reagendamento_data date,
    motivo_cancelamento text
);


ALTER TABLE petshop_demo.appointments OWNER TO postgres;

--
-- Name: customers; Type: TABLE; Schema: petshop_demo; Owner: postgres
--

CREATE TABLE petshop_demo.customers (
    id integer DEFAULT nextval('moura_schema.customers_id_seq'::regclass) NOT NULL,
    nome character varying(255),
    telefone_whatsapp character varying(50) NOT NULL,
    ultima_interacao timestamp without time zone DEFAULT now(),
    data_nascimento character varying(20),
    origem character varying(50) DEFAULT 'Manual'::character varying,
    anotacoes text
);


ALTER TABLE petshop_demo.customers OWNER TO postgres;

--
-- Name: services; Type: TABLE; Schema: petshop_demo; Owner: postgres
--

CREATE TABLE petshop_demo.services (
    id integer DEFAULT nextval('moura_schema.services_id_seq'::regclass) NOT NULL,
    nome character varying(100) NOT NULL,
    duracao_minutos integer DEFAULT 30,
    preco numeric(10,2)
);


ALTER TABLE petshop_demo.services OWNER TO postgres;

--
-- Name: active_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.active_sessions (
    id integer NOT NULL,
    telefone_cliente character varying(50) NOT NULL,
    loja_atual character varying(50) NOT NULL,
    ultima_interacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    dados_sessao json,
    ativo boolean DEFAULT true
);


ALTER TABLE public.active_sessions OWNER TO postgres;

--
-- Name: active_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.active_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.active_sessions_id_seq OWNER TO postgres;

--
-- Name: active_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.active_sessions_id_seq OWNED BY public.active_sessions.id;


--
-- Name: chat_message; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_message (
    id integer NOT NULL,
    merchant_id integer NOT NULL,
    client_phone character varying(50) NOT NULL,
    message_content character varying(2000) NOT NULL,
    sender character varying(50) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    read boolean DEFAULT false NOT NULL
);


ALTER TABLE public.chat_message OWNER TO postgres;

--
-- Name: chat_message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_message_id_seq OWNER TO postgres;

--
-- Name: chat_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_message_id_seq OWNED BY public.chat_message.id;


--
-- Name: client_chat_state; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_chat_state (
    id integer NOT NULL,
    merchant_id integer NOT NULL,
    client_phone character varying(50) NOT NULL,
    client_name character varying(255),
    is_human_service boolean DEFAULT false NOT NULL,
    human_service_started_at timestamp with time zone
);


ALTER TABLE public.client_chat_state OWNER TO postgres;

--
-- Name: client_chat_state_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_chat_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.client_chat_state_id_seq OWNER TO postgres;

--
-- Name: client_chat_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_chat_state_id_seq OWNED BY public.client_chat_state.id;


--
-- Name: merchant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.merchant (
    id integer NOT NULL,
    nome_loja character varying(255) NOT NULL,
    codigo_loja character varying(50),
    telefone_contato character varying(50),
    nome_do_schema character varying(50) NOT NULL,
    area_atuacao character varying(100),
    email character varying(255),
    senha_hash character varying(255),
    push_token character varying(255),
    permitir_sobreposicao boolean DEFAULT false NOT NULL,
    horario_abertura character varying(5) DEFAULT '08:00'::character varying NOT NULL,
    horario_fechamento character varying(5) DEFAULT '18:00'::character varying NOT NULL,
    is_admin boolean DEFAULT false NOT NULL,
    numero_whatsapp character varying(20),
    tem_dashboard boolean DEFAULT false NOT NULL,
    loja_pai_id integer,
    pode_editar_servicos boolean DEFAULT true NOT NULL,
    nome_usuario character varying(255),
    dias_fechados character varying(50),
    horario_almoco_inicio character varying(5),
    horario_almoco_fim character varying(5),
    politica_aceita boolean DEFAULT false NOT NULL,
    foto_perfil character varying,
    meta_access_token character varying(500),
    meta_phone_id character varying(50),
    notificacoes_push_enabled boolean DEFAULT true NOT NULL,
    notificacoes_novos boolean DEFAULT true NOT NULL,
    notificacoes_cancelamentos boolean DEFAULT true NOT NULL,
    notificacoes_lembretes boolean DEFAULT true NOT NULL,
    numero_chefe character varying(20),
    nome_chefe character varying(100)
);


ALTER TABLE public.merchant OWNER TO postgres;

--
-- Name: merchant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.merchant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.merchant_id_seq OWNER TO postgres;

--
-- Name: merchant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.merchant_id_seq OWNED BY public.merchant.id;


--
-- Name: rascunhos_agendamento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rascunhos_agendamento (
    id integer NOT NULL,
    telefone_cliente character varying(50) NOT NULL,
    servico character varying(100),
    data_agendamento character varying(50),
    hora_agendamento character varying(50),
    ultima_interacao timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.rascunhos_agendamento OWNER TO postgres;

--
-- Name: rascunhos_agendamento_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rascunhos_agendamento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rascunhos_agendamento_id_seq OWNER TO postgres;

--
-- Name: rascunhos_agendamento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rascunhos_agendamento_id_seq OWNED BY public.rascunhos_agendamento.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nome character varying,
    telefone character varying
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: whatsapp_message_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.whatsapp_message_log (
    id integer NOT NULL,
    merchant_id integer NOT NULL,
    recipient character varying(50) NOT NULL,
    message_type character varying(50) NOT NULL,
    sent_at timestamp with time zone NOT NULL,
    cost_estimated double precision NOT NULL
);


ALTER TABLE public.whatsapp_message_log OWNER TO postgres;

--
-- Name: whatsapp_message_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.whatsapp_message_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.whatsapp_message_log_id_seq OWNER TO postgres;

--
-- Name: whatsapp_message_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.whatsapp_message_log_id_seq OWNED BY public.whatsapp_message_log.id;


--
-- Name: appointments; Type: TABLE; Schema: template_petshop; Owner: postgres
--

CREATE TABLE template_petshop.appointments (
    id integer DEFAULT nextval('moura_schema.appointments_id_seq'::regclass) NOT NULL,
    customer_id integer,
    service_id integer,
    data_agendamento date NOT NULL,
    horario_agendamento time without time zone NOT NULL,
    status character varying(50) DEFAULT 'pendente'::character varying,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    origem character varying(50),
    recurrence_id text,
    valor_cobrado numeric(10,2),
    is_paid_in_package boolean DEFAULT false,
    numero_ticket integer,
    reagendamento_hora time without time zone,
    tipo_pendencia character varying(20),
    reagendamento_data date,
    motivo_cancelamento text
);


ALTER TABLE template_petshop.appointments OWNER TO postgres;

--
-- Name: customers; Type: TABLE; Schema: template_petshop; Owner: postgres
--

CREATE TABLE template_petshop.customers (
    id integer DEFAULT nextval('moura_schema.customers_id_seq'::regclass) NOT NULL,
    nome character varying(255),
    telefone_whatsapp character varying(50) NOT NULL,
    ultima_interacao timestamp without time zone DEFAULT now(),
    data_nascimento character varying(20),
    origem character varying(50) DEFAULT 'Manual'::character varying,
    anotacoes text
);


ALTER TABLE template_petshop.customers OWNER TO postgres;

--
-- Name: services; Type: TABLE; Schema: template_petshop; Owner: postgres
--

CREATE TABLE template_petshop.services (
    id integer DEFAULT nextval('moura_schema.services_id_seq'::regclass) NOT NULL,
    nome character varying(100) NOT NULL,
    duracao_minutos integer DEFAULT 30,
    preco numeric(10,2)
);


ALTER TABLE template_petshop.services OWNER TO postgres;

--
-- Name: categorias_custo id; Type: DEFAULT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.categorias_custo ALTER COLUMN id SET DEFAULT nextval('jessiely_moura.categorias_custo_id_seq'::regclass);


--
-- Name: custos id; Type: DEFAULT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.custos ALTER COLUMN id SET DEFAULT nextval('jessiely_moura.custos_id_seq'::regclass);


--
-- Name: agendamentos id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.agendamentos ALTER COLUMN id SET DEFAULT nextval('moura_schema.agendamentos_id_seq'::regclass);


--
-- Name: appointment id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointment ALTER COLUMN id SET DEFAULT nextval('moura_schema.appointment_id_seq'::regclass);


--
-- Name: appointments id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointments ALTER COLUMN id SET DEFAULT nextval('moura_schema.appointments_id_seq'::regclass);


--
-- Name: business_hours id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.business_hours ALTER COLUMN id SET DEFAULT nextval('moura_schema.business_hours_id_seq'::regclass);


--
-- Name: categorias_custo id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.categorias_custo ALTER COLUMN id SET DEFAULT nextval('moura_schema.categorias_custo_id_seq'::regclass);


--
-- Name: client id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.client ALTER COLUMN id SET DEFAULT nextval('moura_schema.client_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.customers ALTER COLUMN id SET DEFAULT nextval('moura_schema.customers_id_seq'::regclass);


--
-- Name: custos id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.custos ALTER COLUMN id SET DEFAULT nextval('moura_schema.custos_id_seq'::regclass);


--
-- Name: services id; Type: DEFAULT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.services ALTER COLUMN id SET DEFAULT nextval('moura_schema.services_id_seq'::regclass);


--
-- Name: active_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_sessions ALTER COLUMN id SET DEFAULT nextval('public.active_sessions_id_seq'::regclass);


--
-- Name: chat_message id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message ALTER COLUMN id SET DEFAULT nextval('public.chat_message_id_seq'::regclass);


--
-- Name: client_chat_state id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_chat_state ALTER COLUMN id SET DEFAULT nextval('public.client_chat_state_id_seq'::regclass);


--
-- Name: merchant id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant ALTER COLUMN id SET DEFAULT nextval('public.merchant_id_seq'::regclass);


--
-- Name: rascunhos_agendamento id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rascunhos_agendamento ALTER COLUMN id SET DEFAULT nextval('public.rascunhos_agendamento_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Name: whatsapp_message_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.whatsapp_message_log ALTER COLUMN id SET DEFAULT nextval('public.whatsapp_message_log_id_seq'::regclass);


--
-- Data for Name: agendamentos; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.agendamentos (id, cliente_nome, cliente_whatsapp, data_horario, servico) FROM stdin;
\.


--
-- Data for Name: appointment; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.appointment (id, id_cliente, data_hora_inicio, data_hora_fim, status) FROM stdin;
\.


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.appointments (id, customer_id, service_id, data_agendamento, horario_agendamento, status, criado_em, origem, recurrence_id, valor_cobrado, is_paid_in_package, numero_ticket, tipo_pendencia, reagendamento_data, reagendamento_hora, motivo_cancelamento) FROM stdin;
103	49	2	2026-07-06	14:00:00	aprovado	2026-07-01 18:02:04.528486	whatsapp_lau	\N	\N	f	1	\N	\N	\N	\N
108	54	20	2026-07-04	14:30:00	aprovado	2026-07-01 19:36:45.974723	whatsapp_lau	\N	\N	f	3	\N	\N	\N	\N
107	54	2	2026-07-02	08:00:00	aprovado	2026-07-01 19:05:36.270687	whatsapp_lau	\N	\N	f	2	\N	\N	\N	\N
113	64	19	2026-07-04	08:00:00	aprovado	2026-07-04 12:41:46.873	manual	\N	\N	f	4	\N	\N	\N	\N
114	67	19	2026-07-04	09:00:00	aprovado	2026-07-04 12:42:15.323696	manual	\N	\N	f	5	\N	\N	\N	\N
115	70	23	2026-07-04	09:40:00	aprovado	2026-07-04 12:43:56.96399	manual	\N	\N	f	6	\N	\N	\N	\N
116	62	19	2026-07-04	10:00:00	aprovado	2026-07-04 12:47:03.763987	manual	\N	\N	f	7	\N	\N	\N	\N
117	73	20	2026-07-04	10:30:00	aprovado	2026-07-04 12:49:08.893963	manual	\N	\N	f	8	\N	\N	\N	\N
118	66	20	2026-07-04	11:00:00	aprovado	2026-07-04 12:50:02.826904	manual	\N	\N	f	9	\N	\N	\N	\N
119	76	19	2026-07-04	11:30:00	aprovado	2026-07-04 12:51:49.962069	manual	\N	\N	f	10	\N	\N	\N	\N
120	78	19	2026-07-04	12:30:00	aprovado	2026-07-04 12:53:38.567271	manual	\N	\N	f	11	\N	\N	\N	\N
121	63	19	2026-07-04	13:00:00	aprovado	2026-07-04 12:53:59.959151	manual	\N	\N	f	12	\N	\N	\N	\N
130	46	1	2026-07-06	15:00:00	cancelado	2026-07-06 13:11:13.86711	whatsapp_lau	\N	\N	f	13	\N	\N	\N	\N
133	46	20	2026-07-06	15:40:00	cancelado	2026-07-06 13:44:20.413521	whatsapp_lau	\N	\N	f	16	\N	\N	\N	\N
132	46	22	2026-07-06	15:00:00	cancelado	2026-07-06 13:39:06.948261	whatsapp_lau	\N	\N	f	15	\N	\N	\N	\N
131	46	20	2026-07-06	15:00:00	cancelado	2026-07-06 13:28:53.690942	whatsapp_lau	\N	\N	f	14	\N	\N	\N	\N
134	46	5	2026-07-06	15:00:00	cancelado	2026-07-06 14:05:34.260057	whatsapp_lau	\N	\N	f	17	\N	\N	\N	\N
139	46	5	2026-07-07	15:00:00	recusado	2026-07-07 02:08:36.13543	whatsapp_lau	\N	\N	f	18	\N	\N	\N	\N
\.


--
-- Data for Name: business_hours; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.business_hours (id, dia_da_semana, hora_abertura, hora_fechamento, tempo_atendimento_minutos) FROM stdin;
\.


--
-- Data for Name: categorias_custo; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.categorias_custo (id, nome, criado_em) FROM stdin;
1	Comidas	2026-06-18 23:24:33.270538
2	luz	2026-06-21 01:41:37.38668
\.


--
-- Data for Name: client; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.client (id, numero_whatsapp, nome) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.customers (id, nome, telefone_whatsapp, ultima_interacao, data_nascimento, origem, anotacoes) FROM stdin;
65	Emanueli laser	5544997026771	2026-07-04 12:00:30.029007	\N	Manual	\N
60	Estefani Laser	5544999784263	2026-07-02 23:43:46.434829	\N	Manual	\N
53	Cida top	5544998050902	2026-07-01 19:02:22.353125	\N	Manual	\N
64	Beatriz	5544997025782	2026-07-04 11:59:50.387986	\N	Manual	\N
67	Vanessa sornias	5544999793963	2026-07-04 12:03:23.352356	\N	Manual	\N
70	Graciela	5544998908934	2026-07-04 12:43:01.583917	\N	Manual	\N
62	Sol	5544998458836	2026-07-04 11:56:17.351865	\N	Manual	\N
73	Andreia Romanoli	5544997126315	2026-07-04 12:48:43.081696	\N	Manual	\N
66	Thainá	5544999308423	2026-07-04 12:02:11.884395	\N	Manual	\N
76	Claudia Delnero	5544998492557	2026-07-04 12:51:11.481787	\N	Manual	\N
37	Bloqueio de Agenda	00000000000	2026-06-20 18:51:42.957086	\N	Manual	\N
78	Adriana Sanches	5544999227998	2026-07-04 12:52:56.615039	\N	Manual	\N
63	Fernanda Itaguajé	5544991647214	2026-07-04 11:58:14.367892	\N	Manual	\N
46	Matheus Moura	554199692193	2026-07-07 17:22:06.563137	18/07/2000	WhatsApp (Lau)	\N
49	Eloana Cavalcante	554498119082	2026-07-01 17:58:26.165392	02/06/2003	WhatsApp (Lau)	\N
54	Josiane De Oliveira Cardoso Piovesani	554491171444	2026-07-01 19:02:50.14444	13/06/1979	WhatsApp (Lau)	\N
\.


--
-- Data for Name: custos; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.custos (id, categoria_id, valor, data, descricao, criado_em) FROM stdin;
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: jessiely_moura; Owner: postgres
--

COPY jessiely_moura.services (id, nome, duracao_minutos, preco) FROM stdin;
1	Massagem Relaxante	30	100.00
2	Massagem Model	30	90.00
4	Ventosaterapia	60	100.00
5	Limpeza de Pele	30	160.00
10	Virilha completa	30	65.00
11	Axilas	10	25.00
12	Perna inteira	20	50.00
13	Meia perna	20	35.00
14	Buço nariz	15	30.00
15	Drenagem linfática	60	80.00
16	Pós cirurgia	60	120.00
17	Massagem terapêutica	60	150.00
18	Sobrancelha	30	40.00
19	Depilação a laser  virilha completa	25	150.00
20	Depilação a laser axilas	15	80.00
21	Depilação a laser perna inteira	30	150.00
22	Depilação a laser meia perna	20	100.00
23	Depilação a laser buço	20	60.00
24	Depilação a laser rosto	25	100.00
25	Bloqueio 360 min	360	0.00
\.


--
-- Data for Name: agendamentos; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.agendamentos (id, cliente_nome, cliente_whatsapp, data_horario, servico) FROM stdin;
\.


--
-- Data for Name: appointment; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.appointment (id, id_cliente, data_hora_inicio, data_hora_fim, status) FROM stdin;
\.


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.appointments (id, customer_id, service_id, data_agendamento, horario_agendamento, status, criado_em, origem, recurrence_id, valor_cobrado, is_paid_in_package, numero_ticket, reagendamento_hora, tipo_pendencia, reagendamento_data, motivo_cancelamento) FROM stdin;
102	39	28	2026-07-02	10:30:00	cancelado	2026-07-01 13:31:07.216911	manual	\N	\N	f	1	\N	\N	\N	\N
104	48	27	2026-07-01	15:33:00	aprovado	2026-07-01 18:33:07.34023	manual	\N	\N	f	2	\N	\N	\N	\N
105	48	27	2026-07-01	13:33:00	aprovado	2026-07-01 18:33:36.485997	manual	\N	\N	f	3	\N	\N	\N	\N
106	48	26	2026-07-02	15:34:00	aprovado	2026-07-01 18:34:28.59343	manual	\N	\N	f	4	\N	\N	\N	\N
110	56	26	2026-07-03	19:00:00	pendente	2026-07-02 00:51:38.703619	whatsapp_lau	\N	\N	f	6	\N	\N	\N	\N
109	55	26	2026-07-02	16:00:00	aprovado	2026-07-02 00:45:03.969961	whatsapp_lau	\N	\N	f	5	\N	\N	\N	\N
111	55	26	2026-07-03	12:00:00	aprovado	2026-07-02 18:11:32.492001	whatsapp_lau	\N	\N	f	7	\N	\N	\N	\N
112	55	26	2026-07-03	12:00:00	aprovado	2026-07-02 18:12:58.683714	whatsapp_lau	\N	\N	f	7	\N	cancelamento	\N	Compromisso de última hora
122	55	26	2026-07-06	15:00:00	cancelado	2026-07-04 19:50:16.763808	whatsapp_lau	\N	\N	f	8	\N	\N	\N	\N
124	55	26	2026-07-06	15:00:00	cancelado	2026-07-06 00:53:25.827346	whatsapp_lau	\N	\N	f	10	\N	\N	\N	\N
123	55	28	2026-07-06	12:00:00	cancelado	2026-07-06 00:00:42.70638	whatsapp_lau	\N	\N	f	9	\N	\N	\N	\N
126	55	26	2026-07-06	17:00:00	cancelado	2026-07-06 01:23:42.220907	whatsapp_lau	\N	\N	f	12	\N	\N	\N	\N
125	55	26	2026-07-07	16:00:00	cancelado	2026-07-06 01:14:36.020214	whatsapp_lau	\N	\N	f	11	\N	\N	\N	\N
127	55	26	2026-07-06	15:30:00	cancelado	2026-07-06 01:37:29.996075	whatsapp_lau	\N	\N	f	13	\N	\N	\N	\N
128	55	26	2026-07-06	14:00:00	cancelado	2026-07-06 01:44:06.335943	whatsapp_lau	\N	\N	f	14	\N	\N	\N	\N
135	55	26	2026-07-06	15:00:00	aprovado	2026-07-06 14:06:57.445735	whatsapp_lau	\N	\N	f	16	\N	\N	\N	\N
129	55	26	2026-07-06	15:30:00	cancelado	2026-07-06 01:52:58.172065	whatsapp_lau	\N	\N	f	15	\N	\N	\N	\N
136	55	26	2026-07-06	16:00:00	aprovado	2026-07-06 18:29:53.291555	whatsapp_lau	\N	\N	f	17	\N	\N	\N	\N
138	55	28	2026-07-06	17:30:00	aprovado	2026-07-06 18:29:53.291555	whatsapp_lau	\N	\N	f	19	\N	\N	\N	\N
137	55	27	2026-07-06	17:00:00	aprovado	2026-07-06 18:29:53.291555	whatsapp_lau	\N	\N	f	18	\N	\N	\N	\N
140	55	26	2026-07-07	17:00:00	aprovado	2026-07-07 19:29:43.565614	whatsapp_lau	\N	\N	f	20	\N	\N	\N	\N
141	81	26	2026-07-09	15:00:00	pendente	2026-07-09 02:37:42.323863	WhatsApp (Gestor)	\N	\N	f	\N	\N	\N	\N	\N
142	81	26	2026-07-11	15:00:00	confirmado	2026-07-10 15:09:01.300167	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
143	91	27	2026-07-10	14:00:00	confirmado	2026-07-10 16:16:25.034592	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
144	81	26	2026-07-10	14:00:00	confirmado	2026-07-10 16:17:12.614254	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
145	55	26	2026-07-10	14:00:00	confirmado	2026-07-10 16:25:57.910696	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
146	39	26	2026-07-10	14:00:00	confirmado	2026-07-10 16:29:30.430336	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
147	91	26	2026-07-11	13:00:00	confirmado	2026-07-10 16:32:41.238423	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
148	81	26	2026-07-11	16:00:00	confirmado	2026-07-10 16:32:44.439786	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
149	81	26	2026-07-13	13:00:00	confirmado	2026-07-10 21:38:29.156714	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
150	81	26	2026-07-12	13:00:00	confirmado	2026-07-11 11:22:37.55655	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
151	55	26	2026-07-11	10:01:00	aprovado	2026-07-11 13:01:18.077607	manual	\N	\N	f	21	\N	\N	\N	\N
152	92	27	2026-07-11	15:00:00	aprovado	2026-07-11 13:04:44.126949	whatsapp_lau	\N	\N	f	22	\N	\N	\N	\N
153	92	26	2026-07-10	10:09:00	aprovado	2026-07-11 13:09:18.707485	manual	\N	\N	f	23	\N	\N	\N	\N
154	92	26	2026-07-10	10:10:00	aprovado	2026-07-11 13:10:07.391315	manual	\N	\N	f	24	\N	\N	\N	\N
155	55	26	2026-07-13	15:00:00	aprovado	2026-07-12 21:59:09.441898	whatsapp_lau	\N	\N	f	25	\N	\N	\N	\N
156	96	26	2026-07-14	15:00:00	confirmado	2026-07-13 10:52:14.46086	App (IA)	\N	\N	f	\N	\N	\N	\N	\N
\.


--
-- Data for Name: business_hours; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.business_hours (id, dia_da_semana, hora_abertura, hora_fechamento, tempo_atendimento_minutos) FROM stdin;
\.


--
-- Data for Name: categorias_custo; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.categorias_custo (id, nome, criado_em) FROM stdin;
\.


--
-- Data for Name: client; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.client (id, numero_whatsapp, nome) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.customers (id, nome, telefone_whatsapp, ultima_interacao, data_nascimento, origem, anotacoes) FROM stdin;
56	Lucas Gabriel Ribeiro Ferracioli	554198317356	2026-07-02 00:48:21.322359	09/02/2001	WhatsApp (Lau)	\N
48	Piita	5535991228614	2026-07-01 15:57:37.11767	\N	Manual	\N
81	Bruno Lima	554199905084	2026-07-06 00:05:49.53252	13/10/2002	WhatsApp (Lau)	\N
91	João Jerosch	554187450272	2026-07-09 16:17:44.118556	\N	WhatsApp (Contato do Chefe)	\N
39	Matheus Jandoy	554199999999	2026-06-23 03:09:04.422094	18/07/2000	WhatsApp (Lau)	\N
55	Matheus Moura	554199692193	2026-07-08 01:34:39.027031	18/07/2000	WhatsApp (Lau)	\N
92	Vinicius Vaz	554192388448	2026-07-11 13:00:26.034202	30/07/1995	WhatsApp (Lau)	\N
96	Vitão	555492003773	2026-07-13 10:51:43.857059	\N	Manual	\N
\.


--
-- Data for Name: custos; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.custos (id, categoria_id, valor, data, descricao, criado_em) FROM stdin;
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: moura_schema; Owner: postgres
--

COPY moura_schema.services (id, nome, duracao_minutos, preco) FROM stdin;
26	Corte de cabelo	60	80.00
27	Corte Barba	30	40.00
28	Teste j	60	50.00
\.


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: petshop_demo; Owner: postgres
--

COPY petshop_demo.appointments (id, customer_id, service_id, data_agendamento, horario_agendamento, status, criado_em, origem, recurrence_id, valor_cobrado, is_paid_in_package, numero_ticket, reagendamento_hora, tipo_pendencia, reagendamento_data, motivo_cancelamento) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: petshop_demo; Owner: postgres
--

COPY petshop_demo.customers (id, nome, telefone_whatsapp, ultima_interacao, data_nascimento, origem, anotacoes) FROM stdin;
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: petshop_demo; Owner: postgres
--

COPY petshop_demo.services (id, nome, duracao_minutos, preco) FROM stdin;
29	Banho	60	50.00
30	Tosa	60	70.00
31	Banho e Tosa	120	100.00
32	Hidratação	30	40.00
33	Corte de Unhas	15	20.00
\.


--
-- Data for Name: active_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.active_sessions (id, telefone_cliente, loja_atual, ultima_interacao, dados_sessao, ativo) FROM stdin;
57	554199692193	jessiely_moura	2026-06-20 16:06:23.694817	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Claro, aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a sua data de nascimento?"}, {"role": "user", "content": "Pq?"}, {"role": "assistant", "content": "Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
53	554199692193	jessiely_moura	2026-06-20 15:31:22.738321	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Claro! Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "Limpeza de Pel"}, {"role": "assistant", "content": "Para iniciarmos, como posso te chamar?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Matheus, qual a sua data de nascimento para atualizarmos seu cadastro?"}, {"role": "user", "content": "18/07"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Limpeza de Pel"}, {"role": "assistant", "content": "Qual \\u00e9 o servi\\u00e7o que voc\\u00ea deseja? Limpeza de Pele ou outro?"}, {"role": "user", "content": "Limpeza de Pel"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Limpeza de PelE"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "oi"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
48	554498851300	jessiely_moura	2026-06-18 23:47:04.381707	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 100,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Oque \\u00e9 massagem model"}, {"role": "assistant", "content": "A Massagem Model \\u00e9 uma t\\u00e9cnica que visa modelar o corpo, promovendo a redu\\u00e7\\u00e3o de medidas e melhorando a circula\\u00e7\\u00e3o. Se precisar de mais informa\\u00e7\\u00f5es ou quiser agendar, estou \\u00e0 disposi\\u00e7\\u00e3o!"}, {"role": "user", "content": "Qual cera que vc usa?"}, {"role": "assistant", "content": "A cera utilizada \\u00e9 a cera quente, que proporciona uma depila\\u00e7\\u00e3o eficaz e menos dolorosa. Se precisar de mais informa\\u00e7\\u00f5es ou quiser agendar, estou \\u00e0 disposi\\u00e7\\u00e3o!"}, {"role": "user", "content": "Qual tempo de dura\\u00e7\\u00e3o?"}, {"role": "assistant", "content": "A dura\\u00e7\\u00e3o da Depila\\u00e7\\u00e3o a Cera \\u00e9 de 20 minutos. Se precisar de mais informa\\u00e7\\u00f5es ou quiser agendar, estou \\u00e0 disposi\\u00e7\\u00e3o!"}], "estado": {}, "ja_saudou": true}	f
51	554199692193	jessiely_moura	2026-06-20 15:13:05.906112	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Voc\\u00ea conhece os servi\\u00e7os da Jessiely Moura ou prefere que eu envie a lista de servi\\u00e7os dispon\\u00edveis?"}, {"role": "user", "content": "Quero agendar uma limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
58	554199692193	jessiely_moura	2026-06-20 16:07:38.517952	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
71	554199692193	jessiely_moura	2026-06-23 03:09:04.426987	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {}}	f
35	554199692193	jessiely_moura	2026-06-18 13:28:29.978011	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem"}, {"role": "assistant", "content": "Qual tipo de massagem voc\\u00ea deseja? Temos as seguintes op\\u00e7\\u00f5es: \\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)"}, {"role": "user", "content": "Relaxante"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Massagem Relaxante"]}, "ja_saudou": true}	f
1	554199692193	jessiely_moura	2026-06-16 17:26:06.720589	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR"}	f
3	554199692193	jessiely_moura	2026-06-16 22:44:16.399192	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR"}	f
123	554199692193	moura_schema	2026-07-11 13:24:31.257997	{"state": "AGUARDANDO_INTENCAO", "ja_saudou": true}	f
36	554199692193	jessiely_moura	2026-06-18 13:29:36.193833	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 46, "ticket_alvo": 4}	f
14	554199692193	jessiely_moura	2026-06-18 01:09:09.244375	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "3"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a Cera"]}, "ja_saudou": true}	f
11	554199692193	jessiely_moura	2026-06-17 22:15:36.771818	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 6, "ticket_alvo": 5}	f
7	554199692193	jessiely_moura	2026-06-17 17:13:13.355721	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 1, "ticket_alvo": 2}	f
5	554199692193	jessiely_moura	2026-06-17 16:23:09.447006	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR"}	f
6	554199692193	jessiely_moura	2026-06-17 16:23:48.25675	{"state": "AGUARDANDO_POS_CONSULTA", "intencao": "INTENT_CONSULTAR"}	f
16	554199692193	jessiely_moura	2026-06-18 01:13:44.258659	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR", "historico": [{"role": "user", "content": "sim"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "qual tem?"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual voc\\u00ea gostaria de escolher?"}, {"role": "user", "content": "lim de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
19	554192706305	jessiely_moura	2026-06-18 01:24:59.783127	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR", "historico": [{"role": "user", "content": "sim"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Brendinho farmador de aura 67 sixseven mono akali 1v9 top 10 br escuta e cala boca \\ud83e\\udd2b"}, {"role": "assistant", "content": "Antes de continuarmos, preciso do seu nome para o registro. Como posso te chamar?"}, {"role": "user", "content": "esse \\u00e9 meu nome"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "quero agendar"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "quais tem"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual voc\\u00ea gostaria de escolher?"}, {"role": "user", "content": "lavar cabelo"}, {"role": "assistant", "content": "O servi\\u00e7o 'lavar cabelo' n\\u00e3o est\\u00e1 dispon\\u00edvel. Por favor, escolha um dos servi\\u00e7os listados."}, {"role": "user", "content": "ventosaterapia"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para a Ventosaterapia?"}, {"role": "user", "content": "15/06 10:00"}, {"role": "assistant", "content": "A data escolhida \\u00e9 anterior a hoje. Por favor, escolha uma data v\\u00e1lida."}, {"role": "user", "content": "ontem meio dia"}, {"role": "assistant", "content": "A data escolhida \\u00e9 anterior a hoje. Por favor, escolha uma data v\\u00e1lida."}], "estado": {"servico": ["Ventosaterapia"], "data": null, "hora": "10:00"}, "ja_saudou": true}	f
34	554199692193	jessiely_moura	2026-06-18 13:00:09.372221	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem"}, {"role": "assistant", "content": "Qual tipo de massagem voc\\u00ea deseja: Massagem Relaxante ou Massagem Model?"}, {"role": "user", "content": "Modelo"}, {"role": "assistant", "content": "Qual a data e hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Massagem Model"]}, "ja_saudou": true}	f
54	554199692193	jessiely_moura	2026-06-20 15:32:51.892236	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, como posso te chamar?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Qual a sua data de nascimento para atualizarmos seu cadastro?"}, {"role": "user", "content": "18/07"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "realizar um agendamento"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece os servi\\u00e7os da Jessiely Moura ou prefere que eu envie a lista de servi\\u00e7os dispon\\u00edveis?"}, {"role": "user", "content": "quero fazer uma limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
94	554199692193	moura_schema	2026-07-04 00:06:43.697187	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}}	f
112	554199692193	moura_schema	2026-07-07 02:07:43.749904	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}}	f
72	554199692193	moura_schema	2026-06-23 03:12:25.69103	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Bom dia! \\ud83d\\ude0a Sou a Lau, assistente da *Loja Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}], "estado": {}}	f
73	554199692193	jessiely_moura	2026-06-23 03:19:34.047609	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {}}	f
18	554199692193	jessiely_moura	2026-06-18 01:18:59.556507	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem Relaxante"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "dia 15/06 as 17h"}, {"role": "assistant", "content": "A data informada \\u00e9 inv\\u00e1lida. Por favor, escolha uma data a partir de hoje."}], "estado": {"servico": ["Massagem Relaxante"], "data": null, "hora": "17:00"}, "ja_saudou": true}	f
42	554192706305	jessiely_moura	2026-06-18 19:34:42.591506	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Brendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2b"}, {"role": "assistant", "content": "Antes de continuarmos, preciso do seu nome para o registro. Como posso te chamar?"}, {"role": "user", "content": "Brendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar? Aqui est\\u00e3o as op\\u00e7\\u00f5es dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\n\\u2022 Bloqueio (R$ 0,00)"}, {"role": "user", "content": "o que seria esse bloqueio ?"}, {"role": "assistant", "content": "O servi\\u00e7o de Bloqueio \\u00e9 uma t\\u00e9cnica que visa aliviar tens\\u00f5es e promover relaxamento. Voc\\u00ea gostaria de agendar esse servi\\u00e7o ou escolher outro?"}, {"role": "user", "content": "quero esse para o dia 30 as 9"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "est\\u00e1 fechado o dia todo neste dia?"}, {"role": "assistant", "content": "O servi\\u00e7o de Bloqueio n\\u00e3o est\\u00e1 dispon\\u00edvel no dia 30 de junho. Voc\\u00ea gostaria de escolher outra data ou hor\\u00e1rio?"}, {"role": "user", "content": "30 as 14"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "dia 30/06 as 15"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {"servico": ["Bloqueio"], "data": null, "hora": null}, "ja_saudou": true}	f
55	554199692193	jessiely_moura	2026-06-20 15:57:21.225164	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, como posso te chamar?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Qual a sua data de nascimento para atualizarmos seu cadastro?"}, {"role": "user", "content": "18 07 2000"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Realizar agendamento"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {}, "ja_saudou": true}	f
37	554199692193	jessiely_moura	2026-06-18 13:52:19.138825	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem"}, {"role": "assistant", "content": "Qual tipo de massagem voc\\u00ea deseja: Massagem Relaxante ou Massagem Model?"}, {"role": "user", "content": "Relaxante"}, {"role": "assistant", "content": "Qual a data e hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Massagem Relaxante"]}, "ja_saudou": true}	f
59	554199692193	jessiely_moura	2026-06-20 16:17:40.57232	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os que temos:\\n\\u2022 Massagem Relaxante (R$ 100,00) [Dura\\u00e7\\u00e3o interna: 30 min]\\n\\u2022 Massagem Model (R$ 90,00) [Dura\\u00e7\\u00e3o interna: 30 min]\\n\\u2022 Ventosaterapia (R$ 100,00) [Dura\\u00e7\\u00e3o interna: 60 min]\\n\\u2022 Limpeza de Pele (R$ 160,00) [Dura\\u00e7\\u00e3o interna: 30 min]\\n\\u2022 Virilha completa (R$ 65,00) [Dura\\u00e7\\u00e3o interna: 30 min]\\n\\u2022 Axilas (R$ 25,00) [Dura\\u00e7\\u00e3o interna: 10 min]\\n\\u2022 Perna inteira (R$ 50,00) [Dura\\u00e7\\u00e3o interna: 20 min]\\n\\u2022 Meia perna (R$ 35,00) [Dura\\u00e7\\u00e3o interna: 20 min]\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00) [Dura\\u00e7\\u00e3o interna: 15 min]\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00) [Dura\\u00e7\\u00e3o interna: 60 min]\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00) [Dura\\u00e7\\u00e3o interna: 60 min]\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00) [Dura\\u00e7\\u00e3o interna: 60 min]\\n\\u2022 Sobrancelha (R$ 40,00) [Dura\\u00e7\\u00e3o interna: 30 min]\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00) [Dura\\u00e7\\u00e3o interna: 25 min]\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00) [Dura\\u00e7\\u00e3o interna: 15 min]\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00) [Dura\\u00e7\\u00e3o interna: 30 min]\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00) [Dura\\u00e7\\u00e3o interna: 20 min]\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00) [Dura\\u00e7\\u00e3o interna: 20 min]\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00) [Dura\\u00e7\\u00e3o interna: 25 min]\\n\\nQual deles voc\\u00ea deseja?"}], "estado": {}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
63	554199692193	jessiely_moura	2026-06-20 16:46:02.445144	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Conhe\\u00e7o"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Limpeza de pele e sobrancelha"}, {"role": "assistant", "content": "Qual data e hor\\u00e1rio voc\\u00ea gostaria para o agendamento?"}, {"role": "user", "content": "Hj 14"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Hoje as 14h30"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {"servico": ["Limpeza de Pele", "Sobrancelha"], "data": "2026-06-20", "hora": null}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
79	554199692193	jessiely_moura	2026-06-25 17:09:21.79577	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}}	f
8	554199692193	jessiely_moura	2026-06-17 20:00:09.981784	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Op\\u00e7\\u00e3o 5"}, {"role": "assistant", "content": "Qual data e hor\\u00e1rio voc\\u00ea gostaria para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
9	554199692193	jessiely_moura	2026-06-17 22:12:47.643991	{"state": "AGUARDANDO_POS_CONSULTA", "intencao": "INTENT_CONSULTAR"}	f
12	554199692193	jessiely_moura	2026-06-17 23:40:16.611263	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 5, "ticket_alvo": 4}	f
13	554199692193	jessiely_moura	2026-06-17 23:40:48.450599	{"state": "AGUARDANDO_INTENCAO"}	f
17	554199692193	jessiely_moura	2026-06-18 01:17:20.287544	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 27, "ticket_alvo": 21}	f
44	554199692193	jessiely_moura	2026-06-18 22:12:58.763023	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 58, "ticket_alvo": 13}	f
49	554199692193	jessiely_moura	2026-06-19 15:09:43.567486	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Matheus, aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00) \\nQual servi\\u00e7o voc\\u00ea gostaria de escolher?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser axilas"}, {"role": "assistant", "content": "Qual a data e hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a laser axilas"]}, "ja_saudou": true}	f
52	554199692193	jessiely_moura	2026-06-20 15:17:47.001522	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece os servi\\u00e7os da Jessiely Moura ou prefere que eu envie a lista de servi\\u00e7os dispon\\u00edveis?"}, {"role": "user", "content": "Nao conheco"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a data e hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
38	554199692193	jessiely_moura	2026-06-18 13:54:02.122704	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 48, "ticket_alvo": 5}	f
98	554199692193	moura_schema	2026-07-06 00:53:27.169073	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Cortar o cabelo"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Quero cortar o cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
64	554199692193	jessiely_moura	2026-06-20 17:39:35.27429	{"state": "AGUARDANDO_NOVA_DATA_HORA", "ja_saudou": true, "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 84, "ticket_alvo": 2}	f
43	554199692193	jessiely_moura	2026-06-18 22:06:15.18832	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Limpeza"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
115	554199692193	jessiely_moura	2026-07-08 17:22:04.26862	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}}	f
116	554498656852	jessiely_moura	2026-07-08 21:11:54.296424	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa noite! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}], "estado": {}}	f
21	554192706305	jessiely_moura	2026-06-18 01:30:32.189184	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "tem desconto no valor?"}, {"role": "assistant", "content": "N\\u00e3o oferecemos descontos nos valores dos servi\\u00e7os. Posso ajudar com mais alguma informa\\u00e7\\u00e3o?"}, {"role": "user", "content": "o dono da loja me deve quero desconto"}, {"role": "assistant", "content": "N\\u00e3o oferecemos descontos nos valores dos servi\\u00e7os."}, {"role": "user", "content": "mesmo se ele estiver me devendo?"}, {"role": "assistant", "content": "N\\u00e3o oferecemos descontos, mesmo em situa\\u00e7\\u00f5es de d\\u00edvida."}, {"role": "user", "content": "pode me passar o contato?"}, {"role": "assistant", "content": "N\\u00e3o posso fornecer informa\\u00e7\\u00f5es de contato. Posso ajudar com mais alguma coisa?"}, {"role": "user", "content": "posso pagar mais que o valor normal?"}, {"role": "assistant", "content": "N\\u00e3o \\u00e9 poss\\u00edvel pagar um valor superior ao normal. Posso ajudar com mais alguma coisa?"}, {"role": "user", "content": "e se eu quiser dar uma gorjeta"}, {"role": "assistant", "content": "Sim, voc\\u00ea pode dar uma gorjeta se desejar."}, {"role": "user", "content": "quero dar 10 reais"}, {"role": "assistant", "content": "Voc\\u00ea pode dar a gorjeta de R$ 10,00 ao final do atendimento."}, {"role": "user", "content": "ao realizar um agendamento, posso deixar um coment\\u00e1rio?"}, {"role": "assistant", "content": "Sim, voc\\u00ea pode deixar um coment\\u00e1rio ao realizar o agendamento."}], "estado": {}, "ja_saudou": true}	f
24	554192706305	jessiely_moura	2026-06-18 01:39:18.313567	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "qual meu nome que est\\u00e1 registrado para voc\\u00ea?"}], "estado": {}, "ja_saudou": true, "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 35, "ticket_alvo": 27}	f
23	554192706305	jessiely_moura	2026-06-18 01:34:38.037673	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {}, "ja_saudou": true}	f
29	554199692193	jessiely_moura	2026-06-18 11:54:27.917021	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {}, "ja_saudou": true}	f
56	554199692193	jessiely_moura	2026-06-20 15:59:23.763044	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Realizar Agendamento"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Conhe\\u00e7o"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
80	554498625404	jessiely_moura	2026-06-25 17:19:40.040639	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}], "estado": {}}	f
69	554187450272	jessiely_moura	2026-06-22 20:48:40.594511	{"state": "AGUARDANDO_INTENCAO", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Jo\\u00e3o Pedro Pinto"}, {"role": "assistant", "content": "Prazer em te conhecer, Jo\\u00e3o Pedro! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "13 de dezembro de 0001"}], "estado": {}, "ja_saudou": true}	f
39	554199692193	jessiely_moura	2026-06-18 13:55:12.986089	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 48, "ticket_alvo": 5}	f
65	554199692193	jessiely_moura	2026-06-20 18:53:29.163378	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "conhe\\u00e7o"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Hoje as 17h"}, {"role": "assistant", "content": "O hor\\u00e1rio solicitado j\\u00e1 passou. Por favor, escolha outro hor\\u00e1rio."}], "estado": {"servico": ["Limpeza de Pele"], "data": "2026-06-20", "hora": null}}	f
76	554199692193	jessiely_moura	2026-06-23 20:33:58.594943	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}}	f
117	554199692193	moura_schema	2026-07-09 01:29:32.395309	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}}	f
25	554192706305	jessiely_moura	2026-06-18 02:05:20.553457	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "e forma de pagamento de troca, eu dou dinheiro e ele me da o servi\\u00e7o"}, {"role": "assistant", "content": "N\\u00e3o aceitamos pagamento por troca."}, {"role": "user", "content": "mas a minha troca \\u00e9 em dinheiro"}, {"role": "assistant", "content": "N\\u00e3o aceitamos pagamento por troca, mesmo que em dinheiro."}, {"role": "user", "content": "e dinheiro voc\\u00ea aceita?"}, {"role": "assistant", "content": "Sim, aceitamos pagamento em dinheiro."}, {"role": "user", "content": "mas quero trocar meu dinheiro pelo servi\\u00e7o"}, {"role": "assistant", "content": "N\\u00e3o aceitamos pagamento por troca, apenas em dinheiro."}, {"role": "user", "content": "mas eu quero dar o dinheiro"}, {"role": "assistant", "content": "Aceitamos pagamento em dinheiro pelos servi\\u00e7os."}, {"role": "user", "content": "oi"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "quero realizar agendamento"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Brendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2bBrendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2bBrendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2bBrendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2bBrendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2bBrendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2bBrendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2b"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "limpeza"}, {"role": "assistant", "content": "Qual data e hor\\u00e1rio voc\\u00ea gostaria para a limpeza de pele?"}, {"role": "user", "content": "amanha meio dia"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "pode ser"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {"servico": ["Limpeza de Pele"], "data": "2026-06-19", "hora": null}, "ja_saudou": true}	f
30	554199692193	jessiely_moura	2026-06-18 11:54:36.687826	{"state": "AGUARDANDO_INTENCAO"}	f
10	554199692193	jessiely_moura	2026-06-17 22:13:54.097588	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Opsao 2"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Massagem Model"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Massagem Model"]}, "ja_saudou": true}	f
2	554199692193	jessiely_moura	2026-06-16 22:32:03.135777	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem Relaxante"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Massagem Relaxante"]}, "ja_saudou": true}	f
4	554199692193	jessiely_moura	2026-06-17 16:05:03.209712	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Quero o 3"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a Cera"]}, "ja_saudou": true}	f
15	554199692193	jessiely_moura	2026-06-18 01:10:52.355991	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 25, "ticket_alvo": 20}	f
27	553591228614	jessiely_moura	2026-06-18 03:41:35.842661	{"state": "AGUARDANDO_INTENCAO"}	f
45	554199692193	jessiely_moura	2026-06-18 22:26:28.927667	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Quanto tenpo leva pra fazer uma massagem model"}, {"role": "assistant", "content": "A Massagem Model tem dura\\u00e7\\u00e3o interna de 30 minutos. Posso ajudar com mais alguma informa\\u00e7\\u00e3o?"}, {"role": "user", "content": "Oque \\u00e9 a massagem model"}, {"role": "assistant", "content": "A Massagem Model \\u00e9 uma t\\u00e9cnica que visa modelar o corpo, promovendo relaxamento e al\\u00edvio de tens\\u00f5es. Se precisar de mais informa\\u00e7\\u00f5es ou quiser agendar, estou \\u00e0 disposi\\u00e7\\u00e3o!"}, {"role": "user", "content": "Tenho lipedema posso fazer essa massagem"}, {"role": "assistant", "content": "\\u00c9 recomend\\u00e1vel consultar um profissional de sa\\u00fade antes de realizar a Massagem Model, especialmente em casos de lipedema. Posso ajudar com mais alguma informa\\u00e7\\u00e3o?"}, {"role": "user", "content": "Tem algum risco"}, {"role": "assistant", "content": "A Massagem Model pode n\\u00e3o ser indicada para pessoas com condi\\u00e7\\u00f5es espec\\u00edficas, como lipedema, devido ao risco de agravar a condi\\u00e7\\u00e3o. \\u00c9 importante consultar um profissional de sa\\u00fade para avaliar sua situa\\u00e7\\u00e3o individual."}, {"role": "user", "content": "Oque \\u00e9 cortar de cabelo"}, {"role": "assistant", "content": "Cortar cabelo \\u00e9 um servi\\u00e7o de est\\u00e9tica que envolve a remo\\u00e7\\u00e3o de cabelo para alterar o comprimento ou o estilo. Posso ajudar com mais alguma informa\\u00e7\\u00e3o?"}, {"role": "user", "content": "Quero agendar um corte de cabelo"}, {"role": "assistant", "content": "Na Jessiely Moura, n\\u00e3o oferecemos servi\\u00e7os de corte de cabelo. Voc\\u00ea gostaria de agendar um dos servi\\u00e7os dispon\\u00edveis?"}, {"role": "user", "content": "Sim"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Qual tem"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {}, "ja_saudou": true}	f
60	554199692193	jessiely_moura	2026-06-20 16:18:52.497097	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18/07"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Quero fazer um limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
62	554199692193	jessiely_moura	2026-06-20 16:29:28.280862	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "envia a lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "Sobrancelha"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Sobrancelha"]}}	f
31	554199692193	jessiely_moura	2026-06-18 11:58:43.526636	{"state": "AGUARDANDO_INTENCAO"}	f
33	554199692193	jessiely_moura	2026-06-18 12:55:35.038354	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 44, "ticket_alvo": 2}	f
20	554192706305	jessiely_moura	2026-06-18 01:26:29.781572	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "depila\\u00e7\\u00e3o de pele"}, {"role": "assistant", "content": "Qual a data e hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a Cera"]}, "ja_saudou": true}	f
22	554192706305	jessiely_moura	2026-06-18 01:33:55.085556	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 32, "ticket_alvo": 25}	f
28	553591228614	jessiely_moura	2026-06-18 06:08:11.879518	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR", "historico": [{"role": "user", "content": "Bao, quero"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Gustavo"}, {"role": "assistant", "content": "Gustavo, quais servi\\u00e7os voc\\u00ea gostaria de escolher? Aqui est\\u00e3o os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)"}, {"role": "user", "content": "Todos"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para os agendamentos?"}, {"role": "user", "content": "Meio do ano que vem, num feriado"}, {"role": "assistant", "content": "Por favor, escolha uma data v\\u00e1lida a partir de hoje."}, {"role": "user", "content": "38 de maio"}, {"role": "assistant", "content": "Por favor, escolha uma data v\\u00e1lida a partir de hoje."}], "estado": {"servico": ["Massagem Relaxante", "Massagem Model", "Depila\\u00e7\\u00e3o a Cera", "Ventosaterapia", "Limpeza de Pele"]}, "ja_saudou": true}	f
26	554192706305	jessiely_moura	2026-06-18 02:07:39.927553	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Brendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca\\ud83e\\udd2b"}, {"role": "assistant", "content": "Antes de continuarmos, preciso do seu nome para o registro. Como posso te chamar?"}, {"role": "user", "content": "Brendinhofarmadordeaura67sixsevenmonoakali1v9top10brescutaecalaboca"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "limpeza"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
40	554187450272	jessiely_moura	2026-06-18 14:54:49.901139	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR", "historico": [{"role": "user", "content": "Com certeza, quais lojas est\\u00e3o abertas"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Preciso agendar um corte de cabelo"}, {"role": "assistant", "content": "Antes de continuarmos, preciso do seu nome para o registro. Como posso te chamar?"}, {"role": "user", "content": "Joao"}, {"role": "assistant", "content": "Quais servi\\u00e7os voc\\u00ea gostaria de agendar na Jessiely Moura? Aqui est\\u00e3o as op\\u00e7\\u00f5es dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)"}, {"role": "user", "content": "Um servi\\u00e7o de cada"}, {"role": "assistant", "content": "Qual data e hor\\u00e1rio voc\\u00ea gostaria para o agendamento?"}, {"role": "user", "content": "quanto tempo cada atendimento dura?"}, {"role": "assistant", "content": "Aqui est\\u00e3o as dura\\u00e7\\u00f5es de cada servi\\u00e7o:\\n\\n\\u2022 Massagem Relaxante: 30 min\\n\\u2022 Massagem Model: 30 min\\n\\u2022 Depila\\u00e7\\u00e3o a Cera: 20 min\\n\\u2022 Ventosaterapia: 60 min\\n\\u2022 Limpeza de Pele: 30 min\\n\\nSe precisar de mais informa\\u00e7\\u00f5es ou quiser agendar, \\u00e9 s\\u00f3 avisar!"}], "estado": {"servico": ["Massagem Relaxante", "Massagem Model", "Depila\\u00e7\\u00e3o a Cera", "Ventosaterapia", "Limpeza de Pele"]}, "ja_saudou": true}	f
46	554498851300	jessiely_moura	2026-06-18 23:16:09.431837	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Sandra"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\n\\nQual servi\\u00e7o voc\\u00ea gostaria de escolher?"}, {"role": "user", "content": "Massagem e depila\\u00e7\\u00e3o"}, {"role": "assistant", "content": "Qual tipo de massagem voc\\u00ea deseja? Temos as op\\u00e7\\u00f5es: Massagem Relaxante e Massagem Model."}, {"role": "user", "content": "Relaxante"}, {"role": "assistant", "content": "Qual a data e hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Amanha"}, {"role": "assistant", "content": "Qual hor\\u00e1rio voc\\u00ea gostaria para o agendamento?"}], "estado": {"servico": ["Massagem Relaxante"], "data": "2026-06-19"}, "ja_saudou": true}	f
100	554199692193	moura_schema	2026-07-06 01:23:43.494279	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
61	554199692193	jessiely_moura	2026-06-20 16:24:51.253404	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual a sua data de nascimento?"}, {"role": "user", "content": "18 07"}, {"role": "assistant", "content": "Qual o ano da sua data de nascimento?"}], "estado": {}}	f
66	554199692193	jessiely_moura	2026-06-20 18:54:09.639466	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual \\u00e9 a sua data de nascimento?"}], "estado": {}}	f
89	554491171444	jessiely_moura	2026-07-01 19:36:48.603145	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Conhe\\u00e7o sim"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o laser"}, {"role": "assistant", "content": "Qual dos servi\\u00e7os de depila\\u00e7\\u00e3o a laser voc\\u00ea deseja? \\n\\u2022 Depila\\u00e7\\u00e3o a laser virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "Axilas"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Dia 04/07"}, {"role": "assistant", "content": "Qual hor\\u00e1rio voc\\u00ea gostaria?"}, {"role": "user", "content": "No per\\u00edodo da tarde"}, {"role": "assistant", "content": "Qual hor\\u00e1rio da tarde voc\\u00ea gostaria?"}, {"role": "user", "content": "14:30h"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a laser axilas"], "data": null, "hora": null}}	f
32	554199692193	jessiely_moura	2026-06-18 12:54:03.863694	{"state": "LLM_CONVERSATION", "intencao": "INTENT_CONSULTAR", "historico": [{"role": "user", "content": "Sim"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Agendar"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar? Aqui est\\u00e3o as op\\u00e7\\u00f5es dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)"}, {"role": "user", "content": "Limpeza"}, {"role": "assistant", "content": "Qual tipo de limpeza voc\\u00ea deseja? Limpeza de Pele."}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para a Limpeza de Pele?"}, {"role": "user", "content": "Amanh\\u00e3 08h"}, {"role": "assistant", "content": "Como posso te ajudar?"}], "estado": {"servico": ["Limpeza de Pele"], "data": "2026-06-19", "hora": null}, "ja_saudou": true}	f
41	554199692193	jessiely_moura	2026-06-18 16:23:30.86433	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Os servi\\u00e7os dispon\\u00edveis s\\u00e3o:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Depila\\u00e7\\u00e3o a Cera (R$ 45,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 P\\u00f3s operat\\u00f3rio (R$ 85,00)\\nQual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "2"}, {"role": "assistant", "content": "Qual data e hor\\u00e1rio voc\\u00ea gostaria para o agendamento?"}], "estado": {"servico": ["Massagem Model"]}, "ja_saudou": true}	f
70	554199692193	jessiely_moura	2026-06-23 01:12:32.346103	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Que horas s\\u00e3o nesse exato momento?"}, {"role": "assistant", "content": "A hora atual \\u00e9 22:12."}], "estado": {}}	f
74	554199692193	jessiely_moura	2026-06-23 03:23:34.485225	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Bom dia! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
77	554199692193	jessiely_moura	2026-06-25 16:51:35.026533	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Quero limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}}	f
47	554498851300	jessiely_moura	2026-06-18 23:41:22.268743	{"state": "AGUARDANDO_NOVA_DATA_HORA", "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 71, "ticket_alvo": 12}	f
50	554199692193	jessiely_moura	2026-06-20 15:04:19.004366	{"state": "LLM_CONVERSATION", "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento. Pode me listar quais servi\\u00e7os voc\\u00eas t\\u00eam dispon\\u00edveis?"}, {"role": "assistant", "content": "Para iniciarmos, qual \\u00e9 o seu nome?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Agendar"}, {"role": "assistant", "content": "Matheus, aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "1 op\\u00e7\\u00e3o"}, {"role": "assistant", "content": "Como posso te ajudar?"}, {"role": "user", "content": "Agendar 1 limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}, "ja_saudou": true}	f
82	554199692193	jessiely_moura	2026-06-25 21:24:36.68775	{"state": "AGUARDANDO_POS_CONSULTA", "ja_saudou": true, "intencao": "INTENT_CONSULTAR"}	f
84	554199692193	jessiely_moura	2026-06-28 22:36:01.763977	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Envie a lista"}, {"role": "assistant", "content": "\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Sobrancelha"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Sobrancelha"]}}	f
67	554199692193	jessiely_moura	2026-06-20 19:02:26.138226	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "limpeza de pele dia 26 as 16h"}, {"role": "assistant", "content": "Infelizmente, n\\u00e3o podemos agendar para o dia 26, pois temos um bloqueio das 12:00 \\u00e0s 18:00. Voc\\u00ea pode escolher outro hor\\u00e1rio?"}, {"role": "user", "content": "quero segunda-feira as 12h45"}, {"role": "assistant", "content": "Segunda-feira est\\u00e1 fechado. Por favor, escolha outro dia ou hor\\u00e1rio."}, {"role": "user", "content": "quero ter\\u00e7a-feira as 12h45"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "n\\u00e3o"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "limpeza de pele"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {"servico": ["Limpeza de Pele"], "data": "2026-06-23", "hora": null}}	f
87	554498119082	jessiely_moura	2026-07-01 18:02:06.7045	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Eloana Cavalcante"}, {"role": "assistant", "content": "Prazer em te conhecer, Eloana! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "02/06/2003"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Conhe\\u00e7o"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Sim"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem"}, {"role": "assistant", "content": "Qual tipo de massagem voc\\u00ea deseja? Temos as seguintes op\\u00e7\\u00f5es:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)"}, {"role": "user", "content": "Model"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio que voc\\u00ea gostaria para o agendamento?"}], "estado": {"servico": ["Massagem Model"]}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
90	554199692193	moura_schema	2026-07-02 00:45:05.568151	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa noite! \\ud83d\\ude0a Sou a Lau, assistente da *Loja Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis na Loja Moura:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
95	554199692193	moura_schema	2026-07-04 19:50:18.293779	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Listrq"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Oque o corte de barba"}, {"role": "assistant", "content": "O corte de barba \\u00e9 um servi\\u00e7o que inclui o aparo e o modelado da barba, deixando-a com um visual mais alinhado e bem cuidado. Voc\\u00ea gostaria de agendar esse servi\\u00e7o?"}, {"role": "user", "content": "Quero agendar um corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
91	554198317356	moura_schema	2026-07-02 00:51:41.178321	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa noite! \\ud83d\\ude0a Sou a Lau, assistente da *Loja Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Lucas Gabriel Ribeiro Ferracioli"}, {"role": "assistant", "content": "Prazer em te conhecer, Lucas! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "09/02/2001"}, {"role": "user", "content": "Sim"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Envie a lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}, "ja_saudou": true, "intencao": "INTENT_CONSULTAR"}	f
85	554199692193	jessiely_moura	2026-06-29 15:36:03.08481	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Oque uma massagem model"}, {"role": "assistant", "content": "A Massagem Modeladora \\u00e9 uma t\\u00e9cnica que visa modelar o corpo, reduzindo medidas e melhorando a apar\\u00eancia da pele. Ela utiliza manobras espec\\u00edficas para estimular a circula\\u00e7\\u00e3o e a drenagem linf\\u00e1tica."}, {"role": "user", "content": "Quero realizar um agendamento da massagem model"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Depois amanha meio dia"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {"servico": ["Massagem Model"], "data": "2026-07-01", "hora": null}}	f
68	554199692193	jessiely_moura	2026-06-21 00:17:23.369218	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "N\\u00e3o sei"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Massagem terap\\u00eautica"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Amanh\\u00e3 as 08"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Qual \\u00e9 o pr\\u00f3ximo dia dispon\\u00edvel"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Qual outro dia"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Que dias da semana fica aberto"}, {"role": "assistant", "content": "A Jessiely Moura est\\u00e1 aberta de ter\\u00e7a a s\\u00e1bado, das 08:00 \\u00e0s 18:00."}], "estado": {"servico": ["Massagem terap\\u00eautica"], "data": null, "hora": null}}	f
101	554199692193	moura_schema	2026-07-06 01:37:31.57281	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
96	554199692193	moura_schema	2026-07-06 00:00:44.67352	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Quero ver a lista"}, {"role": "assistant", "content": "\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Teste j"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado?"}], "estado": {"servico": ["Teste j"]}}	f
97	554199905084	moura_schema	2026-07-06 00:07:26.828591	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa noite! \\ud83d\\ude0a Sou a Lau, assistente da *Loja Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Bruno Lima"}, {"role": "assistant", "content": "Prazer em te conhecer, Bruno Lima! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "13/10/2002"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
92	554199692193	moura_schema	2026-07-02 18:11:33.895865	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Sim"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "O primeiro"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
78	554199692193	jessiely_moura	2026-06-25 17:05:49.836344	{"state": "AGUARDANDO_NOVA_DATA_HORA", "ja_saudou": true, "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 94, "ticket_alvo": 4}	f
103	554199692193	moura_schema	2026-07-06 01:53:00.484089	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
105	554199692193	jessiely_moura	2026-07-06 13:28:57.369452	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser axilas"}, {"role": "assistant", "content": "Certo! Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser axilas"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a laser axilas"]}}	f
83	554199692193	jessiely_moura	2026-06-25 21:25:48.929451	{"state": "AGUARDANDO_NOVA_DATA_HORA", "ja_saudou": true, "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "reagendamento", "agendamento_id_alvo": 98, "ticket_alvo": 7}	f
108	554199692193	jessiely_moura	2026-07-06 14:05:35.343408	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Conhe\\u00e7o"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}}	f
75	554199692193	jessiely_moura	2026-06-23 20:12:55.871748	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "N\\u00e3o conhe\\u00e7o"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Sobrancelha"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Sobrancelha"]}}	f
81	554199692193	jessiely_moura	2026-06-25 21:07:35.657111	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "A"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Enbia"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Envie"}, {"role": "assistant", "content": "Aqui est\\u00e3o nossos servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser rosto"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a laser rosto"]}}	f
88	554491171444	jessiely_moura	2026-07-01 19:05:38.097939	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Josiane De Oliveira Cardoso Piovesani"}, {"role": "assistant", "content": "Prazer em te conhecer, Josiane! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "13/06/1979"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Envie a lista por favor"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Massagem model"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Quinta feira"}, {"role": "assistant", "content": "Qual hor\\u00e1rio voc\\u00ea gostaria na quinta-feira?"}], "estado": {"servico": ["Massagem Model"], "data": "2026-07-02"}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
86	554199692193	jessiely_moura	2026-06-30 17:55:21.570959	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Boa tarde! \\ud83d\\ude0a Sou a Lau, assistente da *Jessiely Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Matheus Moura"}, {"role": "assistant", "content": "Prazer em te conhecer, Matheus! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "18/07/2000"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
99	554199692193	moura_schema	2026-07-06 01:14:37.570668	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Manda a lista"}, {"role": "assistant", "content": "\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
102	554199692193	moura_schema	2026-07-06 01:44:08.364192	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejado para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
93	554199692193	moura_schema	2026-07-02 18:12:58.679988	{"state": "AGUARDANDO_MOTIVO_CANCELAMENTO", "ja_saudou": true, "intencao": "INTENT_CONSULTAR", "tipo_solicitacao": "cancelamento", "agendamento_id_alvo": 111, "ticket_alvo": 7}	f
109	554199692193	moura_schema	2026-07-06 14:06:58.533333	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
106	554199692193	jessiely_moura	2026-07-06 13:39:08.867094	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Envia a lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser  meia perna"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a laser meia perna"]}}	f
104	554199692193	jessiely_moura	2026-07-06 13:11:17.04806	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser axila"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o axila"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Envie a lista"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Lista"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "N\\u00e3o conhe\\u00e7o"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "N\\u00e3o conhe\\u00e7o"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Massagem Relaxante (R$ 100,00)\\n\\u2022 Massagem Model (R$ 90,00)\\n\\u2022 Ventosaterapia (R$ 100,00)\\n\\u2022 Limpeza de Pele (R$ 160,00)\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Drenagem linf\\u00e1tica (R$ 80,00)\\n\\u2022 P\\u00f3s cirurgia (R$ 120,00)\\n\\u2022 Massagem terap\\u00eautica (R$ 150,00)\\n\\u2022 Sobrancelha (R$ 40,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)\\n\\u2022 Bloqueio 360 min (R$ 0,00)"}, {"role": "user", "content": "Massagem relaxante"}, {"role": "assistant", "content": "Certo! Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Massagem relaxante"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Massagem Relaxante"]}}	f
107	554199692193	jessiely_moura	2026-07-06 13:44:22.17301	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Conhe\\u00e7o"}, {"role": "assistant", "content": "Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o a laser axilas"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Depila\\u00e7\\u00e3o a laser axilas"]}}	f
110	554199692193	moura_schema	2026-07-06 18:29:55.057139	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Quero a lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Quero agendar todos"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}, {"role": "user", "content": "Hoje 15h"}, {"role": "assistant", "content": "Certo! Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {"servico": ["Corte de cabelo", "Corte Barba", "Teste j"], "data": "2026-07-06", "hora": null}}	f
111	554199692193	moura_schema	2026-07-07 01:12:35.401309	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Qual a sua data de nascimento?"}, {"role": "user", "content": "18 07 2000"}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Certo! Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}, {"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Certo! Qual servi\\u00e7o voc\\u00ea gostaria de agendar?"}], "estado": {}}	f
113	554199692193	jessiely_moura	2026-07-07 02:08:37.690013	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Depila\\u00e7\\u00e3o"}, {"role": "assistant", "content": "Qual tipo de depila\\u00e7\\u00e3o voc\\u00ea deseja? Temos as seguintes op\\u00e7\\u00f5es:\\n\\u2022 Virilha completa (R$ 65,00)\\n\\u2022 Axilas (R$ 25,00)\\n\\u2022 Perna inteira (R$ 50,00)\\n\\u2022 Meia perna (R$ 35,00)\\n\\u2022 Bu\\u00e7o nariz (R$ 30,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser  virilha completa (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser axilas (R$ 80,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser perna inteira (R$ 150,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser meia perna (R$ 100,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser bu\\u00e7o (R$ 60,00)\\n\\u2022 Depila\\u00e7\\u00e3o a laser rosto (R$ 100,00)"}, {"role": "user", "content": "Limpeza de pele"}, {"role": "assistant", "content": "Qual a sua data e hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Limpeza de Pele"]}}	f
114	554199692193	moura_schema	2026-07-07 19:29:45.185638	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Mandar a lista"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "Corte de cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
118	554199692193	moura_schema	2026-07-09 01:34:37.341474	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}], "estado": {}}	f
119	554199692193	moura_schema	2026-07-09 02:37:43.85955	{"state": "BOSS_CONVERSATION", "historico": [{"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Desculpe chefe, tive um problema ao analisar."}, {"role": "user", "content": "Cancelar"}, {"role": "assistant", "content": "Entendi, Matheus Moura. Se precisar de mais alguma coisa, estou \\u00e0 disposi\\u00e7\\u00e3o!"}, {"role": "user", "content": "Ol\\u00e1"}, {"role": "assistant", "content": "Desculpe chefe, tive um problema ao analisar."}, {"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Ol\\u00e1 Matheus Moura! Boa noite. Estou aqui para ajudar. Deseja realizar algum registro na agenda ou adicionar um cliente sem precisar abrir o aplicativo?"}, {"role": "user", "content": "Eu quero fazer um agendamento pro Lucas, um corte de cabelo, para o Piton um corte de barba e para o Bruno um teste."}, {"role": "assistant", "content": "Encontrei estas op\\u00e7\\u00f5es, qual deseja agendar para Lucas? \\n\\u2022 Lucas Almeida\\n\\u2022 Lucas Silva\\n\\nE para Piton e Bruno, posso prosseguir com o agendamento?"}, {"role": "user", "content": "Cancelar"}, {"role": "assistant", "content": "Entendi, Matheus Moura. Se precisar de mais alguma coisa, estou \\u00e0 disposi\\u00e7\\u00e3o!"}, {"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Ol\\u00e1 Matheus Moura! Boa noite. Estou aqui para ajudar. Deseja realizar algum registro na agenda ou adicionar um cliente sem precisar abrir o aplicativo?"}, {"role": "user", "content": "Agendar corte de cabelo para o Bruno amanh\\u00e3 15h"}, {"role": "assistant", "content": "Resumo dos agendamentos:\\n\\u2705 Bruno Lima agendado para 2026-07-09 \\u00e0s 15:00."}]}	f
120	554199692193	moura_schema	2026-07-09 16:17:21.150681	{"state": "BOSS_CONVERSATION", "historico": [{"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Ol\\u00e1 Matheus Moura! Boa tarde. Estou aqui para ajudar. Deseja realizar algum registro na agenda ou adicionar um cliente sem precisar abrir o aplicativo?"}, {"role": "user", "content": "Eu quero agendar um hor\\u00e1rio para o Jo\\u00e3o Ger\\u00f3ski, amanh\\u00e3 \\u00e0s tr\\u00eas horas, um corte de cabelo."}, {"role": "system", "content": "SYSTEM: O cliente 'Jo\\u00e3o Ger\\u00f3ski' n\\u00e3o foi encontrado. Avise-o e pe\\u00e7a para ele enviar o contato (cart\\u00e3o do WhatsApp) do Jo\\u00e3o Ger\\u00f3ski para realizarmos o cadastro imediatamente."}, {"role": "assistant", "content": "N\\u00e3o encontrei o cliente 'Jo\\u00e3o Ger\\u00f3ski'. Poderia, por favor, enviar o contato dele via WhatsApp (anexo de cart\\u00e3o de contato) para que possamos realizar o cadastro imediatamente?"}, {"role": "user", "content": "Jo\\u00e3o"}, {"role": "assistant", "content": "Encontrei estas op\\u00e7\\u00f5es, qual deseja agendar?\\n\\u2022 Jo\\u00e3o Santos\\n\\u2022 Jo\\u00e3o Silva"}]}	f
122	554192388448	moura_schema	2026-07-11 13:04:46.18394	{"state": "LLM_CONVERSATION", "historico": [{"role": "assistant", "content": "Bom dia! \\ud83d\\ude0a Sou a Lau, assistente da *Loja Moura*.\\n\\nPercebi que voc\\u00ea ainda n\\u00e3o tem um cadastro completo com a gente. Para come\\u00e7armos, qual \\u00e9 o seu nome completo?"}, {"role": "user", "content": "Vinicius Vaz"}, {"role": "assistant", "content": "Prazer em te conhecer, Vinicius! \\ud83e\\udd70 Para deixarmos seu cadastro prontinho aqui comigo, qual a sua data de nascimento?"}, {"role": "user", "content": "30/07/1995"}, {"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "me envie a lista por favor"}, {"role": "assistant", "content": "Aqui est\\u00e3o os servi\\u00e7os dispon\\u00edveis:\\n\\u2022 Corte de cabelo (R$ 80,00)\\n\\u2022 Corte Barba (R$ 40,00)\\n\\u2022 Teste j (R$ 50,00)"}, {"role": "user", "content": "corte barba"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o agendamento?"}], "estado": {"servico": ["Corte Barba"]}, "ja_saudou": true, "intencao": "INTENT_AGENDAR"}	f
121	554199692193	moura_schema	2026-07-09 19:42:15.247136	{"state": "BOSS_CONVERSATION", "historico": [{"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Ol\\u00e1 Matheus Moura! Boa tarde. Estou aqui para ajudar. Deseja realizar algum registro na agenda ou adicionar um cliente sem precisar abrir o aplicativo?"}, {"role": "user", "content": "Encerrar"}, {"role": "assistant", "content": "Comando recebido, mas nenhum agendamento foi processado e nenhuma a\\u00e7\\u00e3o solicitada."}, {"role": "user", "content": "Encerrar conversa"}, {"role": "assistant", "content": "Entendido, Matheus Moura. Se precisar de algo mais, estarei aqui para ajudar. Tenha um \\u00f3timo dia!"}]}	f
124	554199692193	moura_schema	2026-07-12 21:59:10.795408	{"state": "LLM_CONVERSATION", "ja_saudou": true, "intencao": "INTENT_AGENDAR", "historico": [{"role": "user", "content": "Quero fazer um agendamento."}, {"role": "assistant", "content": "Voc\\u00ea j\\u00e1 conhece nossos servi\\u00e7os ou prefere que eu envie a lista?"}, {"role": "user", "content": "Quero cortar cabelo"}, {"role": "assistant", "content": "Qual a data e o hor\\u00e1rio desejados para o corte de cabelo?"}], "estado": {"servico": ["Corte de cabelo"]}}	f
\.


--
-- Data for Name: chat_message; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_message (id, merchant_id, client_phone, message_content, sender, "timestamp", read) FROM stdin;
1	17	554199692193	Cancelar	client	2026-07-07 00:10:34.450513+00	f
2	17	554199692193	Oi	client	2026-07-07 00:17:41.143948+00	f
3	17	554199692193	Oi	client	2026-07-07 00:20:42.302903+00	f
4	17	554199692193	Quero falar com um atendente	client	2026-07-07 00:37:21.150234+00	f
5	17	554199692193	oi	client	2026-07-07 00:47:23.515743+00	f
6	17	554199692193	Oi	client	2026-07-07 01:08:31.919435+00	f
7	1	554199692193	olá	merchant	2026-07-07 01:28:01.021536+00	f
8	17	554199692193	olá	merchant	2026-07-07 01:30:51.130358+00	f
9	17	554199692193	Como posso ajudar?	merchant	2026-07-07 01:31:04.298687+00	f
10	17	554199692193	Oi Matheus tudo bem?	client	2026-07-07 01:31:21.256566+00	f
11	17	554199692193	Como posso ajudar?	merchant	2026-07-07 01:34:24.048085+00	f
12	17	554199692193	Oi matheus	client	2026-07-07 01:34:32.760658+00	f
13	17	554199692193	oi	merchant	2026-07-07 01:35:39.231798+00	f
14	17	554199692193	Oi	client	2026-07-07 01:35:44.929039+00	f
15	17	554199692193	oi	merchant	2026-07-07 01:38:34.634847+00	f
16	17	554199692193	Oi	client	2026-07-07 01:38:39.844213+00	f
17	17	554199692193	oiiii	merchant	2026-07-07 01:38:50.386355+00	f
18	17	554199692193	Oiii	client	2026-07-07 01:38:55.72599+00	f
19	17	554199692193	oi	merchant	2026-07-07 01:41:01.951594+00	f
20	17	554199692193	Oie	client	2026-07-07 01:41:07.862607+00	f
21	17	554199692193	Oie	client	2026-07-07 01:41:43.327998+00	f
22	17	554199692193	Ola	client	2026-07-07 01:50:43.346507+00	f
23	17	554199692193	olá	merchant	2026-07-07 01:52:23.643165+00	f
24	17	554199692193	Oiee	client	2026-07-07 01:52:30.843034+00	f
25	17	554199692193	Ola	merchant	2026-07-07 01:53:01.97331+00	f
26	17	554199692193	oie	client	2026-07-07 01:53:15.082136+00	f
27	17	554199692193	ola	merchant	2026-07-07 02:01:32.319947+00	f
28	17	554199692193	Oiiee	client	2026-07-07 02:01:40.039781+00	f
29	17	554199692193	Poi	merchant	2026-07-07 02:05:48.2763+00	f
30	17	554199692193	Oi	client	2026-07-07 02:05:53.652401+00	f
31	17	554199692193	teste	merchant	2026-07-07 02:07:06.585105+00	f
32	17	554199692193	Teste	client	2026-07-07 02:07:11.462976+00	f
\.


--
-- Data for Name: client_chat_state; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_chat_state (id, merchant_id, client_phone, client_name, is_human_service, human_service_started_at) FROM stdin;
1	17	554199692193	Matheus Moura	f	2026-07-07 02:07:11.462684+00
\.


--
-- Data for Name: merchant; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.merchant (id, nome_loja, codigo_loja, telefone_contato, nome_do_schema, area_atuacao, email, senha_hash, push_token, permitir_sobreposicao, horario_abertura, horario_fechamento, is_admin, numero_whatsapp, tem_dashboard, loja_pai_id, pode_editar_servicos, nome_usuario, dias_fechados, horario_almoco_inicio, horario_almoco_fim, politica_aceita, foto_perfil, meta_access_token, meta_phone_id, notificacoes_push_enabled, notificacoes_novos, notificacoes_cancelamentos, notificacoes_lembretes, numero_chefe, nome_chefe) FROM stdin;
24	Jessiely	jessiely_moura_user_jessiely	\N	sub_jessiely_moura_user_jessiely	\N	jessiely	$2b$12$YqtxQdSj8B7rjVC2gjl4C.9Fh1Wdm7RPqs54AFI/iWpzjr2pWUArm	ExponentPushToken[QuvxlvFuiidFWgXBTKnliG]	f	08:00	18:00	f	\N	t	1	t	\N	\N	\N	\N	f	/uploads/24_b49d8b89bb724a52b060657230691cd4.jpg	\N	\N	t	t	t	t	\N	\N
1	Jessiely Moura	jessiely_moura	\N	jessiely_moura	\N	admin	$2b$12$xCrPQDKHRnzykk2ShIh3/e.9kjDm0VxGAOrjAXh2v/1XrQXCAu0se	ExponentPushToken[QuvxlvFuiidFWgXBTKnliG]	f	08:00	18:00	t	1238251112701602	t	\N	t	Matheus Moura	0	12:00	13:00	t	/uploads/1_c811a06067d54fdbab9924a2dd79e2f8.jpg	EAAYTjZC5uRkUBRZBUvNpHZAsWqQZBY7irAZCH2B3AZAChR4R4ZBOZBaUZCclcburGl1kvHmf7tZBj9CgIh1ZBgU7JNrlo5kctJZBiEEgEhvh9ZBNhKDowMRX1oC4VywWOQ7XvOAEXRAjZBRbyCLArKyLimuFLFcSr9ZAEF7OubfSqQBO9E5lwkFbL4UOy2w1dxg7afeO8IfdwZDZD	1238251112701602	t	t	t	t	\N	\N
17	Loja Moura	MOURA	\N	moura_schema	Beleza	\N	\N	\N	f	08:00	18:00	f	554188894240	t	\N	t	Seu Nome Aqui	\N	\N	\N	t	\N	EAAdgaJYwxQ0BR7yUZA5D8qGybZCFPVQ9eRY6ODdsNn1fSUpdWdBKTZBUS0kC2NqkZCFrSaUDHQxeNsi5gydbCO8qHmKdqdz1aIr4aX0tBKbJhHh40AkvfBwJXckQEpOJtFFsOZBGWKY3h1GL21Yd3RLMw0A6v9uhwZAVGg7l887Nfe3avAnkDMyFTSuDZBD1vbW4QZDZD	1136563242867085	t	t	t	t	\N	\N
28	Teste	MOURA_user_teste	\N	sub_MOURA_user_teste	Beleza	teste	$2b$12$IC20IlQaaLSmLH1moLt52.KzAuptkgnBzADSP7GsZaXoSFholwtSO	ExponentPushToken[QuvxlvFuiidFWgXBTKnliG]	f	08:00	18:00	f	\N	f	17	t	\N	\N	\N	\N	f	\N	\N	\N	t	t	t	t	\N	\N
30	Meu Pet Shop Modelo	pet01	\N	petshop_demo	petshop	petshop@teste.com	$2b$12$3/VMyGLUTYMNJJU8xxMjx.IyX/IX8VeSUEkWq177E6rtvwOxPJc1K	\N	f	08:00	18:00	f	\N	f	\N	t	\N	\N	\N	\N	f	\N	\N	\N	t	t	t	t	\N	\N
\.


--
-- Data for Name: rascunhos_agendamento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rascunhos_agendamento (id, telefone_cliente, servico, data_agendamento, hora_agendamento, ultima_interacao) FROM stdin;
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, nome, telefone) FROM stdin;
\.


--
-- Data for Name: whatsapp_message_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.whatsapp_message_log (id, merchant_id, recipient, message_type, sent_at, cost_estimated) FROM stdin;
1	17	554199692193	service	2026-07-07 19:28:59.887559+00	0.15
2	17	554199692193	service	2026-07-07 19:29:11.403788+00	0
3	17	554199692193	service	2026-07-07 19:29:25.739774+00	0
4	17	554199692193	service	2026-07-07 19:29:35.049127+00	0
5	17	554199692193	service	2026-07-07 19:29:45.6219+00	0
6	1	554199692193	service	2026-07-08 17:21:39.296394+00	0.15
7	1	554199692193	service	2026-07-08 17:21:50.655888+00	0
8	1	554199692193	service	2026-07-08 17:22:07.299084+00	0
9	1	554498656852	service	2026-07-08 21:11:55.292364+00	0.15
10	17	554199692193	service	2026-07-09 01:25:01.098069+00	0.15
11	17	554199692193	service	2026-07-09 01:25:58.110595+00	0
12	17	554199692193	service	2026-07-09 01:29:34.716629+00	0
13	17	554199692193	service	2026-07-09 01:31:16.67397+00	0
14	17	554199692193	service	2026-07-09 01:32:35.988479+00	0
15	17	554199692193	service	2026-07-09 01:34:30.706598+00	0
16	17	554199692193	service	2026-07-09 01:34:39.529623+00	0
17	17	554199692193	service	2026-07-09 01:38:18.852266+00	0
18	17	554199692193	service	2026-07-09 01:38:39.242576+00	0
19	17	554199692193	service	2026-07-09 01:38:49.673392+00	0
20	17	554199692193	service	2026-07-09 02:35:06.38414+00	0
21	17	554199692193	service	2026-07-09 02:36:02.790382+00	0
22	17	554199692193	service	2026-07-09 02:36:10.242122+00	0
23	17	554199692193	service	2026-07-09 02:37:04.890619+00	0
24	17	554199692193	service	2026-07-09 02:37:15.937515+00	0
25	17	554199692193	service	2026-07-09 02:37:43.8572+00	0
26	17	554199692193	service	2026-07-09 16:15:41.34372+00	0
27	17	554199692193	service	2026-07-09 16:16:10.412566+00	0
28	17	554199692193	service	2026-07-09 16:16:19.98663+00	0
29	17	554199692193	service	2026-07-09 16:17:22.834646+00	0
30	17	554199692193	service	2026-07-09 19:41:52.483863+00	0
31	17	554199692193	service	2026-07-09 19:42:00.284096+00	0
32	17	554199692193	service	2026-07-09 19:42:17.344808+00	0
33	17	554192388448	service	2026-07-11 13:00:27.12337+00	0.15
34	17	554192388448	service	2026-07-11 13:02:52.945553+00	0
35	17	554192388448	service	2026-07-11 13:03:44.14717+00	0
36	17	554192388448	service	2026-07-11 13:04:03.776896+00	0
37	17	554192388448	service	2026-07-11 13:04:17.186033+00	0
38	17	554192388448	service	2026-07-11 13:04:29.11653+00	0
39	17	554192388448	service	2026-07-11 13:04:46.770008+00	0
40	17	554199692193	service	2026-07-11 13:24:32.252357+00	0.15
41	17	554199692193	service	2026-07-12 21:58:32.897561+00	0.15
42	17	554199692193	service	2026-07-12 21:58:43.688027+00	0
43	17	554199692193	service	2026-07-12 21:59:00.327118+00	0
44	17	554199692193	service	2026-07-12 21:59:11.409332+00	0
\.


--
-- Data for Name: appointments; Type: TABLE DATA; Schema: template_petshop; Owner: postgres
--

COPY template_petshop.appointments (id, customer_id, service_id, data_agendamento, horario_agendamento, status, criado_em, origem, recurrence_id, valor_cobrado, is_paid_in_package, numero_ticket, reagendamento_hora, tipo_pendencia, reagendamento_data, motivo_cancelamento) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: template_petshop; Owner: postgres
--

COPY template_petshop.customers (id, nome, telefone_whatsapp, ultima_interacao, data_nascimento, origem, anotacoes) FROM stdin;
\.


--
-- Data for Name: services; Type: TABLE DATA; Schema: template_petshop; Owner: postgres
--

COPY template_petshop.services (id, nome, duracao_minutos, preco) FROM stdin;
29	Banho	60	50.00
30	Tosa	60	70.00
31	Banho e Tosa	120	100.00
32	Hidratação	30	40.00
33	Corte de Unhas	15	20.00
\.


--
-- Name: categorias_custo_id_seq; Type: SEQUENCE SET; Schema: jessiely_moura; Owner: postgres
--

SELECT pg_catalog.setval('jessiely_moura.categorias_custo_id_seq', 2, true);


--
-- Name: custos_id_seq; Type: SEQUENCE SET; Schema: jessiely_moura; Owner: postgres
--

SELECT pg_catalog.setval('jessiely_moura.custos_id_seq', 5, true);


--
-- Name: agendamentos_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.agendamentos_id_seq', 1, false);


--
-- Name: appointment_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.appointment_id_seq', 1, false);


--
-- Name: appointments_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.appointments_id_seq', 156, true);


--
-- Name: business_hours_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.business_hours_id_seq', 1, false);


--
-- Name: categorias_custo_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.categorias_custo_id_seq', 1, false);


--
-- Name: client_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.client_id_seq', 1, false);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.customers_id_seq', 96, true);


--
-- Name: custos_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.custos_id_seq', 1, false);


--
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: moura_schema; Owner: postgres
--

SELECT pg_catalog.setval('moura_schema.services_id_seq', 33, true);


--
-- Name: active_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.active_sessions_id_seq', 124, true);


--
-- Name: chat_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_message_id_seq', 32, true);


--
-- Name: client_chat_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_chat_state_id_seq', 1, true);


--
-- Name: merchant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.merchant_id_seq', 30, true);


--
-- Name: rascunhos_agendamento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rascunhos_agendamento_id_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, false);


--
-- Name: whatsapp_message_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.whatsapp_message_log_id_seq', 44, true);


--
-- Name: agendamentos agendamentos_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.agendamentos
    ADD CONSTRAINT agendamentos_pkey PRIMARY KEY (id);


--
-- Name: appointment appointment_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.appointment
    ADD CONSTRAINT appointment_pkey PRIMARY KEY (id);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: business_hours business_hours_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.business_hours
    ADD CONSTRAINT business_hours_pkey PRIMARY KEY (id);


--
-- Name: categorias_custo categorias_custo_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.categorias_custo
    ADD CONSTRAINT categorias_custo_pkey PRIMARY KEY (id);


--
-- Name: client client_numero_whatsapp_key; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.client
    ADD CONSTRAINT client_numero_whatsapp_key UNIQUE (numero_whatsapp);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: customers customers_telefone_whatsapp_key; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.customers
    ADD CONSTRAINT customers_telefone_whatsapp_key UNIQUE (telefone_whatsapp);


--
-- Name: custos custos_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.custos
    ADD CONSTRAINT custos_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: agendamentos agendamentos_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.agendamentos
    ADD CONSTRAINT agendamentos_pkey PRIMARY KEY (id);


--
-- Name: appointment appointment_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointment
    ADD CONSTRAINT appointment_pkey PRIMARY KEY (id);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: business_hours business_hours_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.business_hours
    ADD CONSTRAINT business_hours_pkey PRIMARY KEY (id);


--
-- Name: categorias_custo categorias_custo_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.categorias_custo
    ADD CONSTRAINT categorias_custo_pkey PRIMARY KEY (id);


--
-- Name: client client_numero_whatsapp_key; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.client
    ADD CONSTRAINT client_numero_whatsapp_key UNIQUE (numero_whatsapp);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: customers customers_telefone_whatsapp_key; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.customers
    ADD CONSTRAINT customers_telefone_whatsapp_key UNIQUE (telefone_whatsapp);


--
-- Name: custos custos_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.custos
    ADD CONSTRAINT custos_pkey PRIMARY KEY (id);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: petshop_demo; Owner: postgres
--

ALTER TABLE ONLY petshop_demo.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: petshop_demo; Owner: postgres
--

ALTER TABLE ONLY petshop_demo.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: customers customers_telefone_whatsapp_key; Type: CONSTRAINT; Schema: petshop_demo; Owner: postgres
--

ALTER TABLE ONLY petshop_demo.customers
    ADD CONSTRAINT customers_telefone_whatsapp_key UNIQUE (telefone_whatsapp);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: petshop_demo; Owner: postgres
--

ALTER TABLE ONLY petshop_demo.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: active_sessions active_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_sessions
    ADD CONSTRAINT active_sessions_pkey PRIMARY KEY (id);


--
-- Name: chat_message chat_message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_pkey PRIMARY KEY (id);


--
-- Name: client_chat_state client_chat_state_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_chat_state
    ADD CONSTRAINT client_chat_state_pkey PRIMARY KEY (id);


--
-- Name: merchant merchant_codigo_loja_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_codigo_loja_key UNIQUE (codigo_loja);


--
-- Name: merchant merchant_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_email_key UNIQUE (email);


--
-- Name: merchant merchant_nome_do_schema_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_nome_do_schema_key UNIQUE (nome_do_schema);


--
-- Name: merchant merchant_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_pkey PRIMARY KEY (id);


--
-- Name: rascunhos_agendamento rascunhos_agendamento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rascunhos_agendamento
    ADD CONSTRAINT rascunhos_agendamento_pkey PRIMARY KEY (id);


--
-- Name: rascunhos_agendamento rascunhos_agendamento_telefone_cliente_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rascunhos_agendamento
    ADD CONSTRAINT rascunhos_agendamento_telefone_cliente_key UNIQUE (telefone_cliente);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: whatsapp_message_log whatsapp_message_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.whatsapp_message_log
    ADD CONSTRAINT whatsapp_message_log_pkey PRIMARY KEY (id);


--
-- Name: appointments appointments_pkey; Type: CONSTRAINT; Schema: template_petshop; Owner: postgres
--

ALTER TABLE ONLY template_petshop.appointments
    ADD CONSTRAINT appointments_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: template_petshop; Owner: postgres
--

ALTER TABLE ONLY template_petshop.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: customers customers_telefone_whatsapp_key; Type: CONSTRAINT; Schema: template_petshop; Owner: postgres
--

ALTER TABLE ONLY template_petshop.customers
    ADD CONSTRAINT customers_telefone_whatsapp_key UNIQUE (telefone_whatsapp);


--
-- Name: services services_pkey; Type: CONSTRAINT; Schema: template_petshop; Owner: postgres
--

ALTER TABLE ONLY template_petshop.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- Name: ix_chat_message_client_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_message_client_phone ON public.chat_message USING btree (client_phone);


--
-- Name: ix_chat_message_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_message_id ON public.chat_message USING btree (id);


--
-- Name: ix_chat_message_merchant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_message_merchant_id ON public.chat_message USING btree (merchant_id);


--
-- Name: ix_client_chat_state_client_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_client_chat_state_client_phone ON public.client_chat_state USING btree (client_phone);


--
-- Name: ix_client_chat_state_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_client_chat_state_id ON public.client_chat_state USING btree (id);


--
-- Name: ix_client_chat_state_merchant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_client_chat_state_merchant_id ON public.client_chat_state USING btree (merchant_id);


--
-- Name: ix_usuarios_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_usuarios_id ON public.usuarios USING btree (id);


--
-- Name: ix_usuarios_nome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_usuarios_nome ON public.usuarios USING btree (nome);


--
-- Name: ix_usuarios_telefone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_usuarios_telefone ON public.usuarios USING btree (telefone);


--
-- Name: ix_whatsapp_message_log_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_whatsapp_message_log_id ON public.whatsapp_message_log USING btree (id);


--
-- Name: ix_whatsapp_message_log_merchant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_whatsapp_message_log_merchant_id ON public.whatsapp_message_log USING btree (merchant_id);


--
-- Name: custos custos_categoria_id_fkey; Type: FK CONSTRAINT; Schema: jessiely_moura; Owner: postgres
--

ALTER TABLE ONLY jessiely_moura.custos
    ADD CONSTRAINT custos_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES jessiely_moura.categorias_custo(id) ON DELETE CASCADE;


--
-- Name: appointment appointment_id_cliente_fkey; Type: FK CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointment
    ADD CONSTRAINT appointment_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES moura_schema.client(id) ON DELETE CASCADE;


--
-- Name: appointments appointments_customer_id_fkey; Type: FK CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointments
    ADD CONSTRAINT appointments_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES moura_schema.customers(id);


--
-- Name: appointments appointments_service_id_fkey; Type: FK CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.appointments
    ADD CONSTRAINT appointments_service_id_fkey FOREIGN KEY (service_id) REFERENCES moura_schema.services(id);


--
-- Name: custos custos_categoria_id_fkey; Type: FK CONSTRAINT; Schema: moura_schema; Owner: postgres
--

ALTER TABLE ONLY moura_schema.custos
    ADD CONSTRAINT custos_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES moura_schema.categorias_custo(id) ON DELETE CASCADE;


--
-- Name: chat_message chat_message_merchant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_merchant_id_fkey FOREIGN KEY (merchant_id) REFERENCES public.merchant(id);


--
-- Name: client_chat_state client_chat_state_merchant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_chat_state
    ADD CONSTRAINT client_chat_state_merchant_id_fkey FOREIGN KEY (merchant_id) REFERENCES public.merchant(id);


--
-- Name: merchant merchant_loja_pai_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_loja_pai_id_fkey FOREIGN KEY (loja_pai_id) REFERENCES public.merchant(id);


--
-- Name: whatsapp_message_log whatsapp_message_log_merchant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.whatsapp_message_log
    ADD CONSTRAINT whatsapp_message_log_merchant_id_fkey FOREIGN KEY (merchant_id) REFERENCES public.merchant(id);


--
-- PostgreSQL database dump complete
--

\unrestrict d5WG5DLLstxF6jDLyfosC4KE3GNa51kmBB98pEuhpUHDRY6cibGAcca69IVSBn7

