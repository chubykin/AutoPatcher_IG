# Microsoft Developer Studio Generated NMAKE File, Based on MCTeleServer.dsp
!IF "$(CFG)" == ""
CFG=MCTeleServer - Win32 Debug
!MESSAGE No configuration specified. Defaulting to MCTeleServer - Win32 Debug.
!ENDIF 

!IF "$(CFG)" != "MCTeleServer - Win32 Release" && "$(CFG)" != "MCTeleServer - Win32 Debug"
!MESSAGE Invalid configuration "$(CFG)" specified.
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "MCTeleServer.mak" CFG="MCTeleServer - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "MCTeleServer - Win32 Release" (based on "Win32 (x86) Application")
!MESSAGE "MCTeleServer - Win32 Debug" (based on "Win32 (x86) Application")
!MESSAGE 
!ERROR An invalid configuration is specified.
!ENDIF 

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE 
NULL=nul
!ENDIF 

!IF  "$(CFG)" == "MCTeleServer - Win32 Release"

OUTDIR=.\Release
INTDIR=.\Release
# Begin Custom Macros
OutDir=.\Release
# End Custom Macros

ALL : "$(OUTDIR)\MCTeleServer.exe"


CLEAN :
	-@erase "$(INTDIR)\MCTeleServer.obj"
	-@erase "$(INTDIR)\MCTeleServer.pch"
	-@erase "$(INTDIR)\MCTeleServer.res"
	-@erase "$(INTDIR)\MCTeleServerDlg.obj"
	-@erase "$(INTDIR)\StdAfx.obj"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(OUTDIR)\MCTeleServer.exe"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /Zp4 /MT /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /Fp"$(INTDIR)\MCTeleServer.pch" /Yu"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

.c{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.c{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

MTL=midl.exe
MTL_PROJ=/nologo /D "NDEBUG" /mktyplib203 /win32 
RSC=rc.exe
RSC_PROJ=/l 0x409 /fo"$(INTDIR)\MCTeleServer.res" /d "NDEBUG" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\MCTeleServer.bsc" 
BSC32_SBRS= \
	
LINK32=link.exe
LINK32_FLAGS=version.lib /nologo /subsystem:windows /incremental:no /pdb:"$(OUTDIR)\MCTeleServer.pdb" /machine:I386 /out:"$(OUTDIR)\MCTeleServer.exe" 
LINK32_OBJS= \
	"$(INTDIR)\MCTeleServer.obj" \
	"$(INTDIR)\MCTeleServerDlg.obj" \
	"$(INTDIR)\StdAfx.obj" \
	"$(INTDIR)\MCTeleServer.res"

"$(OUTDIR)\MCTeleServer.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ELSEIF  "$(CFG)" == "MCTeleServer - Win32 Debug"

OUTDIR=.\Debug
INTDIR=.\Debug
# Begin Custom Macros
OutDir=.\Debug
# End Custom Macros

ALL : "$(OUTDIR)\MCTeleServer.exe" "$(OUTDIR)\MCTeleServer.bsc"


CLEAN :
	-@erase "$(INTDIR)\MCTeleServer.obj"
	-@erase "$(INTDIR)\MCTeleServer.pch"
	-@erase "$(INTDIR)\MCTeleServer.res"
	-@erase "$(INTDIR)\MCTeleServer.sbr"
	-@erase "$(INTDIR)\MCTeleServerDlg.obj"
	-@erase "$(INTDIR)\MCTeleServerDlg.sbr"
	-@erase "$(INTDIR)\StdAfx.obj"
	-@erase "$(INTDIR)\StdAfx.sbr"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(INTDIR)\vc60.pdb"
	-@erase "$(OUTDIR)\MCTeleServer.bsc"
	-@erase "$(OUTDIR)\MCTeleServer.exe"
	-@erase "$(OUTDIR)\MCTeleServer.ilk"
	-@erase "$(OUTDIR)\MCTeleServer.pdb"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /Zp4 /MTd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\MCTeleServer.pch" /Yu"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 

.c{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.obj::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.c{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cpp{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

.cxx{$(INTDIR)}.sbr::
   $(CPP) @<<
   $(CPP_PROJ) $< 
<<

MTL=midl.exe
MTL_PROJ=/nologo /D "_DEBUG" /mktyplib203 /win32 
RSC=rc.exe
RSC_PROJ=/l 0x409 /fo"$(INTDIR)\MCTeleServer.res" /d "_DEBUG" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\MCTeleServer.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\MCTeleServer.sbr" \
	"$(INTDIR)\MCTeleServerDlg.sbr" \
	"$(INTDIR)\StdAfx.sbr"

"$(OUTDIR)\MCTeleServer.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=version.lib /nologo /subsystem:windows /incremental:yes /pdb:"$(OUTDIR)\MCTeleServer.pdb" /debug /machine:I386 /out:"$(OUTDIR)\MCTeleServer.exe" /pdbtype:sept 
LINK32_OBJS= \
	"$(INTDIR)\MCTeleServer.obj" \
	"$(INTDIR)\MCTeleServerDlg.obj" \
	"$(INTDIR)\StdAfx.obj" \
	"$(INTDIR)\MCTeleServer.res"

"$(OUTDIR)\MCTeleServer.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ENDIF 


!IF "$(NO_EXTERNAL_DEPS)" != "1"
!IF EXISTS("MCTeleServer.dep")
!INCLUDE "MCTeleServer.dep"
!ELSE 
!MESSAGE Warning: cannot find "MCTeleServer.dep"
!ENDIF 
!ENDIF 


!IF "$(CFG)" == "MCTeleServer - Win32 Release" || "$(CFG)" == "MCTeleServer - Win32 Debug"
SOURCE=.\MCTeleServer.cpp

!IF  "$(CFG)" == "MCTeleServer - Win32 Release"


"$(INTDIR)\MCTeleServer.obj" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleServer.pch"


!ELSEIF  "$(CFG)" == "MCTeleServer - Win32 Debug"


"$(INTDIR)\MCTeleServer.obj"	"$(INTDIR)\MCTeleServer.sbr" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleServer.pch"


!ENDIF 

SOURCE=.\MCTeleServer.rc

"$(INTDIR)\MCTeleServer.res" : $(SOURCE) "$(INTDIR)"
	$(RSC) $(RSC_PROJ) $(SOURCE)


SOURCE=.\MCTeleServerDlg.cpp

!IF  "$(CFG)" == "MCTeleServer - Win32 Release"


"$(INTDIR)\MCTeleServerDlg.obj" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleServer.pch"


!ELSEIF  "$(CFG)" == "MCTeleServer - Win32 Debug"


"$(INTDIR)\MCTeleServerDlg.obj"	"$(INTDIR)\MCTeleServerDlg.sbr" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleServer.pch"


!ENDIF 

SOURCE=.\StdAfx.cpp

!IF  "$(CFG)" == "MCTeleServer - Win32 Release"

CPP_SWITCHES=/nologo /Zp4 /MT /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /Fp"$(INTDIR)\MCTeleServer.pch" /Yc"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\StdAfx.obj"	"$(INTDIR)\MCTeleServer.pch" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "MCTeleServer - Win32 Debug"

CPP_SWITCHES=/nologo /Zp4 /MTd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\MCTeleServer.pch" /Yc"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 

"$(INTDIR)\StdAfx.obj"	"$(INTDIR)\StdAfx.sbr"	"$(INTDIR)\MCTeleServer.pch" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 


!ENDIF 

