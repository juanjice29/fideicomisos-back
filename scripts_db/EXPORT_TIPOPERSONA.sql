--------------------------------------------------------
-- Archivo creado  - martes-enero-09-2024   
--------------------------------------------------------
--------------------------------------------------------
--  DDL for Table FIDECOMISOS_TIPODEPERSONA
--------------------------------------------------------

  CREATE TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEPERSONA" 
   (	"ID" NUMBER(11,0) GENERATED BY DEFAULT ON NULL AS IDENTITY MINVALUE 1 MAXVALUE 9999999999999999999999999999 INCREMENT BY 1 START WITH 1 CACHE 20 NOORDER  NOCYCLE  NOKEEP  NOSCALE , 
	"TIPOPERSONA" NVARCHAR2(3), 
	"DESCRIPTION" NVARCHAR2(100)
   ) SEGMENT CREATION IMMEDIATE 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS" ;
REM INSERTING into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEPERSONA
SET DEFINE OFF;
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEPERSONA (ID,TIPOPERSONA,DESCRIPTION) values ('1','J','PERSONA JURIDICA');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEPERSONA (ID,TIPOPERSONA,DESCRIPTION) values ('2','N','PERSONA NATURAL');
--------------------------------------------------------
--  DDL for Index SYS_C0011641
--------------------------------------------------------

  CREATE UNIQUE INDEX "SGC_SOFTWARE_DEV_F"."SYS_C0011641" ON "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEPERSONA" ("ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table FIDECOMISOS_TIPODEPERSONA
--------------------------------------------------------

  ALTER TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEPERSONA" MODIFY ("ID" NOT NULL ENABLE);
  ALTER TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEPERSONA" ADD PRIMARY KEY ("ID")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS"  ENABLE;