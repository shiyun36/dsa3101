import os
import ocrmypdf

def process_pdf(input_pdf_path, output_pdf_path):
    """
    Processes a PDF file.
    """
    if os.path.exists(output_pdf_path):
        print(f"Skipping '{input_pdf_path}': already processed.")
        return

    print(f"Processing '{input_pdf_path}'...")
    try:
        # Force OCR even if the PDF is already tagged.
        ocrmypdf.ocr(input_pdf_path, output_pdf_path, force_ocr=True)
        print(f"Saved OCR version to '{output_pdf_path}'.")
    except Exception as e:
        print(f"Error processing '{input_pdf_path}': {e}")

def process_folder(input_root, output_root):
    for filename in os.listdir(input_root):
        print("Found file:", filename)

    # Iterate over each industry folder in the input root
    for industry in os.listdir(input_root):
        industry_path = os.path.join(input_root, industry)
        if not os.path.isdir(industry_path):
            continue

        # Iterate over each region folder within the industry folder
        for region in os.listdir(industry_path):
            region_path = os.path.join(industry_path, region)
            if not os.path.isdir(region_path):
                continue

            # Create the corresponding output directory if it doesn't exist.
            output_dir = os.path.join(output_root, industry, region)
            os.makedirs(output_dir, exist_ok=True)

            # Process all PDF files in this region folder.
            for filename in os.listdir(region_path):
                if filename.lower().endswith('.pdf'):
                    input_pdf = os.path.join(region_path, filename)
                    base_name = os.path.splitext(filename)[0]
                    output_pdf = os.path.join(output_dir, f"{base_name}_ocr.pdf")
                    process_pdf(input_pdf, output_pdf)

if __name__ == '__main__':
    
    # Parent folder containing both raw_esg and ocr_esg
    parent_dir = r"Datasets"
    input_root_dir = os.path.join(parent_dir, "raw_esg")
    output_root_dir = os.path.join(parent_dir, "ocr_esg")
    
    process_folder(input_root_dir, output_root_dir)