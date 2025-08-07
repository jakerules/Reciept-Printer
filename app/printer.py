from escpos.printer import Usb, Dummy

class PrinterService:
    """
    A service to handle printing operations.
    It sends print jobs to a physical USB printer and also logs the job
    to the console using a dummy printer.
    """
    def __init__(self):
        # NOTE: You must replace these values with your printer's actual IDs!
        VENDOR_ID = 0x04b8  # CHANGE THIS
        PRODUCT_ID = 0x0202 # CHANGE THIS

        self._dummy_printer = Dummy()
        try:
            self._usb_printer = Usb(VENDOR_ID, PRODUCT_ID)
            print("--- Successfully connected to USB printer ---")
        except Exception as e:
            print(f"!!! WARNING: Could not connect to USB printer: {e}")
            print("!!! Printing will only be simulated in the console.")
            self._usb_printer = None

    def print_text(self, text: str):
        """
        Sends text to the USB printer (if available) and the dummy printer.
        """
        # Always print to the dummy printer for logging
        print("--- Logging to Dummy Printer ---")
        print(text)
        # You could also get the raw ESC/POS commands from the dummy printer
        # self._dummy_printer.text(text)
        # raw_commands = self._dummy_printer._read()
        print("--------------------------------")

        # Send to the physical USB printer if it was connected
        if self._usb_printer:
            try:
                print("--- Sending to USB Printer ---")
                self._usb_printer.text(text)
                self._usb_printer.cut()
                print("------------------------------")
            except Exception as e:
                print(f"!!! ERROR: Could not print to USB printer: {e}")

# Create a single, shared instance of the PrinterService.
printer_service = PrinterService()
