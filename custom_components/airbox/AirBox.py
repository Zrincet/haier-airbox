#!/usr/bin/python
import socket
import threading
import time
import select
import logging

_LOGGER = logging.getLogger(__name__)


class device(object):
    def __init__(self, host):
        self.host = host
        self.port = 56800
        self.cs = None
        self.mac = self.connect()
        self.lock = threading.Lock()
        self.learning_packet = [
            0x00, 0x00, 0x27, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0xFF, 0xFF, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
            0x4D, 0x02, 0x5A]
        self.ir_packet = [
            0x00, 0x00, 0x65, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x6c, 0x00, 0x00, 0x00, 0x55, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA,
            0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0x00, 0x00, 0x00, 0x00]
        self.req_packet = [
            0x00, 0x00, 0x27, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0xFF, 0xFF, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
            0x4D, 0x01, 0x59]

    def get_mac(self):
        return self.mac

    def send_packet(self, data):
        try:
            is_tx_cpl = self.cs.sendall(data)
        except Exception as err:
            self.cs.close()
            self.connect()
            is_tx_cpl = self.cs.sendall(data)
        finally:
            pass
        if is_tx_cpl is not None:
            _LOGGER.error("TX error: %s", is_tx_cpl)
            return None
        response = []
        with self.lock:
            while True:
                ready_to_read, ready_to_write, in_error = \
                    select.select([self.cs], [], [], 3.0)
                if ready_to_read:
                    _data = self.cs.recv(512)
                    if _data:
                        response.append(_data)
                else:
                    break
        return response

    def check_sensor(self):
        try:
            self.req_packet[40:52] = self.mac
            response = self.send_packet(bytes(self.req_packet))
            if response:
                self.close()
                return response
            self.close()
            return False
        except Exception as erro:
            _LOGGER.error(str(erro))
            self.close()
            return False

    def send_ir(self, data):
        try:
            self.ir_packet[48:60] = self.mac
            data_len = len(data) + 48
            self.ir_packet[15] = (data_len % 256)
            self.ir_packet[14] = (data_len // 256)
            response = self.send_packet(bytes(self.ir_packet) + data)
            if response:
                self.close()
                return response
            self.close()
            return False
        except Exception as erro:
            self.close()
            return False

    def find_ir_packet(self):
        try:
            # with self.lock:
            while True:
                ready_to_read, ready_to_write, in_error = \
                    select.select([self.cs], [], [], 5.0)
                if ready_to_read:
                    _data = self.cs.recv(1024)
                    if _data:
                        if _data[2] == 0x65 and _data[3] == 0xFE:
                            self.close()
                            return _data
                else:
                    break
            self.close()
            return False
        except Exception as erro:
            self.close()
            return False

    def enter_learning(self):
        try:
            self.learning_packet[40:52] = self.mac
            response = self.send_packet(bytes(self.learning_packet))
            if response:
                return response
            self.close()
            return False
        except Exception as erro:
            self.close()
            return False

    def connect(self):
        try:
            self.cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cs.settimeout(5.0)
            self.cs.connect((self.host, self.port))
            mac_packet = self.cs.recv(512)
            mac = None
            if len(mac_packet) == 95:
                mac = list(mac_packet[40:52])
            self.cs.recv(512)  # 每当建立连接时服务器会直接回复2帧数据，先过滤掉
            return mac
        except Exception as erro:
            self.close()
            return False

    def close(self):
        try:
            self.cs.close()
        except Exception as erro:
            pass

    def getSensor(self):
        response = []
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            cs.settimeout(5.0)
            cs.connect((self.host, self.port))
            mac_packet = cs.recv(512)
            mac = None
            if len(mac_packet) == 95:
                mac = list(mac_packet[40:52])
            cs.recv(512)
            self.req_packet[40:52] = mac
            is_tx_cpl = cs.sendall(bytes(self.req_packet))
            while True:
                ready_to_read, ready_to_write, in_error = \
                    select.select([cs], [], [], 3.0)
                if ready_to_read:
                    _data = cs.recv(512)
                    if _data:
                        response.append(_data)
                else:
                    break
        except Exception as e:
            _LOGGER.error(str(e))
        finally:
            cs.close()
        return response

