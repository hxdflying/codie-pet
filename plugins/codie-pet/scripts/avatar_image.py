from __future__ import annotations

import binascii
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class RgbaImage:
    width: int
    height: int
    pixels: bytes

    def crop(
        self,
        left: int | tuple[int, int, int, int],
        top: int | None = None,
        right: int | None = None,
        bottom: int | None = None,
    ) -> "RgbaImage":
        if isinstance(left, tuple):
            left, top, right, bottom = left
        if top is None or right is None or bottom is None:
            raise TypeError("crop needs left, top, right, and bottom")
        if left < 0 or top < 0 or right > self.width or bottom > self.height:
            raise ValueError("crop box is outside the image")
        out = bytearray()
        for y in range(top, bottom):
            start = (y * self.width + left) * 4
            end = (y * self.width + right) * 4
            out.extend(self.pixels[start:end])
        return RgbaImage(right - left, bottom - top, bytes(out))


def new_rgba(width: int, height: int, color: tuple[int, int, int, int]) -> RgbaImage:
    return RgbaImage(width, height, bytes(color) * (width * height))


def read_png(path: Path) -> RgbaImage:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("missing PNG signature")

    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    idat = bytearray()
    palette: list[tuple[int, int, int]] = []
    transparency = b""

    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_start = offset + 8
        chunk_end = chunk_start + length
        crc_end = chunk_end + 4
        if crc_end > len(data):
            raise ValueError("truncated PNG chunk data")
        chunk_data = data[chunk_start:chunk_end]
        expected_crc = struct.unpack(">I", data[chunk_end:crc_end])[0]
        actual_crc = binascii.crc32(chunk_type)
        actual_crc = binascii.crc32(chunk_data, actual_crc) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"bad PNG CRC for {chunk_type.decode('ascii', 'replace')}")

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
        elif chunk_type == b"PLTE":
            palette = [
                tuple(chunk_data[index : index + 3])
                for index in range(0, len(chunk_data), 3)
            ]
        elif chunk_type == b"tRNS":
            transparency = chunk_data
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break
        offset = crc_end

    if width is None or height is None or bit_depth is None or color_type is None:
        raise ValueError("missing PNG IHDR")
    if bit_depth != 8:
        raise ValueError(f"unsupported PNG bit depth {bit_depth}")
    if interlace != 0:
        raise ValueError("interlaced PNGs are not supported")

    channels_by_type = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
    if color_type not in channels_by_type:
        raise ValueError(f"unsupported PNG color type {color_type}")
    channels = channels_by_type[color_type]
    row_bytes = width * channels
    raw = zlib.decompress(bytes(idat))
    expected = (row_bytes + 1) * height
    if len(raw) != expected:
        raise ValueError("PNG image data length does not match IHDR")

    rows: list[bytes] = []
    previous = bytes(row_bytes)
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor : cursor + row_bytes])
        cursor += row_bytes
        _unfilter_row(row, previous, channels, filter_type)
        rows.append(bytes(row))
        previous = bytes(row)

    rgba = bytearray()
    for row in rows:
        for index in range(0, len(row), channels):
            if color_type == 0:
                gray = row[index]
                rgba.extend((gray, gray, gray, 255))
            elif color_type == 2:
                rgba.extend((row[index], row[index + 1], row[index + 2], 255))
            elif color_type == 3:
                palette_index = row[index]
                try:
                    red, green, blue = palette[palette_index]
                except IndexError as exc:
                    raise ValueError("PNG palette index is out of range") from exc
                alpha = transparency[palette_index] if palette_index < len(transparency) else 255
                rgba.extend((red, green, blue, alpha))
            elif color_type == 4:
                gray = row[index]
                alpha = row[index + 1]
                rgba.extend((gray, gray, gray, alpha))
            elif color_type == 6:
                rgba.extend(row[index : index + 4])

    return RgbaImage(width, height, bytes(rgba))


def _unfilter_row(row: bytearray, previous: bytes, bpp: int, filter_type: int) -> None:
    if filter_type == 0:
        return
    for index in range(len(row)):
        left = row[index - bpp] if index >= bpp else 0
        up = previous[index]
        up_left = previous[index - bpp] if index >= bpp else 0
        if filter_type == 1:
            row[index] = (row[index] + left) & 0xFF
        elif filter_type == 2:
            row[index] = (row[index] + up) & 0xFF
        elif filter_type == 3:
            row[index] = (row[index] + ((left + up) // 2)) & 0xFF
        elif filter_type == 4:
            row[index] = (row[index] + _paeth(left, up, up_left)) & 0xFF
        else:
            raise ValueError(f"unsupported PNG filter {filter_type}")


def _paeth(left: int, up: int, up_left: int) -> int:
    predictor = left + up - up_left
    distances = (
        (abs(predictor - left), left),
        (abs(predictor - up), up),
        (abs(predictor - up_left), up_left),
    )
    return min(distances, key=lambda item: item[0])[1]


def write_png(path: Path, image: RgbaImage) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scanlines = bytearray()
    stride = image.width * 4
    for y in range(image.height):
        scanlines.append(0)
        start = y * stride
        scanlines.extend(image.pixels[start : start + stride])

    ihdr = struct.pack(">IIBBBBB", image.width, image.height, 8, 6, 0, 0, 0)
    data = bytearray(PNG_SIGNATURE)
    data.extend(_png_chunk(b"IHDR", ihdr))
    data.extend(_png_chunk(b"IDAT", zlib.compress(bytes(scanlines), level=9)))
    data.extend(_png_chunk(b"IEND", b""))
    path.write_bytes(bytes(data))


def _png_chunk(chunk_type: bytes, chunk_data: bytes) -> bytes:
    crc = binascii.crc32(chunk_type)
    crc = binascii.crc32(chunk_data, crc) & 0xFFFFFFFF
    return (
        struct.pack(">I", len(chunk_data))
        + chunk_type
        + chunk_data
        + struct.pack(">I", crc)
    )


def pad_to_canvas(image: RgbaImage, canvas_size: tuple[int, int]) -> RgbaImage:
    canvas_w, canvas_h = canvas_size
    if image.width > canvas_w or image.height > canvas_h:
        raise ValueError("image is larger than the target canvas")
    canvas = bytearray(new_rgba(canvas_w, canvas_h, (255, 255, 255, 255)).pixels)
    paste_rgba(canvas, canvas_w, image, (canvas_w - image.width) // 2, (canvas_h - image.height) // 2)
    return RgbaImage(canvas_w, canvas_h, bytes(canvas))


def paste_rgba(target: bytearray, target_width: int, source: RgbaImage, x: int, y: int) -> None:
    for sy in range(source.height):
        for sx in range(source.width):
            src_index = (sy * source.width + sx) * 4
            dst_index = ((y + sy) * target_width + (x + sx)) * 4
            red, green, blue, alpha = source.pixels[src_index : src_index + 4]
            if alpha == 255:
                target[dst_index : dst_index + 4] = bytes((red, green, blue, 255))
            elif alpha:
                inv = 255 - alpha
                target[dst_index] = (red * alpha + target[dst_index] * inv) // 255
                target[dst_index + 1] = (green * alpha + target[dst_index + 1] * inv) // 255
                target[dst_index + 2] = (blue * alpha + target[dst_index + 2] * inv) // 255
                target[dst_index + 3] = 255


def write_gif(path: Path, frames: list[RgbaImage], duration_ms: int) -> None:
    if not frames:
        raise ValueError("GIF needs at least one frame")
    width, height = frames[0].width, frames[0].height
    if any(frame.width != width or frame.height != height for frame in frames):
        raise ValueError("all GIF frames must have the same size")

    path.parent.mkdir(parents=True, exist_ok=True)
    palette = _uniform_palette()
    delay = max(1, int(round(duration_ms / 10)))
    data = bytearray()
    data.extend(b"GIF89a")
    data.extend(struct.pack("<HHBBB", width, height, 0xF7, 0, 0))
    data.extend(palette)
    data.extend(b"\x21\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00")

    for frame in frames:
        indexed = _quantize_to_palette(frame)
        data.extend(b"\x21\xf9\x04\x08")
        data.extend(struct.pack("<H", delay))
        data.extend(b"\x00\x00")
        data.extend(b"\x2c")
        data.extend(struct.pack("<HHHHB", 0, 0, width, height, 0))
        data.append(8)
        encoded = _lzw_encode(indexed, min_code_size=8)
        for start in range(0, len(encoded), 255):
            chunk = encoded[start : start + 255]
            data.append(len(chunk))
            data.extend(chunk)
        data.append(0)

    data.append(0x3B)
    path.write_bytes(bytes(data))


def _uniform_palette() -> bytes:
    palette = bytearray()
    for red_bin in range(8):
        for green_bin in range(8):
            for blue_bin in range(4):
                palette.extend(
                    (
                        round(red_bin * 255 / 7),
                        round(green_bin * 255 / 7),
                        round(blue_bin * 255 / 3),
                    )
                )
    return bytes(palette)


def _quantize_to_palette(image: RgbaImage) -> bytes:
    indexes = bytearray()
    for offset in range(0, len(image.pixels), 4):
        red, green, blue, alpha = image.pixels[offset : offset + 4]
        if alpha < 255:
            inv = 255 - alpha
            red = (red * alpha + 255 * inv) // 255
            green = (green * alpha + 255 * inv) // 255
            blue = (blue * alpha + 255 * inv) // 255
        indexes.append(((red >> 5) << 5) | ((green >> 5) << 2) | (blue >> 6))
    return bytes(indexes)


def _lzw_encode(indexes: bytes, min_code_size: int) -> bytes:
    clear_code = 1 << min_code_size
    end_code = clear_code + 1
    dictionary = {(index,): index for index in range(clear_code)}
    next_code = end_code + 1
    code_size = min_code_size + 1
    writer = _BitWriter()

    def reset_dictionary() -> None:
        nonlocal dictionary, next_code, code_size
        dictionary = {(index,): index for index in range(clear_code)}
        next_code = end_code + 1
        code_size = min_code_size + 1

    writer.write(clear_code, code_size)
    current = (indexes[0],)
    for byte in indexes[1:]:
        candidate = current + (byte,)
        if candidate in dictionary:
            current = candidate
            continue
        writer.write(dictionary[current], code_size)
        if next_code < 4096:
            dictionary[candidate] = next_code
            next_code += 1
            if next_code > (1 << code_size) and code_size < 12:
                code_size += 1
        else:
            writer.write(clear_code, code_size)
            reset_dictionary()
        current = (byte,)

    writer.write(dictionary[current], code_size)
    writer.write(end_code, code_size)
    return writer.finish()


class _BitWriter:
    def __init__(self) -> None:
        self._bits = 0
        self._bit_count = 0
        self._out = bytearray()

    def write(self, code: int, size: int) -> None:
        self._bits |= code << self._bit_count
        self._bit_count += size
        while self._bit_count >= 8:
            self._out.append(self._bits & 0xFF)
            self._bits >>= 8
            self._bit_count -= 8

    def finish(self) -> bytes:
        if self._bit_count:
            self._out.append(self._bits & 0xFF)
            self._bits = 0
            self._bit_count = 0
        return bytes(self._out)


class _BitReader:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._cursor = 0
        self._bits = 0
        self._bit_count = 0

    def read(self, size: int) -> int | None:
        while self._bit_count < size:
            if self._cursor >= len(self._data):
                return None
            self._bits |= self._data[self._cursor] << self._bit_count
            self._cursor += 1
            self._bit_count += 8

        mask = (1 << size) - 1
        code = self._bits & mask
        self._bits >>= size
        self._bit_count -= size
        return code


def inspect_gif(path: Path) -> tuple[tuple[int, int], int]:
    data = path.read_bytes()
    if not (data.startswith(b"GIF87a") or data.startswith(b"GIF89a")):
        raise ValueError("missing GIF signature")
    if len(data) < 13:
        raise ValueError("truncated GIF header")
    width, height, packed, _, _ = struct.unpack("<HHBBB", data[6:13])
    offset = 13
    if packed & 0x80:
        offset += 3 * (2 ** ((packed & 0x07) + 1))
    frame_count = 0
    while offset < len(data):
        marker = data[offset]
        offset += 1
        if marker == 0x3B:
            return (width, height), frame_count
        if marker == 0x21:
            offset += 1
            offset = _skip_sub_blocks(data, offset)
        elif marker == 0x2C:
            if offset + 9 > len(data):
                raise ValueError("truncated GIF image descriptor")
            _, _, frame_w, frame_h, image_packed = struct.unpack("<HHHHB", data[offset : offset + 9])
            if frame_w != width or frame_h != height:
                raise ValueError("GIF image frame size differs from logical screen")
            offset += 9
            if image_packed & 0x80:
                offset += 3 * (2 ** ((image_packed & 0x07) + 1))
            if offset >= len(data):
                raise ValueError("truncated GIF image data")
            min_code_size = data[offset]
            offset += 1
            image_data, offset = _read_sub_blocks(data, offset)
            _validate_gif_lzw(image_data, min_code_size, frame_w * frame_h)
            frame_count += 1
        else:
            raise ValueError(f"unexpected GIF block marker 0x{marker:02x}")
    raise ValueError("missing GIF trailer")


def _read_sub_blocks(data: bytes, offset: int) -> tuple[bytes, int]:
    blocks = bytearray()
    while True:
        if offset >= len(data):
            raise ValueError("truncated GIF sub-block")
        length = data[offset]
        offset += 1
        if length == 0:
            return bytes(blocks), offset
        if offset + length > len(data):
            raise ValueError("truncated GIF sub-block")
        blocks.extend(data[offset : offset + length])
        offset += length


def _skip_sub_blocks(data: bytes, offset: int) -> int:
    while True:
        if offset >= len(data):
            raise ValueError("truncated GIF sub-block")
        length = data[offset]
        offset += 1
        if length == 0:
            return offset
        if offset + length > len(data):
            raise ValueError("truncated GIF sub-block")
        offset += length


def _validate_gif_lzw(data: bytes, min_code_size: int, expected_pixels: int) -> None:
    if min_code_size < 2 or min_code_size > 8:
        raise ValueError(f"unsupported GIF LZW minimum code size {min_code_size}")
    clear_code = 1 << min_code_size
    end_code = clear_code + 1
    reader = _BitReader(data)

    dictionary: dict[int, bytes]
    next_code: int
    code_size: int

    def reset_dictionary() -> None:
        nonlocal dictionary, next_code, code_size
        dictionary = {index: bytes((index,)) for index in range(clear_code)}
        next_code = end_code + 1
        code_size = min_code_size + 1

    reset_dictionary()
    previous: bytes | None = None
    decoded_pixels = 0

    while True:
        code = reader.read(code_size)
        if code is None:
            raise ValueError("missing GIF LZW end code")
        if code == clear_code:
            reset_dictionary()
            previous = None
            continue
        if code == end_code:
            break

        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code and previous is not None:
            entry = previous + previous[:1]
        else:
            raise ValueError(f"invalid GIF LZW code {code}")

        decoded_pixels += len(entry)
        if decoded_pixels > expected_pixels:
            raise ValueError("GIF LZW decoded too many pixels")

        if previous is not None and next_code < 4096:
            dictionary[next_code] = previous + entry[:1]
            next_code += 1
            if next_code == (1 << code_size) and code_size < 12:
                code_size += 1

        previous = entry

    if decoded_pixels != expected_pixels:
        raise ValueError(
            f"GIF LZW decoded {decoded_pixels} pixels, expected {expected_pixels}"
        )
