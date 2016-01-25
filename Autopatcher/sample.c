/*
 * A sample C-program for Sensapex micro manipulator control library
 *
 * Copyright (c) 2012, Sensapex Oy
 * All rights reserved.
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

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/timeb.h>
#include "umanipulatorctl.h"

#define VERSION_STR   "v0.212"
#define COPYRIGHT "Copyright (c) Sensapex. All rights reserved"

#ifndef PORT
#ifdef WIN32
#include <windows.h>
#define PORT "com3"
#define msleep(t) Sleep((t))
#else
#define PORT "/dev/ttyUSB0"
#include <unistd.h>
#define msleep(t) usleep((t)*1000)
#endif
#endif

#define DEV     '1'
#define UNDEF  (-1)
#define TIMEOUT 200
#define UPDATE  200

typedef struct params_s
{
	int x, y, z, X, Y, Z;
	int verbose, timeout, update, loop;
	char *port, dev;
} params_t;

void usage(char **argv)
{
	fprintf(stderr,"usage: %s [generic opts] [pos opts]|[read/write opts] \n",argv[0]);
	fprintf(stderr,"Generic options, serial port (e.g. /dev/ttyUSB1 or com2)\n");
	fprintf(stderr,"-p\tport   \n");
	fprintf(stderr,"-d\tdev \n");
	fprintf(stderr,"-e\tverbose\n");
	fprintf(stderr,"Position change\n");
	fprintf(stderr,"-x\trelative target \n");
	fprintf(stderr,"-y\trelative target \n");
	fprintf(stderr,"-z\trelative target \n");
	fprintf(stderr,"-X\tabs target \n");
	fprintf(stderr,"-Y\tabs target \n");
	fprintf(stderr,"-Z\tabs target \n");
	fprintf(stderr,"-n\tcount\tloop current and target positions \n");
  exit(1);
}

// Exits via usage() if an error occurs
void parse_args(int argc, char *argv[], params_t *params)
  {
  int i, v;
  char c;
  memset(params,0,sizeof(params_t));
  params->X = UNDEF;
  params->Y = UNDEF;
  params->Z = UNDEF;
  params->dev = DEV;
  params->port = PORT;
  params->timeout = TIMEOUT;
  params->update = UPDATE;

  for(i = 1; i < argc; i++)
	{
	if(argv[i][0] == '-')
	  {
	  switch(argv[i][1])
		{
		case 'h': usage(argv);
		case 'v':
			params->verbose = 1;
			break;
		case '1':
			params->verbose = 0;
			break;
		case 'n':
			if(i < argc-1 && (sscanf(argv[++i],"0x%x",&v) == 1 ||
					sscanf(argv[i],"%d",&v) == 1) && v > 0)
			params->loop = v;
		  else
			usage(argv);
		  break;
		case 't':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1 && v > 0)
			params->timeout = v;
		  else
			usage(argv);
		  break;
		case 'u':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1 && v > 0)
			params->update = v;
		  else
			usage(argv);
		  break;
		case 'x':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1)
			params->x = v;
		  else
			usage(argv);
		  break;
		case 'y':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1)
			params->y = v;
		  else
			usage(argv);
		  break;
		case 'z':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1)
			params->z = v;
		  else
			usage(argv);
		  break;
		case 'X':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1 && v >= 0)
			params->X = v;
		  else
			usage(argv);
		  break;
		case 'Y':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1 && v >= 0)
			params->Y = v;
		  else
			usage(argv);
		  break;
		case 'Z':
		  if(i < argc-1 && sscanf(argv[++i],"%d",&v) == 1 && v >= 0)
			params->Z = v;
		  else
			usage(argv);
		  break;
		case 'd':
			if(i < argc-1 && sscanf(argv[++i],"%c",&c) == 1 && c > '0' && c < 'F')
			  params->dev = c;
			else
			  usage(argv);
			break;
		case 'p':
			if(i < argc-1 && argv[i+1][0] != '-')
				params->port = argv[++i];
			else
				usage(argv);
			break;
		default:
			usage(argv);
			break;
		}
	  }
	else
	  usage(argv);
	}
}

int main(int argc, char *argv[])
{
	umanipulatorctl_state_t *handle = NULL;
	int ret, status, stats_target, stats_home, loop = 0;
	int target_x = 0, target_y = 0, target_z = 0;
	int home_x = 0, home_y = 0, home_z = 0;
	unsigned char stats_axis = 0;
	params_t params;

	parse_args(argc, argv, &params);

	if((handle = umanipulatorctl_open(params.port, params.timeout)) == NULL)
	{
		// Feeding NULL handle is intentional, it obtains the
		// last OS error which prevented the port to be opened
		fprintf(stderr, "Can not open %s - %s\n", params.port,
				umanipulatorctl_last_errorstr(handle));
		exit(1);
	}

	if((ret = umanipulatorctl_select_dev(handle, params.dev)) < 0)
	{
		fprintf(stderr, "Select_dev failed - %s\n",
				umanipulatorctl_last_errorstr(handle));
		umanipulatorctl_close(handle);
		exit(2);
	}

	/*
	 * These functions providing the position as return value
	 * might be convenient for labview usage and for C code
	 * umanipulatorctl_get_position
	 */

	if((home_x = umanipulatorctl_x_position(handle)) < 0)
	{
		fprintf(stderr, "Get x position failed - %s\n",
				umanipulatorctl_last_errorstr(handle));
		home_x = 0;
	}
	if((home_y = umanipulatorctl_y_position(handle)) < 0)
	{
		fprintf(stderr, "Get y position failed - %s\n",
				umanipulatorctl_last_errorstr(handle));
		home_y = 0;
	}
	if((home_z = umanipulatorctl_z_position(handle)) < 0)
	{
		fprintf(stderr, "Get z position failed - %s\n",
				umanipulatorctl_last_errorstr(handle));
		home_z = 0;
	}

	/*
	 * position may be small negative presented as unsigned value near 0xffff
	 * this is likely the most efficent way to handle them,
	 * works when short int is 16 bits
	 */
	target_x = home_x = (signed short)home_x;
	target_y = home_y = (signed short)home_y;
	target_z = home_z = (signed short)home_z;

	printf("Current position: %d %d %d\n", home_x, home_y, home_z);

	if(params.x)
	{
		stats_target = target_x = home_x + params.x;
		stats_axis = 'x';
		stats_home = home_x;
	}
	if(params.y)
	{
		stats_target = target_y = home_y + params.y;
		stats_axis = 'y';
		stats_home = home_y;
	}
	if(params.z)
	{
		stats_target = target_z = home_z + params.z;
		stats_axis = 'z';
		stats_home = home_z;
	}
	if(params.X != UNDEF)
	{
		stats_home = home_x;
		stats_target = target_x = params.X;
		stats_axis = 'x';
	}
	if(params.Y != UNDEF)
	{
		stats_home = home_y;
		stats_target = target_y = params.Y;
		stats_axis = 'y';
	}
	if(params.Z != UNDEF)
	{
		stats_home = home_z;
		stats_target = target_z = params.Z;
		stats_axis = 'z';
	}

	do
	{
		int x, y, z, stats_pos;
		if(loop&1)
		{
			x = home_x, y = home_y, z = home_z;
			stats_pos = stats_home;
		}
		else
		{
			x = target_x, y = target_y, z = target_z;
			stats_pos = stats_target;
		}
		if(params.loop)
			printf("Target position: %d %d %d (%d/%d)\n", x, y, z, loop+1, params.loop);
		else
			printf("Target position: %d %d %d\n", x, y, z);

		if((ret = umanipulatorctl_store_mem_position(handle, x, y, z)) < 0)
		{
			fprintf(stderr, "Store_mem_position failed - %s\n",
				umanipulatorctl_last_errorstr(handle));
			continue;
		}
		else if((ret = umanipulatorctl_goto_mem_position(handle)) < 0)
		{
			fprintf(stderr, "Goto_mem_position failed - %s\n",
				umanipulatorctl_last_errorstr(handle));
			continue;
		}
		if(!params.loop && !params.verbose)
			break;
		msleep(params.update);
		status = (int)umanipulatorctl_status(handle);
		while(umanipulatorctl_is_busy_status(status))
		{
			if(params.verbose)
			{
				if(status < 0)
					fprintf(stderr, "Status read failed - %s\n", umanipulatorctl_last_errorstr(handle));
				else if(umanipulatorctl_get_position_ext(handle, params.dev, params.update, &x, &y, &z) < 0)
					fprintf(stderr, "Position read failed - %s\n", umanipulatorctl_last_errorstr(handle));
				else
					printf("%d %d %d status %02X\n", x, y, z, (int)umanipulatorctl_status(handle));
			}
			msleep(params.update);
			status = umanipulatorctl_status(handle);
		}
	} while(++loop < params.loop);

	umanipulatorctl_close(handle);
	exit(ret>=0?0:ret);
}
