#ifndef __ULTRASONIC_USB_HPP__
#define __ULTRASONIC_USB_HPP__

const char ARDUINO_PORT[] = "/dev/ttyACM0";

const uint8_t PACKETLEN = 8;
const uint8_t START		= 0xCA;
const uint8_t LEFT		= 0xD3;
const uint8_t CENTER	= 0xD5;
const uint8_t RIGHT		= 0xD7;
const uint8_t STOP		= 0xCB;

const uint8_t idx_start 	 = 0;
const uint8_t idx_leftid 	 = 1;
const uint8_t idx_leftdata 	 = 2;
const uint8_t idx_centerid 	 = 3;
const uint8_t idx_centerdata = 4;
const uint8_t idx_rightid 	 = 5;
const uint8_t idx_rightdata  = 6;
const uint8_t idx_stop 		 = 7;

const unsigned char REQUEST[] = { 0xBE };

int init_arduino (void);
void get_arduino_data (uint8_t *, uint8_t *, uint8_t *);


#endif /* __ULRASONIC_USB_HPP__ */
