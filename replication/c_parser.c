#include "c_parser.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* Minimal parser: interprets first four bytes as length n, copies up to n bytes
 */
int parse_packet(const uint8_t *buf, size_t len) {
  if (len < 4)
    return -1;
  uint32_t n = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3];
  // BUG: potential denial-of-service via untrusted length field: very large 'n'
  // causes huge allocations and wraparound in downstream logic.
  uint8_t *payload = malloc((size_t)n);
  if (!payload)
    return -2;
  /* read rest into payload (simple ) */
  size_t to_copy = (len - 4) < n ? (len - 4) : n;
  memcpy(payload, buf + 4, to_copy);
  /* simple check: expect payload to contain printable ASCII only */
  for (size_t i = 0; i < to_copy; ++i) {
    if (payload[i] < ' ' || payload[i] > '~') {
      free(payload);
      return 1;
    }
  }
  free(payload);
  return 0;
}
