#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace tecnohead_meter_reader {

inline char hex_digit(uint8_t value) {
  return value < 10 ? static_cast<char>('0' + value) : static_cast<char>('A' + value - 10);
}

inline std::string hex_compact(const std::vector<uint8_t> &bytes) {
  std::string result;
  result.reserve(bytes.size() * 2);
  for (const uint8_t value : bytes) {
    result.push_back(hex_digit(static_cast<uint8_t>(value >> 4)));
    result.push_back(hex_digit(static_cast<uint8_t>(value & 0x0F)));
  }
  return result;
}

inline std::string hex_preview(const std::vector<uint8_t> &bytes, size_t limit = 96) {
  const size_t count = bytes.size() < limit ? bytes.size() : limit;
  std::string result;
  result.reserve(count * 3 + 32);
  for (size_t index = 0; index < count; index++) {
    if (index != 0) {
      result.push_back(' ');
    }
    result.push_back(hex_digit(static_cast<uint8_t>(bytes[index] >> 4)));
    result.push_back(hex_digit(static_cast<uint8_t>(bytes[index] & 0x0F)));
  }
  if (bytes.size() > count) {
    result += " ... (+" + std::to_string(bytes.size() - count) + " bytes)";
  }
  return result;
}

inline std::string ascii_preview(const std::vector<uint8_t> &bytes, size_t limit = 96) {
  const size_t count = bytes.size() < limit ? bytes.size() : limit;
  std::string result;
  result.reserve(count * 4 + 32);
  for (size_t index = 0; index < count; index++) {
    const uint8_t value = bytes[index];
    if (value >= 0x20 && value <= 0x7E && value != '\\' && value != '"') {
      result.push_back(static_cast<char>(value));
    } else {
      result += "\\x";
      result.push_back(hex_digit(static_cast<uint8_t>(value >> 4)));
      result.push_back(hex_digit(static_cast<uint8_t>(value & 0x0F)));
    }
  }
  if (bytes.size() > count) {
    result += " ... (+" + std::to_string(bytes.size() - count) + " bytes)";
  }
  return result;
}

inline std::string json_escape(const std::string &value) {
  std::string result;
  result.reserve(value.size() + 8);
  for (const char character : value) {
    switch (character) {
      case '\\':
        result += "\\\\";
        break;
      case '"':
        result += "\\\"";
        break;
      case '\n':
        result += "\\n";
        break;
      case '\r':
        result += "\\r";
        break;
      case '\t':
        result += "\\t";
        break;
      default:
        result.push_back(character);
        break;
    }
  }
  return result;
}

inline std::string parity_label(const std::string &value) {
  if (value == "Par") {
    return "E";
  }
  if (value == "Ímpar") {
    return "O";
  }
  return "N";
}

inline std::string uart_label(const std::string &baud, const std::string &parity, const std::string &data_bits,
                             const std::string &stop_bits) {
  return baud + " " + data_bits + parity_label(parity) + stop_bits;
}

inline std::string passive_analysis(const std::vector<uint8_t> &bytes) {
  if (bytes.empty()) {
    return "Sem quadro para analisar.";
  }
  bool has_crlf = false;
  bool has_stx = false;
  bool has_etx = false;
  for (size_t index = 0; index < bytes.size(); index++) {
    has_crlf = has_crlf || (index > 0 && bytes[index - 1] == 0x0D && bytes[index] == 0x0A);
    has_stx = has_stx || bytes[index] == 0x02;
    has_etx = has_etx || bytes[index] == 0x03;
  }
  if (bytes.front() == 0x7E) {
    return "Hipótese passiva: início 0x7E compatível com framing HDLC/DLMS; não confirmado.";
  }
  if (has_stx && has_etx) {
    return "Hipótese passiva: par STX/ETX observado; framing genérico, protocolo não confirmado.";
  }
  if (has_crlf) {
    return "Hipótese passiva: delimitador CRLF observado; pode ser texto/IEC, sem confirmação de ABNT.";
  }
  return "RAW: sem indício de framing conhecido nesta amostra; nenhum protocolo foi confirmado.";
}

}  // namespace tecnohead_meter_reader
