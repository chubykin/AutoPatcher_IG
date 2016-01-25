# Microsoft Developer Studio Generated NMAKE File, Based on MCTeleClient.dsp
!IF "$(CFG)" == ""
CFG=MCTeleClient - Win32 Debug
!MESSAGE No configuration specified. Defaulting to MCTeleClient - Win32 Debug.
!ENDIF 

!IF "$(CFG)" != "MCTeleClient - Win32 Release" && "$(CFG)" != "MCTeleClient - Win32 Debug"
!MESSAGE Invalid configuration "$(CFG)" specified.
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "MCTeleClient.mak" CFG="MCTeleClient - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "MCTeleClient - Win32 Release" (based on "Win32 (x86) Application")
!MESSAGE "MCTeleClient - Win32 Debug" (based on "Win32 (x86) Application")
!MESSAGE 
!ERROR An invalid configuration is specified.
!ENDIF 

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE 
NULL=nul
!ENDIF 

!IF  "$(CFG)" == "MCTeleClient - Win32 Release"

OUTDIR=.\Release
INTDIR=.\Release
# Begin Custom Macros
OutDir=.\Release
# End Custom Macros

ALL : "$(OUTDIR)\MCTeleClient.exe"


CLEAN :
	-@erase "$(INTDIR)\MCTeleClient.obj"
	-@erase "$(INTDIR)\MCTeleClient.pch"
	-@erase "$(INTDIR)\MCTeleClient.res"
	-@erase "$(INTDIR)\MCTeleClientDlg.obj"
	-@erase "$(INTDIR)\StdAfx.obj"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(OUTDIR)\MCTeleClient.exe"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /Zp4 /MD /W4 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_AFXDLL" /Fp"$(INTDIR)\MCTeleClient.pch" /Yu"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

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
RSC_PROJ=/l 0x409 /fo"$(INTDIR)\MCTeleClient.res" /d "NDEBUG" /d "_AFXDLL" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\MCTeleClient.bsc" 
BSC32_SBRS= \
	
LINK32=link.exe
LINK32_FLAGS=version.lib /nologo /subsystem:windows /incremental:no /pdb:"$(OUTDIR)\MCTeleClient.pdb" /machine:I386 /out:"$(OUTDIR)\MCTeleClient.exe" 
LINK32_OBJS= \
	"$(INTDIR)\MCTeleClient.obj" \
	"$(INTDIR)\MCTeleClientDlg.obj" \
	"$(INTDIR)\StdAfx.obj" \
	"$(INTDIR)\MCTeleClient.res"

"$(OUTDIR)\MCTeleClient.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ELSEIF  "$(CFG)" == "MCTeleClient - Win32 Debug"

OUTDIR=.\Debug
INTDIR=.\Debug
# Begin Custom Macros
OutDir=.\Debug
# End Custom Macros

ALL : "$(OUTDIR)\MCTeleClient.exe" "$(OUTDIR)\MCTeleClient.bsc"


CLEAN :
	-@erase "$(INTDIR)\MCTeleClient.obj"
	-@erase "$(INTDIR)\MCTeleClient.pch"
	-@erase "$(INTDIR)\MCTeleClient.res"
	-@erase "$(INTDIR)\MCTeleClient.sbr"
	-@erase "$(INTDIR)\MCTeleClientDlg.obj"
	-@erase "$(INTDIR)\MCTeleClientDlg.sbr"
	-@erase "$(INTDIR)\StdAfx.obj"
	-@erase "$(INTDIR)\StdAfx.sbr"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(INTDIR)\vc60.pdb"
	-@erase "$(OUTDIR)\MCTeleClient.bsc"
	-@erase "$(OUTDIR)\MCTeleClient.exe"
	-@erase "$(OUTDIR)\MCTeleClient.ilk"
	-@erase "$(OUTDIR)\MCTeleClient.pdb"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /Zp4 /MDd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_AFXDLL" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\MCTeleClient.pch" /Yu"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 

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
RSC_PROJ=/l 0x409 /fo"$(INTDIR)\MCTeleClient.res" /d "_DEBUG" /d "_AFXDLL" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\MCTeleClient.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\MCTeleClient.sbr" \
	"$(INTDIR)\MCTeleClientDlg.sbr" \
	"$(INTDIR)\StdAfx.sbr"

"$(OUTDIR)\MCTeleClient.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=version.lib /nologo /subsystem:windows /incremental:yes /pdb:"$(OUTDIR)\MCTeleClient.pdb" /debug /machine:I386 /out:"$(OUTDIR)\MCTeleClient.exe" /pdbtype:sept 
LINK32_OBJS= \
	"$(INTDIR)\MCTeleClient.obj" \
	"$(INTDIR)\MCTeleClientDlg.obj" \
	"$(INTDIR)\StdAfx.obj" \
	"$(INTDIR)\MCTeleClient.res"

"$(OUTDIR)\MCTeleClient.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ENDIF 


!IF "$(NO_EXTERNAL_DEPS)" != "1"
!IF EXISTS("MCTeleClient.dep")
!INCLUDE "MCTeleClient.dep"
!ELSE 
!MESSAGE Warning: cannot find "MCTeleClient.dep"
!ENDIF 
!ENDIF 


!IF "$(CFG)" == "MCTeleClient - Win32 Release" || "$(CFG)" == "MCTeleClient - Win32 Debug"
SOURCE=.\MCTeleClient.cpp

!IF  "$(CFG)" == "MCTeleClient - Win32 Release"


"$(INTDIR)\MCTeleClient.obj" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleClient.pch"


!ELSEIF  "$(CFG)" == "MCTeleClient - Win32 Debug"


"$(INTDIR)\MCTeleClient.obj"	"$(INTDIR)\MCTeleClient.sbr" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleClient.pch"


!ENDIF 

SOURCE=.\MCTeleClient.rc

"$(INTDIR)\MCTeleClient.res" : $(SOURCE) "$(INTDIR)"
	$(RSC) $(RSC_PROJ) $(SOURCE)


SOURCE=.\MCTeleClientDlg.cpp

!IF  "$(CFG)" == "MCTeleClient - Win32 Release"


"$(INTDIR)\MCTeleClientDlg.obj" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleClient.pch"


!ELSEIF  "$(CFG)" == "MCTeleClient - Win32 Debug"


"$(INTDIR)\MCTeleClientDlg.obj"	"$(INTDIR)\MCTeleClientDlg.sbr" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCTeleClient.pch"


!ENDIF 

SOURCE=.\StdAfx.cpp

!IF  "$(CFG)" == "MCTeleClient - Win32 Release"

CPP_SWITCHES=/nologo /Zp4 /MD /W4 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_AFXDLL" /Fp"$(INTDIR)\MCTeleClient.pch" /Yc"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\StdAfx.obj"	"$(INTDIR)\MCTeleClient.pch" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "MCTeleClient - Win32 Debug"

CPP_SWITCHES=/nologo /Zp4 /MDd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_AFXDLL" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\MCTeleClient.pch" /Yc"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 

"$(INTDIR)\StdAfx.obj"	"$(INTDIR)\StdAfx.sbr"	"$(INTDIR)\MCTeleClient.pch" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 


!ENDIF 

