from escpos.printer import Usb, Dummy

class PrinterService:
    """
    A service to handle printing operations.
    It sends print jobs to a physical USB printer and also logs the job
    to the console using a dummy printer.
    """
    def __init__(self):
        # =================================================================
        # ===           PRINTER CONFIGURATION - EDIT THIS!              ===
        # =================================================================
        #
        # Find your printer's Vendor ID (VID) and Product ID (PID)
        # and replace the placeholder values below.
        #
        # The '0x' prefix is important!
        #
        VENDOR_ID = 0x04b8  # <-- REPLACE THIS VALUE
        PRODUCT_ID = 0x0202 # <-- REPLACE THIS VALUE
        #
        # --- Advanced Settings ---
        # If you still have issues, you may need to change the output endpoint.
        # Common values are 0x01 (the default), 0x02, or 0x03.
        OUTPUT_ENDPOINT = 0x02 # <-- TRY CHANGING THIS if needed
        # =================================================================
        
        self._dummy_printer = Dummy()
        try:
            self._usb_printer = Usb(VENDOR_ID, PRODUCT_ID, out_ep=OUTPUT_ENDPOINT)
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
