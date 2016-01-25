// MCCMSG_TestBedDlg.cpp : implementation file
//

#include "stdafx.h"
#include "MCCMSG_TestBed.h"
#include "MCCMSG_TestBedDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

// magic number indicating scan detected no devices
static const DWORD s_cdwNoDevice       = 13561;
static const char  s_cszNoDevice[]     = "No Device";
static const char  s_cszNotConnected[] = "MultiClamp not selected";
static const char  s_cszConnected[]    = "MultiClamp selected";

/////////////////////////////////////////////////////////////////////////////
// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	//{{AFX_DATA(CAboutDlg)
	enum { IDD = IDD_ABOUTBOX };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAboutDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	//{{AFX_MSG(CAboutDlg)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//==============================================================================================
// FUNCTION: CAboutDlg
// PURPOSE:  
//
CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
	//{{AFX_DATA_INIT(CAboutDlg)
	//}}AFX_DATA_INIT
}

//==============================================================================================
// FUNCTION: DoDataExchange
// PURPOSE:  
//
void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
	//{{AFX_MSG_MAP(CAboutDlg)
		// No message handlers
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedDlg dialog


//==============================================================================================
// FUNCTION: CMCCMSG_TestBedDlg
// PURPOSE:  Constructor
//
CMCCMSG_TestBedDlg::CMCCMSG_TestBedDlg(CWnd* pParent /*=NULL*/)
	: CDialog     (CMCCMSG_TestBedDlg::IDD, pParent),
     m_hMCCmsg   (NULL ),
     m_uModel    (0    ),
     m_uCOMPortID(0    ),
     m_uDeviceID (0    ),
     m_uChannelID(0    ),
     m_bSelected (FALSE)
{
	//{{AFX_DATA_INIT(CMCCMSG_TestBedDlg)
	m_strModel               = _T("");
	m_strSerialNum           = _T("");
	m_strCOMPortID           = _T("");
	m_strDeviceID            = _T("");
	m_strChannelID           = _T("");
	m_strPipetteOffset       = _T("");
	m_strFastCompCap         = _T("");
	m_strFastCompTau         = _T("");
	m_strSlowCompCap         = _T("");
	m_strSlowCompTau         = _T("");
   m_strInjSlowCurrentLevel = _T("");
	m_strMeter1Value         = _T("");
	//}}AFX_DATA_INIT

   m_szSerialNum[0] = '\0';
   m_strDeviceStatus.Format(s_cszNotConnected);

	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

//==============================================================================================
// FUNCTION: ~CMCCMSG_TestBedDlg
// PURPOSE:  Destructor
//
CMCCMSG_TestBedDlg::~CMCCMSG_TestBedDlg()
{
}

//==============================================================================================
// FUNCTION: OnOK
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnOK() 
{
	OnDestroy();
	CDialog::OnOK();
}

//==============================================================================================
// FUNCTION: DoDataExchange
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CMCCMSG_TestBedDlg)
	DDX_Control(pDX, IDC_SLOWCOMP_TAU_SPINNER, m_spnSlowCompTau);
	DDX_Control(pDX, IDC_SLOWCOMP_CAP_SPINNER, m_spnSlowCompCap);
	DDX_Control(pDX, IDC_FASTCOMP_TAU_SPINNER, m_spnFastCompTau);
	DDX_Control(pDX, IDC_FASTCOMP_CAP_SPINNER, m_spnFastCompCap);
	DDX_Control(pDX, IDC_PIPETTEOFFSETVALUE_SPINNER, m_spnPipetteOffset);
   DDX_Control(pDX, IDC_INJSLOWCURRENTLEVEL_SPINNER, m_spnInjSlowCurrentLevel);
	DDX_Control(pDX, IDC_ZAPDURATION, m_cbxZapDuration);
	DDX_Control(pDX, IDC_SELECTDEVICE, m_cbxDeviceInfo);
   DDX_Control(pDX, IDC_PRIMARYSIGNAL, m_cbxPrimarySignal);
	DDX_Control(pDX, IDC_PRIMARYGAIN, m_cbxPrimaryGain);
	DDX_Control(pDX, IDC_PRIMARYLPF, m_cbxPrimaryLPF);
   DDX_Control(pDX, IDC_SECONDARYSIGNAL, m_cbxSecondarySignal);
	DDX_Control(pDX, IDC_SECONDARYLPF, m_cbxSecondaryLPF);
	DDX_Control(pDX, IDC_SECONDARYGAIN, m_cbxSecondaryGain);
	DDX_Control(pDX, IDC_PRIMARYHPF, m_cbxPrimaryHPF);
	DDX_Text(pDX, IDC_MODEL, m_strModel);
	DDX_Text(pDX, IDC_SERIALNUM, m_strSerialNum);
	DDX_Text(pDX, IDC_COMPORTID, m_strCOMPortID);
	DDX_Text(pDX, IDC_DEVICEID, m_strDeviceID);
	DDX_Text(pDX, IDC_CHANNELID, m_strChannelID);
	DDX_Text(pDX, IDC_PIPETTEOFFSETVALUE, m_strPipetteOffset);
	DDX_Text(pDX, IDC_DEVICESTATUS, m_strDeviceStatus);
	DDX_Text(pDX, IDC_FASTCOMP_CAP, m_strFastCompCap);
	DDX_Text(pDX, IDC_FASTCOMP_TAU, m_strFastCompTau);
	DDX_Text(pDX, IDC_SLOWCOMP_CAP, m_strSlowCompCap);
	DDX_Text(pDX, IDC_SLOWCOMP_TAU, m_strSlowCompTau);
   DDX_Text(pDX, IDC_INJSLOWCURRENTLEVEL, m_strInjSlowCurrentLevel);
	DDX_Control(pDX, IDC_METERIRMS, m_btnMeterIrms);
	DDX_Control(pDX, IDC_METERRESIST, m_btnMeterResist);
	DDX_Control(pDX, IDC_BRIDGEBAL_ENBL, m_btnBridgeBal);
	DDX_Text(pDX, IDC_METER1_VALUE, m_strMeter1Value);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CMCCMSG_TestBedDlg, CDialog)
	//{{AFX_MSG_MAP(CMCCMSG_TestBedDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_CREATE, OnCreate)
	ON_BN_CLICKED(IDC_DESTROY, OnDestroy)
	ON_BN_CLICKED(IDC_SCAN, OnScan)
	ON_CBN_SELCHANGE(IDC_SELECTDEVICE, OnSelChangeSelectDevice)
	ON_BN_CLICKED(IDC_PIPETTEOFFSET, OnPipetteOffset)
	ON_BN_CLICKED(IDC_ZAP, OnZap)
	ON_BN_CLICKED(IDC_BTN_VCLAMP, OnBtnVClamp)
	ON_BN_CLICKED(IDC_BTN_ICLAMP, OnBtnIClamp)
	ON_BN_CLICKED(IDC_BTN_ICLAMPZERO, OnBtnIClampZero)
	ON_EN_CHANGE(IDC_PIPETTEOFFSETVALUE, OnChangePipetteOffsetValue)
	ON_NOTIFY(UDN_DELTAPOS, IDC_PIPETTEOFFSETVALUE_SPINNER, OnDeltaposPipetteOffsetValueSpinner)
	ON_CBN_SELCHANGE(IDC_ZAPDURATION, OnSelchangeZapDuration)
	ON_BN_CLICKED(IDC_FASTCOMP_AUTO, OnFastCompAuto)
	ON_BN_CLICKED(IDC_SLOWCOMP_AUTO, OnSlowCompAuto)
	ON_EN_CHANGE(IDC_FASTCOMP_CAP, OnChangeFastCompCap)
	ON_NOTIFY(UDN_DELTAPOS, IDC_FASTCOMP_CAP_SPINNER, OnDeltaposFastCompCapSpinner)
	ON_EN_CHANGE(IDC_FASTCOMP_TAU, OnChangeFastCompTau)
	ON_NOTIFY(UDN_DELTAPOS, IDC_FASTCOMP_TAU_SPINNER, OnDeltaposFastCompTauSpinner)
	ON_EN_CHANGE(IDC_SLOWCOMP_CAP, OnChangeSlowCompCap)
	ON_NOTIFY(UDN_DELTAPOS, IDC_SLOWCOMP_CAP_SPINNER, OnDeltaposSlowCompCapSpinner)
	ON_EN_CHANGE(IDC_SLOWCOMP_TAU, OnChangeSlowCompTau)
	ON_NOTIFY(UDN_DELTAPOS, IDC_SLOWCOMP_TAU_SPINNER, OnDeltaposSlowCompTauSpinner)
   ON_EN_CHANGE(IDC_INJSLOWCURRENTLEVEL, OnChangeInjSlowCurrentLevel)
   ON_NOTIFY(UDN_DELTAPOS, IDC_INJSLOWCURRENTLEVEL_SPINNER, OnDeltaposInjSlowCurrentLevelSpinner)
   ON_CBN_SELCHANGE(IDC_PRIMARYSIGNAL, OnSelchangePrimarySignal)
	ON_CBN_SELCHANGE(IDC_PRIMARYGAIN, OnSelchangePrimaryGain)
	ON_CBN_SELCHANGE(IDC_PRIMARYLPF, OnSelchangePrimaryLPF)
	ON_CBN_SELCHANGE(IDC_PRIMARYHPF, OnSelchangePrimaryHPF)
   ON_CBN_SELCHANGE(IDC_SECONDARYSIGNAL, OnSelchangeSecondarySignal)
	ON_CBN_SELCHANGE(IDC_SECONDARYGAIN, OnSelchangeSecondaryGain)
	ON_CBN_SELCHANGE(IDC_SECONDARYLPF, OnSelchangeSecondaryLPF)
	ON_BN_CLICKED(IDC_METERRESIST, OnMeterResist)
	ON_BN_CLICKED(IDC_METERIRMS, OnMeterIrms)
	ON_BN_CLICKED(IDC_BRIDGEBAL_AUTO, OnBridgeBalAuto)
	ON_BN_CLICKED(IDC_BRIDGEBAL_ENBL, OnBridgeBalEnbl)
	ON_BN_CLICKED(IDC_METER1, OnGetMeter1)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCCMSG_TestBedDlg message handlers

//==============================================================================================
// FUNCTION: OnInitDialog
// PURPOSE:  
//
BOOL CMCCMSG_TestBedDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	// TODO: Add extra initialization here
   m_cbxZapDuration.SetCurSel(5);

   FillPrimarySignalCombo();
   m_cbxPrimaryGain.SetCurSel(0);
   m_cbxPrimaryLPF.SetCurSel(5);

   FillSecondarySignalCombo();
   m_cbxSecondaryLPF.SetCurSel(0);
	m_cbxSecondaryGain.SetCurSel(0);
	m_cbxPrimaryHPF.SetCurSel(0);
   
   m_spnPipetteOffset.SetRange32(-100, 100);
   m_strPipetteOffset.Format("25");

   m_spnFastCompCap.SetRange32(-3, 36);
   m_strFastCompCap.Format("0");

   m_spnSlowCompCap.SetRange32(0, 3);
   m_strSlowCompCap.Format("0");

   m_spnFastCompTau.SetRange32(0, 2);
   m_strFastCompTau.Format("0");

   m_spnSlowCompTau.SetRange32(10, 4000);
   m_strSlowCompTau.Format("200");

   m_spnInjSlowCurrentLevel.SetRange32(-1000, 1000);
   m_strInjSlowCurrentLevel.Format("0");

   m_cbxDeviceInfo.EnableWindow( FALSE );
   m_cbxDeviceInfo.AddString( s_cszNoDevice );
   m_cbxDeviceInfo.SetItemData( m_cbxDeviceInfo.GetCurSel(), s_cdwNoDevice );
   m_cbxDeviceInfo.SetCurSel( 0 );

   UpdateData(FALSE);
   UIUpdate();

	return TRUE;  // return TRUE  unless you set the focus to a control
}

//==============================================================================================
// FUNCTION: OnSysCommand
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

//==============================================================================================
// FUNCTION: OnPaint
// PURPOSE:  If you add a minimize button to your dialog, you will need the code below
//           to draw the icon.  For MFC applications using the document/view model,
//           this is automatically done for you by the framework.
//
void CMCCMSG_TestBedDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

//==============================================================================================
// FUNCTION: OnQueryDragIcon
// PURPOSE:  The system calls this to obtain the cursor to display while the user drags
//           the minimized window.
HCURSOR CMCCMSG_TestBedDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

//==============================================================================================
// FUNCTION: DisplayErrorMsg
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::DisplayErrorMsg(int nError)
{
   char szError[256];
   MCCMSG_BuildErrorText(m_hMCCmsg, nError, szError, sizeof(szError));
   AfxMessageBox(szError, MB_ICONSTOP);
}

//===============================================================================================
// FUNCTION: UIUpdate
// PURPOSE:  Update controls
//
void CMCCMSG_TestBedDlg::UIUpdate(void)
{
   // enables all controls if DLL has been created
   BOOL bEnable = (BOOL)m_hMCCmsg;
   CWnd * pWnd = GetWindow(GW_CHILD);
   while( pWnd )
   {  
      // all other ctrls are disabled when DLL is uninitialized
      if( pWnd->GetDlgCtrlID() == (WORD)IDC_CREATE )
         pWnd->EnableWindow(!bEnable); 
      else 
         pWnd->EnableWindow(bEnable);

      pWnd = pWnd->GetWindow(GW_HWNDNEXT);
   }

   // exceptions to the above rule follow:

   // close button is always enabled
   pWnd = GetDlgItem(IDOK);
   pWnd->EnableWindow(TRUE);

   // device combo box enabled only when connection established
   pWnd = GetDlgItem(IDC_SELECTDEVICE);
   pWnd->EnableWindow(m_bSelected);
}

//==============================================================================================
// FUNCTION: OnCreate
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnCreate() 
{
   if( !MCCMSG_CheckAPIVersion(MCCMSG_APIVERSION_STR) )
   {
      AfxMessageBox("Version mismatch: AXMULTICLAMPMSG.DLL", MB_ICONSTOP);
      return;
   }

   int nError;
   m_hMCCmsg = MCCMSG_CreateObject(&nError);
   if( !m_hMCCmsg )
   {
      DisplayErrorMsg(nError);
      return;
   }

   // set timeout to 3 sec, default is also 3 sec
   UINT uTimeOut = 3000; // milliseconds
   if( !MCCMSG_SetTimeOut(m_hMCCmsg, uTimeOut, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   UIUpdate();
}

//==============================================================================================
// FUNCTION: OnDestroy
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDestroy() 
{
   MCCMSG_DestroyObject(m_hMCCmsg);
   m_hMCCmsg         = NULL;
	m_strModel        = _T("");
	m_strSerialNum    = _T("");
	m_strCOMPortID    = _T("");
	m_strDeviceID     = _T("");
	m_strChannelID    = _T("");
	m_strDeviceStatus.Format(s_cszNotConnected);
   m_bSelected      = FALSE;

   m_cbxDeviceInfo.ResetContent();
   m_cbxDeviceInfo.AddString( s_cszNoDevice );
   m_cbxDeviceInfo.SetItemData( m_cbxDeviceInfo.GetCurSel(), s_cdwNoDevice );
   m_cbxDeviceInfo.SetCurSel( 0 );

   UpdateData(FALSE);
   UIUpdate();
}

//==============================================================================================
// FUNCTION: OnScan
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnScan() 
{
   int nError, nIndex = 0;
   GetDlgItem(IDC_SCAN)->EnableWindow(FALSE);
   m_cbxDeviceInfo.EnableWindow(FALSE);

   // set timeout to 1 sec, all MultiClamps Commanders must respond within 1 sec 
   UINT uTimeOut = 1000; // milliseconds
   if( !MCCMSG_SetTimeOut(m_hMCCmsg, uTimeOut, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   // find first multiclamp
   if( !MCCMSG_FindFirstMultiClamp(m_hMCCmsg, &m_uModel, m_szSerialNum, sizeof(m_szSerialNum), &m_uCOMPortID, &m_uDeviceID, &m_uChannelID, &nError) )
   {
      DisplayErrorMsg(nError);
      
      GetDlgItem(IDC_SCAN)->EnableWindow(TRUE);
      m_cbxDeviceInfo.ResetContent();
      m_cbxDeviceInfo.AddString( s_cszNoDevice );
      m_cbxDeviceInfo.SetItemData( m_cbxDeviceInfo.GetCurSel(), s_cdwNoDevice );
      m_cbxDeviceInfo.SetCurSel( 0 );
      return;
   }

   // find next multiclamps until none are found
   m_cbxDeviceInfo.ResetContent();
   CString strBuf;
   while(1)
   {  
      // create string with multiclamp details
      if( m_uModel == MCCMSG_HW_TYPE_MC700A )
         strBuf.Format("COM %d, Device %d, Channel %d", m_uCOMPortID, m_uDeviceID, m_uChannelID);
      else if( m_uModel == MCCMSG_HW_TYPE_MC700B )
         strBuf.Format("Serial Number %s , Channel %d", m_szSerialNum, m_uChannelID);

      // stash multiclamp details in combo box
      m_cbxDeviceInfo.AddString(strBuf);
      m_cbxDeviceInfo.SetItemData(nIndex++, m_uModel);

      // search for another multiclamp, break when FALSE
      if( !MCCMSG_FindNextMultiClamp(m_hMCCmsg, &m_uModel, m_szSerialNum, sizeof(m_szSerialNum), &m_uCOMPortID, &m_uDeviceID, &m_uChannelID, &nError) )
         break;
   }

   // restore timeout to 3 sec because some auto commands can take more than 2 secs.
   uTimeOut = 3000; // milliseconds
   if( !MCCMSG_SetTimeOut(m_hMCCmsg, uTimeOut, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   m_cbxDeviceInfo.SetCurSel( 0 );
   m_cbxDeviceInfo.EnableWindow(TRUE);
   GetDlgItem(IDC_SCAN)->EnableWindow(TRUE);
}

//==============================================================================================
// FUNCTION: OnSelChangeSelectDevice
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelChangeSelectDevice() 
{
   int nError = 0;
   UpdateData();

   // check that combo has data
   if( m_cbxDeviceInfo.GetItemData( m_cbxDeviceInfo.GetCurSel() ) == s_cdwNoDevice )
      return;

   // get the combo text
   char szItem[64] = {0};
   int nSel    = m_cbxDeviceInfo.GetCurSel();
   int nRetVal = m_cbxDeviceInfo.GetLBText(nSel, szItem);
   ASSERT(nRetVal != CB_ERR);

   // extract multiclamp 700A info out of combo box
   if( m_cbxDeviceInfo.GetItemData(nSel) == MCCMSG_HW_TYPE_MC700A )
   {
      m_uModel = MCCMSG_HW_TYPE_MC700A;
      int nNumFields = sscanf(szItem, "COM %d, Device %d, Channel %d", &m_uCOMPortID, &m_uDeviceID, &m_uChannelID);
      ASSERT( nNumFields == 3 );

	   m_strSerialNum.Format("Serial Number = NA");
	   m_strCOMPortID.Format("COM port = %d", m_uCOMPortID);
	   m_strDeviceID.Format("Device ID = %d", m_uDeviceID);
   }

   // extract multiclamp 700B info out of combo box
   else if( m_cbxDeviceInfo.GetItemData(nSel) == MCCMSG_HW_TYPE_MC700B )
   {
      m_uModel = MCCMSG_HW_TYPE_MC700B;
      int nNumFields = sscanf(szItem, "Serial Number %s , Channel %d", &m_szSerialNum[0], &m_uChannelID);
      ASSERT( nNumFields == 2 );

	   m_strSerialNum.Format("Serial Number = %s", m_szSerialNum);
	   m_strCOMPortID.Format("COM port = NA");
	   m_strDeviceID.Format("Device ID = NA");
   }
   m_strChannelID.Format("Channel ID = %d", m_uChannelID);

   // display instrument name
   if( m_uModel == MCCMSG_HW_TYPE_MC700A )
      m_strModel.Format("Model = MultiClamp 700A");
   else if( m_uModel == MCCMSG_HW_TYPE_MC700B )
      m_strModel.Format("Model = MultiClamp 700B");
      
   // select the multiclamp
   if( !MCCMSG_SelectMultiClamp(m_hMCCmsg, m_uModel, m_szSerialNum, m_uCOMPortID, m_uDeviceID, m_uChannelID, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

	m_strDeviceStatus.Format(s_cszConnected);
   m_bSelected = TRUE;
   UpdateData(FALSE);
}


//==============================================================================================
// FUNCTION: OnPipetteOffset
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnPipetteOffset() 
{
   // execute auto pipette offset
   int nError = 0;
   if( !MCCMSG_AutoPipetteOffset(m_hMCCmsg, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   // update pippette offset
   double dPipetteOffset;
   if( !MCCMSG_GetPipetteOffset(m_hMCCmsg, &dPipetteOffset, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
   m_strPipetteOffset.Format("%g", dPipetteOffset * 1e+3);
   UpdateData(FALSE);
}

//==============================================================================================
// FUNCTION: OnZap
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnZap() 
{
   int nError = 0;
   if( !MCCMSG_Zap(m_hMCCmsg, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
}

//==============================================================================================
// FUNCTION: OnBtnVClamp
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnBtnVClamp() 
{
   int nError = 0;
   if( !MCCMSG_SetMode(m_hMCCmsg, MCCMSG_MODE_VCLAMP, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
}

//==============================================================================================
// FUNCTION: OnBtnIClamp
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnBtnIClamp() 
{
   int nError = 0;
   if( !MCCMSG_SetMode(m_hMCCmsg, MCCMSG_MODE_ICLAMP, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
}

//==============================================================================================
// FUNCTION: OnBtnIClampZero
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnBtnIClampZero() 
{
   int nError = 0;
   if( !MCCMSG_SetMode(m_hMCCmsg, MCCMSG_MODE_ICLAMPZERO, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
}

//==============================================================================================
// FUNCTION: OnSelChangeZapDuration
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangeZapDuration() 
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   char szBuf[32];
   int nSel = m_cbxZapDuration.GetCurSel();
   m_cbxZapDuration.GetLBText(nSel, szBuf);
   double dZapDuration = atof(szBuf) / 1000000; 

   // send data
   int nError;
   if( !MCCMSG_SetZapDuration(m_hMCCmsg, dZapDuration, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnChangePipetteOffsetValue
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnChangePipetteOffsetValue() 
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   UpdateData();
   double dPipetteOffset = atof(m_strPipetteOffset) / 1000; 

   // send data
   int nError;
   if( !MCCMSG_SetPipetteOffset(m_hMCCmsg, dPipetteOffset, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnDeltaposPipetteOffsetValueSpinner
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDeltaposPipetteOffsetValueSpinner(NMHDR* pNMHDR, LRESULT* pResult) 
{
	NM_UPDOWN* pNMUpDown = (NM_UPDOWN*)pNMHDR;
   
   double dPipetteOffset = (atof(m_strPipetteOffset) + (pNMUpDown->iDelta)) / 1000;   
   m_strPipetteOffset.Format("%g", dPipetteOffset * 1000);
   UpdateData(FALSE);
	
   // send data
   int nError;
   if( !MCCMSG_SetPipetteOffset(m_hMCCmsg, dPipetteOffset, &nError) )
      DisplayErrorMsg(nError);

	*pResult = 0;
}

//==============================================================================================
// FUNCTION: OnFastCompAuto
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnFastCompAuto() 
{
   // execute auto fast comp
   int nError = 0;
   if( !MCCMSG_AutoFastComp(m_hMCCmsg, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   // update fast comp cap
   double dFastCompCap;
   if( !MCCMSG_GetFastCompCap(m_hMCCmsg, &dFastCompCap, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
   m_strFastCompCap.Format("%g", dFastCompCap * 1e+12);

   // update fast comp tau
   double dFastCompTau;
   if( !MCCMSG_GetFastCompTau(m_hMCCmsg, &dFastCompTau, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
   m_strFastCompTau.Format("%g", dFastCompTau * 1e+6);

   // update controls
   UpdateData(FALSE);
}

//==============================================================================================
// FUNCTION: OnSlowCompAuto
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSlowCompAuto() 
{
   // execute auto slow comp
   int nError = 0;
   if( !MCCMSG_AutoSlowComp(m_hMCCmsg, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   // update slow comp cap
   double dSlowCompCap;
   if( !MCCMSG_GetSlowCompCap(m_hMCCmsg, &dSlowCompCap, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
   m_strSlowCompCap.Format("%g", dSlowCompCap * 1e+12);

   // update slow comp tau
   double dSlowCompTau;
   if( !MCCMSG_GetSlowCompTau(m_hMCCmsg, &dSlowCompTau, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }
   m_strSlowCompTau.Format("%g", dSlowCompTau * 1e+6);

   // update controls
   UpdateData(FALSE);
}

//==============================================================================================
// FUNCTION: OnChangeFastCompCap
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnChangeFastCompCap() 
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   UpdateData();
   double dFastCompCap = atof(m_strFastCompCap) / 1e+12; 

   // send data
   int nError;
   if( !MCCMSG_SetFastCompCap(m_hMCCmsg, dFastCompCap, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnDeltaposFastCompCapSpinner
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDeltaposFastCompCapSpinner(NMHDR* pNMHDR, LRESULT* pResult) 
{
	NM_UPDOWN* pNMUpDown = (NM_UPDOWN*)pNMHDR;

   double dFastCompCap = (atof(m_strFastCompCap) + (pNMUpDown->iDelta)) / 1e+12;   
   m_strFastCompCap.Format("%g", dFastCompCap * 1e+12);
   UpdateData(FALSE);
	
   // send data
   int nError;
   if( !MCCMSG_SetFastCompCap(m_hMCCmsg, dFastCompCap, &nError) )
      DisplayErrorMsg(nError);
	
	*pResult = 0;
}

//==============================================================================================
// FUNCTION: OnChangeFastCompTau
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnChangeFastCompTau() 
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   UpdateData();
   double dFastCompTau = atof(m_strFastCompTau) / 1e+6; 

   // send data
   int nError;
   if( !MCCMSG_SetFastCompTau(m_hMCCmsg, dFastCompTau, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnDeltaposFastCompTauSpinner
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDeltaposFastCompTauSpinner(NMHDR* pNMHDR, LRESULT* pResult) 
{
	NM_UPDOWN* pNMUpDown = (NM_UPDOWN*)pNMHDR;

   double dFastCompTau = (atof(m_strFastCompTau) + (pNMUpDown->iDelta)) / 1e+6;   
   m_strFastCompTau.Format("%g", dFastCompTau * 1e+6);
   UpdateData(FALSE);
	
   // send data
   int nError;
   if( !MCCMSG_SetFastCompTau(m_hMCCmsg, dFastCompTau, &nError) )
      DisplayErrorMsg(nError);
	
	*pResult = 0;
}

//==============================================================================================
// FUNCTION: OnChangeSlowCompCap
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnChangeSlowCompCap() 
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   UpdateData();
   double dSlowCompCap = atof(m_strSlowCompCap) / 1e+12; 

   // send data
   int nError;
   if( !MCCMSG_SetSlowCompCap(m_hMCCmsg, dSlowCompCap, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnDeltaposSlowCompCapSpinner
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDeltaposSlowCompCapSpinner(NMHDR* pNMHDR, LRESULT* pResult) 
{
	NM_UPDOWN* pNMUpDown = (NM_UPDOWN*)pNMHDR;

   double dSlowCompCap = (atof(m_strSlowCompCap) + (pNMUpDown->iDelta)) / 1e+12;   
   m_strSlowCompCap.Format("%g", dSlowCompCap * 1e+12);
   UpdateData(FALSE);
	
   // send data
   int nError;
   if( !MCCMSG_SetSlowCompCap(m_hMCCmsg, dSlowCompCap, &nError) )
      DisplayErrorMsg(nError);
	
	*pResult = 0;
}

//==============================================================================================
// FUNCTION: OnChangeSlowCompTau
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnChangeSlowCompTau() 
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   UpdateData();
   double dSlowCompTau = atof(m_strSlowCompTau) / 1e+6; 

   // send data
   int nError;
   if( !MCCMSG_SetSlowCompTau(m_hMCCmsg, dSlowCompTau, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnDeltaposSlowCompTauSpinner
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDeltaposSlowCompTauSpinner(NMHDR* pNMHDR, LRESULT* pResult) 
{
	NM_UPDOWN* pNMUpDown = (NM_UPDOWN*)pNMHDR;

   double dSlowCompTau = (atof(m_strSlowCompTau) + (pNMUpDown->iDelta)) / 1e+6;   
   m_strSlowCompTau.Format("%g", dSlowCompTau * 1e+6);
   UpdateData(FALSE);
	
   // send data
   int nError;
   if( !MCCMSG_SetSlowCompTau(m_hMCCmsg, dSlowCompTau, &nError) )
      DisplayErrorMsg(nError);
	
	*pResult = 0;
}


//==============================================================================================
// FUNCTION: OnSelchangePrimaryGain
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangePrimaryGain() 
{
   if( !m_hMCCmsg )
      return;

   // get primary gain
   char szBuf[32];
   int nSel = m_cbxPrimaryGain.GetCurSel();
   m_cbxPrimaryGain.GetLBText(nSel, szBuf);
   double dPrimaryGain = atof(szBuf); 

   // send data
   int nError;
   if( !MCCMSG_SetPrimarySignalGain(m_hMCCmsg, dPrimaryGain, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnSelchangePrimaryLPF
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangePrimaryLPF() 
{
   if( !m_hMCCmsg )
      return;

   // get primary LPF
   char szBuf[32];
   int nSel = m_cbxPrimaryLPF.GetCurSel();
   m_cbxPrimaryLPF.GetLBText(nSel, szBuf);
   double dPrimaryLPF = atof(szBuf); 

   // send data
   int nError;
   if( !MCCMSG_SetPrimarySignalLPF(m_hMCCmsg, dPrimaryLPF, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnSelchangePrimaryHPF
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangePrimaryHPF() 
{
   if( !m_hMCCmsg )
      return;

   // get primary HPF
   char szBuf[32];
   int nSel = m_cbxPrimaryHPF.GetCurSel();
   m_cbxPrimaryHPF.GetLBText(nSel, szBuf);
   double dPrimaryHPF = atof(szBuf); 

   // send data
   int nError;
   if( !MCCMSG_SetPrimarySignalHPF(m_hMCCmsg, dPrimaryHPF, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnSelchangeSecondaryGain
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangeSecondaryGain() 
{
   if( !m_hMCCmsg )
      return;

   // get secondary gain
   char szBuf[32];
   int nSel = m_cbxSecondaryGain.GetCurSel();
   m_cbxSecondaryGain.GetLBText(nSel, szBuf);
   double dSecondaryGain = atof(szBuf); 

   // send data
   int nError;
   if( !MCCMSG_SetSecondarySignalGain(m_hMCCmsg, dSecondaryGain, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnSelchangeSecondaryLPF
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangeSecondaryLPF() 
{
   if( !m_hMCCmsg )
      return;

   // get secondary LPF
   char szBuf[32];
   int nSel = m_cbxSecondaryLPF.GetCurSel();
   m_cbxSecondaryLPF.GetLBText(nSel, szBuf);
   double dSecondaryLPF = atof(szBuf); 

   // send data
   int nError;
   if( !MCCMSG_SetSecondarySignalLPF(m_hMCCmsg, dSecondaryLPF, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnMeterResist
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnMeterResist() 
{
   // retreive data
   UpdateData();

   // send data
   int nError;
   BOOL bEnable = m_btnMeterResist.GetCheck();
   if( !MCCMSG_SetMeterResistEnable(m_hMCCmsg, bEnable, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnMeterIrms
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnMeterIrms() 
{
   // retreive data
   UpdateData();

   // send data
   int nError;
   BOOL bEnable = m_btnMeterIrms.GetCheck();
   if( !MCCMSG_SetMeterIrmsEnable(m_hMCCmsg, bEnable, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnChangeInjSlowCurrentLevel
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnChangeInjSlowCurrentLevel()
{
   if( !m_hMCCmsg )
      return;

   // get zap duration
   UpdateData();
   double dInjSlowCurrentLevel = atof(m_strInjSlowCurrentLevel) / 1e+3; 

   // send data
   int nError;
   if( !MCCMSG_SetSlowCurrentInjLevel(m_hMCCmsg, dInjSlowCurrentLevel, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnDeltaposInjSlowCurrentLevelSpinner
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnDeltaposInjSlowCurrentLevelSpinner(NMHDR *pNMHDR, LRESULT *pResult)
{
	NM_UPDOWN* pNMUpDown = (NM_UPDOWN*)pNMHDR;

   double dInjSlowCurrentLevel = (atof(m_strInjSlowCurrentLevel) + (pNMUpDown->iDelta)) / 1e+3;   
   m_strInjSlowCurrentLevel.Format("%g", dInjSlowCurrentLevel * 1e+3);
   UpdateData(FALSE);
	
   // send data
   int nError;
   if( !MCCMSG_SetSlowCurrentInjLevel(m_hMCCmsg, dInjSlowCurrentLevel, &nError) )
      DisplayErrorMsg(nError);
	
	*pResult = 0;
}

//==============================================================================================
// FUNCTION: OnSelchangePrimarySignal
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangePrimarySignal()
{
   if( !m_hMCCmsg )
      return;

   UpdateData();
   UINT uSel = m_cbxPrimarySignal.GetCurSel();
   UINT uSignalID = m_cbxPrimarySignal.GetItemData(uSel);

   // send data
   int nError;
   if( !MCCMSG_SetPrimarySignal(m_hMCCmsg, uSignalID, &nError) )
      DisplayErrorMsg(nError);
}

//==============================================================================================
// FUNCTION: OnSelchangeSecondarySignal
// PURPOSE:  
//
void CMCCMSG_TestBedDlg::OnSelchangeSecondarySignal()
{
   if( !m_hMCCmsg )
      return;

   UpdateData();
   UINT uSel = m_cbxSecondarySignal.GetCurSel();
   UINT uSignalID = m_cbxSecondarySignal.GetItemData(uSel);

   // send data
   int nError;
   if( !MCCMSG_SetSecondarySignal(m_hMCCmsg, uSignalID, &nError) )
      DisplayErrorMsg(nError);
}

//===============================================================================================
// FUNCTION: FillPrimarySignalCombo
// PURPOSE:  .
//
BOOL CMCCMSG_TestBedDlg::FillPrimarySignalCombo()
{
   m_cbxPrimarySignal.ResetContent();
   for(UINT i=0; i<sizeof(PRIMARYSIGNAL)/sizeof(SignalDef); i++)
   {
      m_cbxPrimarySignal.AddString( PRIMARYSIGNAL[i].m_pszName );
      m_cbxPrimarySignal.SetItemData( i, PRIMARYSIGNAL[i].m_uID );
   }

   m_cbxPrimarySignal.SetCurSel( 0 );
   return TRUE;
}

//===============================================================================================
// FUNCTION: FillSecondarySignalCombo
// PURPOSE:  .
//
BOOL CMCCMSG_TestBedDlg::FillSecondarySignalCombo()
{
   m_cbxSecondarySignal.ResetContent();
   for(UINT i=0; i<sizeof(SECONDARYSIGNAL)/sizeof(SignalDef); i++)
   {
      m_cbxSecondarySignal.AddString( SECONDARYSIGNAL[i].m_pszName );
      m_cbxSecondarySignal.SetItemData( i, SECONDARYSIGNAL[i].m_uID );
   }

   m_cbxSecondarySignal.SetCurSel( 0 );
   return TRUE;
}

//===============================================================================================
// FUNCTION: OnBridgeBalAuto
// PURPOSE:  .
//
void CMCCMSG_TestBedDlg::OnBridgeBalAuto() 
{
   int nError = 0;
   if( !MCCMSG_AutoBridgeBal(m_hMCCmsg, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }	
}

//===============================================================================================
// FUNCTION: OnBridgeBalAuto
// PURPOSE:  .
//
void CMCCMSG_TestBedDlg::OnBridgeBalEnbl() 
{
   UpdateData();

   // send data
   int nError = 0;
   BOOL bEnable = m_btnBridgeBal.GetCheck();

   if( !MCCMSG_SetBridgeBalEnable(m_hMCCmsg, bEnable, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }	
}

//===============================================================================================
// FUNCTION: OnGetMeter1
// PURPOSE:  .
//
void CMCCMSG_TestBedDlg::OnGetMeter1() 
{
   int nError = 0;
   double dValue = 0.0;
   if( !MCCMSG_GetMeterValue(m_hMCCmsg, &dValue, MCCMSG_METER1, &nError) )
   {
      DisplayErrorMsg(nError);
      return;
   }

   m_strMeter1Value.Format("%.4g mV", dValue);
   UpdateData(FALSE);
}
