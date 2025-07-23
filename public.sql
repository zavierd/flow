/*
 Navicat Premium Data Transfer

 Source Server         : docker中的postgresql-flow项目
 Source Server Type    : PostgreSQL
 Source Server Version : 160009 (160009)
 Source Host           : localhost:5432
 Source Catalog        : product_library
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 160009 (160009)
 File Encoding         : 65001

 Date: 18/07/2025 18:00:55
*/


-- ----------------------------
-- Sequence structure for auth_group_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_group_id_seq";
CREATE SEQUENCE "public"."auth_group_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."auth_group_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for auth_group_permissions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_group_permissions_id_seq";
CREATE SEQUENCE "public"."auth_group_permissions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."auth_group_permissions_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for auth_permission_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_permission_id_seq";
CREATE SEQUENCE "public"."auth_permission_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."auth_permission_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for auth_user_groups_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_user_groups_id_seq";
CREATE SEQUENCE "public"."auth_user_groups_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."auth_user_groups_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for auth_user_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_user_id_seq";
CREATE SEQUENCE "public"."auth_user_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."auth_user_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for auth_user_user_permissions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."auth_user_user_permissions_id_seq";
CREATE SEQUENCE "public"."auth_user_user_permissions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."auth_user_user_permissions_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for django_admin_log_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_admin_log_id_seq";
CREATE SEQUENCE "public"."django_admin_log_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."django_admin_log_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for django_content_type_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_content_type_id_seq";
CREATE SEQUENCE "public"."django_content_type_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;
ALTER SEQUENCE "public"."django_content_type_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for django_migrations_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."django_migrations_id_seq";
CREATE SEQUENCE "public"."django_migrations_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."django_migrations_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_attribute_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_attribute_id_seq";
CREATE SEQUENCE "public"."products_attribute_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_attribute_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_attributevalue_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_attributevalue_id_seq";
CREATE SEQUENCE "public"."products_attributevalue_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_attributevalue_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_brand_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_brand_id_seq";
CREATE SEQUENCE "public"."products_brand_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_brand_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_category_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_category_id_seq";
CREATE SEQUENCE "public"."products_category_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_category_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_productimage_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_productimage_id_seq";
CREATE SEQUENCE "public"."products_productimage_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_productimage_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_productsdimension_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_productsdimension_id_seq";
CREATE SEQUENCE "public"."products_productsdimension_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_productsdimension_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_productspricingrule_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_productspricingrule_id_seq";
CREATE SEQUENCE "public"."products_productspricingrule_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_productspricingrule_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_sku_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_sku_id_seq";
CREATE SEQUENCE "public"."products_sku_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_sku_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_skuattributevalue_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_skuattributevalue_id_seq";
CREATE SEQUENCE "public"."products_skuattributevalue_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_skuattributevalue_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_spu_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_spu_id_seq";
CREATE SEQUENCE "public"."products_spu_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_spu_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_spuattribute_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_spuattribute_id_seq";
CREATE SEQUENCE "public"."products_spuattribute_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_spuattribute_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Sequence structure for products_spudimensiontemplate_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."products_spudimensiontemplate_id_seq";
CREATE SEQUENCE "public"."products_spudimensiontemplate_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "public"."products_spudimensiontemplate_id_seq" OWNER TO "postgres";

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_group";
CREATE TABLE "public"."auth_group" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "name" varchar(150) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "public"."auth_group" OWNER TO "postgres";

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_group_permissions";
CREATE TABLE "public"."auth_group_permissions" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "group_id" int4 NOT NULL,
  "permission_id" int4 NOT NULL
)
;
ALTER TABLE "public"."auth_group_permissions" OWNER TO "postgres";

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_permission";
CREATE TABLE "public"."auth_permission" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content_type_id" int4 NOT NULL,
  "codename" varchar(100) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "public"."auth_permission" OWNER TO "postgres";

-- ----------------------------
-- Table structure for auth_user
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_user";
CREATE TABLE "public"."auth_user" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "password" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "last_login" timestamptz(6),
  "is_superuser" bool NOT NULL,
  "username" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "first_name" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "last_name" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(254) COLLATE "pg_catalog"."default" NOT NULL,
  "is_staff" bool NOT NULL,
  "is_active" bool NOT NULL,
  "date_joined" timestamptz(6) NOT NULL
)
;
ALTER TABLE "public"."auth_user" OWNER TO "postgres";

-- ----------------------------
-- Table structure for auth_user_groups
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_user_groups";
CREATE TABLE "public"."auth_user_groups" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "user_id" int4 NOT NULL,
  "group_id" int4 NOT NULL
)
;
ALTER TABLE "public"."auth_user_groups" OWNER TO "postgres";

-- ----------------------------
-- Table structure for auth_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."auth_user_user_permissions";
CREATE TABLE "public"."auth_user_user_permissions" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "user_id" int4 NOT NULL,
  "permission_id" int4 NOT NULL
)
;
ALTER TABLE "public"."auth_user_user_permissions" OWNER TO "postgres";

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_admin_log";
CREATE TABLE "public"."django_admin_log" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "action_time" timestamptz(6) NOT NULL,
  "object_id" text COLLATE "pg_catalog"."default",
  "object_repr" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "action_flag" int2 NOT NULL,
  "change_message" text COLLATE "pg_catalog"."default" NOT NULL,
  "content_type_id" int4,
  "user_id" int4 NOT NULL
)
;
ALTER TABLE "public"."django_admin_log" OWNER TO "postgres";

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_content_type";
CREATE TABLE "public"."django_content_type" (
  "id" int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1
),
  "app_label" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "public"."django_content_type" OWNER TO "postgres";

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_migrations";
CREATE TABLE "public"."django_migrations" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "app" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "applied" timestamptz(6) NOT NULL
)
;
ALTER TABLE "public"."django_migrations" OWNER TO "postgres";

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS "public"."django_session";
CREATE TABLE "public"."django_session" (
  "session_key" varchar(40) COLLATE "pg_catalog"."default" NOT NULL,
  "session_data" text COLLATE "pg_catalog"."default" NOT NULL,
  "expire_date" timestamptz(6) NOT NULL
)
;
ALTER TABLE "public"."django_session" OWNER TO "postgres";

-- ----------------------------
-- Table structure for products_attribute
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_attribute";
CREATE TABLE "public"."products_attribute" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "unit" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_required" bool NOT NULL,
  "is_filterable" bool NOT NULL,
  "order" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL
)
;
ALTER TABLE "public"."products_attribute" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_attribute"."name" IS '属性的显示名称';
COMMENT ON COLUMN "public"."products_attribute"."code" IS '属性的唯一标识码，用于系统内部识别';
COMMENT ON COLUMN "public"."products_attribute"."type" IS '属性的数据类型，决定了值的存储和显示方式';
COMMENT ON COLUMN "public"."products_attribute"."unit" IS '属性值的计量单位，如cm、kg等';
COMMENT ON COLUMN "public"."products_attribute"."description" IS '属性的详细描述信息';
COMMENT ON COLUMN "public"."products_attribute"."is_required" IS '创建产品时是否必须填写此属性';
COMMENT ON COLUMN "public"."products_attribute"."is_filterable" IS '是否可以作为筛选条件在前台使用';
COMMENT ON COLUMN "public"."products_attribute"."order" IS '属性的显示顺序，数字越小越靠前';
COMMENT ON COLUMN "public"."products_attribute"."is_active" IS '属性状态，false表示已禁用';
COMMENT ON COLUMN "public"."products_attribute"."created_at" IS '属性创建的时间戳';
COMMENT ON COLUMN "public"."products_attribute"."updated_at" IS '属性最后更新的时间戳';
COMMENT ON TABLE "public"."products_attribute" IS '产品属性定义表 - 定义产品的各种可配置属性类型';

-- ----------------------------
-- Table structure for products_attributevalue
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_attributevalue";
CREATE TABLE "public"."products_attributevalue" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "value" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "display_name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "color_code" varchar(7) COLLATE "pg_catalog"."default" NOT NULL,
  "image" varchar(100) COLLATE "pg_catalog"."default",
  "order" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "attribute_id" int8 NOT NULL
)
;
ALTER TABLE "public"."products_attributevalue" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_attributevalue"."value" IS '属性的具体值，如红色、30cm等';
COMMENT ON COLUMN "public"."products_attributevalue"."display_name" IS '属性值的显示名称，为空时使用value字段';
COMMENT ON COLUMN "public"."products_attributevalue"."color_code" IS '颜色属性的十六进制颜色代码，如#FF0000';
COMMENT ON COLUMN "public"."products_attributevalue"."image" IS '属性值的展示图片文件路径';
COMMENT ON COLUMN "public"."products_attributevalue"."order" IS '同属性下值的显示顺序，数字越小越靠前';
COMMENT ON COLUMN "public"."products_attributevalue"."is_active" IS '属性值状态，false表示已禁用';
COMMENT ON COLUMN "public"."products_attributevalue"."created_at" IS '属性值创建的时间戳';
COMMENT ON COLUMN "public"."products_attributevalue"."updated_at" IS '属性值最后更新的时间戳';
COMMENT ON COLUMN "public"."products_attributevalue"."attribute_id" IS '所属的属性ID';
COMMENT ON TABLE "public"."products_attributevalue" IS '属性值表 - 存储每个属性的具体可选值';

-- ----------------------------
-- Table structure for products_brand
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_brand";
CREATE TABLE "public"."products_brand" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "logo" varchar(100) COLLATE "pg_catalog"."default",
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "website" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "contact_person" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "contact_phone" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "contact_email" varchar(254) COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL
)
;
ALTER TABLE "public"."products_brand" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_brand"."name" IS '品牌的正式名称';
COMMENT ON COLUMN "public"."products_brand"."code" IS '品牌的唯一标识码，用于系统内部识别';
COMMENT ON COLUMN "public"."products_brand"."logo" IS '品牌标志图片文件路径';
COMMENT ON COLUMN "public"."products_brand"."description" IS '品牌的详细介绍和特色描述';
COMMENT ON COLUMN "public"."products_brand"."website" IS '品牌官方网站地址';
COMMENT ON COLUMN "public"."products_brand"."contact_person" IS '品牌联系人姓名';
COMMENT ON COLUMN "public"."products_brand"."contact_phone" IS '品牌联系电话号码';
COMMENT ON COLUMN "public"."products_brand"."contact_email" IS '品牌联系邮箱地址';
COMMENT ON COLUMN "public"."products_brand"."is_active" IS '品牌状态，false表示已禁用';
COMMENT ON COLUMN "public"."products_brand"."created_at" IS '品牌创建的时间戳';
COMMENT ON COLUMN "public"."products_brand"."updated_at" IS '品牌最后更新的时间戳';
COMMENT ON TABLE "public"."products_brand" IS '品牌信息表 - 管理产品品牌的基础信息和联系方式';

-- ----------------------------
-- Table structure for products_category
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_category";
CREATE TABLE "public"."products_category" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "order" int4 NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "parent_id" int8,
  "lft" int4 NOT NULL,
  "rght" int4 NOT NULL,
  "tree_id" int4 NOT NULL,
  "level" int4 NOT NULL
)
;
ALTER TABLE "public"."products_category" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_category"."name" IS '分类的显示名称，如：橱柜、地柜、吊柜等';
COMMENT ON COLUMN "public"."products_category"."code" IS '分类的唯一标识码，用于系统内部识别和API调用';
COMMENT ON COLUMN "public"."products_category"."order" IS '同级分类的显示顺序，数字越小越靠前';
COMMENT ON COLUMN "public"."products_category"."description" IS '分类的详细描述信息';
COMMENT ON COLUMN "public"."products_category"."is_active" IS '分类状态，false表示已禁用';
COMMENT ON COLUMN "public"."products_category"."created_at" IS '分类创建的时间戳';
COMMENT ON COLUMN "public"."products_category"."updated_at" IS '分类最后更新的时间戳';
COMMENT ON COLUMN "public"."products_category"."parent_id" IS '上级分类，为空表示顶级分类';
COMMENT ON TABLE "public"."products_category" IS '产品分类表 - 管理产品的多级分类体系，支持无限级嵌套';

-- ----------------------------
-- Table structure for products_pricing_rule
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_pricing_rule";
CREATE TABLE "public"."products_pricing_rule" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "rule_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "threshold_value" numeric(10,2) NOT NULL,
  "unit_increment" numeric(10,2) NOT NULL,
  "calculation_method" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "price_increment" numeric(10,2) NOT NULL,
  "multiplier" numeric(5,2) NOT NULL,
  "max_increment" numeric(10,2),
  "is_active" bool NOT NULL,
  "effective_date" date NOT NULL,
  "expiry_date" date,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "created_by_id" int4,
  "spu_id" int8 NOT NULL,
  "sku_id" int8
)
;
ALTER TABLE "public"."products_pricing_rule" OWNER TO "postgres";

-- ----------------------------
-- Table structure for products_productimage
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_productimage";
CREATE TABLE "public"."products_productimage" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "image" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "alt_text" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "order" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "sku_id" int8 NOT NULL
)
;
ALTER TABLE "public"."products_productimage" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_productimage"."image" IS '产品图片文件路径';
COMMENT ON COLUMN "public"."products_productimage"."alt_text" IS '图片的替代文本，用于SEO和无障碍访问';
COMMENT ON COLUMN "public"."products_productimage"."order" IS '图片的显示顺序，数字越小越靠前';
COMMENT ON COLUMN "public"."products_productimage"."is_active" IS '图片状态，false表示已禁用';
COMMENT ON COLUMN "public"."products_productimage"."created_at" IS '图片上传的时间戳';
COMMENT ON COLUMN "public"."products_productimage"."sku_id" IS '关联的SKU ID';
COMMENT ON TABLE "public"."products_productimage" IS '产品图片表 - 存储每个SKU的多张产品展示图片';

-- ----------------------------
-- Table structure for products_productsdimension
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_productsdimension";
CREATE TABLE "public"."products_productsdimension" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "dimension_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "standard_value" numeric(10,2) NOT NULL,
  "min_value" numeric(10,2),
  "max_value" numeric(10,2),
  "unit" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "custom_unit" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "tolerance" numeric(10,2) NOT NULL,
  "is_key_dimension" bool NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "created_by_id" int4,
  "sku_id" int8 NOT NULL
)
;
ALTER TABLE "public"."products_productsdimension" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_productsdimension"."dimension_type" IS '尺寸的类型，如高度、宽度、厚度等';
COMMENT ON COLUMN "public"."products_productsdimension"."standard_value" IS '产品的标准尺寸值';
COMMENT ON COLUMN "public"."products_productsdimension"."min_value" IS '允许的最小尺寸值';
COMMENT ON COLUMN "public"."products_productsdimension"."max_value" IS '允许的最大尺寸值';
COMMENT ON COLUMN "public"."products_productsdimension"."unit" IS '尺寸的计量单位';
COMMENT ON COLUMN "public"."products_productsdimension"."custom_unit" IS '自定义的计量单位';
COMMENT ON COLUMN "public"."products_productsdimension"."tolerance" IS '尺寸的允许公差范围';
COMMENT ON COLUMN "public"."products_productsdimension"."is_key_dimension" IS '是否为影响定价的关键尺寸';
COMMENT ON COLUMN "public"."products_productsdimension"."description" IS '尺寸的详细描述和说明';
COMMENT ON COLUMN "public"."products_productsdimension"."created_at" IS '记录创建的时间戳';
COMMENT ON COLUMN "public"."products_productsdimension"."updated_at" IS '记录最后更新的时间戳';
COMMENT ON COLUMN "public"."products_productsdimension"."created_by_id" IS '创建此记录的用户ID';
COMMENT ON COLUMN "public"."products_productsdimension"."sku_id" IS '关联的SKU产品';
COMMENT ON TABLE "public"."products_productsdimension" IS '产品尺寸表 - 存储每个SKU的标准尺寸信息';

-- ----------------------------
-- Table structure for products_sku
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_sku";
CREATE TABLE "public"."products_sku" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "sku_id" uuid NOT NULL,
  "price" numeric(10,2) NOT NULL,
  "cost_price" numeric(10,2),
  "market_price" numeric(10,2),
  "stock_quantity" int4 NOT NULL,
  "min_stock" int4 NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "main_image" varchar(100) COLLATE "pg_catalog"."default",
  "selling_points" text COLLATE "pg_catalog"."default" NOT NULL,
  "tags" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "is_featured" bool NOT NULL,
  "launch_date" date,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "brand_id" int8 NOT NULL,
  "created_by_id" int4,
  "spu_id" int8 NOT NULL,
  "remarks" text COLLATE "pg_catalog"."default" NOT NULL
)
;
ALTER TABLE "public"."products_sku" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_sku"."name" IS 'SKU的完整名称，包含属性信息';
COMMENT ON COLUMN "public"."products_sku"."code" IS 'SKU的唯一标识码，通常包含属性编码';
COMMENT ON COLUMN "public"."products_sku"."sku_id" IS '系统生成的UUID，用于内部唯一标识';
COMMENT ON COLUMN "public"."products_sku"."price" IS '产品售价，单位：元';
COMMENT ON COLUMN "public"."products_sku"."cost_price" IS '产品成本价，单位：元';
COMMENT ON COLUMN "public"."products_sku"."market_price" IS '产品市场指导价，单位：元';
COMMENT ON COLUMN "public"."products_sku"."stock_quantity" IS '当前库存数量';
COMMENT ON COLUMN "public"."products_sku"."min_stock" IS '库存预警阈值，低于此值将触发预警';
COMMENT ON COLUMN "public"."products_sku"."description" IS 'SKU的详细描述信息';
COMMENT ON COLUMN "public"."products_sku"."main_image" IS '产品主图文件路径';
COMMENT ON COLUMN "public"."products_sku"."selling_points" IS '产品的主要卖点和特色介绍';
COMMENT ON COLUMN "public"."products_sku"."tags" IS '产品标签，用逗号分隔';
COMMENT ON COLUMN "public"."products_sku"."status" IS '产品状态：草稿、上架、下架、停产';
COMMENT ON COLUMN "public"."products_sku"."is_featured" IS '是否为推荐产品，用于首页等位置展示';
COMMENT ON COLUMN "public"."products_sku"."launch_date" IS '产品的上市日期';
COMMENT ON COLUMN "public"."products_sku"."created_at" IS 'SKU创建的时间戳';
COMMENT ON COLUMN "public"."products_sku"."updated_at" IS 'SKU最后更新的时间戳';
COMMENT ON COLUMN "public"."products_sku"."brand_id" IS '所属的品牌ID';
COMMENT ON COLUMN "public"."products_sku"."created_by_id" IS '创建此SKU的用户ID';
COMMENT ON COLUMN "public"."products_sku"."spu_id" IS '基于的SPU模板ID';
COMMENT ON COLUMN "public"."products_sku"."remarks" IS '产品的补充说明信息，如配件、特殊说明等';
COMMENT ON TABLE "public"."products_sku" IS '品牌产品表 - 具体的可销售产品，包含价格库存等销售信息';

-- ----------------------------
-- Table structure for products_skuattributevalue
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_skuattributevalue";
CREATE TABLE "public"."products_skuattributevalue" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "custom_value" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "attribute_id" int8 NOT NULL,
  "attribute_value_id" int8,
  "sku_id" int8 NOT NULL
)
;
ALTER TABLE "public"."products_skuattributevalue" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_skuattributevalue"."custom_value" IS '自定义属性值，用于非预定义值的属性';
COMMENT ON COLUMN "public"."products_skuattributevalue"."created_at" IS '记录创建的时间戳';
COMMENT ON COLUMN "public"."products_skuattributevalue"."updated_at" IS '记录最后更新的时间戳';
COMMENT ON COLUMN "public"."products_skuattributevalue"."attribute_id" IS '关联的属性ID';
COMMENT ON COLUMN "public"."products_skuattributevalue"."attribute_value_id" IS '关联的预定义属性值ID，与custom_value二选一';
COMMENT ON COLUMN "public"."products_skuattributevalue"."sku_id" IS '关联的SKU ID';
COMMENT ON TABLE "public"."products_skuattributevalue" IS 'SKU属性值关联表 - 关系型存储每个SKU的具体属性值配置';

-- ----------------------------
-- Table structure for products_spu
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_spu";
CREATE TABLE "public"."products_spu" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "name" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "specifications" text COLLATE "pg_catalog"."default" NOT NULL,
  "usage_scenario" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "category_id" int8 NOT NULL,
  "created_by_id" int4,
  "brand_id" int8
)
;
ALTER TABLE "public"."products_spu" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_spu"."name" IS 'SPU的标准名称';
COMMENT ON COLUMN "public"."products_spu"."code" IS 'SPU的唯一标识码';
COMMENT ON COLUMN "public"."products_spu"."description" IS 'SPU的详细描述信息';
COMMENT ON COLUMN "public"."products_spu"."specifications" IS '产品的技术规格和参数说明';
COMMENT ON COLUMN "public"."products_spu"."usage_scenario" IS '产品的适用场景和使用建议';
COMMENT ON COLUMN "public"."products_spu"."is_active" IS 'SPU状态，false表示已禁用';
COMMENT ON COLUMN "public"."products_spu"."created_at" IS 'SPU创建的时间戳';
COMMENT ON COLUMN "public"."products_spu"."updated_at" IS 'SPU最后更新的时间戳';
COMMENT ON COLUMN "public"."products_spu"."category_id" IS '所属的产品分类ID';
COMMENT ON COLUMN "public"."products_spu"."created_by_id" IS '创建此SPU的用户ID';
COMMENT ON COLUMN "public"."products_spu"."brand_id" IS '所属的品牌ID';
COMMENT ON TABLE "public"."products_spu" IS '标准产品单元(SPU)表 - 定义产品的通用属性和模板';

-- ----------------------------
-- Table structure for products_spuattribute
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_spuattribute";
CREATE TABLE "public"."products_spuattribute" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "is_required" bool NOT NULL,
  "default_value" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "order" int4 NOT NULL,
  "attribute_id" int8 NOT NULL,
  "spu_id" int8 NOT NULL
)
;
ALTER TABLE "public"."products_spuattribute" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_spuattribute"."is_required" IS '在此SPU下创建SKU时是否必须配置此属性';
COMMENT ON COLUMN "public"."products_spuattribute"."default_value" IS '此属性在该SPU下的默认值';
COMMENT ON COLUMN "public"."products_spuattribute"."order" IS '属性在该SPU下的显示顺序';
COMMENT ON COLUMN "public"."products_spuattribute"."attribute_id" IS '关联的属性ID';
COMMENT ON COLUMN "public"."products_spuattribute"."spu_id" IS '关联的SPU ID';
COMMENT ON TABLE "public"."products_spuattribute" IS 'SPU属性关联表 - 定义每个SPU支持的属性配置';

-- ----------------------------
-- Table structure for products_spudimensiontemplate
-- ----------------------------
DROP TABLE IF EXISTS "public"."products_spudimensiontemplate";
CREATE TABLE "public"."products_spudimensiontemplate" (
  "id" int8 NOT NULL GENERATED BY DEFAULT AS IDENTITY (
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1
),
  "dimension_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "default_value" numeric(10,2) NOT NULL,
  "min_value" numeric(10,2),
  "max_value" numeric(10,2),
  "unit" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "custom_unit" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "tolerance" numeric(10,2) NOT NULL,
  "is_required" bool NOT NULL,
  "is_key_dimension" bool NOT NULL,
  "description" text COLLATE "pg_catalog"."default" NOT NULL,
  "order" int4 NOT NULL,
  "created_at" timestamptz(6) NOT NULL,
  "updated_at" timestamptz(6) NOT NULL,
  "created_by_id" int4,
  "spu_id" int8 NOT NULL
)
;
ALTER TABLE "public"."products_spudimensiontemplate" OWNER TO "postgres";
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."dimension_type" IS '尺寸的类型，如高度、宽度、厚度等';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."default_value" IS 'SPU的默认尺寸值';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."min_value" IS '允许的最小尺寸值';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."max_value" IS '允许的最大尺寸值';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."unit" IS '尺寸的计量单位';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."custom_unit" IS '自定义的计量单位';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."tolerance" IS '尺寸的允许公差范围';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."is_required" IS '基于此SPU创建SKU时是否必须设置此尺寸';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."is_key_dimension" IS '是否为影响定价的关键尺寸';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."description" IS '尺寸的详细描述和说明';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."order" IS '尺寸在SPU下的显示顺序';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."created_at" IS '记录创建的时间戳';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."updated_at" IS '记录最后更新的时间戳';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."created_by_id" IS '创建此记录的用户ID';
COMMENT ON COLUMN "public"."products_spudimensiontemplate"."spu_id" IS '关联的SPU产品单元';
COMMENT ON TABLE "public"."products_spudimensiontemplate" IS 'SPU尺寸模板表 - 定义SPU级别的标准尺寸模板';

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_group_id_seq"
OWNED BY "public"."auth_group"."id";
SELECT setval('"public"."auth_group_id_seq"', 3, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_group_permissions_id_seq"
OWNED BY "public"."auth_group_permissions"."id";
SELECT setval('"public"."auth_group_permissions_id_seq"', 42, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_permission_id_seq"
OWNED BY "public"."auth_permission"."id";
SELECT setval('"public"."auth_permission_id_seq"', 72, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_user_groups_id_seq"
OWNED BY "public"."auth_user_groups"."id";
SELECT setval('"public"."auth_user_groups_id_seq"', 2, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_user_id_seq"
OWNED BY "public"."auth_user"."id";
SELECT setval('"public"."auth_user_id_seq"', 7, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."auth_user_user_permissions_id_seq"
OWNED BY "public"."auth_user_user_permissions"."id";
SELECT setval('"public"."auth_user_user_permissions_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_admin_log_id_seq"
OWNED BY "public"."django_admin_log"."id";
SELECT setval('"public"."django_admin_log_id_seq"', 50, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_content_type_id_seq"
OWNED BY "public"."django_content_type"."id";
SELECT setval('"public"."django_content_type_id_seq"', 18, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."django_migrations_id_seq"
OWNED BY "public"."django_migrations"."id";
SELECT setval('"public"."django_migrations_id_seq"', 30, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_attribute_id_seq"
OWNED BY "public"."products_attribute"."id";
SELECT setval('"public"."products_attribute_id_seq"', 48, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_attributevalue_id_seq"
OWNED BY "public"."products_attributevalue"."id";
SELECT setval('"public"."products_attributevalue_id_seq"', 200, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_brand_id_seq"
OWNED BY "public"."products_brand"."id";
SELECT setval('"public"."products_brand_id_seq"', 23, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_category_id_seq"
OWNED BY "public"."products_category"."id";
SELECT setval('"public"."products_category_id_seq"', 53, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_productimage_id_seq"
OWNED BY "public"."products_productimage"."id";
SELECT setval('"public"."products_productimage_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_productsdimension_id_seq"
OWNED BY "public"."products_productsdimension"."id";
SELECT setval('"public"."products_productsdimension_id_seq"', 16, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_productspricingrule_id_seq"
OWNED BY "public"."products_pricing_rule"."id";
SELECT setval('"public"."products_productspricingrule_id_seq"', 10, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_sku_id_seq"
OWNED BY "public"."products_sku"."id";
SELECT setval('"public"."products_sku_id_seq"', 210, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_skuattributevalue_id_seq"
OWNED BY "public"."products_skuattributevalue"."id";
SELECT setval('"public"."products_skuattributevalue_id_seq"', 197, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_spu_id_seq"
OWNED BY "public"."products_spu"."id";
SELECT setval('"public"."products_spu_id_seq"', 53, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_spuattribute_id_seq"
OWNED BY "public"."products_spuattribute"."id";
SELECT setval('"public"."products_spuattribute_id_seq"', 141, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."products_spudimensiontemplate_id_seq"
OWNED BY "public"."products_spudimensiontemplate"."id";
SELECT setval('"public"."products_spudimensiontemplate_id_seq"', 3, true);

-- ----------------------------
-- Indexes structure for table auth_group
-- ----------------------------
CREATE INDEX "auth_group_name_a6ea08ec_like" ON "public"."auth_group" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_group
-- ----------------------------
ALTER TABLE "public"."auth_group" ADD CONSTRAINT "auth_group_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table auth_group
-- ----------------------------
ALTER TABLE "public"."auth_group" ADD CONSTRAINT "auth_group_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table auth_group_permissions
-- ----------------------------
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "public"."auth_group_permissions" USING btree (
  "group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "public"."auth_group_permissions" USING btree (
  "permission_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_group_permissions
-- ----------------------------
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" UNIQUE ("group_id", "permission_id");

-- ----------------------------
-- Primary Key structure for table auth_group_permissions
-- ----------------------------
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table auth_permission
-- ----------------------------
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "public"."auth_permission" USING btree (
  "content_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_permission
-- ----------------------------
ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_content_type_id_codename_01ab375a_uniq" UNIQUE ("content_type_id", "codename");

-- ----------------------------
-- Primary Key structure for table auth_permission
-- ----------------------------
ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table auth_user
-- ----------------------------
CREATE INDEX "auth_user_username_6821ab7c_like" ON "public"."auth_user" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_user
-- ----------------------------
ALTER TABLE "public"."auth_user" ADD CONSTRAINT "auth_user_username_key" UNIQUE ("username");

-- ----------------------------
-- Primary Key structure for table auth_user
-- ----------------------------
ALTER TABLE "public"."auth_user" ADD CONSTRAINT "auth_user_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table auth_user_groups
-- ----------------------------
CREATE INDEX "auth_user_groups_group_id_97559544" ON "public"."auth_user_groups" USING btree (
  "group_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "public"."auth_user_groups" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_user_groups
-- ----------------------------
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_user_id_group_id_94350c0c_uniq" UNIQUE ("user_id", "group_id");

-- ----------------------------
-- Primary Key structure for table auth_user_groups
-- ----------------------------
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table auth_user_user_permissions
-- ----------------------------
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "public"."auth_user_user_permissions" USING btree (
  "permission_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "public"."auth_user_user_permissions" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table auth_user_user_permissions
-- ----------------------------
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" UNIQUE ("user_id", "permission_id");

-- ----------------------------
-- Primary Key structure for table auth_user_user_permissions
-- ----------------------------
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table django_admin_log
-- ----------------------------
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "public"."django_admin_log" USING btree (
  "content_type_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "public"."django_admin_log" USING btree (
  "user_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table django_admin_log
-- ----------------------------
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_action_flag_check" CHECK (action_flag >= 0);

-- ----------------------------
-- Primary Key structure for table django_admin_log
-- ----------------------------
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table django_content_type
-- ----------------------------
ALTER TABLE "public"."django_content_type" ADD CONSTRAINT "django_content_type_app_label_model_76bd3d3b_uniq" UNIQUE ("app_label", "model");

-- ----------------------------
-- Primary Key structure for table django_content_type
-- ----------------------------
ALTER TABLE "public"."django_content_type" ADD CONSTRAINT "django_content_type_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table django_migrations
-- ----------------------------
ALTER TABLE "public"."django_migrations" ADD CONSTRAINT "django_migrations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table django_session
-- ----------------------------
CREATE INDEX "django_session_expire_date_a5c62663" ON "public"."django_session" USING btree (
  "expire_date" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "django_session_session_key_c0390e0f_like" ON "public"."django_session" USING btree (
  "session_key" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table django_session
-- ----------------------------
ALTER TABLE "public"."django_session" ADD CONSTRAINT "django_session_pkey" PRIMARY KEY ("session_key");

-- ----------------------------
-- Indexes structure for table products_attribute
-- ----------------------------
CREATE INDEX "idx_attribute_active" ON "public"."products_attribute" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_attribute_code" ON "public"."products_attribute" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_attribute_order" ON "public"."products_attribute" USING btree (
  "order" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "idx_attribute_type" ON "public"."products_attribute" USING btree (
  "type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "products_attribute_code_b06e9e14_like" ON "public"."products_attribute" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_attribute
-- ----------------------------
ALTER TABLE "public"."products_attribute" ADD CONSTRAINT "products_attribute_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table products_attribute
-- ----------------------------
ALTER TABLE "public"."products_attribute" ADD CONSTRAINT "products_attribute_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_attributevalue
-- ----------------------------
CREATE INDEX "idx_attr_value_active" ON "public"."products_attributevalue" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_attr_value_attribute" ON "public"."products_attributevalue" USING btree (
  "attribute_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_attr_value_order" ON "public"."products_attributevalue" USING btree (
  "order" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "products_attributevalue_attribute_id_82b9ba3c" ON "public"."products_attributevalue" USING btree (
  "attribute_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_attributevalue
-- ----------------------------
ALTER TABLE "public"."products_attributevalue" ADD CONSTRAINT "products_attributevalue_attribute_id_value_8f272b11_uniq" UNIQUE ("attribute_id", "value");

-- ----------------------------
-- Primary Key structure for table products_attributevalue
-- ----------------------------
ALTER TABLE "public"."products_attributevalue" ADD CONSTRAINT "products_attributevalue_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_brand
-- ----------------------------
CREATE INDEX "idx_brand_active" ON "public"."products_brand" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_brand_code" ON "public"."products_brand" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_brand_name" ON "public"."products_brand" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "products_brand_code_303886bf_like" ON "public"."products_brand" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_brand
-- ----------------------------
ALTER TABLE "public"."products_brand" ADD CONSTRAINT "products_brand_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table products_brand
-- ----------------------------
ALTER TABLE "public"."products_brand" ADD CONSTRAINT "products_brand_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_category
-- ----------------------------
CREATE INDEX "idx_category_active" ON "public"."products_category" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_category_code" ON "public"."products_category" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_category_parent" ON "public"."products_category" USING btree (
  "parent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_category_code_320f842a_like" ON "public"."products_category" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "products_category_parent_id_3388f6c9" ON "public"."products_category" USING btree (
  "parent_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_category_tree_id_7d9b3ae8" ON "public"."products_category" USING btree (
  "tree_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_category
-- ----------------------------
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_code_key" UNIQUE ("code");

-- ----------------------------
-- Checks structure for table products_category
-- ----------------------------
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_rght_check" CHECK (rght >= 0);
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_level_check" CHECK (level >= 0);
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_tree_id_check" CHECK (tree_id >= 0);
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_lft_check" CHECK (lft >= 0);

-- ----------------------------
-- Primary Key structure for table products_category
-- ----------------------------
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_pricing_rule
-- ----------------------------
CREATE INDEX "products_pricing_rule_sku_id_069983f3" ON "public"."products_pricing_rule" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_productspricingrule_created_by_id_1511c8ad" ON "public"."products_pricing_rule" USING btree (
  "created_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "products_productspricingrule_spu_id_99bbb065" ON "public"."products_pricing_rule" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_pricing_rule
-- ----------------------------
ALTER TABLE "public"."products_pricing_rule" ADD CONSTRAINT "products_productspricing_spu_id_sku_id_rule_type__b72c1b87_uniq" UNIQUE ("spu_id", "sku_id", "rule_type", "threshold_value");

-- ----------------------------
-- Primary Key structure for table products_pricing_rule
-- ----------------------------
ALTER TABLE "public"."products_pricing_rule" ADD CONSTRAINT "products_productspricingrule_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_productimage
-- ----------------------------
CREATE INDEX "idx_product_image_active" ON "public"."products_productimage" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_product_image_order" ON "public"."products_productimage" USING btree (
  "order" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "idx_product_image_sku" ON "public"."products_productimage" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_productimage_sku_id_1ec0d2f5" ON "public"."products_productimage" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table products_productimage
-- ----------------------------
ALTER TABLE "public"."products_productimage" ADD CONSTRAINT "products_productimage_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_productsdimension
-- ----------------------------
CREATE INDEX "idx_dimension_key" ON "public"."products_productsdimension" USING btree (
  "is_key_dimension" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_dimension_sku" ON "public"."products_productsdimension" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_dimension_standard" ON "public"."products_productsdimension" USING btree (
  "standard_value" "pg_catalog"."numeric_ops" ASC NULLS LAST
);
CREATE INDEX "idx_dimension_type" ON "public"."products_productsdimension" USING btree (
  "dimension_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "products_productsdimension_created_by_id_2afe9cd1" ON "public"."products_productsdimension" USING btree (
  "created_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "products_productsdimension_sku_id_af626b72" ON "public"."products_productsdimension" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_productsdimension
-- ----------------------------
ALTER TABLE "public"."products_productsdimension" ADD CONSTRAINT "unique_dimension_per_sku_type" UNIQUE ("sku_id", "dimension_type");

-- ----------------------------
-- Primary Key structure for table products_productsdimension
-- ----------------------------
ALTER TABLE "public"."products_productsdimension" ADD CONSTRAINT "products_productsdimension_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_sku
-- ----------------------------
CREATE INDEX "idx_sku_brand" ON "public"."products_sku" USING btree (
  "brand_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_code" ON "public"."products_sku" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_featured" ON "public"."products_sku" USING btree (
  "is_featured" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_spu" ON "public"."products_sku" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_status" ON "public"."products_sku" USING btree (
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_stock" ON "public"."products_sku" USING btree (
  "stock_quantity" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "products_sku_brand_id_2c917ca5" ON "public"."products_sku" USING btree (
  "brand_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_sku_code_99b8ad43_like" ON "public"."products_sku" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "products_sku_created_by_id_097b2110" ON "public"."products_sku" USING btree (
  "created_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "products_sku_spu_id_af64614e" ON "public"."products_sku" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_sku
-- ----------------------------
ALTER TABLE "public"."products_sku" ADD CONSTRAINT "products_sku_code_key" UNIQUE ("code");
ALTER TABLE "public"."products_sku" ADD CONSTRAINT "products_sku_sku_id_key" UNIQUE ("sku_id");

-- ----------------------------
-- Primary Key structure for table products_sku
-- ----------------------------
ALTER TABLE "public"."products_sku" ADD CONSTRAINT "products_sku_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_skuattributevalue
-- ----------------------------
CREATE INDEX "idx_sku_attr_val_attr" ON "public"."products_skuattributevalue" USING btree (
  "attribute_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_attr_val_sku" ON "public"."products_skuattributevalue" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_sku_attr_val_value" ON "public"."products_skuattributevalue" USING btree (
  "attribute_value_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_skuattributevalue_attribute_id_3fe84c71" ON "public"."products_skuattributevalue" USING btree (
  "attribute_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_skuattributevalue_attribute_value_id_7e162ce3" ON "public"."products_skuattributevalue" USING btree (
  "attribute_value_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_skuattributevalue_sku_id_6a4eebf6" ON "public"."products_skuattributevalue" USING btree (
  "sku_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_skuattributevalue
-- ----------------------------
ALTER TABLE "public"."products_skuattributevalue" ADD CONSTRAINT "products_skuattributevalue_sku_id_attribute_id_8280d46b_uniq" UNIQUE ("sku_id", "attribute_id");

-- ----------------------------
-- Primary Key structure for table products_skuattributevalue
-- ----------------------------
ALTER TABLE "public"."products_skuattributevalue" ADD CONSTRAINT "products_skuattributevalue_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_spu
-- ----------------------------
CREATE INDEX "idx_spu_active" ON "public"."products_spu" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_brand" ON "public"."products_spu" USING btree (
  "brand_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_category" ON "public"."products_spu" USING btree (
  "category_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_code" ON "public"."products_spu" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "products_spu_brand_id_a63f3446" ON "public"."products_spu" USING btree (
  "brand_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_spu_category_id_511302ba" ON "public"."products_spu" USING btree (
  "category_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_spu_code_6fa05456_like" ON "public"."products_spu" USING btree (
  "code" COLLATE "pg_catalog"."default" "pg_catalog"."varchar_pattern_ops" ASC NULLS LAST
);
CREATE INDEX "products_spu_created_by_id_11d4b1b0" ON "public"."products_spu" USING btree (
  "created_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_spu
-- ----------------------------
ALTER TABLE "public"."products_spu" ADD CONSTRAINT "products_spu_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table products_spu
-- ----------------------------
ALTER TABLE "public"."products_spu" ADD CONSTRAINT "products_spu_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_spuattribute
-- ----------------------------
CREATE INDEX "idx_spu_attr_attribute" ON "public"."products_spuattribute" USING btree (
  "attribute_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_attr_spu" ON "public"."products_spuattribute" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_spuattribute_attribute_id_a76ea316" ON "public"."products_spuattribute" USING btree (
  "attribute_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "products_spuattribute_spu_id_cb135248" ON "public"."products_spuattribute" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_spuattribute
-- ----------------------------
ALTER TABLE "public"."products_spuattribute" ADD CONSTRAINT "products_spuattribute_spu_id_attribute_id_243dfc46_uniq" UNIQUE ("spu_id", "attribute_id");

-- ----------------------------
-- Primary Key structure for table products_spuattribute
-- ----------------------------
ALTER TABLE "public"."products_spuattribute" ADD CONSTRAINT "products_spuattribute_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table products_spudimensiontemplate
-- ----------------------------
CREATE INDEX "idx_spu_dim_tmpl_key" ON "public"."products_spudimensiontemplate" USING btree (
  "is_key_dimension" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_dim_tmpl_order" ON "public"."products_spudimensiontemplate" USING btree (
  "order" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_dim_tmpl_spu" ON "public"."products_spudimensiontemplate" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);
CREATE INDEX "idx_spu_dim_tmpl_type" ON "public"."products_spudimensiontemplate" USING btree (
  "dimension_type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "products_spudimensiontemplate_created_by_id_cbb77f9e" ON "public"."products_spudimensiontemplate" USING btree (
  "created_by_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);
CREATE INDEX "products_spudimensiontemplate_spu_id_de46a9c5" ON "public"."products_spudimensiontemplate" USING btree (
  "spu_id" "pg_catalog"."int8_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table products_spudimensiontemplate
-- ----------------------------
ALTER TABLE "public"."products_spudimensiontemplate" ADD CONSTRAINT "unique_spu_dim_tmpl_per_type" UNIQUE ("spu_id", "dimension_type");

-- ----------------------------
-- Primary Key structure for table products_spudimensiontemplate
-- ----------------------------
ALTER TABLE "public"."products_spudimensiontemplate" ADD CONSTRAINT "products_spudimensiontemplate_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table auth_group_permissions
-- ----------------------------
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "public"."auth_permission" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."auth_group_permissions" ADD CONSTRAINT "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "public"."auth_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_permission
-- ----------------------------
ALTER TABLE "public"."auth_permission" ADD CONSTRAINT "auth_permission_content_type_id_2f476e4b_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "public"."django_content_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_user_groups
-- ----------------------------
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_group_id_97559544_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "public"."auth_group" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."auth_user_groups" ADD CONSTRAINT "auth_user_groups_user_id_6a12ed8b_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table auth_user_user_permissions
-- ----------------------------
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm" FOREIGN KEY ("permission_id") REFERENCES "public"."auth_permission" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."auth_user_user_permissions" ADD CONSTRAINT "auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table django_admin_log
-- ----------------------------
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_content_type_id_c4bce8eb_fk_django_co" FOREIGN KEY ("content_type_id") REFERENCES "public"."django_content_type" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."django_admin_log" ADD CONSTRAINT "django_admin_log_user_id_c564eba6_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_attributevalue
-- ----------------------------
ALTER TABLE "public"."products_attributevalue" ADD CONSTRAINT "products_attributeva_attribute_id_82b9ba3c_fk_products_" FOREIGN KEY ("attribute_id") REFERENCES "public"."products_attribute" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_category
-- ----------------------------
ALTER TABLE "public"."products_category" ADD CONSTRAINT "products_category_parent_id_3388f6c9_fk_products_category_id" FOREIGN KEY ("parent_id") REFERENCES "public"."products_category" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_pricing_rule
-- ----------------------------
ALTER TABLE "public"."products_pricing_rule" ADD CONSTRAINT "products_productspri_created_by_id_1511c8ad_fk_auth_user" FOREIGN KEY ("created_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_pricing_rule" ADD CONSTRAINT "products_productspricingrule_sku_id_6e45a351_fk_products_sku_id" FOREIGN KEY ("sku_id") REFERENCES "public"."products_sku" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_pricing_rule" ADD CONSTRAINT "products_productspricingrule_spu_id_99bbb065_fk_products_spu_id" FOREIGN KEY ("spu_id") REFERENCES "public"."products_spu" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_productimage
-- ----------------------------
ALTER TABLE "public"."products_productimage" ADD CONSTRAINT "products_productimage_sku_id_1ec0d2f5_fk_products_sku_id" FOREIGN KEY ("sku_id") REFERENCES "public"."products_sku" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_productsdimension
-- ----------------------------
ALTER TABLE "public"."products_productsdimension" ADD CONSTRAINT "products_productsdim_created_by_id_2afe9cd1_fk_auth_user" FOREIGN KEY ("created_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_productsdimension" ADD CONSTRAINT "products_productsdimension_sku_id_af626b72_fk_products_sku_id" FOREIGN KEY ("sku_id") REFERENCES "public"."products_sku" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_sku
-- ----------------------------
ALTER TABLE "public"."products_sku" ADD CONSTRAINT "products_sku_brand_id_2c917ca5_fk_products_brand_id" FOREIGN KEY ("brand_id") REFERENCES "public"."products_brand" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_sku" ADD CONSTRAINT "products_sku_created_by_id_097b2110_fk_auth_user_id" FOREIGN KEY ("created_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_sku" ADD CONSTRAINT "products_sku_spu_id_af64614e_fk_products_spu_id" FOREIGN KEY ("spu_id") REFERENCES "public"."products_spu" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_skuattributevalue
-- ----------------------------
ALTER TABLE "public"."products_skuattributevalue" ADD CONSTRAINT "products_skuattribut_attribute_id_3fe84c71_fk_products_" FOREIGN KEY ("attribute_id") REFERENCES "public"."products_attribute" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_skuattributevalue" ADD CONSTRAINT "products_skuattribut_attribute_value_id_7e162ce3_fk_products_" FOREIGN KEY ("attribute_value_id") REFERENCES "public"."products_attributevalue" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_skuattributevalue" ADD CONSTRAINT "products_skuattributevalue_sku_id_6a4eebf6_fk_products_sku_id" FOREIGN KEY ("sku_id") REFERENCES "public"."products_sku" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_spu
-- ----------------------------
ALTER TABLE "public"."products_spu" ADD CONSTRAINT "products_spu_brand_id_a63f3446_fk_products_brand_id" FOREIGN KEY ("brand_id") REFERENCES "public"."products_brand" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_spu" ADD CONSTRAINT "products_spu_category_id_511302ba_fk_products_category_id" FOREIGN KEY ("category_id") REFERENCES "public"."products_category" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_spu" ADD CONSTRAINT "products_spu_created_by_id_11d4b1b0_fk_auth_user_id" FOREIGN KEY ("created_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_spuattribute
-- ----------------------------
ALTER TABLE "public"."products_spuattribute" ADD CONSTRAINT "products_spuattribut_attribute_id_a76ea316_fk_products_" FOREIGN KEY ("attribute_id") REFERENCES "public"."products_attribute" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_spuattribute" ADD CONSTRAINT "products_spuattribute_spu_id_cb135248_fk_products_spu_id" FOREIGN KEY ("spu_id") REFERENCES "public"."products_spu" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

-- ----------------------------
-- Foreign Keys structure for table products_spudimensiontemplate
-- ----------------------------
ALTER TABLE "public"."products_spudimensiontemplate" ADD CONSTRAINT "products_spudimensio_created_by_id_cbb77f9e_fk_auth_user" FOREIGN KEY ("created_by_id") REFERENCES "public"."auth_user" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "public"."products_spudimensiontemplate" ADD CONSTRAINT "products_spudimensio_spu_id_de46a9c5_fk_products_" FOREIGN KEY ("spu_id") REFERENCES "public"."products_spu" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;
