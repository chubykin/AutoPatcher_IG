# Microsoft Developer Studio Generated NMAKE File, Based on MCCMSG_TestBed.dsp
!IF "$(CFG)" == ""
CFG=MCCMSG_TestBed - Win32 Debug
!MESSAGE No configuration specified. Defaulting to MCCMSG_TestBed - Win32 Debug.
!ENDIF 

!IF "$(CFG)" != "MCCMSG_TestBed - Win32 Release" && "$(CFG)" != "MCCMSG_TestBed - Win32 Debug"
!MESSAGE Invalid configuration "$(CFG)" specified.
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "MCCMSG_TestBed.mak" CFG="MCCMSG_TestBed - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "MCCMSG_TestBed - Win32 Release" (based on "Win32 (x86) Application")
!MESSAGE "MCCMSG_TestBed - Win32 Debug" (based on "Win32 (x86) Application")
!MESSAGE 
!ERROR An invalid configuration is specified.
!ENDIF 

!IF "$(OS)" == "Windows_NT"
NULL=
!ELSE 
NULL=nul
!ENDIF 

!IF  "$(CFG)" == "MCCMSG_TestBed - Win32 Release"

OUTDIR=.\Release
INTDIR=.\Release
# Begin Custom Macros
OutDir=.\Release
# End Custom Macros

!IF "$(RECURSE)" == "0" 

ALL : "$(OUTDIR)\MCCMSG_TestBed.exe"

!ELSE 

ALL : "AxMultiClampMsg - Win32 Release" "$(OUTDIR)\MCCMSG_TestBed.exe"

!ENDIF 

!IF "$(RECURSE)" == "1" 
CLEAN :"AxMultiClampMsg - Win32 ReleaseCLEAN" 
!ELSE 
CLEAN :
!ENDIF 
	-@erase "$(INTDIR)\MCCMSG_TestBed.obj"
	-@erase "$(INTDIR)\MCCMSG_TestBed.pch"
	-@erase "$(INTDIR)\MCCMSG_TestBed.res"
	-@erase "$(INTDIR)\MCCMSG_TestBedDlg.obj"
	-@erase "$(INTDIR)\StdAfx.obj"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(OUTDIR)\MCCMSG_TestBed.exe"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /Zp4 /MT /W4 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /Fp"$(INTDIR)\MCCMSG_TestBed.pch" /Yu"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

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
RSC_PROJ=/l 0xc09 /fo"$(INTDIR)\MCCMSG_TestBed.res" /d "NDEBUG" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\MCCMSG_TestBed.bsc" 
BSC32_SBRS= \
	
LINK32=link.exe
LINK32_FLAGS=/nologo /subsystem:windows /incremental:no /pdb:"$(OUTDIR)\MCCMSG_TestBed.pdb" /machine:I386 /out:"$(OUTDIR)\MCCMSG_TestBed.exe" 
LINK32_OBJS= \
	"$(INTDIR)\MCCMSG_TestBed.obj" \
	"$(INTDIR)\MCCMSG_TestBedDlg.obj" \
	"$(INTDIR)\StdAfx.obj" \
	"$(INTDIR)\MCCMSG_TestBed.res" \
	"..\AxMultiClampMsg.lib" \
	"..\Release\AxMultiClampMsg.lib"

"$(OUTDIR)\MCCMSG_TestBed.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

!ELSEIF  "$(CFG)" == "MCCMSG_TestBed - Win32 Debug"

OUTDIR=.\Debug
INTDIR=.\Debug
# Begin Custom Macros
OutDir=.\Debug
# End Custom Macros

!IF "$(RECURSE)" == "0" 

ALL : "$(OUTDIR)\MCCMSG_TestBed.exe" "$(OUTDIR)\MCCMSG_TestBed.bsc"

!ELSE 

ALL : "AxMultiClampMsg - Win32 Debug" "$(OUTDIR)\MCCMSG_TestBed.exe" "$(OUTDIR)\MCCMSG_TestBed.bsc"

!ENDIF 

!IF "$(RECURSE)" == "1" 
CLEAN :"AxMultiClampMsg - Win32 DebugCLEAN" 
!ELSE 
CLEAN :
!ENDIF 
	-@erase "$(INTDIR)\MCCMSG_TestBed.obj"
	-@erase "$(INTDIR)\MCCMSG_TestBed.pch"
	-@erase "$(INTDIR)\MCCMSG_TestBed.res"
	-@erase "$(INTDIR)\MCCMSG_TestBed.sbr"
	-@erase "$(INTDIR)\MCCMSG_TestBedDlg.obj"
	-@erase "$(INTDIR)\MCCMSG_TestBedDlg.sbr"
	-@erase "$(INTDIR)\StdAfx.obj"
	-@erase "$(INTDIR)\StdAfx.sbr"
	-@erase "$(INTDIR)\vc60.idb"
	-@erase "$(INTDIR)\vc60.pdb"
	-@erase "$(OUTDIR)\MCCMSG_TestBed.bsc"
	-@erase "$(OUTDIR)\MCCMSG_TestBed.exe"
	-@erase "$(OUTDIR)\MCCMSG_TestBed.ilk"
	-@erase "$(OUTDIR)\MCCMSG_TestBed.pdb"

"$(OUTDIR)" :
    if not exist "$(OUTDIR)/$(NULL)" mkdir "$(OUTDIR)"

CPP=cl.exe
CPP_PROJ=/nologo /Zp4 /MTd /W4 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\MCCMSG_TestBed.pch" /Yu"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 

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
RSC_PROJ=/l 0xc09 /fo"$(INTDIR)\MCCMSG_TestBed.res" /d "_DEBUG" 
BSC32=bscmake.exe
BSC32_FLAGS=/nologo /o"$(OUTDIR)\MCCMSG_TestBed.bsc" 
BSC32_SBRS= \
	"$(INTDIR)\MCCMSG_TestBed.sbr" \
	"$(INTDIR)\MCCMSG_TestBedDlg.sbr" \
	"$(INTDIR)\StdAfx.sbr"

"$(OUTDIR)\MCCMSG_TestBed.bsc" : "$(OUTDIR)" $(BSC32_SBRS)
    $(BSC32) @<<
  $(BSC32_FLAGS) $(BSC32_SBRS)
<<

LINK32=link.exe
LINK32_FLAGS=/nologo /subsystem:windows /incremental:yes /pdb:"$(OUTDIR)\MCCMSG_TestBed.pdb" /debug /machine:I386 /out:"$(OUTDIR)\MCCMSG_TestBed.exe" /pdbtype:sept 
LINK32_OBJS= \
	"$(INTDIR)\MCCMSG_TestBed.obj" \
	"$(INTDIR)\MCCMSG_TestBedDlg.obj" \
	"$(INTDIR)\StdAfx.obj" \
	"$(INTDIR)\MCCMSG_TestBed.res" \
	"..\AxMultiClampMsg.lib" \
	"..\Debug\AxMultiClampMsg.lib"

"$(OUTDIR)\MCCMSG_TestBed.exe" : "$(OUTDIR)" $(DEF_FILE) $(LINK32_OBJS)
    $(LINK32) @<<
  $(LINK32_FLAGS) $(LINK32_OBJS)
<<

OutDir=.\Debug
TargetName=MCCMSG_TestBed
SOURCE="$(InputPath)"
PostBuild_Desc=Copying EXE
DS_POSTBUILD_DEP=$(INTDIR)\postbld.dep

ALL : $(DS_POSTBUILD_DEP)

# Begin Custom Macros
OutDir=.\Debug
# End Custom Macros

$(DS_POSTBUILD_DEP) : "AxMultiClampMsg - Win32 Debug" "$(OUTDIR)\MCCMSG_TestBed.exe" "$(OUTDIR)\MCCMSG_TestBed.bsc"
   \AxonDev\Tools\Update .\Debug\MCCMSG_TestBed exe
	echo Helper for Post-build step > "$(DS_POSTBUILD_DEP)"

!ENDIF 


!IF "$(NO_EXTERNAL_DEPS)" != "1"
!IF EXISTS("MCCMSG_TestBed.dep")
!INCLUDE "MCCMSG_TestBed.dep"
!ELSE 
!MESSAGE Warning: cannot find "MCCMSG_TestBed.dep"
!ENDIF 
!ENDIF 


!IF "$(CFG)" == "MCCMSG_TestBed - Win32 Release" || "$(CFG)" == "MCCMSG_TestBed - Win32 Debug"
SOURCE=.\MCCMSG_TestBed.cpp

!IF  "$(CFG)" == "MCCMSG_TestBed - Win32 Release"


"$(INTDIR)\MCCMSG_TestBed.obj" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCCMSG_TestBed.pch"


!ELSEIF  "$(CFG)" == "MCCMSG_TestBed - Win32 Debug"


"$(INTDIR)\MCCMSG_TestBed.obj"	"$(INTDIR)\MCCMSG_TestBed.sbr" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCCMSG_TestBed.pch"


!ENDIF 

SOURCE=.\MCCMSG_TestBed.rc

"$(INTDIR)\MCCMSG_TestBed.res" : $(SOURCE) "$(INTDIR)"
	$(RSC) $(RSC_PROJ) $(SOURCE)


SOURCE=.\MCCMSG_TestBedDlg.cpp

!IF  "$(CFG)" == "MCCMSG_TestBed - Win32 Release"


"$(INTDIR)\MCCMSG_TestBedDlg.obj" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCCMSG_TestBed.pch"


!ELSEIF  "$(CFG)" == "MCCMSG_TestBed - Win32 Debug"


"$(INTDIR)\MCCMSG_TestBedDlg.obj"	"$(INTDIR)\MCCMSG_TestBedDlg.sbr" : $(SOURCE) "$(INTDIR)" "$(INTDIR)\MCCMSG_TestBed.pch"


!ENDIF 

SOURCE=.\StdAfx.cpp

!IF  "$(CFG)" == "MCCMSG_TestBed - Win32 Release"

CPP_SWITCHES=/nologo /Zp4 /MT /W4 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /Fp"$(INTDIR)\MCCMSG_TestBed.pch" /Yc"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /c 

"$(INTDIR)\StdAfx.obj"	"$(INTDIR)\MCCMSG_TestBed.pch" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ELSEIF  "$(CFG)" == "MCCMSG_TestBed - Win32 Debug"

CPP_SWITCHES=/nologo /Zp4 /MTd /W4 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /FR"$(INTDIR)\\" /Fp"$(INTDIR)\MCCMSG_TestBed.pch" /Yc"stdafx.h" /Fo"$(INTDIR)\\" /Fd"$(INTDIR)\\" /FD /GZ /c 

"$(INTDIR)\StdAfx.obj"	"$(INTDIR)\StdAfx.sbr"	"$(INTDIR)\MCCMSG_TestBed.pch" : $(SOURCE) "$(INTDIR)"
	$(CPP) @<<
  $(CPP_SWITCHES) $(SOURCE)
<<


!ENDIF 

!IF  "$(CFG)" == "MCCMSG_TestBed - Win32 Release"

"AxMultiClampMsg - Win32 Release" : 
   cd "\AxonDev\Comp\AxMultiClampMsg"
   $(MAKE) /$(MAKEFLAGS) /F .\AxMultiClampMsg.mak CFG="AxMultiClampMsg - Win32 Release" 
   cd ".\MCCMSG_TestBed"

"AxMultiClampMsg - Win32 ReleaseCLEAN" : 
   cd "\AxonDev\Comp\AxMultiClampMsg"
   $(MAKE) /$(MAKEFLAGS) /F .\AxMultiClampMsg.mak CFG="AxMultiClampMsg - Win32 Release" RECURSE=1 CLEAN 
   cd ".\MCCMSG_TestBed"

!ELSEIF  "$(CFG)" == "MCCMSG_TestBed - Win32 Debug"

"AxMultiClampMsg - Win32 Debug" : 
   cd "\AxonDev\Comp\AxMultiClampMsg"
   $(MAKE) /$(MAKEFLAGS) /F .\AxMultiClampMsg.mak CFG="AxMultiClampMsg - Win32 Debug" 
   cd ".\MCCMSG_TestBed"

"AxMultiClampMsg - Win32 DebugCLEAN" : 
   cd "\AxonDev\Comp\AxMultiClampMsg"
   $(MAKE) /$(MAKEFLAGS) /F .\AxMultiClampMsg.mak CFG="AxMultiClampMsg - Win32 Debug" RECURSE=1 CLEAN 
   cd ".\MCCMSG_TestBed"

!ENDIF 


!ENDIF 

