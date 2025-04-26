from .c_api import *
from typing import *
from dataclasses import dataclass, field
from enum import Enum

class HierarchyType(Enum):
	FST_HT_SCOPE       = 0
	FST_HT_UPSCOPE     = 1
	FST_HT_VAR         = 2
	FST_HT_ATTRBEGIN   = 3
	FST_HT_ATTREND     = 4

	FST_HT_TREEBEGIN   = 5
	FST_HT_TREEEND     = 6

class ScopeType(Enum):
	VCD_MODULE          = 0
	VCD_TASK            = 1
	VCD_FUNCTION        = 2
	VCD_BEGIN           = 3
	VCD_FORK            = 4
	VCD_GENERATE        = 5
	VCD_STRUCT          = 6
	VCD_UNION           = 7
	VCD_CLASS           = 8
	VCD_INTERFACE       = 9
	VCD_PACKAGE         = 10
	VCD_PROGRAM         = 11
	VHDL_ARCHITECTURE   = 12
	VHDL_PROCEDURE      = 13
	VHDL_FUNCTION       = 14
	VHDL_RECORD         = 15
	VHDL_PROCESS        = 16
	VHDL_BLOCK          = 17
	VHDL_FOR_GENERATE   = 18
	VHDL_IF_GENERATE    = 19
	VHDL_GENERATE       = 20
	VHDL_PACKAGE        = 21

class VarType(Enum):
	VCD_EVENT           = 0
	VCD_INTEGER         = 1
	VCD_PARAMETER       = 2
	VCD_REAL            = 3
	VCD_REAL_PARAMETER  = 4
	VCD_REG             = 5
	VCD_SUPPLY0         = 6
	VCD_SUPPLY1         = 7
	VCD_TIME            = 8
	VCD_TRI             = 9
	VCD_TRIAND          = 10
	VCD_TRIOR           = 11
	VCD_TRIREG          = 12
	VCD_TRI0            = 13
	VCD_TRI1            = 14
	VCD_WAND            = 15
	VCD_WIRE            = 16
	VCD_WOR             = 17
	VCD_PORT            = 18
	VCD_SPARRAY         = 19
	VCD_REALTIME        = 20
	GEN_STRING          = 21
	SV_BIT              = 22
	SV_LOGIC            = 23
	SV_INT              = 24
	SV_SHORTINT         = 25
	SV_LONGINT          = 26
	SV_BYTE             = 27
	SV_ENUM             = 28
	SV_SHORTREAL        = 29

class VarDirection(Enum):
	IMPLICIT    = 0
	INPUT       = 1
	OUTPUT      = 2
	INOUT       = 3
	BUFFER      = 4
	LINKAGE     = 5


@dataclass
class HierarchyScope:
	typ : ScopeType
	name : str = field(default_factory=str)
	component : str = field(default_factory=str)

	def __post_init__(self):
		self.typ =  ScopeType(self.typ)

@dataclass
class HierarchyVar:
	typ : VarType
	direction : VarDirection
	name : str = field(default_factory=str)
	width : int = 0
	handle : int = 0
	is_alias : bool = False

	def __post_init__(self):
		self.typ =  VarType(self.typ)
		self.direction =  VarDirection(self.direction)
		self.is_alias =  self.is_alias != 0

def HierarchyIteratorParser(raw : Tuple[List[int], List[str]]) -> Tuple[HierarchyType, Any]:
	ints, strings = raw
	hier_type = HierarchyType(ints[0])
	hier_content = None
	if hier_type == HierarchyType.FST_HT_SCOPE:
		hier_content = HierarchyScope(
			ints[1],
			strings[0],
			strings[1]
		)
	elif hier_type == HierarchyType.FST_HT_UPSCOPE:
		pass
	elif hier_type == HierarchyType.FST_HT_VAR:
		hier_content = HierarchyVar(
			ints[1],
			ints[2],
			strings[0],
			ints[4],
			ints[3],
			ints[5]
		)
	else:
		assert 0
	return (hier_type, hier_content)

__all__ = ["HandleClass", "HierarchyIteratorParser"]
