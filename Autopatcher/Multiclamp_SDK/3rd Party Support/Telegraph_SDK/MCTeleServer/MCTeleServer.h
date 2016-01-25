//////////////////////////////////////////////////////////////////////////////////////
//
//    Copyright (c) 2003 Axon Instruments, Inc.
//    All rights reserved.
//
//////////////////////////////////////////////////////////////////////////////////////
// FILE:    MCTeleServer.h
// PURPOSE: Implementation of MCTeleServer
//          Main App Class
//

#if !defined(AFX_MCTELESERVER_H__43A9C675_91B1_11D3_91D0_00105AA743D3__INCLUDED_)
#define AFX_MCTELESERVER_H__43A9C675_91B1_11D3_91D0_00105AA743D3__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CMCTeleServerApp:
// See MCTeleServer.cpp for the implementation of this class
//

class CMCTeleServerApp : public CWinApp
{
public:
	CMCTeleServerApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCTeleServerApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CMCTeleServerApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCTELESERVER_H__43A9C675_91B1_11D3_91D0_00105AA743D3__INCLUDED_)
