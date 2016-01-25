//////////////////////////////////////////////////////////////////////////////////////
//
//    Copyright (c) 2003 Axon Instruments, Inc.
//    All rights reserved.
//
//////////////////////////////////////////////////////////////////////////////////////
// FILE:    MCTeleServerDlg.cpp
// PURPOSE: Implementation of MCTeleServer
//          Main Dialog Class
//

#include "stdafx.h"
#include <math.h>
#include "MCTeleServer.h"
#include "MCTeleServerDlg.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

// alarm code which will set off a compilation error
// if the version of the MultiClamp telgraph API changes
// or if the size of the MC_TELEGRAPH_DATA structure changes
static UINT s_uTestMCTGVersion [ ( MCTG_API_VERSION          ==  13 ) ? 1 : 0 ];
static UINT s_uTestMCTGData    [ ( sizeof(MC_TELEGRAPH_DATA) == 256 ) ? 1 : 0 ];

static UINT s_uMCTGOpenMessage       = 0;
static UINT s_uMCTGCloseMessage      = 0;
static UINT s_uMCTGRequestMessage    = 0;
static UINT s_uMCTGReconnectMessage  = 0;
static UINT s_uMCTGBroadcastMessage  = 0;
static UINT s_uMCTGIdMessage         = 0;

static UINT s_uDummyData             = 0;

/////////////////////////////////////////////////////////////////////////////
// CMCTeleServerDlg dialog

//==============================================================================================
// FUNCTION: CMCTeleServerDlg
// PURPOSE:  Constuctor
//
CMCTeleServerDlg::CMCTeleServerDlg(CWnd* pParent /*=NULL*/)
:  CDialog(CMCTeleServerDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CMCTeleServerDlg)
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);

   // initialize the current telegraph state

   // this bit will zero out the padding in the structure
   MC_TELEGRAPH_DATA* pmctd = &m_mctdCurrentState;
   memset(pmctd, 0, sizeof(MC_TELEGRAPH_DATA));
   
   m_mctdCurrentState.uVersion            = MCTG_API_VERSION;
   m_mctdCurrentState.uStructSize         = sizeof(MC_TELEGRAPH_DATA);
   m_mctdCurrentState.uComPortID          = 1;
   m_mctdCurrentState.uAxoBusID           = 0;
   m_mctdCurrentState.uChannelID          = 1;
   m_mctdCurrentState.uOperatingMode      = MCTG_MODE_VCLAMP;
   m_mctdCurrentState.uScaledOutSignal    = AXMCD_OUT_PRI_VC_GLDR_V_CMD_EXT;
   m_mctdCurrentState.dAlpha              = 0.0;
   m_mctdCurrentState.dScaleFactor        = 0.0;
   m_mctdCurrentState.uScaleFactorUnits   = MCTG_UNITS_VOLTS_PER_VOLT;
   m_mctdCurrentState.dLPFCutoff          = 0.0;
   m_mctdCurrentState.dMembraneCap        = 0.0;
   m_mctdCurrentState.dSecondaryAlpha     = 0.0;
   m_mctdCurrentState.dSecondaryLPFCutoff = 0.0;

   // initialize the client list
   for(UINT uX = 0; uX < MCTG_MAX_CLIENTS; ++ uX)
   {
      m_ClientHwndList[uX] = NULL;
   }

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

}

//==============================================================================================
// FUNCTION: DoDataExchange
// PURPOSE:  
//
void CMCTeleServerDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CMCTeleServerDlg)
   DDX_Control( pDX, IDC_SERIALNUM, m_cbxSerialNumber );
	DDX_Control( pDX, IDC_CHANNEL, m_cbxChannelID );
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CMCTeleServerDlg, CDialog)
	//{{AFX_MSG_MAP(CMCTeleServerDlg)
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_CBN_SELCHANGE(IDC_CHANNEL, OnSelChangeChannelID)
	ON_CBN_SELCHANGE(IDC_SERIALNUM, OnSelChangeSerialNum)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMCTeleServerDlg message handlers

//==============================================================================================
// FUNCTION: OnInitDialog
// PURPOSE:  
//
BOOL CMCTeleServerDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
   UINT uRetVal = 0;

   uRetVal = SetTimer( cuTimerEventID,
                       1000,
                       (TIMERPROC) NULL );	
   ASSERT( uRetVal != 0 );


   // initialize combo box selections
   int nRetVal = 0;

   // init serial number
   nRetVal = m_cbxSerialNumber.SetCurSel(0);
   ASSERT(nRetVal != CB_ERR);
   OnSelChangeSerialNum();

   // -1 ( channel IDs start with 1 )
   nRetVal = m_cbxChannelID.SetCurSel(m_mctdCurrentState.uChannelID - 1);
   ASSERT(nRetVal != CB_ERR);

   // request reconnection from existing clients
   ReconnectRequest();

   // get the file version
   char pszFileVer[128];
   GetFileVersion(pszFileVer, sizeof(pszFileVer));
   
   // create dialog title
   char pszTitle[128];
   sprintf(pszTitle, "MultiClamp Telegraph Server %s", pszFileVer );
   SetWindowText(pszTitle);

	return TRUE;  // return TRUE  unless you set the focus to a control
}

//==============================================================================================
// FUNCTION: GetFileVersion
// PURPOSE:  
//
BOOL CMCTeleServerDlg::GetFileVersion( char * pszFileVer, UINT uSize )
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
void CMCTeleServerDlg::OnPaint() 
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
HCURSOR CMCTeleServerDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

//==============================================================================================
// FUNCTION: WindowProc
// PURPOSE:  
//
LRESULT CMCTeleServerDlg::WindowProc(UINT message, WPARAM wParam, LPARAM lParam) 
{
   // process telegraph open message
   // add the sender's HWND to the client list
   // send a telegraph packet to that HWND
   if( message == s_uMCTGOpenMessage )
   {
      UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
      UINT uChannelID = m_mctdCurrentState.uChannelID;
      if( !MCTG_Match700BSignalIDs( uSerialNum,
                                    uChannelID, 
                                    lParam      ) )

      {
         // this request is for another MultiClamp device / channel
         // ignore it
         return TRUE;
      }

      UINT uX = 0;

      // see if the sender's HWND is already in the client list
      for(uX = 0; uX < MCTG_MAX_CLIENTS; ++ uX)
      {
         if(m_ClientHwndList[uX] == (HWND) wParam)
         {
            // failed to add sender's HWND to client list
            // this HWND is already connected
            TRACE2("server(%s,%d): ",
                   m_mctdCurrentState.szSerialNumber,
                   m_mctdCurrentState.uChannelID );
            TRACE1("open failed for 0x%08X: already open\n", wParam);
            return TRUE;
         }
      }

      // attempt to add the sender's HWND to the client list
      // place it in the first available blank slot
      ASSERT(wParam != NULL);
      BOOL bSuccess = FALSE;
      for(uX = 0; uX < MCTG_MAX_CLIENTS; ++ uX)
      {
         if(m_ClientHwndList[uX] == NULL)
         {
            m_ClientHwndList[uX] = (HWND) wParam;
            bSuccess = TRUE;
            break;
         }
      }

      if( bSuccess )
      {
         // successfully added HWND to client list
         TRACE2("server(%s,%d): ",
                m_mctdCurrentState.szSerialNumber,
                m_mctdCurrentState.uChannelID );
         TRACE1("open connection to 0x%08X\n", wParam);
      }
      else
      {
         // failed to add sender's HWND to client list
         // no free slots available
         TRACE2("server(%s,%d): ",
                m_mctdCurrentState.szSerialNumber,
                m_mctdCurrentState.uChannelID );
         TRACE1("open failed for 0x%08X: no free slots\n", wParam);
         return TRUE;
      }

      if( IsWindow( (HWND) wParam ) )
      {
         // HWND is valid, send telegraph packet
         COPYDATASTRUCT cpds;
         cpds.dwData = (DWORD) s_uMCTGRequestMessage;
         cpds.cbData = sizeof(MC_TELEGRAPH_DATA);
         cpds.lpData = &m_mctdCurrentState;

         ::SendMessage ( (HWND) wParam,
                         WM_COPYDATA ,
                         NULL, 
                         (LPARAM) &cpds );

         return TRUE;
      }
      else
      {
         // invalid HWND, remove from client list
         TRACE2("server(%s,%d): ",
                m_mctdCurrentState.szSerialNumber,
                m_mctdCurrentState.uChannelID );
         TRACE1("invalid HWND, removing 0x%08X\n", m_ClientHwndList[uX]);
         m_ClientHwndList[uX] = NULL;
         return TRUE;
      }
   }

   // process telegraph request message
   // *do not* add the sender's HWND to the client list
   // simply send a telegraph packet to that HWND
   if( message == s_uMCTGRequestMessage )
   {
      UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
      UINT uChannelID = m_mctdCurrentState.uChannelID;
      if( !MCTG_Match700BSignalIDs( uSerialNum,
                                    uChannelID,
                                    lParam      ) )
      {
         // this request is for another MultiClamp device / channel
         // ignore it
         return TRUE;
      }

      ASSERT(wParam != NULL);

      COPYDATASTRUCT cpds;
      cpds.dwData = (DWORD) s_uMCTGRequestMessage;
      cpds.cbData = sizeof(MC_TELEGRAPH_DATA);
      cpds.lpData = &m_mctdCurrentState;

      TRACE2("server(%s,%d): ",
             m_mctdCurrentState.szSerialNumber,
             m_mctdCurrentState.uChannelID );
      TRACE1("service packet request from 0x%08X\n", wParam);

      ::SendMessage ( (HWND) wParam,
                      WM_COPYDATA ,
                      NULL, 
                      (LPARAM) &cpds  ); 

      return TRUE;
   }

   // process timer message
   // send a telegraph packet to all HWNDS
   // in the recipient list
   if( ( message      == WM_TIMER        ) &&
       ( wParam       == cuTimerEventID  )    )
   {
      COPYDATASTRUCT cpds;
      cpds.dwData = (DWORD) s_uMCTGRequestMessage;
      cpds.cbData = sizeof(MC_TELEGRAPH_DATA);
      cpds.lpData = &m_mctdCurrentState;

      const UINT cuNumUnitsIDs = 8;
      m_mctdCurrentState.uOperatingMode       = s_uDummyData % MCTG_MODE_NUMCHOICES;
      m_mctdCurrentState.uScaledOutSignal     = s_uDummyData % AXMCD_OUT_NAMES_NUMCHOICES;
      m_mctdCurrentState.uRawOutSignal        = s_uDummyData % AXMCD_OUT_NAMES_NUMCHOICES;
      m_mctdCurrentState.dAlpha               = 1.0e+00 + (s_uDummyData % 2000);
      m_mctdCurrentState.dSecondaryAlpha      = 1.0e+00 + (s_uDummyData % 100);
      m_mctdCurrentState.dScaleFactor         = 5.0e-02 * pow(10.0, (s_uDummyData % 4) );
      m_mctdCurrentState.uScaleFactorUnits    = s_uDummyData % cuNumUnitsIDs;
      m_mctdCurrentState.dRawScaleFactor      = 5.0e-02 * pow(10.0, (s_uDummyData % 4) );
      m_mctdCurrentState.uRawScaleFactorUnits = s_uDummyData % cuNumUnitsIDs;
      m_mctdCurrentState.dLPFCutoff           = 1.0e+02 * (s_uDummyData %  321);
      m_mctdCurrentState.dSecondaryLPFCutoff  = 2.0e+04 * (s_uDummyData % 2) + 1.0e+04;
      m_mctdCurrentState.dMembraneCap         = 1.0e-14 * (s_uDummyData % 1001);

      // dummy version data
      UINT uMajor  = s_uDummyData % 10;
      UINT uMinor  = s_uDummyData % 4;;
      UINT uBugFix = s_uDummyData % 6;;
      UINT uBuild  = s_uDummyData % 100;
      sprintf( m_mctdCurrentState.szAppVersion, "%1d.%1d.%1d.%2.2d", uMajor, uMinor, uBugFix, uBuild );
      sprintf( m_mctdCurrentState.szFirmwareVersion, "%1d.%1d.%1d.%2.2d", uMajor, uMinor, uBugFix, uBuild );
      sprintf( m_mctdCurrentState.szDSPVersion, "%1d.%1d.%1d.%2.2d", uMajor, uMinor, uBugFix, uBuild );

      switch( m_mctdCurrentState.uOperatingMode )
      {
         case MCTG_MODE_VCLAMP:
         {
            m_mctdCurrentState.dExtCmdSens = 1.0e-3  * (s_uDummyData % 101);
            break;
         }
         case MCTG_MODE_ICLAMP:
         {
            m_mctdCurrentState.dExtCmdSens = 1.0e-9  * (s_uDummyData % 101);
            break;
         }
         case MCTG_MODE_ICLAMPZERO:
         {
            // all command signals disabled for I=0
            m_mctdCurrentState.dExtCmdSens = 0.0;
            break;
         }
         default:
         {
            m_mctdCurrentState.dExtCmdSens = 0.0;
            break;
         }
      }

      // iterate over client list and send telegraph packet
      // to each valid HWND
      for(UINT uX = 0; uX < MCTG_MAX_CLIENTS; ++ uX)
      {
         if( m_ClientHwndList[uX] != NULL )
         {
            if( IsWindow( m_ClientHwndList[uX] ) )
            {
               // HWND is valid, send telegraph packet
               TRACE2("server(%s,%d): ",
                      m_mctdCurrentState.szSerialNumber,
                      m_mctdCurrentState.uChannelID );
               TRACE1("send telegraph packet to 0x%08X\n", m_ClientHwndList[uX]);

               ::SendMessage ( m_ClientHwndList[uX],
                               WM_COPYDATA ,
                               NULL, 
                               (LPARAM) &cpds        );
            }
            else
            {
               // invalid HWND, remove from client list
               TRACE2("server(%s,%d): ",
                      m_mctdCurrentState.szSerialNumber,
                      m_mctdCurrentState.uChannelID );
               TRACE1("invalid HWND, removing 0x%08X\n", m_ClientHwndList[uX]);
               m_ClientHwndList[uX] = NULL;
            }
         }
      }

      ++s_uDummyData;
      return TRUE;
   }


   // process telegraph close message
   // delete the sender's HWND from the recipient list
   if( message == s_uMCTGCloseMessage )
   {
      UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
      UINT uChannelID = m_mctdCurrentState.uChannelID;
      if( !MCTG_Match700BSignalIDs( uSerialNum,
                                    uChannelID,
                                    lParam      ) )
      {
         // this request is for another MultiClamp device / channel
         // ignore it
         return TRUE;
      }

      // remove the sender's HWND from the client list
      ASSERT(wParam != NULL);
      BOOL bSuccess = FALSE;
      for( UINT uX = 0; uX < MCTG_MAX_CLIENTS; ++ uX )
      {
         if( m_ClientHwndList[uX] == (HWND) wParam )
         {
            TRACE2("server(%s,%d): ",
                   m_mctdCurrentState.szSerialNumber,
                   m_mctdCurrentState.uChannelID ); 
            TRACE1("close connection to 0x%08X\n", m_ClientHwndList[uX]);
            m_ClientHwndList[uX] = NULL;
            bSuccess = TRUE;
            break;
         }
      }

      if( !bSuccess )
      {
         // failed to remove sender's HWND from client list
         // matching value not found
         TRACE2("server(%s,%d): ",
                m_mctdCurrentState.szSerialNumber,
                m_mctdCurrentState.uChannelID );
         TRACE1("connection to 0x%08X not found\n", wParam);
         return TRUE;
      }

      return TRUE;
   }

   // process telegraph broadcast message
   // respond to sender with an id message
   if( message == s_uMCTGBroadcastMessage )
   {
      UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
      UINT uChannelID = m_mctdCurrentState.uChannelID;
      LPARAM lparamSignalIDs = MCTG_Pack700BSignalIDs( uSerialNum,
                                                       uChannelID  );

      BOOL bSuccess = ::PostMessage( (HWND) wParam,
                                     s_uMCTGIdMessage,
                                     (WPARAM)m_hWnd,
                                     lparamSignalIDs  );

      if( !bSuccess )
      {
         // failed to post ID message
         TRACE2("server(%s,%d): ",
                m_mctdCurrentState.szSerialNumber,
                m_mctdCurrentState.uChannelID );
         TRACE1("connection to 0x%08X not found\n", wParam);
         return TRUE;
      }

      return TRUE;
   }

	return CDialog::WindowProc(message, wParam, lParam);
}

//==============================================================================================
// FUNCTION: OnSelChangeChannelID
// PURPOSE:  
//
void CMCTeleServerDlg::OnSelChangeChannelID() 
{
   int nRetVal = m_cbxChannelID.GetCurSel();
   ASSERT(nRetVal != CB_ERR);

   // +1 ( channel IDs start with 1 )
   m_mctdCurrentState.uChannelID = nRetVal + 1;

   // request reconnection from existing clients
   ReconnectRequest();
}

//==============================================================================================
// FUNCTION: OnSelChangeSerialNum
// PURPOSE:  
//
void CMCTeleServerDlg::OnSelChangeSerialNum() 
{
   // get the currently selected device serial number
   int nCurSel = m_cbxSerialNumber.GetCurSel( );
   m_cbxSerialNumber.GetLBText( nCurSel, m_mctdCurrentState.szSerialNumber );
   ASSERT(nCurSel != CB_ERR);

   // request reconnection from existing clients
   ReconnectRequest();
}

//==============================================================================================
// FUNCTION: ReconnectRequest
// PURPOSE:  
//
void CMCTeleServerDlg::ReconnectRequest()
{
   // post telegraph reconnect message
   // this will cause any existing clients to
   // resend an open message
   TRACE2("server(%s,%d): ",
          m_mctdCurrentState.szSerialNumber,
          m_mctdCurrentState.uChannelID );
   TRACE ("post reconnect message\n");

   UINT uSerialNum = atoi(m_mctdCurrentState.szSerialNumber);
   UINT uChannelID = m_mctdCurrentState.uChannelID;
   LPARAM lparamSignalIDs = MCTG_Pack700BSignalIDs( uSerialNum,
                                                    uChannelID  );

   if( !::PostMessage( HWND_BROADCAST,
                       s_uMCTGReconnectMessage,
                       NULL,
                       lparamSignalIDs          ) )
   {
      ASSERT(FALSE);
      AfxMessageBox("Failed to broadcast reconnect message!");
   }

}