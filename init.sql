--
-- PostgreSQL database dump
--

-- Dumped from database version 17.3
-- Dumped by pg_dump version 17.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: jishe; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA jishe;


ALTER SCHEMA jishe OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: drone; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.drone (
    id integer NOT NULL,
    drone_type character varying(255) NOT NULL,
    states character varying(1) NOT NULL,
    CONSTRAINT drone_states_check CHECK (((states)::text = ANY ((ARRAY['1'::character varying, '0'::character varying])::text[])))
);


ALTER TABLE jishe.drone OWNER TO postgres;

--
-- Name: TABLE drone; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.drone IS '无人机表';


--
-- Name: COLUMN drone.id; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.drone.id IS '无人机编号';


--
-- Name: COLUMN drone.drone_type; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.drone.drone_type IS '机型';


--
-- Name: COLUMN drone.states; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.drone.states IS '无人机状态: 1->正常工作, 0->未工作';


--
-- Name: drone_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.drone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.drone_id_seq OWNER TO postgres;

--
-- Name: drone_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.drone_id_seq OWNED BY jishe.drone.id;


--
-- Name: error; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.error (
    error_id integer NOT NULL,
    error_content text NOT NULL,
    error_found_time timestamp without time zone NOT NULL,
    states character varying(1) NOT NULL,
    user_id integer,
    title character varying(255) DEFAULT ''::character varying NOT NULL,
    CONSTRAINT error_states_check CHECK (((states)::text = ANY ((ARRAY['0'::character varying, '1'::character varying])::text[])))
);


ALTER TABLE jishe.error OWNER TO postgres;

--
-- Name: TABLE error; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.error IS '巡查发现的问题表';


--
-- Name: error_error_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.error_error_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.error_error_id_seq OWNER TO postgres;

--
-- Name: error_error_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.error_error_id_seq OWNED BY jishe.error.error_id;


--
-- Name: goods; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.goods (
    id integer NOT NULL,
    goods_name character varying(255) NOT NULL
);


ALTER TABLE jishe.goods OWNER TO postgres;

--
-- Name: TABLE goods; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.goods IS '货物表';


--
-- Name: COLUMN goods.id; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.goods.id IS '货物种类唯一标识';


--
-- Name: COLUMN goods.goods_name; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.goods.goods_name IS '货物种类名称';


--
-- Name: goods_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.goods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.goods_id_seq OWNER TO postgres;

--
-- Name: goods_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.goods_id_seq OWNED BY jishe.goods.id;


--
-- Name: patrol; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.patrol (
    id integer NOT NULL,
    drone_id integer NOT NULL,
    address character varying(255) NOT NULL,
    predict_fly_time time without time zone NOT NULL,
    fly_start_datetime timestamp without time zone NOT NULL,
    update_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    error_id integer
);


ALTER TABLE jishe.patrol OWNER TO postgres;

--
-- Name: TABLE patrol; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.patrol IS '无人机巡查相关信息表';


--
-- Name: patrol_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.patrol_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.patrol_id_seq OWNER TO postgres;

--
-- Name: patrol_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.patrol_id_seq OWNED BY jishe.patrol.id;


--
-- Name: role; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.role (
    role_id integer NOT NULL,
    role_name character varying(50) NOT NULL
);


ALTER TABLE jishe.role OWNER TO postgres;

--
-- Name: TABLE role; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.role IS '角色表';


--
-- Name: COLUMN role.role_id; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.role.role_id IS '角色唯一标识';


--
-- Name: COLUMN role.role_name; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.role.role_name IS '角色名称';


--
-- Name: role_role_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.role_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.role_role_id_seq OWNER TO postgres;

--
-- Name: role_role_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.role_role_id_seq OWNED BY jishe.role.role_id;


--
-- Name: stock; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.stock (
    id integer NOT NULL,
    warehouse_id integer NOT NULL,
    goods_id integer NOT NULL,
    all_count integer DEFAULT 0 NOT NULL,
    last_add_count integer DEFAULT 0 NOT NULL,
    last_add_date timestamp without time zone NOT NULL
);


ALTER TABLE jishe.stock OWNER TO postgres;

--
-- Name: TABLE stock; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.stock IS '库存表';


--
-- Name: stock_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.stock_id_seq OWNER TO postgres;

--
-- Name: stock_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.stock_id_seq OWNED BY jishe.stock.id;


--
-- Name: user; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe."user" (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(100) NOT NULL,
    email character varying(100) DEFAULT 'default@example.com'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_superuser boolean DEFAULT false NOT NULL,
    name character varying(100),
    phone character varying(15) DEFAULT NULL::character varying,
    createtime timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE jishe."user" OWNER TO postgres;

--
-- Name: TABLE "user"; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe."user" IS '用户表';


--
-- Name: COLUMN "user".id; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".id IS '用户唯一标识';


--
-- Name: COLUMN "user".username; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".username IS '用户名';


--
-- Name: COLUMN "user".password; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".password IS '用户密码';


--
-- Name: COLUMN "user".email; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".email IS '用户电子邮件';


--
-- Name: COLUMN "user".is_active; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".is_active IS '用户是否活跃';


--
-- Name: COLUMN "user".is_superuser; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".is_superuser IS '是否为超级管理员';


--
-- Name: COLUMN "user".name; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".name IS '用户姓名';


--
-- Name: COLUMN "user".phone; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".phone IS '用户电话号码';


--
-- Name: COLUMN "user".createtime; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe."user".createtime IS '账户创建时间（格式：YYYY-MM-DD HH:MI:SS）';


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.user_id_seq OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.user_id_seq OWNED BY jishe."user".id;


--
-- Name: user_role; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.user_role (
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE jishe.user_role OWNER TO postgres;

--
-- Name: TABLE user_role; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.user_role IS '用户-角色关联表';


--
-- Name: warehouse; Type: TABLE; Schema: jishe; Owner: postgres
--

CREATE TABLE jishe.warehouse (
    id integer NOT NULL,
    warehouse_name character varying(255) NOT NULL,
    states character varying(100) NOT NULL
);


ALTER TABLE jishe.warehouse OWNER TO postgres;

--
-- Name: TABLE warehouse; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON TABLE jishe.warehouse IS '仓库表';


--
-- Name: COLUMN warehouse.id; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.warehouse.id IS '仓库唯一标识';


--
-- Name: COLUMN warehouse.warehouse_name; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.warehouse.warehouse_name IS '仓库名字';


--
-- Name: COLUMN warehouse.states; Type: COMMENT; Schema: jishe; Owner: postgres
--

COMMENT ON COLUMN jishe.warehouse.states IS '仓库状态: 正常,异常情况';


--
-- Name: warehouse_id_seq; Type: SEQUENCE; Schema: jishe; Owner: postgres
--

CREATE SEQUENCE jishe.warehouse_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE jishe.warehouse_id_seq OWNER TO postgres;

--
-- Name: warehouse_id_seq; Type: SEQUENCE OWNED BY; Schema: jishe; Owner: postgres
--

ALTER SEQUENCE jishe.warehouse_id_seq OWNED BY jishe.warehouse.id;


--
-- Name: drone id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.drone ALTER COLUMN id SET DEFAULT nextval('jishe.drone_id_seq'::regclass);


--
-- Name: error error_id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.error ALTER COLUMN error_id SET DEFAULT nextval('jishe.error_error_id_seq'::regclass);


--
-- Name: goods id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.goods ALTER COLUMN id SET DEFAULT nextval('jishe.goods_id_seq'::regclass);


--
-- Name: patrol id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.patrol ALTER COLUMN id SET DEFAULT nextval('jishe.patrol_id_seq'::regclass);


--
-- Name: role role_id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.role ALTER COLUMN role_id SET DEFAULT nextval('jishe.role_role_id_seq'::regclass);


--
-- Name: stock id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.stock ALTER COLUMN id SET DEFAULT nextval('jishe.stock_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe."user" ALTER COLUMN id SET DEFAULT nextval('jishe.user_id_seq'::regclass);


--
-- Name: warehouse id; Type: DEFAULT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.warehouse ALTER COLUMN id SET DEFAULT nextval('jishe.warehouse_id_seq'::regclass);


--
-- Data for Name: drone; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.drone (id, drone_type, states) FROM stdin;
1	DJI Mavic 3	1
2	DJI Phantom 4	0
3	Parrot Anafi	1
4	Autel Evo 2	0
5	Skydio 2+	1
6	Yuneec Typhoon H	1
7	DJI Air 2S	0
8	Parrot Bebop 2	1
9	DJI Mini 3 Pro	0
10	Autel Dragonfish	1
11	DJI Inspire 2	1
12	Parrot Disco	0
13	XAG P100	1
14	Walkera Vitus	0
15	DJI T30	1
16	DJI Avata	1
17	Parrot Sequoia	0
18	Autel Nano+	1
19	DJI FPV	1
20	EHang 184	0
\.


--
-- Data for Name: error; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.error (error_id, error_content, error_found_time, states, user_id, title) FROM stdin;
1	仓库A温度异常	2025-03-18 09:00:00	0	1	
2	无人机B电池故障	2025-03-18 10:15:00	1	2	
3	巡逻中发现异常货物摆放	2025-03-18 11:00:00	0	3	
4	无人机C失去信号	2025-03-17 14:30:00	1	4	
5	仓库D安全隐患	2025-03-17 15:45:00	0	1	
\.


--
-- Data for Name: goods; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.goods (id, goods_name) FROM stdin;
1	电子产品
2	食品
3	服装
4	家用电器
5	医药用品
6	书籍
7	家具
8	办公用品
9	运动器材
10	玩具
11	化妆品
12	珠宝
13	汽车配件
14	生鲜
15	日用品
16	建筑材料
17	五金工具
18	乐器
19	宠物用品
20	安全设备
\.


--
-- Data for Name: patrol; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.patrol (id, drone_id, address, predict_fly_time, fly_start_datetime, update_time, error_id) FROM stdin;
1	1	A区	01:30:00	2025-03-18 08:00:00	2025-04-02 20:48:40.565518	\N
3	3	C区	00:45:00	2025-03-18 10:15:00	2025-04-02 20:48:40.565518	\N
5	5	E区	01:45:00	2025-03-17 17:00:00	2025-04-02 20:48:40.565518	\N
7	7	G区	01:00:00	2025-03-16 15:00:00	2025-04-02 20:48:40.565518	\N
9	9	I区	01:20:00	2025-03-15 09:00:00	2025-04-02 20:48:40.565518	\N
10	10	J区	02:10:00	2025-03-14 10:30:00	2025-04-02 20:48:40.565518	5
2	2	B区	02:00:00	2025-03-18 09:30:00	2025-04-02 20:48:40.565518	1
4	4	D区	01:15:00	2025-03-17 16:30:00	2025-04-02 20:48:40.565518	2
6	6	F区	02:30:00	2025-03-16 14:00:00	2025-04-02 20:48:40.565518	3
8	8	H区	00:50:00	2025-03-15 08:45:00	2025-04-02 20:48:40.565518	4
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.role (role_id, role_name) FROM stdin;
1	Super Admin
2	Stock Manager
3	Transport Manager
\.


--
-- Data for Name: stock; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.stock (id, warehouse_id, goods_id, all_count, last_add_count, last_add_date) FROM stdin;
1	1	1	500	50	2025-03-18 10:00:00
2	2	2	600	100	2025-03-18 11:00:00
3	3	3	300	30	2025-03-18 12:00:00
4	4	4	800	200	2025-03-18 09:00:00
5	5	5	1000	150	2025-03-17 14:00:00
6	6	6	1200	300	2025-03-17 15:00:00
7	7	7	700	50	2025-03-16 13:00:00
8	8	8	900	100	2025-03-16 08:00:00
9	9	9	400	20	2025-03-15 17:00:00
10	10	10	1100	150	2025-03-15 19:00:00
11	11	11	500	30	2025-03-14 20:00:00
12	12	12	450	20	2025-03-14 22:00:00
13	13	13	800	50	2025-03-13 18:00:00
14	14	14	600	40	2025-03-13 14:00:00
15	15	15	750	60	2025-03-12 16:00:00
16	16	16	900	80	2025-03-12 10:00:00
17	17	17	1100	120	2025-03-11 11:00:00
18	18	18	950	70	2025-03-11 12:00:00
19	19	19	870	50	2025-03-10 15:00:00
20	20	20	1000	90	2025-03-10 09:00:00
22	1	2	100	10	2025-04-02 17:18:10.11806
23	1	3	520	55	2025-03-16 15:30:00
24	1	4	460	42	2025-03-16 09:15:00
25	1	5	580	65	2025-03-15 14:45:00
26	1	6	620	75	2025-03-14 10:30:00
27	1	7	420	38	2025-03-13 16:20:00
28	1	8	540	52	2025-03-12 13:10:00
29	1	9	380	32	2025-03-11 09:40:00
30	1	10	680	82	2025-03-10 14:00:00
31	2	1	370	32	2025-03-17 08:45:00
32	2	3	470	48	2025-03-16 12:30:00
33	2	4	530	58	2025-03-15 11:20:00
34	2	5	490	46	2025-03-14 15:40:00
35	2	6	570	62	2025-03-13 09:50:00
36	2	7	430	40	2025-03-12 14:15:00
37	2	8	510	50	2025-03-11 10:25:00
38	2	9	390	35	2025-03-10 16:30:00
39	2	10	590	68	2025-03-09 13:45:00
40	3	1	270	28	2025-03-17 10:15:00
41	3	2	330	34	2025-03-16 08:40:00
42	3	4	470	48	2025-03-15 14:50:00
43	3	5	390	38	2025-03-14 11:30:00
44	3	6	430	42	2025-03-13 15:20:00
45	3	7	370	36	2025-03-12 09:45:00
46	3	8	490	46	2025-03-11 13:15:00
47	3	9	310	30	2025-03-10 16:40:00
48	3	10	550	58	2025-03-09 10:50:00
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe."user" (id, username, password, email, is_active, is_superuser, name, phone, createtime) FROM stdin;
1	admin	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	admin@example.com	t	t	管理员	19102645269	2025-04-04 00:01:40.065101
2	zhangsan	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	zhangsan@example.com	t	f	张三	19102645269	2025-04-04 00:01:40.065101
3	lisi	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	lisi@example.com	t	f	李四	19102645269	2025-04-04 00:01:40.065101
4	wangwu	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	wangwu@example.com	t	f	王五	19102645269	2025-04-04 00:01:40.065101
5	zhaoliu	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	zhaoliu@example.com	t	f	赵六	19102645269	2025-04-04 00:01:40.065101
6	qianqi	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	qianqi@example.com	t	f	钱七	19102645269	2025-04-04 00:01:40.065101
7	sunba	$2b$12$WPrJRizcHgE9BMCsdviQHO/qZzdg6uv0UBHc94GLnZpEjH9JPQ3ky	sunba@example.com	t	f	孙八	19102645269	2025-04-04 00:01:40.065101
\.


--
-- Data for Name: user_role; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.user_role (user_id, role_id) FROM stdin;
1	1
2	2
3	3
4	3
\.


--
-- Data for Name: warehouse; Type: TABLE DATA; Schema: jishe; Owner: postgres
--

COPY jishe.warehouse (id, warehouse_name, states) FROM stdin;
1	北京仓库	正常
2	上海仓库	正常
3	广州仓库	正常
4	深圳仓库	正常
5	成都仓库	正常
6	杭州仓库	正常
7	西安仓库	正常
8	武汉仓库	仓库温度异常
9	南京仓库	货物摆放混乱
10	天津仓库	正常
11	重庆仓库	正常
12	苏州仓库	正常
13	长沙仓库	安防系统故障
14	郑州仓库	正常
15	青岛仓库	正常
16	沈阳仓库	正常
17	大连仓库	正常
18	合肥仓库	正常
19	昆明仓库	正常
20	哈尔滨仓库	正常
\.


--
-- Name: drone_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.drone_id_seq', 1, false);


--
-- Name: error_error_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.error_error_id_seq', 1, false);


--
-- Name: goods_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.goods_id_seq', 1, false);


--
-- Name: patrol_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.patrol_id_seq', 1, false);


--
-- Name: role_role_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.role_role_id_seq', 1, false);


--
-- Name: stock_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.stock_id_seq', 48, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.user_id_seq', 1, false);


--
-- Name: warehouse_id_seq; Type: SEQUENCE SET; Schema: jishe; Owner: postgres
--

SELECT pg_catalog.setval('jishe.warehouse_id_seq', 1, false);


--
-- Name: drone drone_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.drone
    ADD CONSTRAINT drone_pkey PRIMARY KEY (id);


--
-- Name: error error_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.error
    ADD CONSTRAINT error_pkey PRIMARY KEY (error_id);


--
-- Name: goods goods_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.goods
    ADD CONSTRAINT goods_pkey PRIMARY KEY (id);


--
-- Name: patrol patrol_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.patrol
    ADD CONSTRAINT patrol_pkey PRIMARY KEY (id);


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (role_id);


--
-- Name: role role_role_name_key; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.role
    ADD CONSTRAINT role_role_name_key UNIQUE (role_name);


--
-- Name: stock stock_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.stock
    ADD CONSTRAINT stock_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user_role user_role_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.user_role
    ADD CONSTRAINT user_role_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: warehouse warehouse_pkey; Type: CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.warehouse
    ADD CONSTRAINT warehouse_pkey PRIMARY KEY (id);


--
-- Name: ix_user_email; Type: INDEX; Schema: jishe; Owner: postgres
--

CREATE INDEX ix_user_email ON jishe."user" USING btree (email);


--
-- Name: patrol patrol_drone_id_fkey; Type: FK CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.patrol
    ADD CONSTRAINT patrol_drone_id_fkey FOREIGN KEY (drone_id) REFERENCES jishe.drone(id) ON DELETE CASCADE;


--
-- Name: stock stock_goods_id_fkey; Type: FK CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.stock
    ADD CONSTRAINT stock_goods_id_fkey FOREIGN KEY (goods_id) REFERENCES jishe.goods(id) ON DELETE CASCADE;


--
-- Name: stock stock_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.stock
    ADD CONSTRAINT stock_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES jishe.warehouse(id) ON DELETE CASCADE;


--
-- Name: user_role user_role_role_id_fkey; Type: FK CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.user_role
    ADD CONSTRAINT user_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES jishe.role(role_id) ON DELETE CASCADE;


--
-- Name: user_role user_role_user_id_fkey; Type: FK CONSTRAINT; Schema: jishe; Owner: postgres
--

ALTER TABLE ONLY jishe.user_role
    ADD CONSTRAINT user_role_user_id_fkey FOREIGN KEY (user_id) REFERENCES jishe."user"(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

