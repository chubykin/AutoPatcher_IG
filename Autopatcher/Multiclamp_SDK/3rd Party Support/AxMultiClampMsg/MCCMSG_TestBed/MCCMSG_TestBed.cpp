// MCCMSG_TestBed.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "MCCMSG_TestBed.h"
#include "MCCMSG_TestBedDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedApp

BEGIN_MESSAGE_MAP(CMCCMSG_TestBedApp, CWinApp)
	//{{AFX_MSG_MAP(CMCCMSG_TestBedApp)
		// NOTE - the ClassWizard will add and remove mapping macros here.
		//    DO NOT EDIT what you see in these blocks of generated code!
	//}}AFX_MSG
	ON_COMMAND(ID_HELP, CWinApp::OnHelp)
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedApp construction

CMCCMSG_TestBedApp::CMCCMSG_TestBedApp()
{
	// TODO: add construction code here,
	// Place all significant initialization in InitInstance
}

/////////////////////////////////////////////////////////////////////////////
// The one and only CMCCMSG_TestBedApp object

CMCCMSG_TestBedApp theApp;

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedApp initialization

BOOL CMCCMSG_TestBedApp::InitInstance()
{
	CMCCMSG_TestBedDlg dlg;
	m_pMainWnd = &dlg;
	int nResponse = dlg.DoModal();
	if (nResponse == IDOK)
	{
		// TODO: Place code here to handle when the dialog is
		//  dismissed with OK
	}
	else if (nResponse == IDCANCEL)
	{
		// TODO: Place code here to handle when the dialog is
		//  dismissed with Cancel
	}

	// Since the dialog has been closed, return FALSE so that we exit the
	//  application, rather than start the application's message pump.
	return FALSE;
}
