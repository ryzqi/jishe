-- Active: 1742538900907@@127.0.0.1@5432@postgres@jishe
-- 创建 jishe 架构
CREATE SCHEMA IF NOT EXISTS jishe;

-- 无人机表
CREATE TABLE jishe.drone (
    id SERIAL PRIMARY KEY,
    drone_type VARCHAR(255) NOT NULL,
    states VARCHAR(1) NOT NULL CHECK (states IN ('1', '0'))
);
COMMENT ON TABLE jishe.drone IS '无人机表';
COMMENT ON COLUMN jishe.drone.id IS '无人机编号';
COMMENT ON COLUMN jishe.drone.drone_type IS '机型';
COMMENT ON COLUMN jishe.drone.states IS '无人机状态: 1->正常工作, 0->未工作';

-- 问题表
CREATE TABLE jishe.error (
    error_id SERIAL PRIMARY KEY,
    error_content TEXT NOT NULL,
    error_found_time TIMESTAMP NOT NULL,
    states VARCHAR(1) NOT NULL CHECK (states IN ('0', '1'))
);
COMMENT ON TABLE jishe.error IS '巡查发现的问题表';
COMMENT ON COLUMN jishe.error.error_id IS '问题编号';
COMMENT ON COLUMN jishe.error.error_content IS '问题内容';
COMMENT ON COLUMN jishe.error.error_found_time IS '问题发现时间';
COMMENT ON COLUMN jishe.error.states IS '问题状态: 0->待解决, 1->正在解决';

-- 货物表
CREATE TABLE jishe.goods (
    id SERIAL PRIMARY KEY,
    goods_name VARCHAR(255) NOT NULL
);
COMMENT ON TABLE jishe.goods IS '货物表';
COMMENT ON COLUMN jishe.goods.id IS '货物种类唯一标识';
COMMENT ON COLUMN jishe.goods.goods_name IS '货物种类名称';

-- 巡查记录表
CREATE TABLE jishe.patrol (
    id SERIAL PRIMARY KEY,
    drone_id INT NOT NULL REFERENCES jishe.drone(id) ON DELETE CASCADE,
    address VARCHAR(255) NOT NULL,
    predict_fly_time TIME NOT NULL,
    fly_start_datetime TIMESTAMP NOT NULL
);
COMMENT ON TABLE jishe.patrol IS '无人机巡查相关信息表';
COMMENT ON COLUMN jishe.patrol.id IS '巡查记录唯一标识';
COMMENT ON COLUMN jishe.patrol.drone_id IS '无人机编号';
COMMENT ON COLUMN jishe.patrol.address IS '在寻路段';
COMMENT ON COLUMN jishe.patrol.predict_fly_time IS '预计飞行时长';
COMMENT ON COLUMN jishe.patrol.fly_start_datetime IS '开始飞行时间';

-- 角色表
CREATE TABLE jishe.role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);
COMMENT ON TABLE jishe.role IS '角色表';
COMMENT ON COLUMN jishe.role.role_id IS '角色唯一标识';
COMMENT ON COLUMN jishe.role.role_name IS '角色名称';

-- 仓库表
CREATE TABLE jishe.warehouse (
    id SERIAL PRIMARY KEY,
    warehouse_name VARCHAR(255) NOT NULL,
    states VARCHAR(100) NOT NULL
);
COMMENT ON TABLE jishe.warehouse IS '仓库表';
COMMENT ON COLUMN jishe.warehouse.id IS '仓库唯一标识';
COMMENT ON COLUMN jishe.warehouse.warehouse_name IS '仓库名字';
COMMENT ON COLUMN jishe.warehouse.states IS '仓库状态: 正常,异常情况';

-- 库存表
CREATE TABLE jishe.stock (
    id SERIAL PRIMARY KEY,
    warehouse_id INT NOT NULL REFERENCES jishe.warehouse(id) ON DELETE CASCADE,
    goods_id INT NOT NULL REFERENCES jishe.goods(id) ON DELETE CASCADE,
    all_count INT NOT NULL DEFAULT 0,
    last_add_count INT NOT NULL DEFAULT 0,
    last_add_date TIMESTAMP NOT NULL
);
COMMENT ON TABLE jishe.stock IS '库存表';
COMMENT ON COLUMN jishe.stock.id IS '库存唯一标识';
COMMENT ON COLUMN jishe.stock.warehouse_id IS '仓库唯一标识';
COMMENT ON COLUMN jishe.stock.goods_id IS '货物种类唯一标识';
COMMENT ON COLUMN jishe.stock.all_count IS '总库存量';
COMMENT ON COLUMN jishe.stock.last_add_count IS '新增库存量';
COMMENT ON COLUMN jishe.stock.last_add_date IS '新增库存时间';


-- 用户表（使用双引号避免保留字冲突）
CREATE TABLE jishe."user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(256) NOT NULL
);
COMMENT ON TABLE jishe."user" IS '用户表';
COMMENT ON COLUMN jishe."user".id IS '用户唯一标识';
COMMENT ON COLUMN jishe."user".username IS '用户名';
COMMENT ON COLUMN jishe."user".password IS '用户密码';

-- 用户角色关联表
CREATE TABLE jishe.user_role (
    user_id INT NOT NULL REFERENCES jishe."user"(id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES jishe.role(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);
COMMENT ON TABLE jishe.user_role IS '用户-角色关联表';
COMMENT ON COLUMN jishe.user_role.user_id IS '用户唯一标识';
COMMENT ON COLUMN jishe.user_role.role_id IS '角色唯一标识';



INSERT INTO
    jishe.drone
VALUES (1, 'DJI Mavic 3', '1'),
    (2, 'DJI Phantom 4', '0'),
    (3, 'Parrot Anafi', '1'),
    (4, 'Autel Evo 2', '0'),
    (5, 'Skydio 2+', '1'),
    (6, 'Yuneec Typhoon H', '1'),
    (7, 'DJI Air 2S', '0'),
    (8, 'Parrot Bebop 2', '1'),
    (9, 'DJI Mini 3 Pro', '0'),
    (10, 'Autel Dragonfish', '1'),
    (11, 'DJI Inspire 2', '1'),
    (12, 'Parrot Disco', '0'),
    (13, 'XAG P100', '1'),
    (14, 'Walkera Vitus', '0'),
    (15, 'DJI T30', '1'),
    (16, 'DJI Avata', '1'),
    (17, 'Parrot Sequoia', '0'),
    (18, 'Autel Nano+', '1'),
    (19, 'DJI FPV', '1'),
    (20, 'EHang 184', '0');

INSERT INTO
    jishe.error
VALUES (
        1,
        '仓库A温度异常',
        '2025-03-18 09:00:00',
        '0'
    ),
    (
        2,
        '无人机B电池故障',
        '2025-03-18 10:15:00',
        '1'
    ),
    (
        3,
        '巡逻中发现异常货物摆放',
        '2025-03-18 11:00:00',
        '0'
    ),
    (
        4,
        '无人机C失去信号',
        '2025-03-17 14:30:00',
        '1'
    ),
    (
        5,
        '仓库D安全隐患',
        '2025-03-17 15:45:00',
        '0'
    ),
    (
        6,
        '无人机E航线偏离',
        '2025-03-16 12:20:00',
        '1'
    ),
    (
        7,
        '巡逻过程中发现火灾隐患',
        '2025-03-16 13:10:00',
        '0'
    ),
    (
        8,
        '无人机F摄像头故障',
        '2025-03-15 17:40:00',
        '1'
    ),
    (
        9,
        '仓库G门锁异常',
        '2025-03-15 18:30:00',
        '0'
    ),
    (
        10,
        '无人机H未按计划返回',
        '2025-03-14 20:50:00',
        '1'
    );

INSERT INTO
    jishe.goods
VALUES (1, '电子产品'),
    (2, '食品'),
    (3, '服装'),
    (4, '家用电器'),
    (5, '医药用品'),
    (6, '书籍'),
    (7, '家具'),
    (8, '办公用品'),
    (9, '运动器材'),
    (10, '玩具'),
    (11, '化妆品'),
    (12, '珠宝'),
    (13, '汽车配件'),
    (14, '生鲜'),
    (15, '日用品'),
    (16, '建筑材料'),
    (17, '五金工具'),
    (18, '乐器'),
    (19, '宠物用品'),
    (20, '安全设备');

INSERT INTO
    jishe.patrol
VALUES (
        1,
        1,
        'A区巡逻路线',
        '01:30:00',
        '2025-03-18 08:00:00'
    ),
    (
        2,
        2,
        'B区巡逻路线',
        '02:00:00',
        '2025-03-18 09:30:00'
    ),
    (
        3,
        3,
        'C区巡逻路线',
        '00:45:00',
        '2025-03-18 10:15:00'
    ),
    (
        4,
        4,
        'D区巡逻路线',
        '01:15:00',
        '2025-03-17 16:30:00'
    ),
    (
        5,
        5,
        'E区巡逻路线',
        '01:45:00',
        '2025-03-17 17:00:00'
    ),
    (
        6,
        6,
        'F区巡逻路线',
        '02:30:00',
        '2025-03-16 14:00:00'
    ),
    (
        7,
        7,
        'G区巡逻路线',
        '01:00:00',
        '2025-03-16 15:00:00'
    ),
    (
        8,
        8,
        'H区巡逻路线',
        '00:50:00',
        '2025-03-15 08:45:00'
    ),
    (
        9,
        9,
        'I区巡逻路线',
        '01:20:00',
        '2025-03-15 09:00:00'
    ),
    (
        10,
        10,
        'J区巡逻路线',
        '02:10:00',
        '2025-03-14 10:30:00'
    );

INSERT INTO
    jishe.role
VALUES (2, 'Stock Manager'),
    (1, 'Super Admin'),
    (3, 'Transport Manager');

INSERT INTO
    jishe.stock
VALUES (
        1,
        1,
        1,
        500,
        50,
        '2025-03-18 10:00:00'
    ),
    (
        2,
        2,
        2,
        600,
        100,
        '2025-03-18 11:00:00'
    ),
    (
        3,
        3,
        3,
        300,
        30,
        '2025-03-18 12:00:00'
    ),
    (
        4,
        4,
        4,
        800,
        200,
        '2025-03-18 09:00:00'
    ),
    (
        5,
        5,
        5,
        1000,
        150,
        '2025-03-17 14:00:00'
    ),
    (
        6,
        6,
        6,
        1200,
        300,
        '2025-03-17 15:00:00'
    ),
    (
        7,
        7,
        7,
        700,
        50,
        '2025-03-16 13:00:00'
    ),
    (
        8,
        8,
        8,
        900,
        100,
        '2025-03-16 08:00:00'
    ),
    (
        9,
        9,
        9,
        400,
        20,
        '2025-03-15 17:00:00'
    ),
    (
        10,
        10,
        10,
        1100,
        150,
        '2025-03-15 19:00:00'
    ),
    (
        11,
        11,
        11,
        500,
        30,
        '2025-03-14 20:00:00'
    ),
    (
        12,
        12,
        12,
        450,
        20,
        '2025-03-14 22:00:00'
    ),
    (
        13,
        13,
        13,
        800,
        50,
        '2025-03-13 18:00:00'
    ),
    (
        14,
        14,
        14,
        600,
        40,
        '2025-03-13 14:00:00'
    ),
    (
        15,
        15,
        15,
        750,
        60,
        '2025-03-12 16:00:00'
    ),
    (
        16,
        16,
        16,
        900,
        80,
        '2025-03-12 10:00:00'
    ),
    (
        17,
        17,
        17,
        1100,
        120,
        '2025-03-11 11:00:00'
    ),
    (
        18,
        18,
        18,
        950,
        70,
        '2025-03-11 12:00:00'
    ),
    (
        19,
        19,
        19,
        870,
        50,
        '2025-03-10 15:00:00'
    ),
    (
        20,
        20,
        20,
        1000,
        90,
        '2025-03-10 09:00:00'
    );

INSERT INTO
    jishe.user
VALUES (1, 'admin', '123456'),
    (2, 'zhangsan', '123456'),
    (3, 'lisi', '123456'),
    (4, 'wangwu', '123456'),
    (5, 'zhangsan', '123456'),
    (6, 'lisi', '123456'),
    (7, 'wangwu', '123456');

INSERT INTO jishe.user_role VALUES (1, 1), (2, 2), (3, 3), (4, 3);

INSERT INTO
    jishe.warehouse
VALUES (1, '北京仓库', '正常'),
    (2, '上海仓库', '正常'),
    (3, '广州仓库', '正常'),
    (4, '深圳仓库', '正常'),
    (5, '成都仓库', '正常'),
    (6, '杭州仓库', '正常'),
    (7, '西安仓库', '正常'),
    (8, '武汉仓库', '仓库温度异常'),
    (9, '南京仓库', '货物摆放混乱'),
    (10, '天津仓库', '正常'),
    (11, '重庆仓库', '正常'),
    (12, '苏州仓库', '正常'),
    (13, '长沙仓库', '安防系统故障'),
    (14, '郑州仓库', '正常'),
    (15, '青岛仓库', '正常'),
    (16, '沈阳仓库', '正常'),
    (17, '大连仓库', '正常'),
    (18, '合肥仓库', '正常'),
    (19, '昆明仓库', '正常'),
    (20, '哈尔滨仓库', '正常');


