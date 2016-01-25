/*
 * A command interface for Sensapex micromanipulator
 *
 * Copyright (c) 2012, Sensapex Oy
 * All rights reserved.
 *
 * This module is proprietary.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGE.
 *
 */

#ifndef UMANIPULATORCTL_H
#define UMANIPULATORCTL_H

#if defined(_WIN32) || defined(_WIN64) || defined(WIN32) || defined(WIN64)
#if defined(EXTSERIALPORT_LIBRARY)
#  define UMANIPULATORCTLSHARED_EXPORT __declspec(dllimport)
#else
#  define UMANIPULATORCTLSHARED_EXPORT __declspec(dllexport)
#endif
#else
#  define UMANIPULATORCTLSHARED_EXPORT
#endif

/*
 * The pre compiler comdition below is utilized by C++ compilers and is
 * ignored by pure C types
 */

#ifdef __cplusplus
extern "C" {
#endif

typedef enum umanipulatorctl_error_e
{
	UMANIPULATORCTL_NO_ERROR  = 0,
	UMANIPULATORCTL_OS_ERROR  = -1,
	UMANIPULATORCTL_NOT_OPEN  = -2,
	UMANIPULATORCTL_TIMEOUT   = -3,
	UMANIPULATORCTL_INVALID_ARG  = -4,
	UMANIPULATORCTL_INVALID_DEV  = -5,
	UMANIPULATORCTL_INVALID_RESP = -6,
	UMANIPULATORCTL_INVALID_CRC  = -7,
} umanipulatorctl_error_t;

typedef enum umanipulatorctl_status_e
{
	UMANIPULATORCTL_STATUS_READ_ERROR = -1,
	UMANIPULATORCTL_STATUS_X_MOVING   = 0x01,
	UMANIPULATORCTL_STATUS_Y_MOVING   = 0x02,
	UMANIPULATORCTL_STATUS_Z_MOVING   = 0x04,
	UMANIPULATORCTL_STATUS_X_BUSY     = 0x08,
	UMANIPULATORCTL_STATUS_Y_BUSY     = 0x10,
	UMANIPULATORCTL_STATUS_Z_BUSY     = 0x20,
	UMANIPULATORCTL_STATUS_VIRTUAL_Z  = 0x40,
	UMANIPULATORCTL_STATUS_JAMMED     = 0x80
} umanipulatorctl_status_t;

#define UMANIPULATORCTL_MAX_MANIPULATORS 15
#define UMANIPULATORCTL_DEF_REFRESH_TIME 2500
#define UMANIPULATORCTL_MAX_POSITION     20400

typedef struct umanipulatorctl_positions_s
{
	unsigned long x, x_last_updated;
	unsigned long y, y_last_updated;
	unsigned long z, z_last_updated;
} umanipulatorctl_positions_t;

typedef struct umanipulatorctl_state_s
{
	struct extserial_port_state_s *port;
	unsigned char last_device_sent;
	unsigned char last_device_received;
	unsigned char last_device_position_read_received;
	unsigned long last_received_time;
	unsigned long refresh_time_limit;
	umanipulatorctl_positions_t last_positions[UMANIPULATORCTL_MAX_MANIPULATORS];
	umanipulatorctl_positions_t target_positions[UMANIPULATORCTL_MAX_MANIPULATORS];
	int last_error;
	char errorstr_buffer[80];
} umanipulatorctl_state_t;

/*
 * For init, NULL return value means an error, obtain reason from errno
 */
UMANIPULATORCTLSHARED_EXPORT umanipulatorctl_state_t *umanipulatorctl_open(const char *port,
																		   const unsigned int timeout);
/*
 * Close the port (if open) and free the state structure allocated in open
 */
UMANIPULATORCTLSHARED_EXPORT void umanipulatorctl_close(umanipulatorctl_state_t *hndl);

/*
 * For all other functions, a negative values means error, got the possible error number
 * or description using some of these, often the last one is enough
 */
UMANIPULATORCTLSHARED_EXPORT int  umanipulatorctl_last_os_error(const umanipulatorctl_state_t *hndl);
UMANIPULATORCTLSHARED_EXPORT umanipulatorctl_error_t umanipulatorctl_last_error(const umanipulatorctl_state_t *hndl);
UMANIPULATORCTLSHARED_EXPORT const char *umanipulatorctl_errorstr(int ret_code);

UMANIPULATORCTLSHARED_EXPORT const char *umanipulatorctl_last_errorstr(umanipulatorctl_state_t *hndl);

/*
 * The simplified interface stores both the device and the refresh time into the state
 * sturcture and use those for all requests
 */
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_select_dev(umanipulatorctl_state_t *hndl,
															 const unsigned char dev);
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_set_refresh_time_limit(umanipulatorctl_state_t *hndl,
															 const unsigned int value);

/*
 * Read status, see umanipulatorctl_status_t for bit definitions
 */

UMANIPULATORCTLSHARED_EXPORT umanipulatorctl_status_t umanipulatorctl_status(umanipulatorctl_state_t *hndl);

/*
 * Status is a bit map and not all bits mean the manipulator being busy.
 * Detect busy state using these functions
 */

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_is_busy(umanipulatorctl_state_t *hndl);
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_is_busy_status(umanipulatorctl_status_t status);

/*
 * Obtain position, uses the cache value if found and refreshed inside the time limit
 */
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_x_position(umanipulatorctl_state_t *hndl);
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_y_position(umanipulatorctl_state_t *hndl);
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_z_position(umanipulatorctl_state_t *hndl);
/*
 * an alternate method using pointers where the values are stored
 * function return value counts number of stored values (x, y, z may be NULL)
 */
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_get_position(umanipulatorctl_state_t *hndl,
														   int *x, int *y, int *z);
/*
 * Store position into memory location, either the current one
 */
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_store_mem_current_position(umanipulatorctl_state_t *hndl);
/*
 * Or by giving the position values
 */
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_store_mem_position(umanipulatorctl_state_t *hndl,
																	const int x, const int y, const int z);
/*
 * Goto to the stored position
 */
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_goto_mem_position(umanipulatorctl_state_t *hndl);

/*
 * Retrieve the stored position, this is local copy stored by last store_mem_position,
 * not read from manipulator and thus not what was stored by store_mem_current_position
 */

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_get_mem_position(umanipulatorctl_state_t *hndl,
														   int *x, int *y, int *z);
/*
 * Lower layer API carrying the device id.
 * These functions are used internally by the above API functions.
 * They may be used also if the application needs to control multiple manipulators
 * at the ame time
 */

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_ping(umanipulatorctl_state_t *hndl,
														   const unsigned char dev);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_is_busy_ext(umanipulatorctl_state_t *hndl,
															const unsigned char dev);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_status_ext(umanipulatorctl_state_t *hndl,
															const unsigned char dev);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_store_mem_current_position_ext(umanipulatorctl_state_t *hndl,
																				const unsigned char dev);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_store_mem_position_ext(umanipulatorctl_state_t *hndl,
																		const unsigned char dev,
																	const int x, const int y, const int z);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_goto_mem_position_ext(umanipulatorctl_state_t *hndl,
																	   const unsigned char dev);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_get_mem_position_ext(umanipulatorctl_state_t *hndl,
																	  const unsigned char dev,
																	  int *x, int *y, int *z);
/*
 * This method can be called to read the serial port and thus update the positions
 * into the cache from the responses to the Control Unit
 */

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_recv(umanipulatorctl_state_t *hndl);

/*
 * An advanced API allowing to control the position value timings
 * zero time_limit reads cached positions without sending any messages
 * to the manipulator, intented to be used when the Control Unit is not in PC mode.
 *
 * If elapsed is not NULL, the referred variable will be populated milli seconds
 * since the position was updated
 */

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_get_position_ext(umanipulatorctl_state_t *hndl,
														   const unsigned char dev,
														   const unsigned int time_limit,
														   int *x, int *y, int *z);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_x_position_ext(umanipulatorctl_state_t *hndl,
															 const unsigned char dev,
															 const unsigned int time_limit,
															 unsigned int *elapsed);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_y_position_ext(umanipulatorctl_state_t *hndl,
															 const unsigned char dev,
															 const unsigned time_limit,
															 unsigned int *elapsed);

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_z_position_ext(umanipulatorctl_state_t *hndl,
															 const unsigned char dev,
															 const unsigned int time_limit,
															 unsigned int *elapsed);
/*
 * Internal functions used for development purpose, They require
 * the cmd and address values to be known.
 */

UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_cmd(umanipulatorctl_state_t *hndl,
														   const unsigned char dev,
														   const unsigned char cmd);
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_read(umanipulatorctl_state_t *hndl,
														   const unsigned char dev,
														   const unsigned char addr);
UMANIPULATORCTLSHARED_EXPORT int umanipulatorctl_write(umanipulatorctl_state_t *hndl,
														   const unsigned char dev,
														   const unsigned char addr,
														   const unsigned short val);

#ifdef __cplusplus
} // end of extern "C"

//
// Inline C++ wrapper, also this without any dependency to Qt or std class libraries
//

#define UMANIPULATORCTL_USE_LAST_DEV  0

class UManipulatorCtl
{
public:
	UManipulatorCtl() {  _handle = NULL; }
	virtual ~UManipulatorCtl() { if(_handle) umanipulatorctl_close(_handle); }

	bool open(const char *port, const unsigned int timeout)
	{	return (_handle = umanipulatorctl_open(port, timeout)) != NULL; }

	bool isOpen()
	{ 	return _handle != NULL; }

	void close()
	{	umanipulatorctl_close(_handle); _handle = NULL; }

	bool select(const int dev)
	{	return  umanipulatorctl_select_dev(_handle, getDev(dev)) >= 0; }

	bool ping(const int dev)
	{	return  umanipulatorctl_ping(_handle, getDev(dev)) >= 0; }

	bool cmd(unsigned char cmd, const int dev = UMANIPULATORCTL_USE_LAST_DEV)
	{	return	umanipulatorctl_cmd(_handle, getDev(dev), cmd) >= 0; }

	bool update()
	{	return _handle && umanipulatorctl_recv(_handle) > 0; }

	bool getPositions(int *x, int *y, int *z,
					  const int dev = UMANIPULATORCTL_USE_LAST_DEV,
					  const unsigned int timeLimit = UMANIPULATORCTL_DEF_REFRESH_TIME)
	{	return umanipulatorctl_get_position_ext(_handle, getDev(dev), timeLimit, x, y, z) >= 0;	}

	bool storeMem(const int dev = UMANIPULATORCTL_USE_LAST_DEV)
	{	return umanipulatorctl_store_mem_current_position_ext(_handle, getDev(dev)) >= 0;	}

	bool storeMem(const int x, const int y, const int z,
				  const int dev = UMANIPULATORCTL_USE_LAST_DEV)
	{	return umanipulatorctl_store_mem_position_ext(_handle, getDev(dev), x,y,z) >= 0; }

	bool getMem(int *x, int *y, int *z, const int dev = UMANIPULATORCTL_USE_LAST_DEV)
	{	return umanipulatorctl_get_mem_position_ext(_handle, getDev(dev),x,y,z) >= 0; }

	bool gotoMem(const int dev = UMANIPULATORCTL_USE_LAST_DEV)
	{	return umanipulatorctl_goto_mem_position_ext(_handle, getDev(dev)) >= 0; }

	bool gotoMem(const int x, const int y, const int z,
				 const int dev = UMANIPULATORCTL_USE_LAST_DEV)
	{	return  storeMem(x, y, z, dev) && gotoMem(dev); }

	int lastError()
	{	return umanipulatorctl_last_error(_handle); }

	const char *lastErrorText()
	{ 	return umanipulatorctl_last_errorstr(_handle); }
private:
	unsigned char getDev(const int dev)
	{
		if(dev == UMANIPULATORCTL_USE_LAST_DEV && _handle)
			return _handle->last_device_sent;
		return dev + 0x30;
	}
	umanipulatorctl_state_t *_handle;
};

#endif /* c++ */

#endif /* UMANIPULATORCTL_H */

