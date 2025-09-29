#ifndef C_PARSER_H
#define C_PARSER_H
#include <stddef.h>
#include <stdint.h>

int parse_packet(const uint8_t *buf, size_t len);

#endif
