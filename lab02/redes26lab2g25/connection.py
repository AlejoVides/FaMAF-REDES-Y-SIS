# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from base64 import b64encode
import logging
import os
import errno

from constants import (
    BAD_EOL,
    BAD_OFFSET,
    BAD_REQUEST,
    CODE_OK,
    COMMANDS,
    CONTENT_LENGTH_PREFIX,
    EOL,
    FILE_NOT_FOUND,
    INTERNAL_ERROR,
    INVALID_ARGUMENTS,
    INVALID_COMMAND,
    error_messages,
#    fatal_status,
)

logger = logging.getLogger(__name__)

EOL_BYTES = EOL.encode("ascii")
NEWLINE_BYTES = b"\n"
MAX_LINE_LENGTH = 1024 * 10

class Connection:
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, sock: socket.socket, directory: str) -> None:
        self.socket = sock
        self.directory = directory
        self.buffer = b""

    def handle(self) -> None:
        """
        Atiende eventos de la conexión hasta que termina.
        """
        handlers = {
            "get_file_listing": self._get_file_listing,
            "get_metadata": self._get_metadata,
            "get_slice": self._get_slice,
            "help": self._help,
            "quit": self._quit,
        }
        while True:
            if self._read_bytes():
                logger.info("Client disconnected")
                break
            if EOL_BYTES not in self.buffer:
                logger.warning("Line too long, closing connection")
                self._send_response(BAD_REQUEST)
                break
            line, _, self.buffer = self.buffer.partition(EOL_BYTES)
            if NEWLINE_BYTES in line:
                logger.warning("Bad EOL detected, closing connection")
                self._send_response(BAD_EOL)
                break
            command = line.decode("ascii").split()
            if not command:
                logger.warning("Empty command line, closing connection")
                self._send_response(BAD_REQUEST)
                break
            if command[0] not in COMMANDS:
                logger.warning("Invalid command received: %s", command[0])
                self._send_response(INVALID_COMMAND)
            else:
                try:
                    logger.info("Request: %s", " ".join(command))
                    handlers[command[0]](command[1:])
                    if command[0] == "quit" and not command[1:]:
                        logger.info("Closing connection...")
                        break
                except Exception as e:
                    logger.error("Internal error while handling command: %s", e)
                    self._send_response(INTERNAL_ERROR)
                    break
        self.socket.close()

    def _read_bytes(self) -> bool:
        """
        Lee bytes del socket y los acumula en el buffer hasta encontrar
        un EOL o alcanzar el límite máximo de línea.
        Retorna True si el cliente cerró la conexión, False en caso contrario.
        """
        while EOL_BYTES not in self.buffer and len(self.buffer) < MAX_LINE_LENGTH:
            data = self.socket.recv(MAX_LINE_LENGTH)
            if data == b"":
                return True
            self.buffer += data
        return False

    def _send_response(self, code: int, lines: list[str] = None) -> None:
        """
        Envía una respuesta al cliente formada por una línea de estado
        y opcionalmente líneas de contenido adicionales. Si se proporciona
        `lines`, se unen separadas por EOL formando el payload.
        """
        status_line = f"{code} {error_messages[code]}{EOL}"
        payload = EOL.join(lines) + EOL if lines else ""
        self.socket.sendall((status_line + payload).encode("ascii"))

    def _send_raw_response(self, code: int, headers: dict[str, str], data: bytes) -> None:
        """
        Envía una respuesta en modo raw al cliente, construyendo
        la línea de estado seguida de los headers (uno por línea)
        y luego enviando los datos binarios sin modificación.
        """
        status_line = f"{code} {error_messages[code]}{EOL}"
        headers_str = "".join(f"{k} {v}{EOL}" for k, v in headers.items()) + EOL
        self.socket.sendall((status_line + headers_str).encode("ascii"))
        self.socket.sendall(data)

    def _get_file_listing(self, args: list[str]) -> None:
        if args:
            logger.warning("get_file_listing takes no arguments")
            self._send_response(INVALID_ARGUMENTS)
        else:
            self._send_response(CODE_OK, os.listdir(self.directory) + [""])

    def _get_metadata(self, args: list[str]) -> None:
        if not args:
            logger.warning("get_metadata requires a filename argument")
            self._send_response(INVALID_ARGUMENTS)
        elif len(args) == 1:
            try:
                file = os.path.join(self.directory, args[0])
                size = os.path.getsize(file)
                self._send_response(CODE_OK, [str(size)])
            except OSError as e:
                 if e.errno in (errno.ENOENT, errno.ENAMETOOLONG):
                     logger.warning("File not found or name too long: %s", args[0])
                     self._send_response(FILE_NOT_FOUND)
                 else:
                     raise  # otros errores suben a handle → INTERNAL_ERROR
        else:
            logger.warning("get_metadata takes exactly one argument")
            self._send_response(INVALID_ARGUMENTS)

    def _get_slice(self, args: list[str]) -> None:
        if len(args) not in (3, 4):
            logger.warning("get_slice takes exactly three or four arguments")
            self._send_response(INVALID_ARGUMENTS)
        elif len(args) == 4 and args[3] != "raw":
            logger.warning("Invalid raw token: %s", args[3])
            self._send_response(INVALID_ARGUMENTS)
        else:
            if (not args[1].isdigit() or not args[2].isdigit()):
                logger.warning("get_slice requires offset and length to be integers")
                self._send_response(INVALID_ARGUMENTS)
                return
            try:
                file = os.path.join(self.directory, args[0])
                if (int(args[1]) + int(args[2])) > os.path.getsize(file):
                    logger.warning("get_slice offset and length exceed file size")
                    self._send_response(BAD_OFFSET)
                    return
                with open(file, 'rb') as f:
                    f.seek(int(args[1]))
                    data = f.read(int(args[2]))
                if len(args) == 3: # modo base64
                    self._send_response(CODE_OK, [b64encode(data).decode("ascii")])
                else: # modo raw
                    self._send_raw_response(CODE_OK, {CONTENT_LENGTH_PREFIX:args[2]}, data)
            except OSError as e:
                 if e.errno in (errno.ENOENT, errno.ENAMETOOLONG):
                     logger.warning("File not found or name too long: %s", args[0])
                     self._send_response(FILE_NOT_FOUND)
                 else:
                     raise  # otros errores suben a handle → INTERNAL_ERROR

    def _help(self, args: list[str]) -> None:
        if args:
            logger.warning("help takes no arguments")
            self._send_response(INVALID_ARGUMENTS)
        else:
            self._send_response(CODE_OK, COMMANDS + [""])

    def _quit(self, args: list[str]) -> None:
        if args:
            logger.warning("quit takes no arguments")
            self._send_response(INVALID_ARGUMENTS)
        else:
            self._send_response(CODE_OK)
