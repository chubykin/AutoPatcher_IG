//////////////////////////////////////////////////////////////////////////////////////
//
//    Copyright (c) 2003 Axon Instruments, Inc.
//    All rights reserved.
//
//////////////////////////////////////////////////////////////////////////////////////
// FILE:    MCTeleServerDlg.h
// PURPOSE: Implementation of MCTeleServer
//          Main Dialog Class
//

#if !defined(AFX_MCTELESERVERDLG_H__09280B7B_9085_11D3_91D0_00105AA743D3__INCLUDED_)
#define AFX_MCTELESERVERDLG_H__09280B7B_9085_11D3_91D0_00105AA743D3__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "\AxonDev\Comp\Common\MultiClampBroadcastMsg.hpp"

const UINT cuTimerEventID = 1255; // arbitrary

/////////////////////////////////////////////////////////////////////////////
// CMCTeleServerDlg dialog

class CMCTeleServerDlg : public CDialog
{
// Construction
public:
	CMCTeleServerDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	//{{AFX_DATA(CMCTeleServerDlg)
	enum { IDD = IDD_MCTELESERVER_DIALOG };
	CComboBox	m_cbxSerialNumber;
	CComboBox	m_cbxChannelID;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCTeleServerDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	virtual LRESULT WindowProc(UINT message, WPARAM wParam, LPARAM lParam);
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON              m_hIcon;
   MC_TELEGRAPH_DATA  m_mctdCurrentState;
   HWND               m_ClientHwndList[MCTG_MAX_CLIENTS];

   BOOL   GetFileVersion( char * pszFileVer, UINT uSize );
   void   ReconnectRequest( );

	// Generated message map functions
	//{{AFX_MSG(CMCTeleServerDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnSelChangeChannelID();
	afx_msg void OnSelChangeSerialNum();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCTELESERVERDLG_H__09280B7B_9085_11D3_91D0_00105AA743D3__INCLUDED_)
