--------------------------------------------------------
-- Archivo creado  - martes-enero-09-2024   
--------------------------------------------------------
--------------------------------------------------------
--  DDL for Table FIDECOMISOS_TIPODEDOCUMENTO
--------------------------------------------------------

  CREATE TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" 
   (	"TIPODOCUMENTO" NVARCHAR2(3), 
	"DESCRIPCION" NVARCHAR2(100), 
	"IDTIPOPERSONA_ID" NUMBER(11,0)
   ) SEGMENT CREATION IMMEDIATE 
  PCTFREE 10 PCTUSED 40 INITRANS 1 MAXTRANS 255 
 NOCOMPRESS LOGGING
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS" ;
REM INSERTING into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO
SET DEFINE OFF;
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('TI','Tarjeta de Identidad','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('CE','C�dula de Extranjer�a','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('NN','NIT Persona Natural','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('NE','NIT Persona Extranjera','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('NJ','NIT Persona Jur�dica','1');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('PA','Pasaporte','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('RC','Registro Civil','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('RM','Registro Medico','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('RU','Numero unico identificacion','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('PEP','Permiso Especial Permanencia','2');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('EE','Empresas Extranjeras','1');
Insert into SGC_SOFTWARE_DEV_F.FIDECOMISOS_TIPODEDOCUMENTO (TIPODOCUMENTO,DESCRIPCION,IDTIPOPERSONA_ID) values ('CC','C�dula de Ciudadan�a','2');
--------------------------------------------------------
--  DDL for Index SYS_C0011644
--------------------------------------------------------

  CREATE UNIQUE INDEX "SGC_SOFTWARE_DEV_F"."SYS_C0011644" ON "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" ("TIPODOCUMENTO") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  DDL for Index FIDECOMISO_IDTIPOPERS_94790070
--------------------------------------------------------

  CREATE INDEX "SGC_SOFTWARE_DEV_F"."FIDECOMISO_IDTIPOPERS_94790070" ON "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" ("IDTIPOPERSONA_ID") 
  PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS" ;
--------------------------------------------------------
--  Constraints for Table FIDECOMISOS_TIPODEDOCUMENTO
--------------------------------------------------------

  ALTER TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" MODIFY ("TIPODOCUMENTO" NOT NULL ENABLE);
  ALTER TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" MODIFY ("IDTIPOPERSONA_ID" NOT NULL ENABLE);
  ALTER TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" ADD PRIMARY KEY ("TIPODOCUMENTO")
  USING INDEX PCTFREE 10 INITRANS 2 MAXTRANS 255 COMPUTE STATISTICS 
  STORAGE(INITIAL 65536 NEXT 1048576 MINEXTENTS 1 MAXEXTENTS 2147483645
  PCTINCREASE 0 FREELISTS 1 FREELIST GROUPS 1
  BUFFER_POOL DEFAULT FLASH_CACHE DEFAULT CELL_FLASH_CACHE DEFAULT)
  TABLESPACE "USERS"  ENABLE;
--------------------------------------------------------
--  Ref Constraints for Table FIDECOMISOS_TIPODEDOCUMENTO
--------------------------------------------------------

  ALTER TABLE "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEDOCUMENTO" ADD CONSTRAINT "FIDECOMIS_IDTIPOPER_94790070_F" FOREIGN KEY ("IDTIPOPERSONA_ID")
	  REFERENCES "SGC_SOFTWARE_DEV_F"."FIDECOMISOS_TIPODEPERSONA" ("ID") DEFERRABLE INITIALLY DEFERRED ENABLE;
