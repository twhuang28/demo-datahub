DROP TABLE IF EXISTS if_polaris.customer_feature;
CREATE TABLE if_polaris.customer_feature(
    cust_no character varying,
    age integer,
    flam1 numeric, 
    etl_dt date
);
COMMENT ON TABLE if_polaris.customer_feature IS '顧客特徵資料';
COMMENT ON COLUMN if_polaris.customer_feature.cust_no IS '顧客ID';
COMMENT ON COLUMN if_polaris.customer_feature.age IS '顧客年齡';
COMMENT ON COLUMN if_polaris.customer_feature.flam1 IS '顧客信用卡消費金額';
COMMENT ON COLUMN if_polaris.customer_feature.etl_dt IS '處理日期';
INSERT INTO if_polaris.customer_feature VALUES
    ('A123456789',50,5000,now()),
    ('A123111111',20,500,now()),
    ('A122222222',10,300,now());
