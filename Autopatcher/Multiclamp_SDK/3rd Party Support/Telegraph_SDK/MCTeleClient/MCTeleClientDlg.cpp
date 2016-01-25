//////////////////////////////////////////////////////////////////////////////////////
//
//    Copyright (c) 2003 Axon Instruments, Inc.
//    All rights reserved.
//
//////////////////////////////////////////////////////////////////////////////////////
// FILE:    MCTeleClientDlg.cpp
// PURPOSE: Implementation of MCTeleClient
//          Main Dialog Class
//

#include "stdafx.h"
#include "MCTeleClient.h"
#include "MCTeleClientDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

// alarm code which will set off a compilation error
// if the version of the MultiClamp telegraph API changes
// or if the size of the MC_TELEGRAPH_DATA structure changes
static UINT s_uTestMCTGVersion [ ( MCTG_API_VERSION          ==  13 ) ? 1 : 0 ];
static UINT s_uTestMCTGData    [ ( sizeof(MC_TELEGRAPH_DATA) == 256 ) ? 1 : 0 ];

static       UINT s_uMCTGOpenMessage          = 0;
static       UINT s_uMCTGCloseMessage         = 0;
static       UINT s_uMCTGRequestMessage       = 0;
static       UINT s_uMCTGReconnectMessage     = 0;
static       UINT s_uMCTGBroadcastMessage     = 0;
static       UINT s_uMCTGIdMessage            = 0;

static const UINT s_cuConnectionTimerEventID  = 13377; // arbitrary
static const UINT s_cuConnectionTimerInterval = 1000;  // millisec

static const UINT s_cuRequestTimerEventID     = 24488; // arbitrary
static const UINT s_cuRequestTimerInterval    = 1000;  // millisec
static const UINT s_cuScanMultiClampTimeOutMS = 10;
static const UINT s_cuNumMultiClampScans      = 100;

// magic number indicating USB port scan detected no devices
static const DWORD s_cdwNoDevice              = 13561;
static const char  s_cszNoDevice[]            = "No Device";

static void MessagePump()
{
   MSG msg;
   while( PeekMessage( &msg, NULL, 0, 0, PM_REMOVE ) )
   {               
      TranslateMessage( &msg );
      DispatchMessage( &msg );
   }
}      

/////////////////////////////////////////////////////////////////////////////
// CMCTeleClientDlg dialog

//==============================================================================================
// FUNCTION: CMCTeleClientDlg
// PURPOSE:  
//
CMCTeleClientDlg::CMCTeleClientDlg(CWnd* pParent /*=NULL*/)
:  CDialog(CMCTeleClientDlg::IDD, pParent),
   m_bIsConnected    ( FALSE ),
   m_bIsConnecting   ( FALSE ),
   m_bScanning       ( FALSE ),
   m_bRequestPending ( FALSE )
{
	//{{AFX_DATA_INIT(CMCTeleClientDlg)
	m_cstrMode           = _T("");
	m_cstrPriSignal      = _T("");
	m_cstrPriAlpha       = _T("");
	m_cstrPriScaleFactor = _T("");
	m_cstrPriLPFCutoff   = _T("");
	m_cstrSecSignal      = _T("");
	m_cstrSecAlpha       = _T("");
	m_cstrSecScaleFactor = _T("");
	m_cstrSecLPFCutoff   = _T("");
	m_cstrMembraneCap    = _T("");
	m_cstrExtCmdSens     = _T("");
	m_cstrAppVer         = _T("");
	m_cstrDSPVer         = _T("");
	m_cstrFirmwareVer    = _T("");
	m_cstrSN             = _T("");
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);

   m_vSerialNum.clear();

   s_uMCTGOpenMessage = RegisterWindowMessage( MCTG_OPEN_MESSAGE_STR );
   ASSERT( s_uMCTGOpenMessage != 0 );

   s_uMCTGCloseMessage = RegisterWindowMessage( MCTG_CLOSE_MESSAGE_STR );
   ASSERT( s_uMCTGCloseMessage != 0 );

   s_uMCTGRequestMessage = RegisterWindowMessage( MCTG_REQUEST_MESSAGE_STR );
   ASSERT( s_uMCTGRequestMessage != 0 );

   s_uMCTGReconnectMessage = RegisterWindowMessage( MCTG_RECONNECT_MESSAGE_STR );
   ASSERT( s_uMCTGReconnectMessage != 0 );

   s_uMCTGBroadcastMessage = RegisterWindowMessage( MCTG_BROADCAST_MESSAGE_STR );
   ASSERT( s_uMCTGBroadcastMessage != 0 );

   s_uMCTGIdMessage = RegisterWindowMessage( MCTG_ID_MESSAGE_STR );
   ASSERT( s_uMCTGIdMessage != 0 );

   // initialize the current telegraph state

   // this bit will zero out the padding in the structure
   MC_TELEGRAPH_DATA* pmctd = &m_mctdCurrentState;
   memset(pmctd, 0, sizeof(MC_TELEGRAPH_DATA));

   m_mctdCurrentState.uVersion              = MCTG_API_VERSION;
   m_mctdCurrentState.uStructSize           = sizeof(MC_TELEGRAPH_DATA);
   m_mctdCurrentState.uComPortID            = 1;
   m_mctdCurrentState.uAxoBusID             = 0;
   m_mctdCurrentState.uChannelID            = 1;
   m_mctdCurrentState.uOperatingMode        = MCTG_MODE_VCLAMP;
   m_mctdCurrentState.uScaledOutSignal      = AXMCD_OUT_PRI_VC_GLDR_V_CMD_EXT;
   m_mctdCurrentState.dAlpha                = 0.0;
   m_mctdCurrentState.dScaleFactor          = 0.0;
   m_mctdCurrentState.uScaleFactorUnits     = MCTG_UNITS_VOLTS_PER_VOLT;
   m_mctdCurrentState.dRawScaleFactor       = 0.0;
   m_mctdCurrentState.uRawScaleFactorUnits  = MCTG_UNITS_VOLTS_PER_VOLT;
   m_mctdCurrentState.dLPFCutoff            = 0.0;
   m_mctdCurrentState.dMembraneCap          = 0.0;
   m_mctdCurrentState.dExtCmdSens           = 0.0;
   m_mctdCurrentState.dSecondaryAlpha       = 0.0;
   m_mctdCurrentState.dSecondaryLPFCutoff   = 0.0;
}

//==============================================================================================
// FUNCTION: ~CMCTeleClientDlg
// PURPOSE:  
//
CMCTeleClientDlg::~CMCTeleClientDlg()
{
}

//==============================================================================================
// FUNCTION: DoDataExchange
// PURPOSE:  
//
void CMCTeleClientDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CMCTeleClientDlg)
	DDX_Control ( pDX, IDC_SERIALNUM,       m_cbxSerialNum    );
	DDX_Control ( pDX, IDC_CHANNEL,         m_cbxChannel         );
	DDX_Control ( pDX, IDC_SCAN,            m_btnScan            );
	DDX_Control ( pDX, IDC_CONNECT,         m_btnConnect         );
	DDX_Control ( pDX, IDC_BROADCAST,       m_btnBroadcast       );
	DDX_Control ( pDX, IDC_DEVICELIST,      m_lbxDeviceList      ); 
	DDX_Text    ( pDX, IDC_MODE,            m_cstrMode           );
	DDX_Text    ( pDX, IDC_SIGNAL_PRI,      m_cstrPriSignal      );
	DDX_Text    ( pDX, IDC_ALPHA_PRI,       m_cstrPriAlpha       );
	DDX_Text    ( pDX, IDC_SCALEFACTOR_PRI, m_cstrPriScaleFactor );
	DDX_Text    ( pDX, IDC_LPFCUTOFF_PRI,   m_cstrPriLPFCutoff   );
	DDX_Text    ( pDX, IDC_SIGNAL_SEC,      m_cstrSecSignal      );
	DDX_Text    ( pDX, IDC_ALPHA_SEC,       m_cstrSecAlpha       );
	DDX_Text    ( pDX, IDC_SCALEFACTOR_SEC, m_cstrSecScaleFactor );
	DDX_Text    ( pDX, IDC_LPFCUTOFF_SEC,   m_cstrSecLPFCutoff   );
	DDX_Text    ( pDX, IDC_MEMBRANECAP,     m_cstrMembraneCap    );
	DDX_Text    ( pDX, IDC_EXTCMDSENS,      m_cstrExtCmdSens     );
	DDX_Text    ( pDX, IDC_APPVER,          m_cstrAppVer         );
	DDX_Text    ( pDX, IDC_DSPVER,          m_cstrDSPVer         );
	DDX_Text    ( pDX, IDC_FIRMVER,         m_cstrFirmwareVer    );
	DDX_Text    ( pDX, IDC_SN,              m_cstrSN             );
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CMCTeleClientDlg, CDialog)
	//{{AFX_MSG_MAP(CMCTeleClientDlg)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_CONNECT, OnConnect)
	ON_CBN_SELCHANGE(IDC_CHANNEL, OnSelChangeChannel)
	ON_BN_CLICKED(IDC_REQUEST, OnRequest)
	ON_WM_CLOSE()
	ON_BN_CLICKED(IDC_BROADCAST, OnBroadcast)
	ON_BN_CLICKED(IDC_SCAN, OnScan)
	ON_LBN_SELCHANGE(IDC_DEVICELIST, OnSelChangeDeviceList)
	ON_CBN_SELCHANGE(IDC_SERIALNUM, OnSelChangeSerialNum)
	ON_WM_COPYDATA()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCTeleClientDlg message handlers


//==============================================================================================
// FUNCTION: OnInitDialog
// PURPOSE:  
//
BOOL CMCTeleClientDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	

   // initialize combo box selections
   int nRetVal = 0;

   // serial num init
   m_cbxSerialNum.ResetContent();
   m_cbxSerialNum.AddString( s_cszNoDevice );
   m_cbxSerialNum.SetItemData( m_cbxSerialNum.GetCurSel(), s_cdwNoDevice );
   m_cbxSerialNum.EnableWindow( FALSE );
   m_cbxSerialNum.SetCurSel( 0 );

   // -1 ( channel IDs start with 1 )
   nRetVal = m_cbxChannel.SetCurSel(m_mctdCurrentState.uChannelID - 1);
   ASSERT(nRetVal != CB_ERR);

   // -1 ( no device selection)
   m_lbxDeviceList.ResetContent();

   ClearDisplay();

   // get the file version
   char pszFileVer[128];
   GetFileVersion(pszFileVer, sizeof(pszFileVer));
   
   // create dialog title
   char pszTitle[128];
   sprintf(pszTitle, "MultiClamp Telegraph Client %s", pszFileVer);
   SetWindowText(pszTitle);

	return TRUE;  // return TRUE  unless you set the focus to a control
}

//==============================================================================================
// FUNCTION: GetFileVersion
// PURPOSE:  
//
BOOL CMCTeleClientDlg::GetFileVersion( char * pszFileVer, UINT uSize )
{
   // write application's executable file name
   // in the local string buffer for use with
   // GetFileVersionInfoSize( ) and GetFileVersionInfo( )
   sprintf( pszFileVer, "%s.exe", AfxGetAppName( ) );

   // find out how big the version info resource is
   DWORD dwVersionInfoSize = 0;
   DWORD dwHandle          = 0;
   dwVersionInfoSize = GetFileVersionInfoSize( pszFileVer, &dwHandle );
   if( dwVersionInfoSize == 0 )
   {
      ASSERT( FALSE );
      return FALSE;
   }

   // allocate version info buffer
   char* pVersionInfoBuf = new char[dwVersionInfoSize];
   if ( pVersionInfoBuf == NULL )
   {
      ASSERT( FALSE );
      return FALSE;
   }

   // read the version info data
   if( !GetFileVersionInfo( pszFileVer,
                            dwHandle,
                            dwVersionInfoSize,
                            pVersionInfoBuf    ) )
   {
      ASSERT( FALSE );
      delete pVersionInfoBuf;
      return FALSE;
   }               

   // some variables we will need for VerQueryValue( )
   void* pvVersionString    = NULL;
   UINT  uVersionStringSize = 0;

   /////////////////////////////////////////////////////////////////
   // initialize file verison string
   /////////////////////////////////////////////////////////////////
   if( !VerQueryValue( pVersionInfoBuf, 
                       "\\StringFileInfo\\040904B0\\FileVersion", 
                       &pvVersionString,
                       &uVersionStringSize 
                      ) )
   {
      ASSERT( FALSE );
      delete pVersionInfoBuf;
      return FALSE;
   }
   else
   {   
      // truncate version string if it exceeds our buffer length
      if( uVersionStringSize >= uSize )
      {
         // -1 to guarantee at least 1 '\0'
         uVersionStringSize = uSize - 1;
      }
      memset( pszFileVer, '\0', uSize );
      strncpy(pszFileVer, (char*) pvVersionString, uVersionStringSize);
   }

   delete [] pVersionInfoBuf;
   return TRUE;
}

//==============================================================================================
// FUNCTION: OnPaint
// PURPOSE:  If you add a minimize button to your dialog, you will need the code below
//           to draw the icon.  For MFC applications using the document/view model,
//           this is automatically done for you by the framework.
//
void CMCTeleClientDlg::OnPaint() 
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
//
HCURSOR CMCTeleClientDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

//==============================================================================================
// FUNCTION: WindowProc
// PURPOSE:  
//
LRESULT CMCTeleClientDlg::WindowProc(UINT message, WPARAM wParam, LPARAM lParam) 
{
   if( ( message == WM_TIMER                   ) &&
       ( wParam  == s_cuConnectionTimerEventID )    )
   {
      // connection timer has gone off
      // we are no longer attempting to connect
      m_bIsConnecting = FALSE;

      KillTimer( s_cuConnectionTimerEventID );

      if(!m_bIsConnected)
      {
         // timed out without establishing a connection
         m_btnScan.EnableWindow( TRUE );
         AfxMessageBox("Failed to connect!");
      }

      return TRUE;
   }

   if( ( message == WM_TIMER                   ) &&
       ( wParam  == s_cuRequestTimerEventID )    )
   {
      // packet request timer has gone off  
      KillTimer( s_cuRequestTimerEventID );

      if(m_bRequestPending)
      {
         // timed out without receiving requested packet
         AfxMessageBox("Requested packet not received!");
      }

      return TRUE;
   }

   if( message == WM_COPYDATA )
   {
      COPYDATASTRUCT* pcpds = (COPYDATASTRUCT*) lParam;
      if( ( pcpds->cbData == sizeof( MC_TELEGRAPH_DATA )    ) &&
          ( pcpds->dwData == (DWORD) s_uMCTGRequestMessage  )    )
      {
         // this WM_COPYDATA message contains MC_TELEGRAPH_DATA
         MC_TELEGRAPH_DATA* pmctdReceived    = (MC_TELEGRAPH_DATA*) pcpds->lpData;

         // here is a special case for the demo driver
         if( strncmp( pmctdReceived->szSerialNumber,  
                      "Demo Driver", 
                      sizeof(pmctdReceived->szSerialNumber) ) == 0 )
         {
            strncpy( pmctdReceived->szSerialNumber, 
                     "00000000",
                     sizeof(pmctdReceived->szSerialNumber) );
         }

         // is it the correct serial number
         if( strncmp( pmctdReceived->szSerialNumber, 
                      m_mctdCurrentState.szSerialNumber, 
                      sizeof(m_mctdCurrentState.szSerialNumber) ) != 0 )
         {
            // this message is from another MultiClamp device so ignore it
            return TRUE;
         }
                                 
         // is it on our channel ?
         if( pmctdReceived->uChannelID != m_mctdCurrentState.uChannelID )
         {
            // this message is from another MultiClamp channel so ignore it
            return TRUE;
         }

         // copy all telegraph packet data into data member struct
         m_mctdCurrentState = *pmctdReceived;

         if( m_bIsConnecting )
         {
            // our attempt to connect has succeeded before the timeout.
            // m_bIsConnected must be set before calling UpdateDisplay()
            m_btnScan.EnableWindow( FALSE );
            m_bIsConnected  = TRUE;
            m_bIsConnecting = FALSE;

            // we are finished with this timer
            KillTimer( s_cuConnectionTimerEventID );
         }

         if( m_bRequestPending )
         {
            // the requested packet has arrived before the timeout
            m_bRequestPending  = FALSE;

            // we are finished with this timer
            KillTimer( s_cuRequestTimerEventID );
         }

         UpdateDisplay();
         return TRUE;
      }
   }

   // process telegraph reconnect message
   if( message == s_uMCTGReconnectMessage )
   {
      if(!m_bIsConnected)
      {
         // there is no telegraph connection to reestablish.
         // ignore this request
         m_btnScan.EnableWindow( TRUE );
         return TRUE;
      }

      UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
      UINT uChannelID = m_mctdCurrentState.uChannelID;
      if(!MCTG_Match700BSignalIDs( uSerialNum,
                                   uChannelID,
                                   lParam      ) )
      {
         // this request is from a MultiClamp device / channel
         // other than the one we are connected to.
         // ignore it
         return TRUE;
      }

      // resend the open message to reestablish the connection
      // to the requesting server
      m_bIsConnected = FALSE;
      OnConnect();
      return TRUE;
   }

   // process telegraph id message
   if( message == s_uMCTGIdMessage )
   {
      // display the identification details of the server.
      UINT uSerialNum = 0;
      UINT uChannelID = 0;
      if( !MCTG_Unpack700BSignalIDs( lParam, &uSerialNum, &uChannelID ) )
      {
         return TRUE;
      }

      if( m_bScanning )
      {
         // stash serial number away
         AddSerialNum( uSerialNum );
      }
      else
      {
         OnBroadcastResponse( uSerialNum, uChannelID );
      }

      return TRUE;
   }

    return CDialog::WindowProc(message, wParam, lParam);
}

//==============================================================================================
// FUNCTION: UpdateDisplay
// PURPOSE:  
//
void CMCTeleClientDlg::UpdateDisplay()
{
   // enable / disable connection parameter widgets
   UpdateEnabling();

   // update the telegraph parameter display fields
   const unsigned int cuMaxDisplayStringSize = 128;
   char pszTemp[cuMaxDisplayStringSize];

   ///////////////////////////////////////////////////////////////////
   // operating mode
   ///////////////////////////////////////////////////////////////////
   if(m_mctdCurrentState.uOperatingMode < MCTG_MODE_NUMCHOICES)
   {
      sprintf( pszTemp, MCTG_MODE_NAMES[m_mctdCurrentState.uOperatingMode] );
   } 
   else
   {
      // this data is out of range
      // handle as you will
      sprintf(pszTemp, "Invalid Operating Mode!");
   }
	m_cstrMode = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // primary scaled output signal
   ///////////////////////////////////////////////////////////////////
   if(m_mctdCurrentState.uScaledOutSignal < AXMCD_OUT_NAMES_NUMCHOICES)
   {
      sprintf( pszTemp, MCTG_OUT_GLDR_LONG_NAMES[m_mctdCurrentState.uScaledOutSignal] );
   } 
   else
   {
      // this data is out of range
      // handle as you will
	   sprintf(pszTemp, "Go Bombers!");
   }
	m_cstrPriSignal = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // secondary scaled output signal
   ///////////////////////////////////////////////////////////////////
   if(m_mctdCurrentState.uRawOutSignal < AXMCD_OUT_NAMES_NUMCHOICES)
   {
      sprintf( pszTemp, MCTG_OUT_GLDR_LONG_NAMES[m_mctdCurrentState.uRawOutSignal] );
   } 
   else
   {
      // this data is out of range
      // handle as you will
	   sprintf(pszTemp, "Go Bombers!");
   }
	m_cstrSecSignal = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // primary alpha
   ///////////////////////////////////////////////////////////////////
   sprintf(pszTemp, "%.3f", m_mctdCurrentState.dAlpha);
	m_cstrPriAlpha = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // secondary alpha
   ///////////////////////////////////////////////////////////////////
   sprintf(pszTemp, "%.3f", m_mctdCurrentState.dSecondaryAlpha);
	m_cstrSecAlpha = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // primary scale factor and units
   ///////////////////////////////////////////////////////////////////
   switch( m_mctdCurrentState.uScaleFactorUnits )
   {
      case MCTG_UNITS_VOLTS_PER_VOLT:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/V", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MILLIVOLT:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/mV", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MICROVOLT:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/µV", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_AMP:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/A", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MILLIAMP:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/mA", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MICROAMP:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/µA", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_NANOAMP:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/nA", m_mctdCurrentState.dScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_PICOAMP:
      {
         m_cstrPriScaleFactor.Format( "%0.2f V/pA", m_mctdCurrentState.dScaleFactor );
         break;
      }
      default:
      {
         // invalid units identifier
         ASSERT( FALSE );
         break;
      }
   }
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // secondary scale factor and units
   ///////////////////////////////////////////////////////////////////
   switch( m_mctdCurrentState.uRawScaleFactorUnits )
   {
      case MCTG_UNITS_VOLTS_PER_VOLT:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/V", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MILLIVOLT:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/mV", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MICROVOLT:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/µV", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_AMP:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/A", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MILLIAMP:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/mA", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_MICROAMP:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/µA", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_NANOAMP:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/nA", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      case MCTG_UNITS_VOLTS_PER_PICOAMP:
      {
         m_cstrSecScaleFactor.Format( "%0.2f V/pA", m_mctdCurrentState.dRawScaleFactor );
         break;
      }
      default:
      {
         // invalid units identifier
         ASSERT( FALSE );
         break;
      }
   }
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // primary LPF cutoff
   ///////////////////////////////////////////////////////////////////
   if(m_mctdCurrentState.dLPFCutoff >= MCTG_LPF_BYPASS )
   {
	   sprintf(pszTemp, "%.0f Hz", m_mctdCurrentState.dLPFCutoff);
	   strcat(pszTemp, " ( Bypass )");
   }
   else
   {
	   sprintf(pszTemp, "%.0f Hz", m_mctdCurrentState.dLPFCutoff);
   }
	m_cstrPriLPFCutoff = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // secocndary LPF cutoff
   ///////////////////////////////////////////////////////////////////
   if(m_mctdCurrentState.dSecondaryLPFCutoff >= MCTG_LPF_BYPASS )
   {
	   sprintf(pszTemp, "%.0f Hz", m_mctdCurrentState.dSecondaryLPFCutoff);
	   strcat(pszTemp, " ( Bypass )");
   }
   else
   {
	   sprintf(pszTemp, "%.0f Hz", m_mctdCurrentState.dSecondaryLPFCutoff);
   }
	m_cstrSecLPFCutoff = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // membrane capacitance
   ///////////////////////////////////////////////////////////////////
   if(m_mctdCurrentState.dMembraneCap == MCTG_NOMEMBRANECAP)
   {
      sprintf(pszTemp, "N/A");
   }
   else
   {
      sprintf(pszTemp, "%.3f pF", m_mctdCurrentState.dMembraneCap * 1.0e12);
   }
	m_cstrMembraneCap = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // external command sensitivity
   ///////////////////////////////////////////////////////////////////
   switch( m_mctdCurrentState.uOperatingMode )
   {
      case MCTG_MODE_VCLAMP:
      {
         if( m_mctdCurrentState.dExtCmdSens <= 0.0 )
         {
            sprintf(pszTemp, "OFF");
         }
         else
         {
            sprintf(pszTemp, "%.0f mV/V", m_mctdCurrentState.dExtCmdSens * 1.0e3);
         }
         break;
      }
      case MCTG_MODE_ICLAMP:
      case MCTG_MODE_ICLAMPZERO:
      {
         if( m_mctdCurrentState.dExtCmdSens <= 0.0   )
         {
            sprintf(pszTemp, "OFF");
         }
         else if( m_mctdCurrentState.dExtCmdSens < 1.0e-9 )
         {
            sprintf(pszTemp, "%.0f pA/V", m_mctdCurrentState.dExtCmdSens * 1.0e12);
         }
         else
         {
            sprintf(pszTemp, "%.0f nA/V", m_mctdCurrentState.dExtCmdSens * 1.0e9);
         }
         break;
      }
      default:
      {
         sprintf(pszTemp, "Invalid Operating Mode!");
         break;
      }
   }
	m_cstrExtCmdSens = pszTemp;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // application version number
   ///////////////////////////////////////////////////////////////////
   m_cstrAppVer = m_mctdCurrentState.szAppVersion;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // firmware version number
   ///////////////////////////////////////////////////////////////////
   m_cstrFirmwareVer = m_mctdCurrentState.szFirmwareVersion;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // DSP version number
   ///////////////////////////////////////////////////////////////////
   m_cstrDSPVer = m_mctdCurrentState.szDSPVersion;
   ///////////////////////////////////////////////////////////////////

   ///////////////////////////////////////////////////////////////////
   // Serial number number
   ///////////////////////////////////////////////////////////////////
   m_cstrSN = m_mctdCurrentState.szSerialNumber;
   ///////////////////////////////////////////////////////////////////

   UpdateData(FALSE);
}

//==============================================================================================
// FUNCTION: ClearDisplay
// PURPOSE:  
//
void CMCTeleClientDlg::ClearDisplay()
{
   // enable / disable connection parameter widgets
   UpdateEnabling();

   // clear the telegraph parameter display fields
	m_cstrMode           = "";
	m_cstrPriSignal      = "";
   m_cstrPriAlpha       = "";
	m_cstrPriScaleFactor = "";
	m_cstrPriLPFCutoff   = "";
	m_cstrSecSignal      = "";
   m_cstrSecAlpha       = "";
	m_cstrSecScaleFactor = "";
	m_cstrSecLPFCutoff   = "";
	m_cstrMembraneCap    = "";
	m_cstrExtCmdSens     = "";
   m_cstrAppVer         = "";
	m_cstrDSPVer         = "";
	m_cstrFirmwareVer    = "";
	m_cstrSN             = "";

   UpdateData(FALSE);
}

//==============================================================================================
// FUNCTION: UpdateEnabling
// PURPOSE:  
//
void CMCTeleClientDlg::UpdateEnabling()
{
   // enable / disable connection parameter combo boxes
   if( m_cbxSerialNum.GetItemData(m_cbxSerialNum.GetCurSel()) == s_cdwNoDevice) // no device
      m_cbxSerialNum.EnableWindow(FALSE);
   else
      m_cbxSerialNum.EnableWindow(!m_bIsConnected);

   m_cbxChannel.EnableWindow(!m_bIsConnected);

   // set connect / disconnect button text appropriately
   if(m_bIsConnected)
   {
      m_btnConnect.SetWindowText("Disconnect");
   }
   else
   {
      m_btnConnect.SetWindowText("Connect");
   }
}

//==============================================================================================
// FUNCTION: OnConnect
// PURPOSE:  
//
void CMCTeleClientDlg::OnConnect() 
{
   ASSERT(m_hWnd != NULL);

   // pack up serial number and channel data 
   UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
   UINT uChannelID = m_mctdCurrentState.uChannelID;
   LPARAM lparamSignalIDs = MCTG_Pack700BSignalIDs( uSerialNum,
                                                    uChannelID  );
   if( m_bIsConnected )
   {
      // we are already connected
      // this is a request to disconnect

      // post telegraph close message
      TRACE1("client(0x%08X): ",  m_hWnd);
      TRACE ("post close message\n");
      if( !::PostMessage( HWND_BROADCAST,
                          s_uMCTGCloseMessage,
                          (WPARAM) m_hWnd,
                          lparamSignalIDs      ) )
      {
         ASSERT(FALSE);
         AfxMessageBox("Failed to close connection!");
      }

      m_bIsConnected = FALSE;
      m_btnScan.EnableWindow( TRUE );
      ClearDisplay();
   }
   else
   {
      // we are not connected
      // this is a request to connect
      m_bIsConnecting = TRUE;

      // post telegraph open message
      TRACE1("client(0x%08X): ",  m_hWnd);
      TRACE ("post open message\n");
      if( !::PostMessage( HWND_BROADCAST,
                          s_uMCTGOpenMessage,
                          (WPARAM) m_hWnd,
                          lparamSignalIDs     ) )
      {
         ASSERT(FALSE);
         m_bIsConnecting = FALSE;
         m_btnScan.EnableWindow( TRUE );
         AfxMessageBox("Failed to open connection!");
      }

      // set a timer event for the connection timeout
      UINT uRetVal = SetTimer( s_cuConnectionTimerEventID,
                               s_cuConnectionTimerInterval,
                              (TIMERPROC) NULL              );	
      ASSERT( uRetVal != 0 );
      m_btnScan.EnableWindow( FALSE );
      
      // the window procedure will handle the rest
   }

}

//==============================================================================================
// FUNCTION: OnRequest
// PURPOSE:  
//
void CMCTeleClientDlg::OnRequest() 
{
   ASSERT(m_hWnd != NULL);

   // pack up serial number and channel data 
   UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
   UINT uChannelID = m_mctdCurrentState.uChannelID;
   LPARAM lparamSignalIDs = MCTG_Pack700BSignalIDs( uSerialNum,
                                                    uChannelID  );
   ClearDisplay();

   m_bRequestPending = TRUE;

   // post telegraph packet request message
   TRACE1("client(0x%08X): ",  m_hWnd);
   TRACE ("post packet request message\n");
   if( !::PostMessage( HWND_BROADCAST,
                       s_uMCTGRequestMessage,
                       (WPARAM) m_hWnd,
                       lparamSignalIDs        ) )
   {
      ASSERT(FALSE);
      AfxMessageBox("Failed to request telegraph packet!");
   }

   // set a timer event for the request timeout
   UINT uRetVal = SetTimer( s_cuRequestTimerEventID,
                            s_cuRequestTimerInterval,
                           (TIMERPROC) NULL              );	
   ASSERT( uRetVal != 0 );
   
   // the window procedure will handle the rest
}

//==============================================================================================
// FUNCTION: OnSelChangeChannel
// PURPOSE:  
//
void CMCTeleClientDlg::OnSelChangeChannel() 
{
   int nRetVal = m_cbxChannel.GetCurSel();
   ASSERT(nRetVal != CB_ERR);

   // +1 ( channel IDs start with 1 )
   m_mctdCurrentState.uChannelID = nRetVal + 1;
}

//==============================================================================================
// FUNCTION: OnSelChangeSerialNum
// PURPOSE:  
//
void CMCTeleClientDlg::OnSelChangeSerialNum() 
{
   // check that combo has data
   if( m_cbxSerialNum.GetItemData( m_cbxSerialNum.GetCurSel() ) == s_cdwNoDevice )
      return;

   // get the currently selected device serial number
   int nCurSel = m_cbxSerialNum.GetCurSel( );
   m_cbxSerialNum.GetLBText( nCurSel, m_mctdCurrentState.szSerialNumber );
   ASSERT(nCurSel != CB_ERR);
}

//==============================================================================================
// FUNCTION: OnClose
// PURPOSE:  
//
void CMCTeleClientDlg::OnClose() 
{
   if(m_bIsConnected)
   {
      ASSERT(m_hWnd != NULL);

      // pack up serial number and channel data 
      UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
      UINT uChannelID = m_mctdCurrentState.uChannelID;
      LPARAM lparamSignalIDs = MCTG_Pack700BSignalIDs( uSerialNum,
                                                       uChannelID  );

      // post telegraph close message
      TRACE1("client(0x%08X): ",  m_hWnd);
      TRACE ("post close message\n");
      if( !::PostMessage( HWND_BROADCAST,
                          s_uMCTGCloseMessage,
                          (WPARAM) m_hWnd,
                          lparamSignalIDs      ) )
      {
         ASSERT(FALSE);
         AfxMessageBox("Failed to close connection!");
      }

      m_btnScan.EnableWindow( TRUE );
      m_bIsConnected = FALSE;
   }
	
	CDialog::OnClose();
}

//==============================================================================================
// FUNCTION: OnBroadcast
// PURPOSE:  
//
void CMCTeleClientDlg::OnBroadcast() 
{
   ASSERT(m_hWnd != NULL);

   m_lbxDeviceList.ResetContent();

   if( !::PostMessage( HWND_BROADCAST,
                       s_uMCTGBroadcastMessage,
                       (WPARAM) m_hWnd,
                       (LPARAM) 0            ) )
   {
      ASSERT(FALSE);
      AfxMessageBox("Failed to broadcast to telegraph servers!");
   }
}

//***********************************************************************************************
// METHOD:     OnScan
// PURPOSE:    Request a packet from all servers out there
//             to populate serial number combo
//
void CMCTeleClientDlg::OnScan()
{
   ASSERT(m_hWnd != NULL);

   m_bScanning = TRUE;

   // post a multiclamp 700B scan message
   if( !::PostMessage( HWND_BROADCAST,
                       s_uMCTGBroadcastMessage,
                       (WPARAM) m_hWnd,
                       (LPARAM) 0          ) )
   {
      TRACE("Failed to scan servers!");
      return;
   }

   // disable scan button and hold down.
   m_cbxSerialNum.EnableWindow( FALSE );
   m_btnScan.EnableWindow( FALSE );
   m_btnScan.SetState( TRUE );

   // make sure the serial number list is empty before populating
   m_vSerialNum.clear();

   // scan c_uNumMultiClampScans times to make sure we get a response
   for( int i=1; i<=s_cuNumMultiClampScans; i++ )
   {
      DWORD dwStartTime = GetTickCount();
      do
         MessagePump();
      while( s_cuScanMultiClampTimeOutMS > (GetTickCount() - dwStartTime) );
   }

   // fill the serial number combo using the accumulated serial number list.
   m_cbxSerialNum.ResetContent();
   SerialNumList::iterator iter;
   for( iter = m_vSerialNum.begin(); iter != m_vSerialNum.end(); iter++ )
   {
      // get a pointer to each string in the list
      CString * pSN = iter;
      char szSerialNum[16] = {0};
      strncpy( szSerialNum, (char *)pSN->GetBuffer(pSN->GetLength()), sizeof(szSerialNum) );
      
      // skip duplicates
      int nIndex = m_cbxSerialNum.FindStringExact( 0, szSerialNum );
      if( nIndex != CB_ERR )
         continue;

      // add the string and numerical conversion (as data) to the combo
      nIndex = m_cbxSerialNum.AddString( szSerialNum );
      if( nIndex != CB_ERRSPACE )
         m_cbxSerialNum.SetItemData( nIndex, atoi(szSerialNum) );
      else
         m_cbxSerialNum.ResetContent();
   }
   
   // update serial number combo
   m_cbxSerialNum.EnableWindow( TRUE );
   m_cbxSerialNum.SetCurSel( 0 );
   m_btnScan.EnableWindow( TRUE );
   m_btnScan.SetState( FALSE );

   // tag combo with "No Device" and set data to magic number if no clients found
   if( m_cbxSerialNum.GetCount() == 0 )
   {
      m_cbxSerialNum.AddString( s_cszNoDevice );
      m_cbxSerialNum.SetItemData( m_cbxSerialNum.GetCurSel(), s_cdwNoDevice );
      m_cbxSerialNum.EnableWindow( FALSE );
      m_cbxSerialNum.SetCurSel( 0 );

      // warn that no servers were found
      CString cstrMessage;
      cstrMessage = "No servers found.\n\n";
      cstrMessage += "Start MultiClamp 700B Commander or MCTeleServer and rescan.\n";
      int nRetVal = AfxMessageBox( cstrMessage,
                                   MB_OK |
                                   MB_ICONINFORMATION, 
                                   (UINT) -1           );
   }

   OnSelChangeSerialNum();
   m_bScanning = FALSE;
}

//==============================================================================================
// METHOD:     AddSerialNum
// PURPOSE:    Add a client serial number to a list.
//             Used for populating a combo box of available clients
//
void CMCTeleClientDlg::AddSerialNum( UINT uSerialNum )
{
   // format serial number
   char szSerialNum[16] = {0};
   sprintf(szSerialNum, "%.8d", uSerialNum);

   // push onto CString vector
   if( m_vSerialNum.size() < MCTG_MAX_SERVERS )
      m_vSerialNum.push_back( szSerialNum );
}

//==============================================================================================
// FUNCTION: OnSelChangeDeviceList
// PURPOSE:  
//
void CMCTeleClientDlg::OnSelChangeDeviceList() 
{
   ASSERT(m_hWnd != NULL);

   char szItem[32] = {0};
   char szSerialNum[16] = {0};
   int nSel = m_lbxDeviceList.GetCurSel();
   int nRetVal = m_lbxDeviceList.GetText( nSel, szItem);
   ASSERT(nRetVal != CB_ERR);

   int nChannelID = -1;
   nRetVal = sscanf(szItem, "SN %s , Ch %d", szSerialNum, &nChannelID);
   ASSERT( nChannelID>=0 && nRetVal==2 );

   // check that combo has data
   if( m_cbxSerialNum.GetItemData( m_cbxSerialNum.GetCurSel() ) == s_cdwNoDevice )
      return;

   // search combo data and set 
   nRetVal = m_cbxSerialNum.FindString(0, szSerialNum);
   nRetVal = m_cbxSerialNum.SetCurSel(nRetVal);
   m_cbxSerialNum.GetLBText( nRetVal, m_mctdCurrentState.szSerialNumber );
   ASSERT(nRetVal != CB_ERR);
   
   // assumes that combo contents and data are in sync
   // -1 ( channel IDs start with 1 )
   nRetVal = m_cbxChannel.SetCurSel(nChannelID - 1);
   m_mctdCurrentState.uChannelID = (UINT) nChannelID;
   ASSERT(nRetVal != CB_ERR);
}


//==============================================================================================
// FUNCTION: OnBroadcastResponse
// PURPOSE:  
//
void CMCTeleClientDlg::OnBroadcastResponse(UINT uSerialNum, UINT uChannelID) 
{
   ASSERT(m_hWnd != NULL);

   char szItem[32] = {0};
   sprintf(szItem, "SN %.8d , Ch %1d", uSerialNum, uChannelID);
   int nRv = m_lbxDeviceList.AddString(szItem);
   ASSERT( nRv != LB_ERRSPACE && nRv != LB_ERR );
}
