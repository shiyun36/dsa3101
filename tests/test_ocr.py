import ocrmypdf

def test_ocrmypdf(input_file, output_file):
    print("Starting OCR process...")
    try:
        # Process the PDF with OCR; this might take a few seconds.
        result = ocrmypdf.ocr(input_file, output_file, deskew=True, force_ocr=True)
        print("OCR processing completed successfully!")
        print("Result:", result)  # Note: ocrmypdf.ocr may return None if successful.
    except Exception as e:
        print(f"Error during OCR: {e}")

if __name__ == "__main__":
    # Use absolute paths or confirm that these files are in the current directory.
    test_ocrmypdf("2023-2024_Sustainability_Report_(ENG)_.pdf", "LGoutput.pdf")