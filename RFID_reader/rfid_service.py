#SPI multiple
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from std_srvs.srv import Trigger
#from pn532 import PN532_SPI
from RFID_reader.pn532 import PN532_SPI
import RPi.GPIO as GPIO

READER_CONFIG = {
    'Holder_1': 2,
    'Holder_2': 3,
    'Holder_3': 4,
    'Holder_4': 17,
    'Holder_5': 27,
    'Holder_6': 22,
#    'Holder_7': 14,
#    'Holder_8': 15,
#    'Holder_9': 18,
#    'Holder_10': 23,
#    'Holder_11': 24,
#    'Holder_12': 25,
#    'Holder_13': 1,
#    'Holder_14': 12,
#    'Holder_15': 16,
#    'Holder_16': 20,
#    'Holder_17': 21,
#    'Holder_18': 0,
#    'Holder_19': 5,
#    'Holder_20': 6,
#    'Holder_21': 13,
#    'Holder_22': 19,
#    'Holder_23': 26,
}

class RFIDService(Node):
    def __init__(self):
        super().__init__('rfid_service')
        self.readers = {}

        for reader_id, cs_pin in READER_CONFIG.items():
            try:
                pn532 = PN532_SPI(debug=False, reset=None, cs=cs_pin)
                ic, ver, rev, support = pn532.get_firmware_version()
                pn532.SAM_configuration()
                self.readers[reader_id] = pn532
                self.get_logger().info(f'Reader [{reader_id}] ready on  CS GPIO{cs_pin}')
            except Exception as e:
                self.get_logger().error(f'Reader [{reader_id}] not detected: {e}')
                self.readers[reader_id] = None

        # Service 1: scan all readers
        self.create_service(Trigger, 'scan_all', self.scan_all_callback)

        # Service 2: one trigger per reader
        for reader_id in self.readers:
            self.create_service(
                Trigger,
                f'scan_one/{reader_id}',
                lambda req, res, rid=reader_id: self.scan_one_callback(req, res, rid)
            )

        self.get_logger().info('RFID Service ready.')

    def _read_tag(self, reader_id):
        pn532 = self.readers.get(reader_id)
        if pn532 is None:
            return None, 'Reader not connected'
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            return '-'.join([hex(i) for i in uid]), None
        return None, 'No tag'

    def scan_all_callback(self, request, response):
        results = []
        for reader_id in self.readers:
            uid, error = self._read_tag(reader_id)
            results.append(f'{reader_id}:{uid if uid else error}')
        response.success = True
        response.message = '|'.join(results)
        self.get_logger().info(f'Scan all: {response.message}')
        return response

    def scan_one_callback(self, request, response, reader_id):
        uid, error = self._read_tag(reader_id)
        if uid:
            response.success = True
            response.message = f'{reader_id}:{uid}'
        else:
            response.success = False
            response.message = f'{reader_id}:{error}'
        self.get_logger().info(f'Scan one: {response.message}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = RFIDService()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try:
            rclpy.shutdown()
        except Exception:
            pass
        try:
            GPIO.cleanup()
        except Exception:
            pass

if __name__ == '__main__':
    main()
