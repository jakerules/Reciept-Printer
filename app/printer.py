from escpos.printer import Dummy

class PrinterService:
    """
    A service to handle printing operations.
    This implementation uses a 'dummy' printer that outputs to the console,
    allowing for development without a physical printer.
    """
    def __init__(self):
        self._printer = Dummy()

    def print_text(self, text: str):
        """
        Sends text to the dummy printer.
        """
        try:
            # The dummy printer doesn't output to stdout directly.
            # It writes to an internal buffer. We can inspect this buffer
            # for verification if needed, but for now, we'll just log
            # what we intend to print.
            print("--- Sending to Dummy Printer ---")
            print(text)
            print("--------------------------------")

            # These commands are what would be sent to a real printer.
            self._printer.text(text)
            self._printer.cut()

        except Exception as e:
            print(f"An error occurred with the printer service: {e}")

# Create a single, shared instance of the PrinterService.
printer_service = PrinterService()
