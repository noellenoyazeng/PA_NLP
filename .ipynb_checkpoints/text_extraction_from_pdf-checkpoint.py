def split_and_save_pdf(input_pdf_path: str, max_pages_per_file: int):
    # Create a folder to store the split PDFs
    output_folder = os.path.join(os.path.dirname(input_pdf_path), 'pdf_chunks')
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_paths = []
    
    # Open the input PDF
    with open(input_pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        
        # Calculate the number of files needed
        num_files = (num_pages + max_pages_per_file - 1) // max_pages_per_file
        
        # Split the PDF into multiple files
        for i in range(num_files):
            start_page = i * max_pages_per_file
            end_page = min((i + 1) * max_pages_per_file, num_pages)
            
            pdf_writer = PdfWriter()
            # Etract pages and add to tthe new PDF writer
            for page_num in range(start_page,end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            
            output_pdf_path = os.path.join(output_folder,f'pdf{i+1}.pdf')
            
            # Save the new PDF file
            with open(output_pdf_path, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
                
            print(f'Saved:{output_pdf_path}')
            pdf_paths.append(output_pdf_path)
            
    return pdf_paths
                
