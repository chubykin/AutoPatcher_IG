// MCCMSG_TestBedDlg.h : header file
//

#if !defined(AFX_MCCMSG_TESTBEDDLG_H__0504C761_EC65_4106_93D3_CEFC0955A21A__INCLUDED_)
#define AFX_MCCMSG_TESTBEDDLG_H__0504C761_EC65_4106_93D3_CEFC0955A21A__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "..\AxMultiClampMsg.h"

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedDlg dialog

class CMCCMSG_TestBedDlg : public CDialog
{
// Attributes
private:
   HMCCMSG     m_hMCCmsg;

   char        m_szSerialNum[16];
   UINT        m_uModel;
   UINT        m_uCOMPortID;
   UINT        m_uDeviceID;
   UINT        m_uChannelID;
   BOOL        m_bSelected;

// Construction
public:
	CMCCMSG_TestBedDlg(CWnd* pParent = NULL);	// standard constructor
	~CMCCMSG_TestBedDlg();

// Dialog Data
	//{{AFX_DATA(CMCCMSG_TestBedDlg)
	enum { IDD = IDD_MCCMSG_TESTBED_DIALOG };
	CSpinButtonCtrl	m_spnSlowCompTau;
	CSpinButtonCtrl	m_spnSlowCompCap;
	CSpinButtonCtrl	m_spnFastCompTau;
	CSpinButtonCtrl	m_spnFastCompCap;
	CSpinButtonCtrl	m_spnPipetteOffset;
	CSpinButtonCtrl	m_spnInjSlowCurrentLevel;
	CComboBox	      m_cbxZapDuration;
	CComboBox	      m_cbxDeviceInfo;
	CComboBox	      m_cbxPrimarySignal;
   CComboBox	      m_cbxPrimaryGain;
	CComboBox	      m_cbxPrimaryLPF;
	CComboBox	      m_cbxSecondarySignal;
	CComboBox	      m_cbxSecondaryLPF;
	CComboBox	      m_cbxSecondaryGain;
	CComboBox	      m_cbxPrimaryHPF;
	CString	         m_strModel;
	CString	         m_strSerialNum;
	CString          	m_strCOMPortID;
	CString	         m_strDeviceID;
	CString	         m_strChannelID;
	CString	         m_strPipetteOffset;
	CString	         m_strDeviceStatus;
	CString				m_strFastCompCap;
	CString				m_strFastCompTau;
	CString				m_strSlowCompCap;
	CString				m_strSlowCompTau;
   CString				m_strInjSlowCurrentLevel;
	CString	         m_strMeter1Value;
	CButton	         m_btnMeterIrms;
	CButton	         m_btnMeterResist;
	CButton	         m_btnBridgeBal;
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CMCCMSG_TestBedDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	//{{AFX_MSG(CMCCMSG_TestBedDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnCreate();
	afx_msg void OnDestroy();
	afx_msg void OnScan();
	afx_msg void OnSelChangeSelectDevice();
	afx_msg void OnPipetteOffset();
	afx_msg void OnZap();
	afx_msg void OnBtnVClamp();
	afx_msg void OnBtnIClamp();
	afx_msg void OnBtnIClampZero();
	afx_msg void OnChangePipetteOffsetValue();
	afx_msg void OnDeltaposPipetteOffsetValueSpinner(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnSelchangeZapDuration();
	afx_msg void OnFastCompAuto();
	afx_msg void OnSlowCompAuto();
	afx_msg void OnChangeFastCompCap();
	afx_msg void OnDeltaposFastCompCapSpinner(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnChangeFastCompTau();
	afx_msg void OnDeltaposFastCompTauSpinner(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnChangeSlowCompCap();
	afx_msg void OnDeltaposSlowCompCapSpinner(NMHDR* pNMHDR, LRESULT* pResult);
	afx_msg void OnChangeSlowCompTau();
	afx_msg void OnDeltaposSlowCompTauSpinner(NMHDR* pNMHDR, LRESULT* pResult);
   afx_msg void OnChangeInjSlowCurrentLevel();
   afx_msg void OnDeltaposInjSlowCurrentLevelSpinner(NMHDR *pNMHDR, LRESULT *pResult);
   afx_msg void OnSelchangePrimarySignal();
	afx_msg void OnSelchangePrimaryGain();
	afx_msg void OnSelchangePrimaryLPF();
	afx_msg void OnSelchangePrimaryHPF();
   afx_msg void OnSelchangeSecondarySignal();
	afx_msg void OnSelchangeSecondaryGain();
	afx_msg void OnSelchangeSecondaryLPF();
	afx_msg void OnMeterResist();
	afx_msg void OnMeterIrms();
	afx_msg void OnGetMeter1();
	afx_msg void OnBridgeBalAuto();
	afx_msg void OnBridgeBalEnbl();
	virtual void OnOK();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
private:
   void DisplayErrorMsg(int nError);
   void UIUpdate(void);
   BOOL FillPrimarySignalCombo();
   BOOL FillSecondarySignalCombo();
};

// Signal struct definition
struct SignalDef
{
   UINT          m_uID;     // signal ID
   LPCSTR        m_pszName; // signal name
};

// This macro is used to initialize signal structs.
#define IDPLUSNAME(ID) ID, #ID

// Primary signal indices and names
static const SignalDef PRIMARYSIGNAL[] =
{
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_MEMBCURRENT),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_MEMBPOTENTIAL),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_PIPPOTENTIAL),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_100XACMEMBPOTENTIAL),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_EXTCMDPOTENTIAL),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_AUXILIARY1),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_VC_AUXILIARY2),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_MEMBPOTENTIAL),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_MEMBCURRENT),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_CMDCURRENT),
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_100XACMEMBPOTENTIAL), 
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_EXTCMDCURRENT), 
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_AUXILIARY1), 
   IDPLUSNAME(MCCMSG_PRI_SIGNAL_IC_AUXILIARY2)
};

// Secondary signal indices and names
static const SignalDef SECONDARYSIGNAL[] =
{
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_MEMBCURRENT), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_MEMBPOTENTIAL), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_PIPPOTENTIAL), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_100XACMEMBPOTENTIAL), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_EXTCMDPOTENTIAL), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_AUXILIARY1), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_VC_AUXILIARY2), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_MEMBPOTENTIAL), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_MEMBCURRENT), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_CMDCURRENT), 
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_PIPPOTENTIAL),
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_100XACMEMBPOTENTIAL),
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_EXTCMDCURRENT),
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_AUXILIARY1),
   IDPLUSNAME(MCCMSG_SEC_SIGNAL_IC_AUXILIARY2)
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_MCCMSG_TESTBEDDLG_H__0504C761_EC65_4106_93D3_CEFC0955A21A__INCLUDED_)
