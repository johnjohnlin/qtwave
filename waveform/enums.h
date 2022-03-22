#pragma once

#ifdef __cplusplus
#define ENUMINT :int
#else
#define ENUMINT
#endif

enum fstWriterPackType ENUMINT {
    FST_WR_PT_ZLIB             = 0,
    FST_WR_PT_FASTLZ           = 1,
    FST_WR_PT_LZ4              = 2
};

enum fstFileType ENUMINT {
    FST_FT_MIN                 = 0,

    FST_FT_VERILOG             = 0,
    FST_FT_VHDL                = 1,
    FST_FT_VERILOG_VHDL        = 2,

    FST_FT_MAX                 = 2
};

enum fstBlockType ENUMINT {
    FST_BL_HDR                 = 0,
    FST_BL_VCDATA              = 1,
    FST_BL_BLACKOUT            = 2,
    FST_BL_GEOM                = 3,
    FST_BL_HIER                = 4,
    FST_BL_VCDATA_DYN_ALIAS    = 5,
    FST_BL_HIER_LZ4            = 6,
    FST_BL_HIER_LZ4DUO         = 7,
    FST_BL_VCDATA_DYN_ALIAS2   = 8,

    FST_BL_ZWRAPPER            = 254,   /* indicates that whole trace is gz wrapped */
    FST_BL_SKIP                = 255    /* used while block is being written */
};

enum fstScopeType ENUMINT {
    FST_ST_MIN                 = 0,

    FST_ST_VCD_MODULE          = 0,
    FST_ST_VCD_TASK            = 1,
    FST_ST_VCD_FUNCTION        = 2,
    FST_ST_VCD_BEGIN           = 3,
    FST_ST_VCD_FORK            = 4,
    FST_ST_VCD_GENERATE        = 5,
    FST_ST_VCD_STRUCT          = 6,
    FST_ST_VCD_UNION           = 7,
    FST_ST_VCD_CLASS           = 8,
    FST_ST_VCD_INTERFACE       = 9,
    FST_ST_VCD_PACKAGE         = 10,
    FST_ST_VCD_PROGRAM         = 11,

    FST_ST_VHDL_ARCHITECTURE   = 12,
    FST_ST_VHDL_PROCEDURE      = 13,
    FST_ST_VHDL_FUNCTION       = 14,
    FST_ST_VHDL_RECORD         = 15,
    FST_ST_VHDL_PROCESS        = 16,
    FST_ST_VHDL_BLOCK          = 17,
    FST_ST_VHDL_FOR_GENERATE   = 18,
    FST_ST_VHDL_IF_GENERATE    = 19,
    FST_ST_VHDL_GENERATE       = 20,
    FST_ST_VHDL_PACKAGE        = 21,

    FST_ST_MAX                 = 21,

    FST_ST_GEN_ATTRBEGIN       = 252,
    FST_ST_GEN_ATTREND         = 253,

    FST_ST_VCD_SCOPE           = 254,
    FST_ST_VCD_UPSCOPE         = 255
};

enum fstVarType ENUMINT {
    FST_VT_MIN                 = 0,     /* start of vartypes */

    FST_VT_VCD_EVENT           = 0,
    FST_VT_VCD_INTEGER         = 1,
    FST_VT_VCD_PARAMETER       = 2,
    FST_VT_VCD_REAL            = 3,
    FST_VT_VCD_REAL_PARAMETER  = 4,
    FST_VT_VCD_REG             = 5,
    FST_VT_VCD_SUPPLY0         = 6,
    FST_VT_VCD_SUPPLY1         = 7,
    FST_VT_VCD_TIME            = 8,
    FST_VT_VCD_TRI             = 9,
    FST_VT_VCD_TRIAND          = 10,
    FST_VT_VCD_TRIOR           = 11,
    FST_VT_VCD_TRIREG          = 12,
    FST_VT_VCD_TRI0            = 13,
    FST_VT_VCD_TRI1            = 14,
    FST_VT_VCD_WAND            = 15,
    FST_VT_VCD_WIRE            = 16,
    FST_VT_VCD_WOR             = 17,
    FST_VT_VCD_PORT            = 18,
    FST_VT_VCD_SPARRAY         = 19,    /* used to define the rownum (index) port for a sparse array */
    FST_VT_VCD_REALTIME        = 20,

    FST_VT_GEN_STRING          = 21,    /* generic string type   (max len is defined dynamically via fstWriterEmitVariableLengthValueChange) */

    FST_VT_SV_BIT              = 22,
    FST_VT_SV_LOGIC            = 23,
    FST_VT_SV_INT              = 24,    /* declare as size = 32 */
    FST_VT_SV_SHORTINT         = 25,    /* declare as size = 16 */
    FST_VT_SV_LONGINT          = 26,    /* declare as size = 64 */
    FST_VT_SV_BYTE             = 27,    /* declare as size = 8  */
    FST_VT_SV_ENUM             = 28,    /* declare as appropriate type range */
    FST_VT_SV_SHORTREAL        = 29,    /* declare and emit same as FST_VT_VCD_REAL (needs to be emitted as double, not a float) */

    FST_VT_MAX                 = 29     /* end of vartypes */
};

enum fstVarDir ENUMINT {
    FST_VD_MIN         = 0,

    FST_VD_IMPLICIT    = 0,
    FST_VD_INPUT       = 1,
    FST_VD_OUTPUT      = 2,
    FST_VD_INOUT       = 3,
    FST_VD_BUFFER      = 4,
    FST_VD_LINKAGE     = 5,

    FST_VD_MAX         = 5
};

enum fstHierType ENUMINT {
    FST_HT_MIN         = 0,

    FST_HT_SCOPE       = 0,
    FST_HT_UPSCOPE     = 1,
    FST_HT_VAR         = 2,
    FST_HT_ATTRBEGIN   = 3,
    FST_HT_ATTREND     = 4,

    /* FST_HT_TREEBEGIN and FST_HT_TREEEND are not yet used by FST but are currently used when fstHier bridges other formats */
    FST_HT_TREEBEGIN   = 5,
    FST_HT_TREEEND     = 6,

    FST_HT_MAX         = 6
};

enum fstAttrType ENUMINT {
    FST_AT_MIN         = 0,

    FST_AT_MISC        = 0,     /* self-contained: does not need matching FST_HT_ATTREND */
    FST_AT_ARRAY       = 1,
    FST_AT_ENUM        = 2,
    FST_AT_PACK        = 3,

    FST_AT_MAX         = 3
};

enum fstMiscType ENUMINT {
    FST_MT_MIN         = 0,

    FST_MT_COMMENT     = 0,     /* use fstWriterSetComment() to emit */
    FST_MT_ENVVAR      = 1,     /* use fstWriterSetEnvVar() to emit */
    FST_MT_SUPVAR      = 2,     /* use fstWriterCreateVar2() to emit */
    FST_MT_PATHNAME    = 3,     /* reserved for fstWriterSetSourceStem() string -> number management */
    FST_MT_SOURCESTEM  = 4,     /* use fstWriterSetSourceStem() to emit */
    FST_MT_SOURCEISTEM = 5,     /* use fstWriterSetSourceInstantiationStem() to emit */
    FST_MT_VALUELIST   = 6,	/* use fstWriterSetValueList() to emit, followed by fstWriterCreateVar*() */
    FST_MT_ENUMTABLE   = 7,	/* use fstWriterCreateEnumTable() and fstWriterEmitEnumTableRef() to emit */
    FST_MT_UNKNOWN     = 8,

    FST_MT_MAX         = 8
};

enum fstArrayType ENUMINT {
    FST_AR_MIN         = 0,

    FST_AR_NONE        = 0,
    FST_AR_UNPACKED    = 1,
    FST_AR_PACKED      = 2,
    FST_AR_SPARSE      = 3,

    FST_AR_MAX         = 3
};

enum fstEnumValueType ENUMINT {
    FST_EV_SV_INTEGER           = 0,
    FST_EV_SV_BIT               = 1,
    FST_EV_SV_LOGIC             = 2,
    FST_EV_SV_INT               = 3,
    FST_EV_SV_SHORTINT          = 4,
    FST_EV_SV_LONGINT           = 5,
    FST_EV_SV_BYTE              = 6,
    FST_EV_SV_UNSIGNED_INTEGER  = 7,
    FST_EV_SV_UNSIGNED_BIT      = 8,
    FST_EV_SV_UNSIGNED_LOGIC    = 9,
    FST_EV_SV_UNSIGNED_INT      = 10,
    FST_EV_SV_UNSIGNED_SHORTINT = 11,
    FST_EV_SV_UNSIGNED_LONGINT  = 12,
    FST_EV_SV_UNSIGNED_BYTE     = 13,

    FST_EV_REG			= 14,
    FST_EV_TIME			= 15,

    FST_EV_MAX                  = 15
};

enum fstPackType ENUMINT {
    FST_PT_NONE          = 0,
    FST_PT_UNPACKED      = 1,
    FST_PT_PACKED        = 2,
    FST_PT_TAGGED_PACKED = 3,

    FST_PT_MAX           = 3
};

enum fstSupplementalVarType ENUMINT {
    FST_SVT_MIN                    = 0,

    FST_SVT_NONE                   = 0,

    FST_SVT_VHDL_SIGNAL            = 1,
    FST_SVT_VHDL_VARIABLE          = 2,
    FST_SVT_VHDL_CONSTANT          = 3,
    FST_SVT_VHDL_FILE              = 4,
    FST_SVT_VHDL_MEMORY            = 5,

    FST_SVT_MAX                    = 5
};

enum fstSupplementalDataType ENUMINT {
    FST_SDT_MIN                    = 0,

    FST_SDT_NONE                   = 0,

    FST_SDT_VHDL_BOOLEAN           = 1,
    FST_SDT_VHDL_BIT               = 2,
    FST_SDT_VHDL_BIT_VECTOR        = 3,
    FST_SDT_VHDL_STD_ULOGIC        = 4,
    FST_SDT_VHDL_STD_ULOGIC_VECTOR = 5,
    FST_SDT_VHDL_STD_LOGIC         = 6,
    FST_SDT_VHDL_STD_LOGIC_VECTOR  = 7,
    FST_SDT_VHDL_UNSIGNED          = 8,
    FST_SDT_VHDL_SIGNED            = 9,
    FST_SDT_VHDL_INTEGER           = 10,
    FST_SDT_VHDL_REAL              = 11,
    FST_SDT_VHDL_NATURAL           = 12,
    FST_SDT_VHDL_POSITIVE          = 13,
    FST_SDT_VHDL_TIME              = 14,
    FST_SDT_VHDL_CHARACTER         = 15,
    FST_SDT_VHDL_STRING            = 16,

    FST_SDT_MAX                    = 16,

    FST_SDT_SVT_SHIFT_COUNT        = 10, /* FST_SVT_* is ORed in by fstWriterCreateVar2() to the left after shifting FST_SDT_SVT_SHIFT_COUNT */
    FST_SDT_ABS_MAX                = ((1<<(FST_SDT_SVT_SHIFT_COUNT))-1)
};
