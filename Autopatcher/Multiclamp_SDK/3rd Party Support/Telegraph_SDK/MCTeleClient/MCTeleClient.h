//////////////////////////////////////////////////////////////////////////////////////
//
//    Copyright (c) 2003 Axon Instruments, Inc.
//    All rights reserved.
//
//////////////////////////////////////////////////////////////////////////////////////
// FILE:    MCTeleClient.h
// PURPOSE: Implementation of MCTeleClient
//          Main App Class
//

#if !defined(AFX_MCTELECLIENT_H__5D151BD5_91B7_11D3_91D0_00105AA743D3__INCLUDED_)
#define AFX_MCTELECLIENT_H__5D151BD5_91B7_11D3_91D0_00105AA743D3__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CMCTeleClientApp:
// See MCTeleClient.cpp for the implementation of this class
//

class CMCTeleClientApp : public CWinApp
{
public:
	CMCTeleClientApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCTeleClientApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CMCTeleClientApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCTELECLIENT_H__5D151BD5_91B7_11D3_91D0_00105AA743D3__INCLUDED_)
