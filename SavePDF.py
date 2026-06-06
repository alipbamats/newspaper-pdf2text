import fitz  # PyMuPDF library

# Open the original PDF file
src_pdf = fitz.open("/home/user/Downloads/hakikat_2023-45.pdf")

# Create an empty, new PDF document
output_pdf = fitz.open()

# Insert a single page (from_page and to_page are inclusive, 0-based indices)
output_pdf.insert_pdf(src_pdf, from_page=0, to_page=3)

# Save the new PDF containing just that page
output_pdf.save("/home/user/Downloads/0_3_hakikat_2023-45.pdf")

# Close both files to free up system memory
output_pdf.close()
src_pdf.close()
