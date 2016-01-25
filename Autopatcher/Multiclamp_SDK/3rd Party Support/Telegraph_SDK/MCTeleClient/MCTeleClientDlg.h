//////////////////////////////////////////////////////////////////////////////////////
//
//    Copyright (c) 2003 Axon Instruments, Inc.
//    All rights reserved.
//
//////////////////////////////////////////////////////////////////////////////////////
// FILE:    MCTeleClientDlg.h
// PURPOSE: Implementation of MCTeleClient
//          Main Dialog Class
//

#if !defined(AFX_MCTELECLIENTDLG_H__BBCEE25B_8E32_11D3_91CF_00105AA743D3__INCLUDED_)
#define AFX_MCTELECLIENTDLG_H__BBCEE25B_8E32_11D3_91CF_00105AA743D3__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "\AxonDev\Comp\Common\MultiClampBroadcastMsg.hpp"
#include <vector>

/////////////////////////////////////////////////////////////////////////////
// CMCTeleClientDlg dialog

class CMCTeleClientDlg : public CDialog
{
// Construction
public:
	CMCTeleClientDlg(CWnd* pParent = NULL);	// standard constructor
   ~CMCTeleClientDlg();

   typedef std::vector<CString> SerialNumList;
   SerialNumList m_vSerialNum;               // vector of client serial numbers for combo box

   // Dialog Data
	//{{AFX_DATA(CMCTeleClientDlg)
	enum { IDD = IDD_MCTELECLIENT_DIALOG };
	CComboBox	m_cbxSerialNum;
	CComboBox	m_cbxChannel;
	CButton	   m_btnScan;
	CButton	   m_btnConnect;
	CButton	   m_btnBroadcast;
	CListBox	   m_lbxDeviceList;
	CString	   m_cstrMode;
	CString	   m_cstrPriSignal;
	CString	   m_cstrPriAlpha;
	CString	   m_cstrPriScaleFactor;
	CString	   m_cstrPriLPFCutoff;
	CString	   m_cstrSecSignal;
	CString	   m_cstrSecAlpha;
	CString	   m_cstrSecScaleFactor;
	CString	   m_cstrSecLPFCutoff;
	CString	   m_cstrMembraneCap;
	CString	   m_cstrExtCmdSens;
	CString	m_cstrAppVer;
	CString	m_cstrDSPVer;
	CString	m_cstrFirmwareVer;
	CString	m_cstrSN;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCTeleClientDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	virtual LRESULT WindowProc(UINT message, WPARAM wParam, LPARAM lParam);
	//}}AFX_VIRTUAL

// Implementation
protected:
   BOOL               m_bIsConnected;      // TRUE if connected 
                                           // to a MultiClamp telegraph server

   BOOL               m_bIsConnecting;     // TRUE if attempting to connect
                                           // to a MultiClamp telegraph server

   BOOL               m_bScanning;         // TRUE if busy scanning serial numbers
                                           // of available MultiClamp telegraph servers

   BOOL               m_bRequestPending;   // TRUE if waiting for a requested packet
                                           // from a MultiClamp telegraph server

   MC_TELEGRAPH_DATA  m_mctdCurrentState;

  	HICON              m_hIcon;

   BOOL   GetFileVersion( char * pszFileVer, UINT uSize );
   void   UpdateDisplay();
   void   ClearDisplay();
   void   UpdateEnabling();
	void   OnBroadcastResponse( UINT uSerialNum, UINT uChannelID );
   void   AddSerialNum( UINT uSerialNum );

	// Generated message map functions
	//{{AFX_MSG(CMCTeleClientDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnConnect();
	afx_msg void OnSelChangeChannel();
	afx_msg void OnRequest();
	afx_msg void OnClose();
	afx_msg void OnBroadcast();
   afx_msg void OnScan();
   afx_msg void OnSelChangeDeviceList();
	afx_msg void OnSelChangeSerialNum();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCTELECLIENTDLG_H__BBCEE25B_8E32_11D3_91CF_00105AA743D3__INCLUDED_)
