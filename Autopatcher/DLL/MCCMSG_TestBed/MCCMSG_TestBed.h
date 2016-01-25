// MCCMSG_TestBed.h : main header file for the MCCMSG_TESTBED application
//

#if !defined(AFX_MCCMSG_TESTBED_H__3C679690_0E90_4F92_9DED_1CCA2B0FDF86__INCLUDED_)
#define AFX_MCCMSG_TESTBED_H__3C679690_0E90_4F92_9DED_1CCA2B0FDF86__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedApp:
// See MCCMSG_TestBed.cpp for the implementation of this class
//

class CMCCMSG_TestBedApp : public CWinApp
{
public:
	CMCCMSG_TestBedApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCCMSG_TestBedApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CMCCMSG_TestBedApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCCMSG_TESTBED_H__3C679690_0E90_4F92_9DED_1CCA2B0FDF86__INCLUDED_)
