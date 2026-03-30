#include <iostream>
#include <string>
#include <atomic>
#include <chrono>
#include <cstring>
#include <stdlib.h>
#include <errno.h>
#include <termios.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "ultrasonic_ros/ultrasonic_usb.hpp"

int arduino_fd;

int init_arduino(void)
{
	/* Open USB "file" as Read-Write (O_RDWR)
	 * and do not become process's controlling terminal
	*/
	arduino_fd = open (ARDUINO_PORT, O_RDWR | O_NOCTTY);
	if (arduino_fd < 0)
	{
		return -1;
	}
	
	struct termios tty;
	memset(&tty, 0, sizeof(tty));
	
	if (tcgetattr(arduino_fd, &tty) != 0)
	{
		close(arduino_fd);
		return -2;
	}
	
	cfsetispeed(&tty, B9600);
	cfsetospeed(&tty, B9600);
	
	/* Control modes 
	 *   Character size mask = 8
	 *   Enable receiver
	 *   Ignore modem control lines
	 */
	tty.c_cflag = CS8 | CREAD | CLOCAL;
	
	/* Clearing all of below puts us in "non-canonical" mode,
	 *   or "raw" mode (characters immediately available instead
	 *   of having to wait for a line-ending character)
	 */
	 
	/* Input modes */
	tty.c_iflag = 0;
	
	/* Output modes */
	tty.c_oflag = 0;
	
	/* Local modes */
	tty.c_lflag = 0;
	
	/* Special characters 
	 *   Read minimum PACKETLEN (8) characters
	 *   0.5s timeout
	 */
	tty.c_cc[VMIN] = PACKETLEN;
	tty.c_cc[VTIME] = 5;
	
	/* Apply new configuration immediately */
	if (tcsetattr(arduino_fd, TCSANOW, &tty) != 0)
	{
		close(arduino_fd);
		return -3;
	}
	
	/* Discards data written but not transmitted,
	 *   or data received but not read
	 */
	tcflush(arduino_fd, TCIOFLUSH);
	
	return 0;
}

void get_arduino_data (uint8_t *l, uint8_t *c, uint8_t *r)
{
	char read_buf[PACKETLEN];
	tcflush(arduino_fd, TCIFLUSH);
	
	/* Write 1 byte request */
	int bytes_written = write(arduino_fd, REQUEST, sizeof(REQUEST));
	if (bytes_written < 0)
	{
		*l = 0xFF;
		*c = 0xFF;
		*r = 0xFF;
		return;
	}
	/* Small delay to give Arduino time */
	usleep (10000);
	
	/* Read 8 bytes from Arduino */
	memset(read_buf, 0, sizeof(read_buf));
	int num_bytes = read(arduino_fd, read_buf, sizeof(read_buf));
	
	/* If error, set data to "invalid" */
	if (num_bytes < 0)
	{
		*l = 0xFF;
		*c = 0xFF;
		*r = 0xFF;
		return;
	}
	/* If nothing received, set data to "invalid" */
	else if (num_bytes == 0)
	{
		*l = 0xFF;
		*c = 0xFF;
		*r = 0xFF;
		return;
	}
	/* If less than 8 bytes received, set data to "invalid" */
	else if (num_bytes != PACKETLEN)
	{
		*l = 0xFF;
		*c = 0xFF;
		*r = 0xFF;
		return;
	}
	
	/* If START and STOP bytes are incorrect, packet is most 
	 *   likely also incorrect, set data to "invalid"
	 */
	if ((unsigned char)read_buf[idx_start] != START || (unsigned char)read_buf[idx_stop] != STOP)
	{
		*l = 0xFF;
		*c = 0xFF;
		*r = 0xFF;
		return;
	}
	
	/* If any sensor ID byte is incorrect, packet is most
	 *   likely also incorrect, set data to "invalid"
	 */
	if ((unsigned char)read_buf[idx_leftid] != LEFT ||
		(unsigned char)read_buf[idx_centerid] != CENTER ||
		(unsigned char)read_buf[idx_rightid] != RIGHT)
	{
		*l = 0xFF;
		*c = 0xFF;
		*r = 0xFF;
		return;
	}
	
	/* If packet is correct length and well-formatted,
	 *   set data to their corresponding values
	 */
	*l = (uint8_t)(unsigned char)read_buf[idx_leftdata];
	*c = (uint8_t)(unsigned char)read_buf[idx_centerdata];
	*r = (uint8_t)(unsigned char)read_buf[idx_rightdata];
}






