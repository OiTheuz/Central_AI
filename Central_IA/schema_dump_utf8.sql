--
-- PostgreSQL database dump
--

\restrict krmFJnj9YFSlBwDTcV0cf4IWwYUcDBDV966gM2JiYW5i3s9608bsHSnoIWnpQUR

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

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
-- Name: jessiely_moura; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA jessiely_moura;


ALTER SCHEMA jessiely_moura OWNER TO postgres;

--
-- Name: moura_schema; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA moura_schema;


ALTER SCHEMA moura_schema OWNER TO postgres;

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
    is_paid_in_package boolean DEFAULT false
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
    is_paid_in_package boolean DEFAULT false
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
    ultima_interacao timestamp without time zone DEFAULT now()
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
    ultima_interacao timestamp without time zone DEFAULT now()
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
    numero_whatsapp character varying(20)
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
-- Name: active_sessions active_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_sessions
    ADD CONSTRAINT active_sessions_pkey PRIMARY KEY (id);


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
-- Name: merchant merchant_nome_loja_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_nome_loja_key UNIQUE (nome_loja);


--
-- Name: merchant merchant_numero_whatsapp_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.merchant
    ADD CONSTRAINT merchant_numero_whatsapp_key UNIQUE (numero_whatsapp);


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
-- PostgreSQL database dump complete
--

\unrestrict krmFJnj9YFSlBwDTcV0cf4IWwYUcDBDV966gM2JiYW5i3s9608bsHSnoIWnpQUR

