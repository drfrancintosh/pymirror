import subprocess

class PMFont:
	def __init__(self, font_name, font_size):
		self.font_name = font_name
		self.font_size = font_size
		pass

	def font_path(self):
		output = subprocess.check_output(["fc-list"], text=True)
		fonts = output.split("\n")
		for font in fonts:
			if self.font_name in font: return font.split(":")[0]
		return self.font_name

def main():
	pmfont = PMFont("DejaVuSans", 64)
	font_name = pmfont.font_path()
	print(font_name)

if __name__ == "__main__":
	main()
