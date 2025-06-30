from ifmta.ifta import Ifta
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from automatic_sizing import zero_pad

img_path = "assets/christofou.jpg"

img = Image.open(img_path).convert("L")
img.thumbnail((256,256),Image.LANCZOS)
img = np.array(img)
img = img/img.max()
img = zero_pad(np.array([img]), (512,512)).squeeze()



eod = Ifta(img)

plt.imshow(eod[-1])
plt.imsave("assets/eod.png", eod[-1])
plt.show()

img = Image.open("assets/eod.png")
img = np.array(img)
print(img.shape)
