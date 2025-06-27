import matplotlib.pyplot as plt
import io
from PIL import Image

def line_plot(x, y, title="Graph", xlabel="X", ylabel="Y"):
    plt.figure()
    plt.plot(x, y)          # no custom colors
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return Image.open(buf)

