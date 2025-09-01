from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        #logo
        self.image('Reportes/logo_vertical.png',15,0,20)
        # fuente
        self.set_font('helvetica','B',20)
        #titulo
        self.cell(0, 20, 'Titulo', border= True, ln=1, align='C')
        self.ln(20)



pdf = PDF('P','mm','Letter')

# Set auto page break
pdf.set_auto_page_break(auto=True, margin=15)

pdf.add_page()

# Especificando fuentes
pdf.set_font('helvetica','',16)

# Agregar texto
# w = width
# h = height
# text
pdf.cell(40, 10, 'Hello World!')
pdf.cell(80, 10, 'Good Bye World!')

for i in range(1, 41):
    pdf.cell(0, 10, f'Esta es la linea {i} :D', ln=True)


pdf.output('pdf_1.pdf')