/*
 * Copyright (c) 2009-2018 Tony Bybell.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * SPDX-License-Identifier: MIT
 */

#ifndef FST_API_H
#define FST_API_H

#ifdef __cplusplus
extern "C" {
#endif

#include "enums.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <zlib.h>
#include <inttypes.h>
#if defined(_MSC_VER)
    #include "fst_win_unistd.h"
#else
    #include <unistd.h>
#endif
#include <time.h>

#define FST_RDLOAD "FSTLOAD | "

typedef uint32_t fstHandle;
typedef uint32_t fstEnumHandle;

struct fstHier
{
unsigned char htyp;

union {
        /* if htyp == FST_HT_SCOPE */
        struct fstHierScope {
                unsigned char typ; /* FST_ST_MIN ... FST_ST_MAX */
                const char *name;
                const char *component;
                uint32_t name_length;           /* strlen(u.scope.name) */
                uint32_t component_length;      /* strlen(u.scope.component) */
                } scope;

        /* if htyp == FST_HT_VAR */
        struct fstHierVar {
                unsigned char typ; /* FST_VT_MIN ... FST_VT_MAX */
                unsigned char direction; /* FST_VD_MIN ... FST_VD_MAX */
                unsigned char svt_workspace; /* zeroed out by FST reader, for client code use */
                unsigned char sdt_workspace; /* zeroed out by FST reader, for client code use */
                unsigned int  sxt_workspace; /* zeroed out by FST reader, for client code use */
                const char *name;
                uint32_t length;
                fstHandle handle;
                uint32_t name_length; /* strlen(u.var.name) */
                unsigned is_alias : 1;
                } var;

        /* if htyp == FST_HT_ATTRBEGIN */
        struct fstHierAttr {
                unsigned char typ; /* FST_AT_MIN ... FST_AT_MAX */
                unsigned char subtype; /* from fstMiscType, fstArrayType, fstEnumValueType, fstPackType */
                const char *name;
                uint64_t arg; /* number of array elements, struct members, or some other payload (possibly ignored) */
                uint64_t arg_from_name; /* for when name is overloaded as a variable-length integer (FST_AT_MISC + FST_MT_SOURCESTEM) */
                uint32_t name_length; /* strlen(u.attr.name) */
                } attr;
        } u;
};


struct fstETab
{
char *name;
uint32_t elem_count;
char **literal_arr;
char **val_arr;
};


/*
 * writer functions
 */
void            fstWriterClose(void *ctx);
void *          fstWriterCreate(const char *nam, int use_compressed_hier);
fstEnumHandle   fstWriterCreateEnumTable(void *ctx, const char *name, uint32_t elem_count, unsigned int min_valbits, const char **literal_arr, const char **val_arr);
                /* used for Verilog/SV */
fstHandle       fstWriterCreateVar(void *ctx, enum fstVarType vt, enum fstVarDir vd,
                        uint32_t len, const char *nam, fstHandle aliasHandle);
                /* future expansion for VHDL and other languages.  The variable type, data type, etc map onto
                   the current Verilog/SV one.  The "type" string is optional for a more verbose or custom description */
fstHandle       fstWriterCreateVar2(void *ctx, enum fstVarType vt, enum fstVarDir vd,
                        uint32_t len, const char *nam, fstHandle aliasHandle,
                        const char *type, enum fstSupplementalVarType svt, enum fstSupplementalDataType sdt);
void            fstWriterEmitDumpActive(void *ctx, int enable);
void 		fstWriterEmitEnumTableRef(void *ctx, fstEnumHandle handle);
void            fstWriterEmitValueChange(void *ctx, fstHandle handle, const void *val);
void            fstWriterEmitValueChange32(void *ctx, fstHandle handle,
                        uint32_t bits, uint32_t val);
void            fstWriterEmitValueChange64(void *ctx, fstHandle handle,
                        uint32_t bits, uint64_t val);
void            fstWriterEmitValueChangeVec32(void *ctx, fstHandle handle,
                        uint32_t bits, const uint32_t *val);
void            fstWriterEmitValueChangeVec64(void *ctx, fstHandle handle,
                        uint32_t bits, const uint64_t *val);
void            fstWriterEmitVariableLengthValueChange(void *ctx, fstHandle handle, const void *val, uint32_t len);
void            fstWriterEmitTimeChange(void *ctx, uint64_t tim);
void            fstWriterFlushContext(void *ctx);
int             fstWriterGetDumpSizeLimitReached(void *ctx);
int             fstWriterGetFseekFailed(void *ctx);
void            fstWriterSetAttrBegin(void *ctx, enum fstAttrType attrtype, int subtype,
                        const char *attrname, uint64_t arg);
void            fstWriterSetAttrEnd(void *ctx);
void            fstWriterSetComment(void *ctx, const char *comm);
void            fstWriterSetDate(void *ctx, const char *dat);
void            fstWriterSetDumpSizeLimit(void *ctx, uint64_t numbytes);
void            fstWriterSetEnvVar(void *ctx, const char *envvar);
void            fstWriterSetFileType(void *ctx, enum fstFileType filetype);
void            fstWriterSetPackType(void *ctx, enum fstWriterPackType typ);
void            fstWriterSetParallelMode(void *ctx, int enable);
void            fstWriterSetRepackOnClose(void *ctx, int enable);       /* type = 0 (none), 1 (libz) */
void            fstWriterSetScope(void *ctx, enum fstScopeType scopetype,
                        const char *scopename, const char *scopecomp);
void            fstWriterSetSourceInstantiationStem(void *ctx, const char *path, unsigned int line, unsigned int use_realpath);
void            fstWriterSetSourceStem(void *ctx, const char *path, unsigned int line, unsigned int use_realpath);
void            fstWriterSetTimescale(void *ctx, int ts);
void            fstWriterSetTimescaleFromString(void *ctx, const char *s);
void            fstWriterSetTimezero(void *ctx, int64_t tim);
void            fstWriterSetUpscope(void *ctx);
void		fstWriterSetValueList(void *ctx, const char *vl);
void            fstWriterSetVersion(void *ctx, const char *vers);


/*
 * reader functions
 */
void            fstReaderClose(void *ctx);
void            fstReaderClrFacProcessMask(void *ctx, fstHandle facidx);
void            fstReaderClrFacProcessMaskAll(void *ctx);
uint64_t        fstReaderGetAliasCount(void *ctx);
const char *    fstReaderGetCurrentFlatScope(void *ctx);
void *          fstReaderGetCurrentScopeUserInfo(void *ctx);
int             fstReaderGetCurrentScopeLen(void *ctx);
const char *    fstReaderGetDateString(void *ctx);
int             fstReaderGetDoubleEndianMatchState(void *ctx);
uint64_t        fstReaderGetDumpActivityChangeTime(void *ctx, uint32_t idx);
unsigned char   fstReaderGetDumpActivityChangeValue(void *ctx, uint32_t idx);
uint64_t        fstReaderGetEndTime(void *ctx);
int             fstReaderGetFacProcessMask(void *ctx, fstHandle facidx);
int             fstReaderGetFileType(void *ctx);
int             fstReaderGetFseekFailed(void *ctx);
fstHandle       fstReaderGetMaxHandle(void *ctx);
uint64_t        fstReaderGetMemoryUsedByWriter(void *ctx);
uint32_t        fstReaderGetNumberDumpActivityChanges(void *ctx);
uint64_t        fstReaderGetScopeCount(void *ctx);
uint64_t        fstReaderGetStartTime(void *ctx);
signed char     fstReaderGetTimescale(void *ctx);
int64_t         fstReaderGetTimezero(void *ctx);
uint64_t        fstReaderGetValueChangeSectionCount(void *ctx);
char *          fstReaderGetValueFromHandleAtTime(void *ctx, uint64_t tim, fstHandle facidx, char *buf);
uint64_t        fstReaderGetVarCount(void *ctx);
const char *    fstReaderGetVersionString(void *ctx);
struct fstHier *fstReaderIterateHier(void *ctx);
int             fstReaderIterateHierRewind(void *ctx);
int             fstReaderIterBlocks(void *ctx,
                        void (*value_change_callback)(void *user_callback_data_pointer, uint64_t time, fstHandle facidx, const unsigned char *value),
                        void *user_callback_data_pointer, FILE *vcdhandle);
int             fstReaderIterBlocks2(void *ctx,
                        void (*value_change_callback)(void *user_callback_data_pointer, uint64_t time, fstHandle facidx, const unsigned char *value),
                        void (*value_change_callback_varlen)(void *user_callback_data_pointer, uint64_t time, fstHandle facidx, const unsigned char *value, uint32_t len),
                        void *user_callback_data_pointer, FILE *vcdhandle);
void            fstReaderIterBlocksSetNativeDoublesOnCallback(void *ctx, int enable);
void *          fstReaderOpen(const char *nam);
void *          fstReaderOpenForUtilitiesOnly(void);
const char *    fstReaderPopScope(void *ctx);
int             fstReaderProcessHier(void *ctx, FILE *vcdhandle);
const char *    fstReaderPushScope(void *ctx, const char *nam, void *user_info);
void            fstReaderResetScope(void *ctx);
void            fstReaderSetFacProcessMask(void *ctx, fstHandle facidx);
void            fstReaderSetFacProcessMaskAll(void *ctx);
void            fstReaderSetLimitTimeRange(void *ctx, uint64_t start_time, uint64_t end_time);
void            fstReaderSetUnlimitedTimeRange(void *ctx);
void            fstReaderSetVcdExtensions(void *ctx, int enable);


/*
 * utility functions
 */
int             fstUtilityBinToEscConvertedLen(const unsigned char *s, int len); /* used for mallocs for fstUtilityBinToEsc() */
int             fstUtilityBinToEsc(unsigned char *d, const unsigned char *s, int len);
int             fstUtilityEscToBin(unsigned char *d, unsigned char *s, int len);
struct fstETab *fstUtilityExtractEnumTableFromString(const char *s);
void 		fstUtilityFreeEnumTable(struct fstETab *etab); /* must use to free fstETab properly */


#ifdef __cplusplus
}
#endif

#endif
