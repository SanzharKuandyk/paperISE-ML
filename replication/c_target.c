#include "c_parser.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* Small harness: read up to 8192 bytes from stdin and call parse_packet.
   Returns exit code 0 on normal completion, non-zero if parse_packet indicates
   a problem. */

int main(void) {
  size_t cap = 8192;
  uint8_t *buf = (uint8_t *)malloc(cap);
  if (!buf)
    return 2;
  size_t readn = fread(buf, 1, cap, stdin);
  int r = parse_packet(buf, readn);
  free(buf);
  if (r == 0)
    return 0;
  return 1;
}
